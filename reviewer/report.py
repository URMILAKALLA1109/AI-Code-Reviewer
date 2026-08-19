PYLINT_SEVERITY = {"E": "High", "W": "Medium", "C": "Low", "R": "Low"}
FLAKE8_SEVERITY = {"E": "Medium", "W": "Low", "F": "High", "C": "Low"}


def _pylint_severity(type_code: str) -> str:
    return PYLINT_SEVERITY.get(type_code[0], "Low")


def _flake8_severity(type_code: str) -> str:
    return FLAKE8_SEVERITY.get(type_code[0], "Low")


def combine_issues(pylint_issues: list, flake8_issues: list, bandit_issues: list) -> list:
    combined = []

    for issue in pylint_issues:
        combined.append({
            "tool": "pylint",
            "line": issue.get("line"),
            "type": issue.get("type"),
            "severity": _pylint_severity(issue.get("type", "C")),
            "message": issue.get("message")
        })

    for issue in flake8_issues:
        combined.append({
            "tool": "flake8",
            "line": issue.get("line"),
            "type": issue.get("type"),
            "severity": _flake8_severity(issue.get("type", "E")),
            "message": issue.get("message")
        })

    for issue in bandit_issues:
        combined.append({
            "tool": "bandit",
            "line": issue.get("line"),
            "type": issue.get("type"),
            "severity": issue.get("severity", "Medium"),
            "message": issue.get("message")
        })

    return combined
