import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "reviewer"))

from static_analyzer import (
    save_code_to_temp_file,
    run_pylint, parse_pylint_output,
    run_flake8, parse_flake8_output,
    run_bandit, parse_bandit_output,
)
from report import combine_issues
from ai_reviewer import build_review_prompt, generate_review

# ── Severity display ──────────────────────────────────────────────────────────

SEVERITY_ICON  = {"High": "🔴", "Medium": "🟠", "Low": "🟡"}
SEVERITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}

# ── Beginner-friendly explanations ───────────────────────────────────────────
# Keys are issue type codes. Each entry has:
#   title  – plain-English name shown as the card headline
#   what   – why this is a problem
#   fix    – concrete action to take

ISSUE_EXPLANATIONS = {
    # Pylint – convention
    "C0114": {
        "title": "Missing module description",
        "what":  "Your file has no description at the top. Other developers (and your future self) won't know what this file does.",
        "fix":   'Add a short description at the very top of the file:\n```python\n"""This module does XYZ."""\n```',
    },
    "C0115": {
        "title": "Missing class description",
        "what":  "Your class has no description. It's unclear what the class represents.",
        "fix":   'Add a docstring right after the class definition:\n```python\nclass MyClass:\n    """Represents a ..."""\n```',
    },
    "C0116": {
        "title": "Missing function description",
        "what":  "Your function has no description. It's unclear what it does, what it accepts, or what it returns.",
        "fix":   'Add a docstring right after the `def` line:\n```python\ndef my_func():\n    """Does XYZ and returns ..."""\n```',
    },
    "C0301": {
        "title": "Line is too long",
        "what":  "This line exceeds the recommended 100-character limit, making it hard to read.",
        "fix":   "Break the line into multiple shorter lines or use parentheses to wrap it.",
    },
    "C0303": {
        "title": "Trailing whitespace",
        "what":  "There are invisible space characters at the end of this line.",
        "fix":   "Remove the trailing spaces. Most editors can do this automatically on save.",
    },
    "C0304": {
        "title": "File doesn't end with a blank line",
        "what":  "Python files should end with a single blank line. Some tools and editors expect this.",
        "fix":   "Add one blank line at the very end of your file.",
    },
    "C0321": {
        "title": "Multiple statements on one line",
        "what":  "You have more than one statement on a single line, which makes code harder to read and debug.",
        "fix":   "Put each statement on its own line.",
    },
    # Pylint – warning
    "W0611": {
        "title": "Imported module is never used",
        "what":  "You imported something but never used it. This wastes memory and confuses readers.",
        "fix":   "Remove the unused import line.",
    },
    "W0612": {
        "title": "Variable is created but never used",
        "what":  "You assigned a value to a variable but never read it. This is likely a mistake or leftover code.",
        "fix":   "Either use the variable, or remove the line that creates it.",
    },
    "W0613": {
        "title": "Function argument is never used",
        "what":  "A parameter was passed to the function but never used inside it.",
        "fix":   "Either use the parameter or prefix it with `_` (e.g. `_unused`) to signal it's intentionally ignored.",
    },
    "W0621": {
        "title": "Variable name reused from outer scope",
        "what":  "A variable inside this function has the same name as one in the outer scope, which can cause confusion.",
        "fix":   "Rename the inner variable to something distinct.",
    },
    # Pylint – error
    "E0001": {
        "title": "Syntax error — Python can't read this code",
        "what":  "Python cannot parse this file. There is a typo or structural mistake that prevents the code from running at all.",
        "fix":   "Look at the line number and check for missing colons, brackets, or quotes.",
    },
    "E0102": {
        "title": "Function or class defined more than once",
        "what":  "You have two definitions with the same name. The second one silently overwrites the first.",
        "fix":   "Rename one of them or remove the duplicate.",
    },
    "E0401": {
        "title": "Module could not be imported",
        "what":  "Python cannot find the module you are trying to import. It may not be installed.",
        "fix":   "Install the missing package with `pip install <package-name>` or check the import spelling.",
    },
    # Flake8 – style errors
    "E101": {
        "title": "Mixed tabs and spaces",
        "what":  "Your file mixes tab characters and spaces for indentation. Python requires consistency.",
        "fix":   "Convert all indentation to spaces (4 spaces per level is the standard).",
    },
    "E111": {
        "title": "Wrong indentation amount",
        "what":  "The indentation on this line is not a multiple of 4 spaces.",
        "fix":   "Use exactly 4 spaces per indentation level.",
    },
    "E225": {
        "title": "Missing spaces around operator",
        "what":  "Operators like `=`, `+`, `-`, `==` should have a space on each side for readability.",
        "fix":   'Change `x=1+2` to `x = 1 + 2`.',
    },
    "E231": {
        "title": "Missing space after comma or colon",
        "what":  "There should be a space after commas and colons to improve readability.",
        "fix":   'Change `def f(a,b)` to `def f(a, b)`.',
    },
    "E302": {
        "title": "Expected two blank lines before this",
        "what":  "Top-level functions and classes should be separated by two blank lines.",
        "fix":   "Add two blank lines before this function or class definition.",
    },
    "E303": {
        "title": "Too many blank lines",
        "what":  "There are more blank lines here than the style guide allows (max 2 between top-level, max 1 inside).",
        "fix":   "Remove the extra blank lines.",
    },
    "E501": {
        "title": "Line is too long",
        "what":  "This line is longer than 79 characters, making it hard to read without scrolling.",
        "fix":   "Break the line into multiple shorter lines or use parentheses to wrap it.",
    },
    "E711": {
        "title": "Comparison to None done incorrectly",
        "what":  'Using `== None` is not recommended. Python has a specific way to check for None.',
        "fix":   'Use `is None` or `is not None` instead of `== None` or `!= None`.',
    },
    "E712": {
        "title": "Comparison to True/False done incorrectly",
        "what":  'Using `== True` or `== False` is not recommended.',
        "fix":   'Use `if condition:` instead of `if condition == True:`.',
    },
    # Flake8 – warnings
    "W291": {
        "title": "Trailing whitespace",
        "what":  "There are invisible space characters at the end of this line.",
        "fix":   "Remove the trailing spaces. Most editors can do this automatically on save.",
    },
    "W292": {
        "title": "File doesn't end with a newline",
        "what":  "The file should end with a single newline character.",
        "fix":   "Add one blank line at the very end of your file.",
    },
    "W293": {
        "title": "Whitespace on a blank line",
        "what":  "A line that looks empty actually contains spaces or tabs.",
        "fix":   "Clear the whitespace from blank lines.",
    },
    # Flake8 – pyflakes
    "F401": {
        "title": "Imported module is never used",
        "what":  "You imported something but never used it anywhere in the file.",
        "fix":   "Remove the unused import line.",
    },
    "F811": {
        "title": "Name defined more than once",
        "what":  "A variable, function, or import is defined twice. The second definition overwrites the first.",
        "fix":   "Remove or rename the duplicate definition.",
    },
    "F841": {
        "title": "Variable is assigned but never used",
        "what":  "You stored a value in a variable but never read it. This is likely a mistake.",
        "fix":   "Either use the variable or remove the assignment.",
    },
    # Bandit – security
    "B101": {
        "title": "Use of assert in production code",
        "what":  "`assert` statements are removed when Python runs in optimised mode (`-O`), so they should not be used for security or validation checks.",
        "fix":   "Replace `assert` with a proper `if` check and raise an appropriate exception.",
    },
    "B105": {
        "title": "Possible hardcoded password",
        "what":  "A string that looks like a password is assigned directly in the code. If this code is shared or committed, the password is exposed.",
        "fix":   "Load the password from an environment variable:\n```python\nimport os\npassword = os.getenv('MY_PASSWORD')\n```",
    },
    "B106": {
        "title": "Possible hardcoded password in function argument",
        "what":  "A password-like value is passed directly as a function argument.",
        "fix":   "Use an environment variable instead of a hardcoded string.",
    },
    "B107": {
        "title": "Possible hardcoded password in function default",
        "what":  "A function parameter has a hardcoded default value that looks like a password.",
        "fix":   "Use `None` as the default and load the real value from an environment variable inside the function.",
    },
    "B301": {
        "title": "Use of pickle is unsafe",
        "what":  "Unpickling data from an untrusted source can execute arbitrary code and is a serious security risk.",
        "fix":   "Use a safe format like JSON for data serialisation when the source is not fully trusted.",
    },
    "B307": {
        "title": "Use of eval() is dangerous",
        "what":  "`eval()` executes any Python code passed to it as a string. If that string comes from user input, an attacker can run malicious code.",
        "fix":   "Use `ast.literal_eval()` if you only need to parse simple values, or redesign to avoid evaluating strings as code.",
    },
    "B311": {
        "title": "Use of random is not cryptographically secure",
        "what":  "The `random` module is not suitable for security-sensitive tasks like generating tokens or passwords.",
        "fix":   "Use the `secrets` module instead:\n```python\nimport secrets\ntoken = secrets.token_hex(16)\n```",
    },
    "B501": {
        "title": "SSL certificate verification disabled",
        "what":  "Disabling SSL verification means the connection is vulnerable to man-in-the-middle attacks.",
        "fix":   "Remove `verify=False` and let SSL verification run normally.",
    },
    "B601": {
        "title": "Possible shell injection via paramiko",
        "what":  "Passing unsanitised input to a shell command over SSH can allow an attacker to run arbitrary commands.",
        "fix":   "Validate and sanitise all input before passing it to shell commands.",
    },
    "B602": {
        "title": "Subprocess call with shell=True is risky",
        "what":  "Using `shell=True` with user-controlled input can allow shell injection attacks.",
        "fix":   "Pass a list of arguments instead of a string, and set `shell=False`.",
    },
    "B603": {
        "title": "Subprocess call without shell=True — verify inputs",
        "what":  "Even without `shell=True`, passing unvalidated input to a subprocess can be dangerous.",
        "fix":   "Validate all inputs before passing them to subprocess calls.",
    },
    "B608": {
        "title": "Possible SQL injection",
        "what":  "Building SQL queries by concatenating strings with user input allows attackers to manipulate your database.",
        "fix":   "Use parameterised queries:\n```python\ncursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))\n```",
    },
}

