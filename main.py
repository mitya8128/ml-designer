import argparse
import ast
import re

from architecture.compiler import compile_semantic_model
from analyzer.main_pipeline import analyze_code
from analyzer.parser import is_valid_python
from analyzer.repo_analyzer import analyze_repository
from architecture.loader import load_architecture
from verifier.verifier import verify_architecture
from llm.factory import get_llm
from llm.services.code_generator import CodeGenerator
from system_prompt import SYSTEM_PROMPT
from pipelines.repo_pipeline import generate_and_refine_repository
from prompts.rebuild_arch_prompts import build_repair_prompt
from prompts.rebuild_code_generation_prompts import build_code_repair_prompt
from utils.yaml_utils import extract_yaml, normalize_yaml
from utils.code_utils import extract_code


DEFAULT_ARCH_PATH = "sessions/architecture.yaml"
DEFAULT_CODE_PATH = "sessions/generated_code.py"
DEFAULT_REPO_DIR = "sessions/generated_repo"


def flatten_errors(error_map):
    return sum(error_map.values(), [])


# =========================
# YAML SAFE NORMALIZATION
# =========================
def safe_normalize_yaml(text: str) -> str:
    try:
        return normalize_yaml(text)
    except Exception:
        return text


# =========================
# ANALYZER WRAPPER (SAFE)
# =========================
def analyze_generated_code(arch_path, code_path):

    print("\n=== Running Code Analyzer ===")

    # =====================
    # LOAD CODE
    # =====================
    try:
        with open(code_path) as f:
            code = f.read()
    except Exception as e:
        print("Failed to read code:", e)
        return {
            "errors": {
                "syntax": [f"Failed to read code: {e}"],
                "semantic": [],
                "architecture": []
            },
            "warnings": [],
            "metrics": {},
            "score": 0
        }

    # =====================
    # LOAD ARCH (optional)
    # =====================
    arch = None
    if arch_path is not None:
        try:
            arch = load_architecture(arch_path)
        except Exception:
            print("⚠️ Failed to load architecture, continuing without it")

    # =====================
    # SYNTAX CHECK
    # =====================
    valid, syntax_error = is_valid_python(code)

    if not valid:
        print("❌ Syntax error detected")

        result = {
            "errors": {
                "syntax": [f"Syntax error: {syntax_error}"],
                "semantic": [],
                "architecture": []
            },
            "warnings": [],
            "metrics": {},
            "score": 0
        }

    else:
        try:
            result = analyze_code(code, arch)

        except Exception as e:
            print("Analyzer failed:", e)

            result = {
                "errors": {
                    "syntax": [],
                    "semantic": [f"Analyzer error: {e}"],
                    "architecture": []
                },
                "warnings": [],
                "metrics": {},
                "score": 0
            }

    # =====================
    # PRINT RESULT
    # =====================
    print("\n=== ANALYSIS RESULT ===")
    print("Score:", result.get("score"))

    # ---- ERRORS (structured) ----
    print("\nErrors:")

    error_map = result.get("errors", {})

    for level, errs in error_map.items():
        if errs:
            print(f"\n[{level.upper()}]")
            for e in errs:
                print("-", e)

    # ---- WARNINGS ----
    print("\nWarnings:")
    for w in result.get("warnings", []):
        print("-", w)

    # ---- METRICS ----
    print("\nMetrics:")
    for k, v in result.get("metrics", {}).items():
        print(f"{k}: {v}")

    return result


# =========================
# CODE GENERATION + REPAIR LOOP
# =========================
def generate_and_refine_code(llm, arch_path, code_path, max_iters=3):

    generator = CodeGenerator(llm)

    # initial generation
    generator.generate_from_architecture(arch_path, code_path)

    for i in range(max_iters):

        print(f"\n=== Code analysis iteration {i+1} ===")

        result = analyze_generated_code(arch_path, code_path)

        error_map = result.get("errors", {})
        errors = flatten_errors(error_map)
        warnings = result.get("warnings", [])

        if not errors:
            print("✅ Code passed analysis")
            return

        print(f"❌ Found {len(errors)} errors, regenerating...")

        try:
            with open(code_path) as f:
                code = f.read()
        except Exception:
            code = ""

        repair_prompt = build_code_repair_prompt(code, errors, warnings)

        raw_output = llm.generate("", repair_prompt)
        new_code = extract_code(raw_output)

        with open(code_path, "w") as f:
            f.write(new_code)

    print("⚠️ Max refinement iterations reached")


