import streamlit as st
import openai
import os
from dotenv import load_dotenv
import ast
from radon.complexity import cc_visit, cc_rank
import pandas as pd

# Load .env variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI
client = openai.OpenAI(api_key=api_key)

# GPT explain
def explain_code(code_snippet):
    prompt = f"Explain this Python code in simple terms for a beginner:\n\n{code_snippet}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

# GPT suggestion
def suggest_improvement(code_snippet):
    prompt = f"Suggest improvements for this Python code, such as simplifying logic or adding docstrings:\n\n{code_snippet}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

# Function parser
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

# Streamlit UI
st.set_page_config(page_title="Python Code Explainer & Analyzer", layout="wide")

st.markdown("""
    <h1 style='text-align: center;'>Python Code Explainer & Analyzer</h1>
    <h4 style='text-align: center;'>A project by Aditya Holla</h4>
    <hr style='border: 1px solid #f0f0f0; margin-top: 10px; margin-bottom: 30px;'>
""", unsafe_allow_html=True)

with st.spinner('Please upload a file and wait while we analyze your code...'):
    uploaded_file = st.file_uploader("Upload a Python (.py) file", type="py")

if uploaded_file is not None:
    code = uploaded_file.read().decode("utf-8")
    st.code(code, language='python')

    # --- STRUCTURE & COMPLEXITY ANALYSIS ---
    analyzer = FunctionAnalyzer(code)
    analyzer.visit(analyzer.tree)
    results = analyzer.analyze_complexity()

    if results:
        df = pd.DataFrame(results)
        df["lines"] = df.apply(lambda row: f"{row['start']}-{row['end']}", axis=1)
        df["docstring"] = df["docstring"].apply(lambda x: "Yes" if x else "No")
        df["flag"] = df["complexity"].apply(lambda x: "⚠️" if x > 10 else "OK")
        df["rank"] = df["complexity"].apply(lambda x: cc_rank(x))

        search_term = st.text_input("Search for a function (by name):")
        if search_term:
            df = df[df["name"].str.contains(search_term, case=False, na=False)]

        st.subheader("Function Complexity & Docstring Summary")
        st.dataframe(
            df[["name", "lines", "complexity", "rank", "flag", "docstring"]]
            .rename(columns={
                "name": "Function",
                "complexity": "Complexity",
                "rank": "Rank",
                "flag": "Flag",
                "docstring": "Docstring"
            }),
            use_container_width=True
        )

        # --- GPT Suggestion for Most Complex Function ---
        most_complex = max(results, key=lambda f: f["complexity"])
        if most_complex["complexity"] > 10:
            code_lines = code.splitlines()[most_complex["start"] - 1 : most_complex["end"]]
            fn_code = "\n".join(code_lines)

            st.subheader("GPT Suggestion for Most Complex Function")
            st.code(fn_code, language='python')
            suggestion = suggest_improvement(fn_code)
            st.markdown(f"**Suggestions:** {suggestion}")

    else:
        st.info("No functions found to analyze.")

    #  Explains code line b line
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

    visitor = LineByLineVisitor(code)
    line_blocks = visitor.parse()

    st.subheader("Line-by-Line Explanation")
    for block in line_blocks:
        with st.expander(f"{block['type']} (Line {block['lineno']})"):
            st.code(block['source'], language='python')
            explanation = explain_code(block['source'])
            st.markdown(f"**Explanation:** {explanation}")
