import joblib
import json
import logging
import os
import traceback

# Check if running in AWS Lambda environment
if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
    # Running in Lambda, use Lambda-specific path
    model_file = '/opt/ml/model.pkl'
else:
    # Running locally, use local path
    model_file = './app/model.pkl'

model = joblib.load(model_file)


# model_file = '/opt/ml/model.pkl'
# model = joblib.load(model_file)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the version number
VERSION = "1.0"

def validate_input(data):
    # Check work_year
    if "work_year" in data:
        if data["work_year"] < 2019 or data["work_year"] > 2023:
            raise ValueError("Invalid work_year. It should be between 2020 and 2023.")

    # Check company_size
    allowed_company_sizes = ["Large", "Medium", "Small"]
    if "company_size" in data and data["company_size"] not in allowed_company_sizes:
        raise ValueError("Invalid company_size. Allowed values are Large, Medium, Small.")

    # Check other required fields
    required_fields = ["work_year", "experience_level", "employment_type", "job_title", "salary", 
                       "salary_currency", "employee_residence", "remote_ratio", "company_location", 
                       "company_size"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required attribute: {field}")
        

def common_logic(data):
    validate_input(data)
    preds = model.predict(data)
    formatted_pred = "${:.2f}".format(float(preds[0]))
    return formatted_pred

def predict_salary(data):
    try:
        formatted_pred = common_logic(data)
        return formatted_pred
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise e

def lambda_handler(event, context):
    try:
        data = event
        formatted_pred = common_logic(data)

        response = {
            'statusCode': 200,
            'body': json.dumps({
                'version': VERSION,
                'salary_in_usd': formatted_pred
            })
        }
        return response
    except ValueError as ve:
        response = {
            'statusCode': 400,  
            'body': json.dumps({
                'version': VERSION,
                'error': str(ve)
            })
        }
        return response
    except Exception as e:
        traceback.print_exc()
        response = {
            'statusCode': 500,
            'body': json.dumps({
                'version': VERSION,
                'error': 'An internal error occurred'
            })
        }
        return response
