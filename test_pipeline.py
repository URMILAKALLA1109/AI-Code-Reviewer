import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "reviewer"))

from app import review_code


SAMPLE_CODE = """\
def add(a,b):
    password = 'secret123'
    x = 10
    return a+b
"""


def test_review_code_pipeline():
    result = review_code(SAMPLE_CODE)

    assert isinstance(result, tuple)
    assert len(result) == 5

    combined, pylint_issues, flake8_issues, bandit_issues, review = result

    assert isinstance(combined, list)
    assert isinstance(pylint_issues, list)
    assert isinstance(flake8_issues, list)
    assert isinstance(bandit_issues, list)
    assert isinstance(review, str)

    print("Test passed: full pipeline executed successfully.")


