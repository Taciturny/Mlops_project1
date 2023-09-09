"""
Integration tests for the Data Science Salary Predictor.
"""
import os
import sys
import json
import pytest

sys.path.append("..")  

from project.predict import app
from project.config import Config  

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_endpoint(client):
    """Test the home endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to Data Science Salary Predictor" in response.data

def test_predict_endpoint_valid_input(client):
    """Test the /predict endpoint with valid input."""
    data = {
        "salary": 25000  
    }
    response = client.post('/predict', json=data)
    assert response.status_code == 200
    result = json.loads(response.data.decode('utf-8'))
    assert 'salary_in_usd' in result
    assert 'model_version' in result
    assert isinstance(result['salary_in_usd'], float)

def test_predict_endpoint_missing_data(client):
    """Test the /predict endpoint with missing data."""
    data = {

        "work_year": 2023,
        "experience_level": "MI",
        "employment_type": "FL",
        "job_title": "Data Scientist",
        # "salary": 25000,
        "salary_currency": "EUR",
        "employee_residence": "US",
        "remote_ratio": 0,
        "company_location": "US",
        "company_size": "Large",
    }
    response = client.post('/predict', json=data)
    assert response.status_code == 400
    result = json.loads(response.data.decode('utf-8'))
    assert 'error' in result
    assert 'Missing "salary" field' in result['error']


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=Config.PORT)


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
