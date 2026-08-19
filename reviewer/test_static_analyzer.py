import os
from static_analyzer import save_code_to_temp_file, run_pylint, parse_pylint_output, run_flake8, run_bandit, parse_bandit_output

# --- Test 1: save_code_to_temp_file ---
sample_code = "def hello():\n    print('Hello, World!')\n"

path = save_code_to_temp_file(sample_code)

print(f"Temp file path: {path}")
assert os.path.exists(path), "Temp file was not created!"
print("Test passed: file exists.")

os.remove(path)
print(f"Temp file deleted: {path}")

# --- Test 2: run_pylint ---
# Issues: missing module docstring, variable x unused, no newline at end
bad_code = "def add(a,b):\n    x = 10\n    return a+b"

path = save_code_to_temp_file(bad_code)
output = run_pylint(path)

print("\n--- Pylint Output ---")
print(output)

assert output.strip() != "", "Pylint returned no output!"
print("Test passed: pylint returned output.")

# --- Test 3: parse_pylint_output ---
issues = parse_pylint_output(output)

print("\n--- Parsed Issues ---")
for issue in issues:
    print(issue)

assert isinstance(issues, list), "Result is not a list!"
assert len(issues) > 0, "No issues were parsed!"
assert all(k in issues[0] for k in ("line", "type", "message")), "Missing keys in issue dict!"
print("\nTest passed: issues parsed correctly.")

os.remove(path)

# --- Test 4: run_flake8 ---
# Issues: line too long, missing whitespace around operator, unused import
flake8_code = "import os\nx=1+2\nprint('this line is way too long and will definitely exceed the default 79 character line length limit set by pep8')"

path = save_code_to_temp_file(flake8_code)
output = run_flake8(path)

print("\n--- Flake8 Output ---")
print(output)

assert isinstance(output, str), "Flake8 output is not a string!"
assert output.strip() != "", "Flake8 returned no output!"
print("Test passed: flake8 returned output.")

os.remove(path)

# --- Test 5: run_bandit ---
# Issues: hardcoded password, use of eval()
bandit_code = "password = 'secret123'\neval(input('Enter code: '))\n"

path = save_code_to_temp_file(bandit_code)
output = run_bandit(path)

print("\n--- Bandit Output ---")
print(output)

assert isinstance(output, str), "Bandit output is not a string!"
assert output.strip() != "", "Bandit returned no output!"
print("Test passed: bandit returned output.")

# --- Test 6: parse_bandit_output ---
issues = parse_bandit_output(output)

print("\n--- Parsed Bandit Issues ---")
for issue in issues:
    print(issue)

assert isinstance(issues, list), "Result is not a list!"
assert len(issues) > 0, "No bandit issues were parsed!"
assert all(k in issues[0] for k in ("line", "type", "severity", "message")), "Missing keys in bandit issue dict!"
print("\nTest passed: bandit issues parsed correctly.")

os.remove(path)
