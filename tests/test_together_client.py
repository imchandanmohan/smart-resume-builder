from unittest.mock import patch
from src.api import together_client

@patch("src.api.together_client.query_together_ai")
def test_query_together_ai_job_title(mock_query):
    # Simulate a fake response from the API
    mock_query.return_value = "Senior Machine Learning Engineer"

    prompt = """Extract the job title:

    We are hiring a **Senior Machine Learning Engineer** to work on cutting-edge AI systems at OpenAI in San Francisco."""

    result = together_client.query_together_ai(prompt)

    assert isinstance(result, str), "Expected a string result"
    assert len(result.strip()) > 0, "Expected non-empty result"
    assert "engineer" in result.lower(), "Expected job title to contain 'engineer'"
  
