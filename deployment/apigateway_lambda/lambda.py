import json
import pickle
import traceback

# Define the version number
VERSION = "1.0"

def load_model_from_file(model_path):
    with open(model_path, 'rb') as model_file:
        model = pickle.load(model_file)
    return model

model_path = 'model.pkl'
model = load_model_from_file(model_path)

def lambda_test(event, context):
    try:
        data = event
        preds = model.predict(data)
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
        traceback.print_exc()
        response = {
            'statusCode': 500,
            'body': json.dumps({
                'version': VERSION,
                'error': 'An internal error occurred'
            })
        }
        return response
