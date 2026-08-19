from ai_reviewer import build_review_prompt

sample_code = "def add(a,b):\n    x = 10\n    return a+b"

sample_issues = [
    {"tool": "pylint", "line": 1, "type": "C0116", "severity": "Low",    "message": "Missing function docstring"},
    {"tool": "flake8", "line": 1, "type": "E231",  "severity": "Medium", "message": "missing whitespace after comma"},
    {"tool": "bandit", "line": 2, "type": "B105",  "severity": "Low",    "message": "Possible hardcoded password"},
]

prompt = build_review_prompt(sample_code, sample_issues)

print("--- Generated Prompt ---")
print(prompt)

assert isinstance(prompt, str), "Prompt is not a string!"
assert "Python Code:" in prompt, "Prompt missing code section!"
assert "Detected Issues:" in prompt, "Prompt missing issues section!"
assert "def add(a,b):" in prompt, "Prompt missing original code!"
assert all(i["message"] in prompt for i in sample_issues), "Prompt missing one or more issue messages!"
assert "Explanation:" in prompt, "Prompt missing Explanation field!"
assert "Suggestion:" in prompt, "Prompt missing Suggestion field!"

print("Test passed: build_review_prompt() works correctly.")
