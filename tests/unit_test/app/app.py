import json
import pickle
import logging
import traceback

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define the version number
VERSION = "1.0"
# pylint: disable=line-too-long
MODEL_URI = 's3://artifactss31991/models/2/7baf08eb142744abb2a41e386fbab279/artifacts/random_forest_model_v1/model.pkl'

s3 = boto3.client('s3')


def validate_input(data):
    # Check work_year
    if "work_year" in data:
        if data["work_year"] < 2019 or data["work_year"] > 2023:
            raise ValueError("Invalid work_year. It should be between 2020 and 2023.")

    # Check company_size
    allowed_company_sizes = ["Large", "Medium", "Small"]
    if "company_size" in data and data["company_size"] not in allowed_company_sizes:
        raise ValueError(
            "Invalid company_size. Allowed values are Large, Medium, Small."
        )

    # Check other required fields
    required_fields = [
        "work_year",
        "experience_level",
        "employment_type",
        "job_title",
        "salary",
        "salary_currency",
        "employee_residence",
        "remote_ratio",
        "company_location",
        "company_size",
    ]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required attribute: {field}")


def load_model_from_s3(uri):
    try:
        bucket, key = parse_s3_uri(uri)
        response = s3.get_object(Bucket=bucket, Key=key)
        model_data = response['Body'].read()
        model = pickle.loads(model_data)
        return model
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        # pylint: disable=broad-exception-raised
        raise Exception(f"Error loading model from S3: {str(e)}") from e



logger.info('Loading model from file...')


def parse_s3_uri(uri):
    # Parse S3 URI into bucket and key
    uri = uri.replace("s3://", "")
    parts = uri.split('/')
    bucket = parts[0]
    key = '/'.join(parts[1:])
    return bucket, key


model = load_model_from_s3(MODEL_URI)


def common_logic(data):
    validate_input(data)
    preds = model.predict(data)
    formatted_pred = f"${float(preds[0]):.2f}"
    return formatted_pred


def predict_salary(data):
    try:
        formatted_pred = common_logic(data)
        return formatted_pred
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise e


# pylint: disable=unused-argument
def lambda_handler(event, context):
    try:
        data = event
        formatted_pred = common_logic(data)

        response = {
            'statusCode': 200,
            'body': json.dumps({'version': VERSION, 'salary_in_usd': formatted_pred}),
        }
        return response
    except ValueError as ve:
        response = {
            'statusCode': 400,
            'body': json.dumps({'version': VERSION, 'error': str(ve)}),
        }
        return response
    # pylint: disable=unused-variable
    except Exception as e: 
        traceback.print_exc()
        response = {
            'statusCode': 500,
            'body': json.dumps(
                {'version': VERSION, 'error': 'An internal error occurred'}
            ),
        }
        return response
