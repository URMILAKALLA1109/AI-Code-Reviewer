import json
import sys
import os
from io import BytesIO
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "reviewer"))

from app import review_code

MOCK_AI_RESPONSE = (
    "Line: 1\nSeverity: Medium\nIssue: E231 (flake8)\n"
    "Explanation: Missing whitespace after comma in function arguments.\n"
    "Suggestion: Change 'def add(a,b)' to 'def add(a, b)'.\n"
)

SAMPLE_CODE = """\
def add(a,b):
    password = 'secret123'
    x = 10
    return a+b
"""


def make_mock_bedrock_response(text: str) -> dict:
    body = json.dumps({"content": [{"text": text}]}).encode("utf-8")
    return {"body": BytesIO(body)}


def test_review_code_pipeline():
    with patch("ai_reviewer.boto3.client") as mock_boto_client:
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        mock_client.invoke_model.return_value = make_mock_bedrock_response(MOCK_AI_RESPONSE)

        result = review_code(SAMPLE_CODE)

        mock_boto_client.assert_called_once_with("bedrock-runtime", region_name="us-east-1")
        mock_client.invoke_model.assert_called_once()

        assert isinstance(result, str), "Result is not a string!"
        assert result == MOCK_AI_RESPONSE, "AI response does not match mock!"

    print("Test passed: full pipeline executed successfully.")
    print("\n--- Mocked AI Review Output ---")
    print(result)


test_review_code_pipeline()
