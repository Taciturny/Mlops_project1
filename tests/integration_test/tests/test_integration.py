"""
Integration tests for the Data Science Salary Predictor.
"""
import os
import sys
import json
import pytest

sys.path.append("..")  

from project.predict import app
from project.test_data import data




# Define it once at the module level, no need to redefine in functions
@pytest.fixture
def client():
    """
    Pytest fixture for configuring a test client for the Flask application.

    This fixture sets the 'TESTING' configuration to True for the Flask application,
    which is a common practice for configuring the application for testing. It yields
    the configured test client, allowing it to be used in test functions.

    Yields:
        FlaskClient: A test client for making HTTP requests to the Flask application.
    """
    app.config['TESTING'] = True
    yield client


def test_home_endpoint() -> None:
    """
    Test the home endpoint.

    This function sends a GET request to the home endpoint and checks if the response
    status code is 200 and if the response message matches the expected welcome message.

    Returns:
        None
    """
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == "Welcome to Data Science Salary Predictor"


def test_invalid_json_data():
    """
    Test handling of invalid JSON data.

    This function checks if the server handles invalid JSON data correctly by sending
    a POST request with an incorrectly formatted JSON payload. It checks that the
    response status code is 400 and that an "error" key is present in the response JSON.

    Returns:
        None
    """
    response = client.post('/predict', json={"invalid_key": "value"})
    assert response.status_code == 400
    assert "error" in response.json


def test_missing_json_data():
    """
    Test handling of missing JSON data.

    This function checks if the server handles missing JSON data correctly by sending
    a POST request with an empty JSON payload. It checks that the response status code
    is 400 and that an "error" key is present in the response JSON.

    Returns:
        None
    """
    response = client.post(
        '/predict', data=json.dumps({}), content_type='application/json'
    )
    assert response.status_code == 400
    assert "error" in response.json


def test_valid_prediction():
    """
    Test a valid prediction request.

    This function checks if the server correctly handles a valid prediction request
    by sending a POST request with valid data. It checks that the response status code
    is 200 and that the response JSON contains the expected keys, "salary_in_usd" and
    "model_version."

    Returns:
        None
    """
    response = client.post('/predict', json=data)
    assert response.status_code == 200
    assert "salary_in_usd" in response.json
    assert "model_version" in response.json


def test_internal_error():
    """
    Test handling of internal server error.

    This function checks if the server correctly handles internal errors by sending
    a POST request with invalid data. It checks that the response status code is 400
    and that an "error" key is present in the response JSON.

    Returns:
        None
    """
    response = client.post('/predict', json={"invalid_key": "value"})
    assert response.status_code == 400
    assert "error" in response.json


def test_single_model_version():
    """
    Test setting the MODEL_URI environment variable.

    This function sets the MODEL_URI environment variable to a specific S3 bucket path
    representing a single model version. It is intended for configuring the testing
    environment but does not perform any direct tests.

    Returns:
        None
    """
    # Set the MODEL_URI environment variable to your S3 bucket path (your single model version)
    os.environ["MODEL_URI"] = (
        "s3://artifactss31991/models/2/7baf08eb142744abb2a41e386fbab279/"
        "artifacts/random_forest_model_v1"
    )


if __name__ == "__main__":
    pytest.main()

    # client = app.test_client()
