import streamlit as st
import openai
import os
from dotenv import load_dotenv
from parser import LineByLineVisitor
from radon.complexity import cc_visit, cc_rank

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Set up OpenAI client
client = openai.OpenAI(api_key=api_key)

# GPT: Explain code
def explain_code(code_snippet):
    prompt = f"Explain this Python code in simple terms for a beginner:\n\n{code_snippet}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

# GPT: Suggest improvements
def suggest_improvement(code_snippet):
    prompt = f"Suggest improvements for this Python code, such as simplifying logic or adding docstrings:\n\n{code_snippet}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

# Streamlit UI
st.title("Python Code Explainer")

uploaded_file = st.file_uploader("Upload a Python (.py) file", type="py")

if uploaded_file is not None:
    code = uploaded_file.read().deco de("utf-8")
    st.code(code, language='python')

    visitor = LineByLineVisitor(code)
    line_blocks = visitor.parse()

    # Analyze complexity across whole code
    complexity_scores = visitor.get_complexity_scores()
    complexity_map = {
        c.lineno: (c.complexity, cc_rank(c.complexity)) for c in complexity_scores
    }

    for block in line_blocks:
        with st.expander(f"{block['type']} (Line {block['lineno']})"):
            st.code(block['source'], language='python')

            explanation = explain_code(block['source'])
            st.markdown(f"**Explanation:** {explanation}")

            if block['lineno'] in complexity_map:
                score, rank = complexity_map[block['lineno']]
                st.warning(f"⚠️ Cyclomatic Complexity: {score} ({rank})")

            suggestions = suggest_improvement(block['source'])
            st.markdown(f"**Suggestions:** {suggestions}")
