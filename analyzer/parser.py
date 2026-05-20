import ast


def is_valid_python(code: str):
    try:
        ast.parse(code)
        return True, ""
    except Exception as e:
        return False, str(e)


class CallVisitor(ast.NodeVisitor):

    def __init__(self):
        self.current_function = None
        self.calls = []  # (caller, callee)

    def visit_FunctionDef(self, node):

        prev = self.current_function
        self.current_function = node.name

        self.generic_visit(node)

        self.current_function = prev

    def visit_Call(self, node):

        if self.current_function is None:
            return

        func_name = self._get_call_name(node)

        if func_name:
            self.calls.append((self.current_function, func_name))

        self.generic_visit(node)

    def _get_call_name(self, node):

        # case: foo()
        if isinstance(node.func, ast.Name):
            return node.func.id

        # case: obj.method()
        if isinstance(node.func, ast.Attribute):
            return node.func.attr

        return None


def extract_functions(code, path):

    try:
        tree = ast.parse(code)

    except SyntaxError as e:

        print(f"\n[SyntaxError] in file: {path}")
        print(f"line {e.lineno}:{e.offset} -> {e.msg}")

        if e.text:
            print(e.text.rstrip())

        raise

    functions = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            name = node.name
            input_type = None
            output_type = None

            if node.args.args:
                arg = node.args.args[0]
                if arg.annotation:
                    input_type = ast.unparse(arg.annotation)

            if node.returns:
                output_type = ast.unparse(node.returns)

            functions[name] = {"input": input_type,
                               "output": output_type}

    return functions


def extract_types(tree):

    types = set()

    for node in ast.walk(tree):

        if isinstance(node, ast.AnnAssign):
            if node.annotation:
                types.add(ast.unparse(node.annotation))

        if isinstance(node, ast.arg):
            if node.annotation:
                types.add(ast.unparse(node.annotation))

        if isinstance(node, ast.FunctionDef):
            if node.returns:
                types.add(ast.unparse(node.returns))

    return types


def extract_calls(code: str):

    tree = ast.parse(code)

    visitor = CallVisitor()
    visitor.visit(tree)

    return visitor.calls


def build_call_graph(functions, calls):

    graph = {name: set() for name in functions.keys()}

    for caller, callee in calls:

        if caller not in graph:
            graph[caller] = set()

        graph[caller].add(callee)

    return graph