FALLBACK_EXPLANATION = {
    "what": "This issue was flagged by a static analysis tool. Review the message for details.",
    "fix":  "Refer to the tool's documentation or the message above for guidance on how to fix this.",
}


# ── Backend pipeline ──────────────────────────────────────────────────────────

def review_code(source_code: str) -> tuple:
    path = save_code_to_temp_file(source_code)
    try:
        pylint_issues = parse_pylint_output(run_pylint(path))
        flake8_issues = parse_flake8_output(run_flake8(path))
        bandit_issues = parse_bandit_output(run_bandit(path))
    finally:
        os.remove(path)

    combined = combine_issues(pylint_issues, flake8_issues, bandit_issues)
    prompt   = build_review_prompt(source_code, combined)
    review   = generate_review(combined)
    return combined, pylint_issues, flake8_issues, bandit_issues, review


# ── Deduplication ─────────────────────────────────────────────────────────────

def group_issues(combined: list) -> list:
    """
    Merge issues from different tools that refer to the same line and
    share the same type code prefix (e.g. W0612 and F841 are both
    'unused variable'). Groups are keyed by (line, type_code) so that
    genuinely different issues on the same line are kept separate.
    Returns a list of grouped dicts sorted by severity then line number.
    """
    groups: dict = {}
    for issue in combined:
        key = (issue["line"], issue["type"])
        if key not in groups:
            groups[key] = {
                "line":     issue["line"],
                "type":     issue["type"],
                "severity": issue["severity"],
                "message":  issue["message"],
                "tools":    [issue["tool"]],
            }
        else:
            if issue["tool"] not in groups[key]["tools"]:
                groups[key]["tools"].append(issue["tool"])

    return sorted(
        groups.values(),
        key=lambda i: (SEVERITY_ORDER.get(i["severity"], 3), i["line"]),
    )


