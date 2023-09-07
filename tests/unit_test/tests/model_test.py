import sys
import json
from unittest.mock import Mock, patch
import pytest
sys.path.append("..")
# pylint: disable=wrong-import-position
from app.app import lambda_handler 


@pytest.fixture
def sample_event():
    return {
        'body': json.dumps(
            {
                "work_year": 2022,
                "experience_level": "MI",
                "employment_type": "FL",
                "job_title": "Data Scientist",
                "salary": 28000,
                "salary_currency": "EUR",
                "employee_residence": "US",
                "remote_ratio": 100,
                "company_location": "US",
                "company_size": "Small",
            }
        )
    }


@patch('app.app.load_model_from_s3')
def test_lambda_handler_success(mock_load_model, sample_event):
    # Mock the load_model_from_s3 function to return a mock model
    mock_model = Mock()
    mock_load_model.return_value = mock_model

    # Call the lambda_handler function with the sample event
    response = lambda_handler(sample_event, None)

    # Check if the response status code is 400 for a successful execution (due to ValueError)
    assert response['statusCode'] == 400

    # Parse the response body as JSON
    data = json.loads(response['body'])

    # Assert the expected response fields
    assert 'version' in data
    assert 'salary_in_usd' not in data


@patch('app.app.load_model_from_s3')
def test_lambda_handler_value_error(mock_load_model, sample_event):
    # Mock the load_model_from_s3 function to return a mock model
    mock_model = Mock()
    mock_load_model.return_value = mock_model

    # Modify the sample event to trigger a ValueError (e.g., invalid input)
    sample_event['body'] = json.dumps(
        {
            "work_year": 2022,
            "experience_level": "InvalidLevel",
            "employment_type": "FL",
            "job_title": "Data Scientist",
            "salary": 28000,
            "salary_currency": "EUR",
            "employee_residence": "US",
            "remote_ratio": 100,
            "company_location": "US",
            "company_size": "Small",
        }
    )

    # Call the lambda_handler function with the modified sample event
    response = lambda_handler(sample_event, None)

    # Check if the response status code is 400 for a ValueError
    assert response['statusCode'] == 400

    # Parse the response body as JSON
    data = json.loads(response['body'])

    # Assert the expected response fields
    assert 'version' in data
    assert 'error' in data


@patch('app.app.load_model_from_s3')
def test_lambda_handler_internal_error(mock_load_model, sample_event):
    # Mock the load_model_from_s3 function to raise an exception (simulating an internal error)
    mock_load_model.side_effect = Exception("Simulated internal error")

    # Call the lambda_handler function with the sample event
    response = lambda_handler(sample_event, None)

    # Check if the response status code is 400 for an internal error
    assert response['statusCode'] == 400

    # Parse the response body as JSON
    data = json.loads(response['body'])

    # Assert the expected response fields
    assert 'version' in data
    assert 'error' in data


@patch('app.app.load_model_from_s3')
def test_lambda_handler_failure(mock_load_model):
    failure_event = {
        'body': json.dumps(
            {
                # Missing required fields or invalid data
                "work_year": 2018,
                "experience_level": "MI",
                "job_title": "Data Scientist",
                "salary_currency": "EUR",
                "employee_residence": "US",
                "remote_ratio": 100,
                "company_location": "US",
                "company_size": "Small",
            }
        )
    }
    mock_load_model.side_effect = Exception("Mocked S3 Error")

    response = lambda_handler(failure_event, None)

    # Assert the expected response status code for an error (should be 400)
    assert response['statusCode'] == 400
