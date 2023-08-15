import mlflow
import os
import json
import logging


RUN_ID = os.getenv('RUN_ID')

logged_model = f's3://artifactss31991/2/{RUN_ID}/artifacts/random_forest_model_v1'

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_model_pipeline():
    if logged_model is None:
        raise ValueError("MODEL_URI environment variable not set")
    model = mlflow.pyfunc.load_model(logged_model)
    return model

model = load_model_pipeline()

def predict(data):
    preds = model.predict(data)
    return float(preds[0])


def lambda_handler(event, context):
    try:
        data = json.loads(event['body'])
        if data is None:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid JSON data'})}
        
        pred = predict(data)
        formatted_pred = round(pred, 2)

        result = {
            'salary': formatted_pred
        }

        return {'statusCode': 200, 'body': json.dumps(result)}
    except json.JSONDecodeError:
        return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid JSON data'})}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': 'An internal error occurred'})}