# =========================
# ARCHITECTURE GENERATION LOOP
# =========================
def generate_architecture_loop(llm, user_prompt, arch_path, max_attempts):

    prompt = user_prompt

    best_arch = None
    best_errors = None
    best_yaml_text = None

    for attempt in range(max_attempts):

        print(f"\n=== Architecture generation attempt {attempt+1} ===")

        response = llm.generate(SYSTEM_PROMPT, prompt)

        yaml_text = extract_yaml(response)
        yaml_text = safe_normalize_yaml(yaml_text)

        with open(arch_path, "w") as f:
            f.write(yaml_text)

        try:
            arch = load_architecture(arch_path)
        except Exception as e:
            print("YAML parsing error:", e)
            prompt = build_repair_prompt(prompt, [str(e)])
            continue

        errors = verify_architecture(arch)

        if best_errors is None or len(errors) < len(best_errors):
            best_arch = arch
            best_errors = errors
            best_yaml_text = yaml_text

        if not errors:
            print("Architecture verified successfully")
            return arch

        print("Verification errors:")
        for e in errors:
            print("-", e)

        prompt = build_repair_prompt(prompt, errors)

    print("\n⚠️ Max attempts reached")

    if best_arch is not None:
        print(f"Using best candidate with {len(best_errors)} errors")

        with open(arch_path, "w") as f:
            f.write(best_yaml_text)

        return best_arch

    raise RuntimeError("Failed to generate any architecture")


# =========================
# MAIN ENTRYPOINT
# =========================
def main():

    parser = argparse.ArgumentParser(
        description="AI Architecture Compiler CLI"
    )

    parser.add_argument("--prompt", type=str)
    parser.add_argument("--model", type=str, default="gemma3:latest")
    parser.add_argument("--provider", type=str, default="ollama")

    parser.add_argument("--arch", type=str, default=DEFAULT_ARCH_PATH)
    parser.add_argument("--code", type=str, default=DEFAULT_CODE_PATH)

    parser.add_argument("--no-code", action="store_true")
    parser.add_argument("--no-analyze", action="store_true")

    parser.add_argument("--from-arch", action="store_true",
                        help="Use existing architecture")

    parser.add_argument("--analyze-only", action="store_true",
                        help="Analyze only code")
    
    parser.add_argument( "--repo", type=str, 
                        help="Path to repository for multi-file analysis")

    parser.add_argument("--max-attempts", type=int, default=6)

    parser.add_argument("--mode", type=str, default="single", 
                        choices=["single", "repository"], help="Generation mode")

    parser.add_argument("--repo-dir", type=str, default=DEFAULT_REPO_DIR, 
                        help="Output directory for repository generation")

    args = parser.parse_args()

    llm = get_llm(args.provider, args.model)

    arch = None
    
    # === MODE 4: analyze repository-wide:
    if args.repo:

        print("\n=== Repository Analysis ===")

        result = analyze_repository(args.repo)

        print("\nErrors:")
        for e in result["errors"]:
            print("-", e)

        print("\nMetrics:")
        for k, v in result["metrics"].items():
            print(f"{k}: {v}")

        return

    # === MODE 3: analyze only ===
    if args.analyze_only:
        analyze_generated_code(None, args.code)
        return

    # === MODE 2: existing architecture ===
    if args.from_arch:
        arch = load_architecture(args.arch)

    # === MODE 1: generate architecture ===
    else:
        if not args.prompt:
            raise ValueError("Prompt required unless using --from-arch or --analyze-only")

        arch = generate_architecture_loop(
            llm,
            args.prompt,
            args.arch,
            args.max_attempts
        )

    # === code generation + refinement ===
    if not args.no_code:
        # =====================
        # SINGLE FILE MODE
        # =====================
        if args.mode == "single":
            print("\n=== SINGLE FILE MODE ===")
            generate_and_refine_code(llm, args.arch, args.code)

        # =====================
        # REPOSITORY MODE
        # =====================
        elif args.mode == "repository":
            print("\n=== REPOSITORY MODE ===")
            semantic_model = compile_semantic_model(arch)

            generate_and_refine_repository(llm, semantic_model, args.repo_dir)

    # === final analysis ===
    elif not args.no_analyze:

        # =====================
        # SINGLE FILE ANALYSIS
        # =====================
        if args.mode == "single":
            analyze_generated_code(args.arch, args.code)

        # =====================
        # REPOSITORY ANALYSIS
        # =====================
        elif args.mode == "repository":
            result = analyze_repository(args.repo_dir)
            print("\nErrors:")
            for e in result["errors"]:
                print("-", e)

            print("\nMetrics:")
            for k, v in result["metrics"].items():
                print(f"{k}: {v}")


if __name__ == "__main__":
    main()