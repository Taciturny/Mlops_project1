# Mlops_projectdtc


# Data Science Prediction

## Problem Statement

### Description
The project addresses the challenge of accurately estimating the salaries of Data Scientists, benefiting both job seekers and employers in the data science field. Here is the dataset [Link](https://www.kaggle.com/datasets/arnabchaki/data-science-salaries-2023)

### Why it's Important
Accurate salary estimates promote fairness and transparency in the hiring process, reducing friction in negotiations and enhancing job market efficiency.

### Beneficiaries
This project benefits job seekers, employers, and the broader data science community by providing a reliable salary estimation tool.

## Objective

The primary objective is to develop and deploy a predictive model for precise Data Scientist salary estimates.

### Key Outcomes
Completion of this project will result in a user-friendly tool for job seekers and employers in data science.

## Metrics

Model performance will be assessed using the Root Mean Squared Error (RMSE).


## Installation

Provide step-by-step instructions for installing any dependencies and setting up the environment needed to run your predictive model. For example:

```bash
# Clone the repository
git clone https://github.com/Taciturny/Mlops_projectdtc.git

# Change to the project directory
cd Mlops_projectdtc
```

## Reproducibility Steps

### Step 1: Configure AWS Environment

1. After cloning, create an account in AWS [Sign-Up](https://portal.aws.amazon.com/billing/signup#/start/email)
2. Locate the IAM services under Roles and create the User & Access keys
3. Assign the AdministratorFullAccess permission for this project (Note: This permission is typically not advisable, but it's used for this project)
4. Download AWS CLI locally [AWS CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
5. Configure AWS CLI and provide the keys from step 2
6. Create an S3 bucket for terraform state using the AWS CLI:

   ```bash
   aws s3 mb s3://[bucket_name]
   ```

### Step 2: Configure Terraform
1. Locally download and configure Terraform [Link](https://www.terraform.io/downloads)
2. Navigate to infrastructure directory. You can change the bucket name, postgresusername, db and passowrd
3. Run the following commands to provision the cloud services

```bash
    terraform init
    terraform plan
    terraform apply --auto-approve
```
4. Copy the output and save
5. Copy Project Files to the EC2 Instance
# Copy MLflow, orchestration, Docker Compose, and environment configuration files to the EC2 instance
    scp -i "path/to/your/Mlops_projectdtc/infrastructure/mlops1.pem" -r "path_to_files/mlflow" ubuntu@[EC2_IP]:~
    scp -i "path/to/your/Mlops_projectdtc/infrastructure/mlops1.pem" -r "path_to_files/orchestration" ubuntu@[EC2_IP]:~
    scp -i "path/to/your/Mlops_projectdtc/infrastructure/mlops1.pem" "path_to_files/docker-compose.yml" ubuntu@[EC2_IP]:~
    scp -i "path/to/your/Mlops_projectdtc/infrastructure/mlops1.pem" "path_to_files/.env" ubuntu@[EC2_IP]:~

6.  SSH to the EC2 Instance
```bash    
ssh -i "path/to/your/Mlops_projectdtc/infrastructure/mlops1.pem" ubuntu@[EC2_IP]
```
7. Run the command to start the mlflow and prefect servers
```bash
sudo docker-compose up --build -d
```

### Step 3: Environment Setup
1. Activate the pip env
```bash
    pipenv shell
```
2. Set the environment variables for AWS configuration. 
NB: MLFLOW_TRACKING_URI is your EC2_IP
For Linux/macOS:
```bash
    export AWS_ACCESS_KEY_ID=[AWS_ACCESS_KEY_ID]
    export AWS_SECRET_ACCESS_KEY=[AWS_SECRET_ACCESS_KEY]
    export MLFLOW_TRACKING_URI=[MLFLOW_TRACKING_URI]
```
For Windows (using Git Bash or VS Code):
```bash
    set AWS_ACCESS_KEY_ID=[AWS_ACCESS_KEY_ID]
    set AWS_SECRET_ACCESS_KEY=[AWS_SECRET_ACCESS_KEY]
    set MLFLOW_TRACKING_URI=[MLFLOW_TRACKING_URI]
```
3. Also set the environment for the RDS (You can change or use the deafult set)
```bash
    export MLFLOW_TRACKING_USERNAME=mlflow
    export MLFLOW_TRACKING_PASSWORD=tacy12345
    export MLFLOW_TRACKING_DB_TYPE=postgresql
    export MLFLOW_TRACKING_DB_URI=postgresql://mlflow:tacy12345@my-mlflow-db-instance.c8p9u7rep2a1.us-east-1.rds.amazonaws.com:5432/mydb100
```

### Step 4.  Setup the Prefect Cloud
#### You can use the prefect servers or prefect cloud
1. Sign up an account from Prefect Cloud [Prefect Cloud](https://app.prefect.cloud/auth/login)
2. Create your workspace and generate your API Key [API-Key](https://docs.prefect.io/2.11.4/cloud/users/api-keys/)
3. Login into prefect on your terminals
```bash
    prefect cloud login -k '<api-key>'
```
### Step 5: Model Training
The artifacts are saved in s3. You can change the Bucket name in infrsatructure/main.tf
```bash
    Run the train.py under the path src/train.py
```

### Step 6 Model Deployment
To deploy this application, follow these steps:

1. Navigate to deployment/web_flask folder and build the docker-compose
```bash
sudo docker-compose up --build -d
```
Test the Flask app
```bash
python test.py
```

Also navigate to deployment/lambda_apigateway folder.
1. Install AWS SAM CLI. If you haven't already, you can find installation instructions [here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html).
2. Buiid the docker cointainer:
```bash
docker build -t ds-salary.v1 .
```
3. Run your SAM locally
```bash
sam local invoke MyLambdaFunction -e event.json --log-file output.log
```
4. If the local testing is successful, proceed with the deployment. Provide your S3 bucket name and execute the following command to package the application:
```bash
sam package --template-file template.yaml --s3-bucket <your-s3-bucket> --output-template-file packaged-template.yaml
```
```bash
sam deploy --template-file packaged-template.yaml --stack-name <your-stack-name> --capabilities CAPABILITY_IAM
```
