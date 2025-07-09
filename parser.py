import ast
from radon.complexity import cc_visit


class LineByLineVisitor(ast.NodeVisitor):
    def __init__(self, code):
        self.code = code
        self.lines = []

    def generic_visit(self, node):
        if hasattr(node, 'lineno'):
            self.lines.append({
                'type': type(node).__name__,
                'lineno': node.lineno,
                'source': ast.get_source_segment(self.code, node)
            })
        super().generic_visit(node)

    def parse(self):
        tree = ast.parse(self.code)
        self.visit(tree)
        return sorted(self.lines, key=lambda x: x['lineno'])

    def get_complexity_scores(self):
        return cc_visit(self.code)