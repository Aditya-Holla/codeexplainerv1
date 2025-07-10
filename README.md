# Code Companion

**Code Companion** is a Python code explanation and static analysis tool that helps developers understand, review, and improve `.py` files. It combines structured code parsing, complexity analysis, and AI-generated explanations using OpenAI's GPT.

---

## Features

- **Code Explanation with GPT**
  - Parses `.py` files using Python’s `ast` module
  - Sends code blocks (functions, classes, etc.) to OpenAI’s GPT API
  - Returns natural-language explanations to help users understand the code

- **Code Complexity and Quality Dashboard**
  - Uses `radon` to calculate cyclomatic complexity for each function
  - Flags high-complexity functions and those missing docstrings
  - Displays a summary table of function structure and maintainability

- **Web Interface with Streamlit**
  - Allows users to upload Python files and view results in-browser
  - Displays explanation results and function summaries in a structured layout
  - Additional features planned, including export options and customization

---

## How It Works

1. The user uploads a `.py` file via the Streamlit app
2. The code is parsed using Python’s `ast` module to identify structure
3. Each block is processed through:
   - OpenAI GPT API for human-readable explanation
   - `radon` for cyclomatic complexity scoring
4. The results are displayed in a structured dashboard within the app

---

## Tech Stack

- Python 3.10+
- `ast` (built-in Python module)
- `radon` (complexity analysis)
- OpenAI GPT API (natural language explanation)
- Streamlit (web interface)

---

## Installation

```bash
git clone https://github.com/yourusername/code-companion.git
cd code-companion
pip install -r requirements.txt
streamlit run app.py
