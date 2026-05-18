from llm.services.repository_generator import RepositoryGenerator
from analyzer.repo_pipeline import analyze_repository_generation
from .stages.syntax_stage import check_syntax
from .stages.semantic_stage import check_semantics
from .stages.repair_stage import repair_code


def generate_and_refine_repository(llm, semantic_model, output_dir, max_iters=3):

    generator = RepositoryGenerator(llm)
    state = generator.generate_repository(semantic_model, output_dir)

    for iteration in range(max_iters):
        print(f"\n=== Repository refinement iteration {iteration+1} ===")
        errors_found = False
        for module_name, module_path in (state.generated_modules.items()):
            print(f"\nChecking module: {module_name}")

            with open(module_path) as f:
                code = f.read()

            node = semantic_model.nodes[module_name]

            # =====================
            # SYNTAX STAGE
            # =====================
            syntax_result = check_syntax(code)
            if not syntax_result["valid"]:
                errors_found = True
                print("\n[SYNTAX ERRORS]")
                for e in syntax_result["errors"]:
                    print("-", e)

                repaired_code = repair_code(llm, code, syntax_result["errors"])

                with open(module_path, "w") as f:
                    f.write(repaired_code)

                continue

            # =====================
            # SEMANTIC STAGE
            # =====================
            semantic_result = check_semantics(node, code)
            semantic_errors = semantic_result.get("errors", [])

            semantic_warnings = semantic_result.get("warnings", [])

            # ---- WARNINGS ----
            if semantic_warnings:
                print("\n[SEMANTIC WARNINGS]")
                for w in semantic_warnings:
                    print("-", w)

            # ---- ERRORS ----
            if semantic_errors:
                errors_found = True
                print("\n[SEMANTIC ERRORS]")
                for e in semantic_errors:
                    print("-", e)

                repaired_code = repair_code(llm, code, semantic_errors)

                with open(module_path, "w") as f:
                    f.write(repaired_code)

                continue

        # =====================
        # FINAL RESULT
        # =====================
        if not errors_found:
            print("\n✅ Repository passed verification")
            try:
                result = analyze_repository_generation(output_dir)
                print("\nRepository Metrics:")
                for k, v in result.get("metrics",{}).items():
                    print(f"{k}: {v}")

            except Exception as e:
                print("\n⚠️ Repository analysis failed:")
                print(e)

            return state

    print("\n⚠️ Max repository refinement iterations reached")

    return state