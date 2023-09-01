# Mlops_projectdtc


# Data Science Salary Prediction

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

```bash
# Clone the repository
git clone https://github.com/Taciturny/Mlops_projectdtc.git

# Change to the project directory
cd Mlops_projectdtc
```

![Prefect Architecture](Project_archet/project_arch.jpg)

# Project Structure
```bash
Mlops_projectdtc/
│
├── aws_infrastructure/        # AWS infrastructure setup
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── mlflow_setup.sh        # Script to install and configure MLflow
│
├── mlflow/                    # MLflow setup on AWS EC2 instance
│   ├── Dockerfile-mlflow
│   └── requirements.txt
│
├── orchestration/             # Prefect workflows and task definitions
│   ├── prefect_agent_config
│   ├── Dockerfile.prefect_agent.py
│   ├── Dockerfile.prefect_server.py
│   └── prefect_setup.sh
│
├── src/                        # Model training
│   ├── train_model.py
│   └── ...
│
├── deployment/                 # Model deployment configuration 
│   ├── web_flask/
│   ├── apigateway_lambda/
│   └── ...
│
├── monitoring/                # Directory for monitoring related files
│   ├── baseline_model.ipynb
│   ├── evidently_metrics.py
│   └── .....
│
├── tests/              # Directory for testing related files
│   ├── interation_test
│   └── unit_test
│
└── README.md                  # Detailed project documentation and instructions
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
3. Run the following commands to provision the cloud services and delete when done

```bash
    terraform init
    terraform plan
    terraform apply --auto-approve
    terraform destroy --auto-approve
```
4. Copy the output and save

5. Copy Project Files to the EC2 Instance

 Copy MLflow, orchestration, Docker Compose, and environment configuration files to the EC2 instance
 ```bash
    scp -i "path/to/your/Mlops_projectdtc/infrastructure/mlops1.pem" -r "path_to_files/mlflow" ec2-user@your-ec2-instance:/path/on/ec2/
    scp -i "path/to/your/Mlops_projectdtc/infrastructure/mlops1.pem" -r "path_to_files/orchestration" ec2-user@your-ec2-instance:/path/on/ec2/
    scp -i "path/to/your/Mlops_projectdtc/infrastructure/mlops1.pem" "path_to_files/docker-compose.yml" ec2-user@your-ec2-instance:/path/on/ec2/
    scp -i "path/to/your/Mlops_projectdtc/infrastructure/mlops1.pem" "path_to_files/.env" ec2-user@your-ec2-instance:/path/on/ec2/
 ```

6.  SSH to the EC2 Instance
```bash    
ssh -i "path/to/your/Mlops_projectdtc/infrastructure/mlops1.pem" ec2-user@your-ec2-instance:/path/on/ec2/
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
![Mlflow-ui](Project_archet/mlflow1.png)

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
![Prefect-ui](Project_archet/prefect2.png)

### Step 6 Model Deployment
To deploy this application, follow these steps:

1. Navigate to deployment/web_flask folder and build the docker-compose
```bash
sudo docker-compose up --build -d
```
Test the Flask app
```bash
python predict.py && python test.py
```

Also navigate to deployment/sam-app/ folder.
1. Install AWS SAM CLI. If you haven't already, you can find installation instructions [here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html).
2. Build SAM
```bash
sam build
```
3. Validate SAM
```bash
sam validate --lint
```
4. Run SAM locally
```bash
sam local invoke PredictFunction -e event.json 
```
5. If the local testing is successful, proceed with the deployment. Use 'sam deploy --guided' only once:
```bash
sam deploy --guided
```
Here is how it should be

![sam-deploy](Project_archet/term1.png)


6. Navigate to the Api Gateway on the console and get your API ID for the URL endpoint and use either terminale or postman:
![Postman](Project_archet/postman.png)


```bash
curl -X POST https://<API_ID>.execute-api.us-east-1.amazonaws.com/dev/predict -H "Content-Type: application/json" -d @events/event.json
```

8. Delete the stack after testing:
```bash
aws cloudformation delete-stack --stack-name <your-stack-name>
```

### Step 7 Monitoring (Locally)
Navigate to the `monitoring` folder.
1. Create a Conda environment and install the required dependencies from `requirements.txt`:
```bash
conda create -n myenv python=3.11
conda activate myenv
pip install -r requirements.txt
```
2. Build the Docker Compose environment for PostgreSQL and Grafana.
```bash
docker-compose up --build -d
```
3. Run the notebook (baseline_model.ipynb) and save the training and testing CSV data.

4. Execute the script. When it's done, stop the Docker Compose environment.
```bash
python evidently_metrics.py
```
![](Project_archet/datadrift1.png)

### Step 8: Tests (Unit and Integration Tests)

1. Navigate to the `test` folder and install `pytest` and `pylint` as development dependencies:

    ```bash
    pipenv install pytest pylint --dev
    ```

2. Go to the `integration_test` folder and run pytest for the tests:

    ```bash
    pipenv run pytest tests/
    ```

3. Additionally, you can run `pylint` on your project by executing the following command from the project's root directory:

    ```bash
    pipenv run pylint --recursive=y .
    ```

4. Navigate to the `unit_tests` folder and run pytest for the tests:

    ```bash
    pipenv run pytest tests/
    ```
