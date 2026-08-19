import json
from io import BytesIO
from unittest.mock import MagicMock, patch
from ai_reviewer import call_bedrock, build_review_prompt

MOCK_RESPONSE_TEXT = (
    "Line: 1\nSeverity: Low\nIssue: C0116 (pylint)\n"
    "Explanation: The function is missing a docstring.\n"
    "Suggestion: Add a docstring describing what the function does.\n"
)

def make_mock_response(text: str) -> dict:
    body = json.dumps({"content": [{"text": text}]}).encode("utf-8")
    return {"body": BytesIO(body)}


def test_call_bedrock_returns_ai_text():
    sample_code = "def add(a, b):\n    return a + b"
    sample_issues = [
        {"tool": "pylint", "line": 1, "type": "C0116", "severity": "Low", "message": "Missing function docstring"}
    ]
    prompt = build_review_prompt(sample_code, sample_issues)

    with patch("ai_reviewer.boto3.client") as mock_boto_client:
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        mock_client.invoke_model.return_value = make_mock_response(MOCK_RESPONSE_TEXT)

        result = call_bedrock(prompt)

        mock_boto_client.assert_called_once_with("bedrock-runtime", region_name="us-east-1")
        mock_client.invoke_model.assert_called_once()
        assert isinstance(result, str), "Result is not a string!"
        assert result == MOCK_RESPONSE_TEXT, "Returned text does not match mock response!"

    print("Test passed: call_bedrock() returned the expected AI response.")
    print("\n--- Mocked AI Response ---")
    print(result)


test_call_bedrock_returns_ai_text()
