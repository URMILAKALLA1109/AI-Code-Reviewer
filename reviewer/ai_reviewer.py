def build_review_prompt(code: str, issues: list) -> str:
    issues_text = ""
    for i, issue in enumerate(issues, start=1):
        issues_text += (
            f"{i}. Tool: {issue['tool']} | Line: {issue['line']} | "
            f"Severity: {issue['severity']} | Type: {issue['type']} | "
            f"Message: {issue['message']}\n"
        )

    prompt = f"""You are an expert Python code reviewer.

Below is a Python code snippet followed by a list of issues detected by static analysis tools (Pylint, Flake8, Bandit).

Your task:
- Review each detected issue carefully.
- Explain what the issue means in plain language.
- Provide a practical, corrected code fix for each issue.
- Return your feedback as a structured list.

For each issue, respond in exactly this format:
---
Line: <line number>
Severity: <severity>
Issue: <issue type and tool>
Explanation: <clear explanation of what the issue means>
Suggestion: <corrected code or actionable fix>
---

Python Code:
```python
{code}
```

Detected Issues:
{issues_text}

Provide structured feedback for every issue listed above.
"""
    return prompt


def generate_review(issues: list) -> str:
    if not issues:
        return "✅ No issues detected. The code looks clean."

    lines = ["**Static Analysis Review**\n"]
    for issue in issues:
        lines.append("---")
        lines.append(f"Line: {issue['line']}")
        lines.append(f"Severity: {issue['severity']}")
        lines.append(f"Issue: {issue['type']} ({issue['tool']})")
        lines.append(f"Explanation: `{issue['tool']}` flagged this line.")
        lines.append(f"Suggestion: Review and fix — {issue['message']}")
        lines.append("---\n")
    return "\n".join(lines)