# ── Issue card renderer ───────────────────────────────────────────────────────

def render_issue_card(issue: dict):
    type_code  = issue["type"]
    severity   = issue["severity"]
    icon       = SEVERITY_ICON.get(severity, "⚪")
    exp        = ISSUE_EXPLANATIONS.get(type_code, FALLBACK_EXPLANATION)
    title      = exp.get("title", issue["message"])
    tools_str  = ", ".join(t.capitalize() for t in issue["tools"])
    label      = f"{icon} **{title}** — Line {issue['line']}  `{severity}`"

    with st.expander(label, expanded=(severity == "High")):
        col_left, col_right = st.columns([1, 1], gap="medium")

        with col_left:
            st.markdown("**❓ What's wrong?**")
            st.markdown(exp.get("what", issue["message"]))
            st.markdown(f"<small>Code: `{type_code}` &nbsp;|&nbsp; Detected by: **{tools_str}**</small>",
                        unsafe_allow_html=True)

        with col_right:
            st.markdown("**🔧 How to fix it?**")
            st.markdown(exp.get("fix", "See the tool documentation for guidance."))


# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="AI Code Reviewer", page_icon="🔍", layout="wide")

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("## 🔍 AI Code Reviewer")
st.markdown(
    "Paste or upload your Python code to get an instant analysis using "
    "**Pylint**, **Flake8**, and **Bandit**, followed by an AI-powered review from **AWS Bedrock (Claude)**."
)
st.divider()

