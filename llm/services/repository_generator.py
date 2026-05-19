import os

from generation.state import GenerationState
from generation.planner import compute_generation_order

from prompts.module_generation_prompt import (
    build_module_generation_prompt,
)

from utils.code_utils import extract_code


class RepositoryGenerator:

    def __init__(self, llm):
        self.llm = llm

    def generate_repository(self, semantic_model, output_dir):

        os.makedirs(output_dir, exist_ok=True)
        state = GenerationState(
            semantic_model=semantic_model,
        )

        generation_order = compute_generation_order(
            semantic_model
        )

        print("\nGeneration order:")

        for module_name in generation_order:
            print("-", module_name)

        for module_name in generation_order:
            node = semantic_model.nodes[module_name]
            print(f"\n=== Generating module: {module_name} ===")
            
            prompt = build_module_generation_prompt(
                node,
                state,
            )

            raw_output = self.llm.generate(
                "",
                prompt,
            )

            code = extract_code(raw_output)

            module_path = os.path.join(
                output_dir,
                f"{module_name}.py"
            )

            with open(module_path, "w") as f:
                f.write(code)

            state.generated_modules[module_name] = module_path

        return state