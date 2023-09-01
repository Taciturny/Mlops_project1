import requests

# Data to send in the request body
data = {
    "work_year": 2023,
    "experience_level": "MI",
    "employment_type": "FL",
    "job_title": "Data Scientist",
    "salary": 5000,
    "salary_currency": "EUR",
    "employee_residence": "US",
    "remote_ratio": 100,
    "company_location": "US",
    "company_size": "Medium"
}

url = 'http://localhost:9696/predict'
response = requests.post(url, json=data)
print(response.json())
