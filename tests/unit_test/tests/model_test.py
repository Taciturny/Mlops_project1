import json
import sys
import os
from ..app.app import lambda_handler

# Add the parent directory of the test script to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_lambda_handler_success():
    # Construct the path to the 'events' directory
    events_dir = os.path.join(project_root, 'events')

    # Load the event data from events/event.json
    event_file = os.path.join(events_dir, 'event.json')
    with open(event_file) as f:
        event = json.load(f)

    # Call the lambda_handler function and capture the response
    response = lambda_handler(event, None)

    # Parse the response JSON
    response_data = json.loads(response['body'])

    # Assert the expected response status code for success
    assert response['statusCode'] == 200

    # Define the expected salary_in_usd based on your event data
    expected_salary_in_usd = 33948.88

    # Extract the actual salary_in_usd from the response and remove '$' and ','
    actual_salary_in_usd_str = response_data['salary_in_usd'].replace('$', '').replace(',', '')

    # Convert the cleaned string to a float
    actual_salary_in_usd = float(actual_salary_in_usd_str)

    # Assert that the actual salary matches the expected salary
    assert actual_salary_in_usd == float(expected_salary_in_usd)



def test_lambda_handler_error():
    # Bad input data that should trigger an error
    event = {
        "experience_level": "MI",
        "employment_type": "FL",
        "job_title": "Data Scientist",
        "salary": 50000,
        "salary_currency": "EUR",
        "employee_residence": "US",
        "remote_ratio": 200,  # Invalid value
        "company_location": "AFR",  # Invalid location
        "company_size": "Big"
    }

    # Call the lambda_handler function with the error-inducing event
    response = lambda_handler(event, None)

    # Assert the expected response status code for an error (should be 400)
    assert response['statusCode'] == 400
