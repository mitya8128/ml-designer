STDLIB_ALLOWLIST = {
    "os",
    "sys",
    "json",
    "re",
    "typing",
    "logging",
    "datetime",
    "math",
    "pathlib",
}


def verify_module(node, semantic_summary):

    errors = []
    warnings = []

    imports = semantic_summary["imports"]

    allowed = set(node.depends_on)

    for imported in imports:
        root = imported.split(".")[0]
        if root in STDLIB_ALLOWLIST:
            continue
        if root == node.name:
            continue
        if root not in allowed:
            warnings.append(f"Unexpected external dependency: {root}")

    exported_functions = set(semantic_summary["functions"])

    for required_export in node.exports:
        if required_export not in exported_functions:
            errors.append(f"Missing export: {required_export}")

    return {"errors": errors, "warnings": warnings}