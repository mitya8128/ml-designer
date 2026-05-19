import ast


def extract_imports(code: str):

    tree = ast.parse(code)

    imports = {}

    for node in ast.walk(tree):

        # from x import y
        if isinstance(node, ast.ImportFrom):

            module = node.module

            if module is None:
                continue

            for alias in node.names:

                imports[alias.name] = {
                    "module": module,
                    "original": alias.name,
                    "asname": alias.asname or alias.name
                }

        # import x
        elif isinstance(node, ast.Import):

            for alias in node.names:

                imports[alias.name] = {
                    "module": alias.name,
                    "original": None,
                    "asname": alias.asname or alias.name
                }

    return imports