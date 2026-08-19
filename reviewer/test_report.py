from report import combine_issues

pylint_issues = [
    {"line": 1, "type": "C0114", "message": "Missing module docstring"},
    {"line": 2, "type": "W0612", "message": "Unused variable 'x'"},
    {"line": 3, "type": "E0001", "message": "Syntax error"}
]

flake8_issues = [
    {"line": 2, "column": 2, "type": "E225", "message": "missing whitespace around operator"},
    {"line": 3, "column": 80, "type": "E501", "message": "line too long (116 > 79 characters)"},
    {"line": 1, "column": 1, "type": "F401", "message": "'os' imported but unused"}
]

bandit_issues = [
    {"line": 1, "type": "B105", "severity": "Low", "message": "Possible hardcoded password: 'secret123'"},
    {"line": 2, "type": "B307", "severity": "Medium", "message": "Use of possibly insecure function - consider using safer ast.literal_eval."}
]

combined = combine_issues(pylint_issues, flake8_issues, bandit_issues)

print("--- Combined Issues ---")
for issue in combined:
    print(issue)

assert isinstance(combined, list), "Result is not a list!"
assert len(combined) == 8, f"Expected 8 issues, got {len(combined)}"
assert all(k in issue for issue in combined for k in ("tool", "line", "type", "severity", "message")), "Missing keys!"

pylint_results = [i for i in combined if i["tool"] == "pylint"]
flake8_results = [i for i in combined if i["tool"] == "flake8"]
bandit_results = [i for i in combined if i["tool"] == "bandit"]

assert pylint_results[0]["severity"] == "Low"
assert pylint_results[1]["severity"] == "Medium"
assert pylint_results[2]["severity"] == "High"
assert flake8_results[0]["severity"] == "Medium"
assert flake8_results[2]["severity"] == "High"
assert bandit_results[0]["severity"] == "Low"
assert bandit_results[1]["severity"] == "Medium"

print("\nTest passed: combine_issues() works correctly.")
