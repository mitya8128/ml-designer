import os

from analyzer.semantic_summary import extract_semantic_summary
from verifier.module_verifier import verify_module


def analyze_repository_generation(semantic_model, generation_state):

    all_errors = []

    for module_name, path in generation_state.generated_modules.items():
        with open(path) as f:
            code = f.read()
        summary = extract_semantic_summary(code)
        node = semantic_model.nodes[module_name]
        errors = verify_module(
            node,
            summary,
        )
        generation_state.semantic_summaries[
            module_name
        ] = summary
        all_errors.extend(errors)

    return all_errors