import base64
import json

data = {
    "work_year": 2022,
    "experience_level": "MI",
    "employment_type": "FL",
    "job_title": "Data Scientist",
    "salary": 28000,
    "salary_currency": "EUR",
    "employee_residence": "US",
    "remote_ratio": 100,
    "company_location": "US",
    "company_size": "Small"
}

# Convert the data dictionary to a JSON string
data_json = json.dumps(data)

# Encode the JSON string to base64
encoded_data = base64.b64encode(data_json.encode('utf-8')).decode('utf-8')

print(encoded_data)
