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



class FunctionAnalyzer(ast.NodeVisitor):
    def __init__(self, code):
        self.code = code
        self.tree = ast.parse(code)
        self.functions = []

    def visit_FunctionDef(self, node):
        docstring = ast.get_docstring(node) is not None
        start = node.lineno
        end = max([n.lineno for n in ast.walk(node) if hasattr(n, 'lineno')], default=start)
        self.functions.append({
            "name": node.name,
            "start": start,
            "end": end,
            "docstring": docstring,
        })
        self.generic_visit(node)

    def analyze_complexity(self):
        scores = cc_visit(self.code)
        complexity_map = {s.name: s.complexity for s in scores}
        for fn in self.functions:
            fn["complexity"] = complexity_map.get(fn["name"], 0)
        return self.functions
