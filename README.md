# AI Code Reviewer

A Streamlit web application that analyzes Python code using industry-standard static analysis tools — **Pylint**, **Flake8**, and **Bandit** — and delivers a structured code review with plain-English explanations and fix suggestions. No cloud account or API key required.

---

## Features

- Paste Python code directly into the editor
- Upload a `.py` file for instant analysis
- **Pylint** — code quality, style, and convention checks
- **Flake8** — PEP 8 style and syntax checks
- **Bandit** — security vulnerability scanning
- Combined severity-based issue reporting (High / Medium / Low)
- Beginner-friendly issue cards with plain-English explanations and fix suggestions
- Structured local review with plain-English explanations and fix suggestions
- Clean, interactive **Streamlit** UI with file upload support

---

## How It Works

```
User pastes code or uploads .py file
            │
            ▼
  ┌─────────────────────┐
  │   Save to temp .py  │
  └─────────┬───────────┘
            │
     ┌──────┴──────┐
     ▼             ▼             ▼
  Pylint        Flake8         Bandit
  (quality)     (style)      (security)
     │             │             │
     └──────┬──────┘─────────────┘
            ▼
     Parse & Combine Issues
     (severity tagging + deduplication)
            │
            ▼
     Build AI Review Prompt
            │
       ┌────┴────┐
       ▼         ▼
  AWS Bedrock   Mock Review
  (if configured) (fallback)
       │         │
       └────┬────┘
            ▼
     Display Results in Streamlit UI
     (Summary · Issue Cards · Review)
```

---

## Project Structure

```
AI-Code-Reviewer/
├── app.py                        # Streamlit UI and pipeline entry point
├── requirements.txt              # Project dependencies
├── .env                          # AWS credentials (never commit this)
├── .gitignore                    # Excludes .env and cache files
├── test_pipeline.py              # End-to-end mock pipeline test
└── reviewer/
    ├── static_analyzer.py        # Pylint, Flake8, Bandit runners and parsers
    ├── report.py                 # Issue combiner and severity mapper
    ├── ai_reviewer.py            # Prompt builder, Bedrock client, mock fallback
    ├── test_static_analyzer.py   # Tests for static analysis functions
    ├── test_report.py            # Tests for combine_issues()
    ├── test_ai_reviewer.py       # Tests for build_review_prompt()
    └── test_bedrock.py           # Mock-based Bedrock integration test
```

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| Streamlit | Web UI framework |
| Pylint | Code quality and style analysis |
| Flake8 | PEP 8 compliance checks |
| Bandit | Security vulnerability scanning |


---

## Installation

### 1. Clone or download the project

```bash
git clone https://github.com/<your-username>/AI-Code-Reviewer.git
cd AI-Code-Reviewer
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## Example Usage

1. Open the app with `streamlit run app.py`
2. Paste the following code into the editor:

```python
import os

def add(a,b):
    password = 'secret123'
    x = 10
    return a+b
```

3. Click **▶ Review Code**
4. The app will display:
   - A summary showing High / Medium / Low issue counts
   - Individual issue cards explaining each problem
   - A structured review with explanations and fix suggestions

---

## Example Issues Detected

| Tool | Issue | Example |
|---|---|---|
| Pylint | Unused variable | `x = 10` is assigned but never used |
| Pylint | Missing docstring | Function has no description |
| Flake8 | Missing whitespace | `def add(a,b)` should be `def add(a, b)` |
| Flake8 | Line too long | Line exceeds 79 characters |
| Bandit | Hardcoded password | `password = 'secret123'` |
| Bandit | Use of `eval()` | `eval()` is a security risk |

---

## Future Enhancements

- Export analysis report as PDF or Markdown
- Review history with session storage
- Support for additional languages (JavaScript, TypeScript)
- GitHub repository URL input for remote code review
- Custom rule configuration for Pylint and Flake8
- Side-by-side code diff with suggested fixes applied
- User authentication for saved reviews

---

## Author

Built as a portfolio project demonstrating:
- Python application development
- Static code analysis tooling
- Streamlit UI development
- Software testing with mocks

> Feel free to fork, extend, and use this project as a learning reference.
