import tempfile
import os
import subprocess
import re

def save_code_to_temp_file(source_code: str) -> str:
    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
        encoding="utf-8"
    )
    temp_file.write(source_code)
    temp_file.close()
    return temp_file.name


def run_pylint(file_path: str) -> str:
    result = subprocess.run(
        ["pylint", file_path, "--output-format=text"],
        capture_output=True,
        text=True
    )
    return result.stdout + result.stderr

def parse_pylint_output(output: str) -> list:
    issues = []
    pattern = re.compile(r".+:(\d+):\d+:\s([CWEF]\d+):\s(.+)")
    for line in output.splitlines():
        match = pattern.match(line)
        if match:
            issues.append({
                "line": int(match.group(1)),
                "type": match.group(2),
                "message": match.group(3).strip()
            })
    return issues

def run_flake8(file_path: str) -> str:
    result = subprocess.run(
        ["flake8", file_path],
        capture_output=True,
        text=True
    )
    return result.stdout + result.stderr

def run_bandit(file_path: str) -> str:
    result = subprocess.run(
        ["bandit", "-f", "txt", file_path],
        capture_output=True,
        text=True
    )
    return result.stdout + result.stderr

def parse_flake8_output(output: str) -> list:
    issues = []
    pattern = re.compile(r".+:(\d+):(\d+):\s([A-Z]\d+)\s(.+)")
    for line in output.splitlines():
        match = pattern.match(line)
        if match:
            issues.append({
                "line": int(match.group(1)),
                "column": int(match.group(2)),
                "type": match.group(3),
                "message": match.group(4).strip()
            })
    return issues

def parse_bandit_output(output: str) -> list:
    issues = []
    issue_pattern = re.compile(r">>\s+Issue:\s+\[(\w+)[^\]]*\]\s+(.+)")
    severity_pattern = re.compile(r"Severity:\s+(\w+)")
    location_pattern = re.compile(r"Location:.+:(\d+):\d+")

    current = {}
    for line in output.splitlines():
        line = line.strip()
        m = issue_pattern.match(line)
        if m:
            current = {"type": m.group(1), "message": m.group(2).strip()}
            continue
        m = severity_pattern.match(line)
        if m and current:
            current["severity"] = m.group(1)
            continue
        m = location_pattern.match(line)
        if m and current:
            current["line"] = int(m.group(1))
            issues.append(current)
            current = {}
    return issues
