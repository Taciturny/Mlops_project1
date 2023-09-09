import os
import mlflow
from flask import Flask, request, jsonify, json
from config import Config
import logging
import traceback
import boto3


# Access the GitHub Actions secrets as environment variables
# aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
# aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]
# aws_region = "us-east-1"




# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask('Data Science-prediction')
app.logger.setLevel(logging.INFO)  # Set the logging level


@app.route('/')
def home():
    return "Welcome to Data Science Salary Predictor"


def load_model_pipeline():
    if Config.MODEL_URI is None:
        raise ValueError("MODEL_URI environment variable not set")
    model = mlflow.pyfunc.load_model(Config.MODEL_URI)
    return model

model = load_model_pipeline()

def predict(data):
    preds = model.predict(data)
    return float(preds[0])


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    app.logger.info('Received prediction request')
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Invalid JSON data'}), 400

        if not data:
            return jsonify({'error': 'Missing data'}), 400

        if 'salary' not in data:
            return jsonify({'error': 'Missing "salary" field'}), 400

        pred = predict(data)
        formatted_pred = round(pred, 2)

        run_id = Config.get_run_id()

        result = {
            'salary_in_usd': formatted_pred,
            'model_version': run_id
        }

        return jsonify(result)
    except json.JSONDecodeError:
        app.logger.error('Invalid JSON data received')
        return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as e:
        app.logger.error(f'Error: {str(e)}')
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'An internal error occurred'}), 500




if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=Config.PORT)
