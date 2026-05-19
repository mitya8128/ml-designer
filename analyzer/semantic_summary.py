import ast


class SemanticSummaryVisitor(ast.NodeVisitor):

    def __init__(self):
        self.imports = set()
        self.functions = set()
        self.classes = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)

        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.functions.add(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.classes.add(node.name)
        self.generic_visit(node)


def extract_semantic_summary(code: str):
    tree = ast.parse(code)
    visitor = SemanticSummaryVisitor()
    visitor.visit(tree)
    return {
        "imports": sorted(visitor.imports),
        "functions": sorted(visitor.functions),
        "classes": sorted(visitor.classes),
    }