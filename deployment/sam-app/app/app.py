import json
import pickle
import traceback
import boto3
import logging
import base64

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define the version number
VERSION = "1.0"
MODEL_URI = 's3://artifactss31991/models/2/7baf08eb142744abb2a41e386fbab279/artifacts/random_forest_model_v1/model.pkl'

s3 = boto3.client('s3')

def load_model_from_s3(uri):
    try:
        bucket, key = parse_s3_uri(uri)
        response = s3.get_object(Bucket=bucket, Key=key)
        model_data = response['Body'].read()
        model = pickle.loads(model_data)
        return model
    except Exception as e:
        logger.error(f"Error loading model from S3: {str(e)}")
        traceback.print_exc()
        raise Exception(f"Error loading model from S3: {str(e)}")

logger.info('Loading model from file...')

def parse_s3_uri(uri):
    # Parse S3 URI into bucket and key
    uri = uri.replace("s3://", "")  
    parts = uri.split('/')
    bucket = parts[0]
    key = '/'.join(parts[1:])
    return bucket, key

model = load_model_from_s3(MODEL_URI)

def lambda_handler(event, context):
    try:
        logger.info("Loading data from....")
        body = event['body']

        logger.info("Processing JSON data...")
        decoded_json = json.loads(body)
        preds = model.predict(decoded_json)

        formatted_pred = "${:.2f}".format(float(preds[0]))

        response = {
            'statusCode': 200,
            'body': json.dumps({
                'version': VERSION,
                'salary': formatted_pred
            })
        }
        return response
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        traceback.print_exc()
        response = {
            'statusCode': 500,
            'body': json.dumps({
                'version': VERSION,
                'error': 'An internal error occurred'
            })
        }
        return response