# ── Code Input ────────────────────────────────────────────────────────────────

st.markdown("### 📂 Input")
upload_col, paste_col = st.columns([1, 2], gap="large")

with upload_col:
    st.markdown("**Upload a Python file**")
    uploaded_file = st.file_uploader("Choose a .py file", type=["py"], label_visibility="collapsed")

with paste_col:
    st.markdown("**Or paste your code**")
    default_code = uploaded_file.read().decode("utf-8") if uploaded_file else ""
    code_input   = st.text_area(
        label="Python Code",
        value=default_code,
        placeholder="Paste your Python code here...",
        height=250,
        label_visibility="collapsed",
    )

st.divider()

# ── Review Button ─────────────────────────────────────────────────────────────

if st.button("▶ Review Code", type="primary"):
    if not code_input.strip():
        st.warning("Please upload a file or paste Python code before reviewing.")
        st.stop()

    with st.spinner("Running static analysis and AI review..."):
        try:
            combined, pylint_issues, flake8_issues, bandit_issues, ai_review = review_code(code_input)
        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")
            st.stop()

    grouped = group_issues(combined)

    st.divider()

    # ── Summary Metrics ───────────────────────────────────────────────────────

    st.markdown("### 📊 Review Summary")

    high   = sum(1 for i in grouped if i["severity"] == "High")
    medium = sum(1 for i in grouped if i["severity"] == "Medium")
    low    = sum(1 for i in grouped if i["severity"] == "Low")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Issues", len(grouped))
    m2.metric("🔴 High",      high)
    m3.metric("🟠 Medium",    medium)
    m4.metric("🟡 Low",       low)

    st.divider()

    # ── Problems Found ────────────────────────────────────────────────────────

    st.markdown("### ❌ Problems Found" if grouped else "")

    if not grouped:
        st.success("✅ No problems found — your code passed all static analysis checks.")
    else:
        for issue in grouped:
            render_issue_card(issue)

    st.divider()

    # ── AI Review ─────────────────────────────────────────────────────────────

    st.markdown("### 🤖 AI Review")
    with st.container():
        st.markdown(ai_review)
