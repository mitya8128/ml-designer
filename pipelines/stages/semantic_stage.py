from analyzer.semantic_summary import extract_semantic_summary
from verifier.module_verifier import verify_module


def check_semantics(node, code):

    summary = extract_semantic_summary(code)

    result = verify_module(node, summary)
    
    errors = result["errors"]
    warnings = result["warnings"]

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "summary": summary
    }