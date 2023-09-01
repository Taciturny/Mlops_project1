import pandas as pd
import joblib
import optuna
import boto3
import os
import mlflow
import mlflow.sklearn
from typing import List, Tuple, Any, Dict
import zipfile
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import mean_squared_error, mean_absolute_error
from datetime import timedelta
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient
from mlflow.entities.model_registry.model_version import ModelVersion
from prefect import task, Flow
# from prefect.engine.executors import SequentialExecutor
from optuna.samplers import TPESampler
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import IntervalSchedule


mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])
EXPERIMENT_NAME =  'RandomForest_training:v1'
HYO_EXPERIMENT_NAME = 'RandomForest_tuning'
MODEL_NAME = 'RandomForest_Salary_Prediction_Model'
mlflow.sklearn.autolog()

# mlflow.set_experiment(EXPERIMENT_NAME) EXPERIMENT_NAME = 'RandomForest_best_model'
# @task(retries=3, retry_delay_seconds=2, name='Experiment setup')
def setup_experiment():
    print("Current Working Directory:", os.getcwd())
    
    data_path = "../data/ds_sal.zip"
    print("Data file path:", os.path.abspath(data_path))

    if os.path.exists(data_path):
        print("File exists.")
    else:
        print("File does not exist.")

    mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])
    mlflow.sklearn.autolog()


# @task(retries=3, retry_delay_seconds=2, name='Read Data')
def load_data(zip_data: str, csv_name: str) -> pd.DataFrame:
    '''
    Load data from a CSV file inside a ZIP file

    Args:
        zip_data (str): Path to the ZIP file containing the CSV file.
        csv_name (str): Name of the CSV file within the ZIP archive.

    Returns:
        pd.DataFrame: A DataFrame containing the loaded data.
    '''
    with zipfile.ZipFile(zip_data, 'r') as zip_ref:
        df = pd.read_csv(zip_ref.open(csv_name))
    return df



# @task(retries=3,retry_delay_seconds=2, name='Preprocess Data')
def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Preprocess the data, rename categories within columns, and remove outliers.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The preprocessed DataFrame.
    '''
    # Rename categories within columns
    df['experience_level'].replace(['SE', 'MI', 'EN', 'EX'],
                                   ['Senior_level', 'Mid_level', 'Entry_level', 'Executive_level'],
                                   inplace=True)
    df['employment_type'].replace(['FT', 'PT', 'CT', 'FL'],
                                  ['Full_time', 'Part_time', 'Contract', 'Freelance'],
                                  inplace=True)
    df['remote_ratio'].replace([0, 50, 100], ['Onsite', 'Hybrid', 'Remote'], inplace=True)
    df['company_size'].replace(['L', 'M', 'S'], ['Large', 'Medium', 'Small'], inplace=True)

    # Remove outlier
    df = df[df['salary_in_usd'] < 300000]

    return df


# @task(retries=3,retry_delay_seconds=2, name='Splitting Data')
def split_data(df: pd.DataFrame, target_column: str, test_size=0.2, random_state=42):
    '''
    Split the data into training and testing sets.

    Args:
        df (pd.DataFrame): The input DataFrame.
        target_column (str): The name of the target column.
        test_size (float, optional): The proportion of the data to include in the test split.
        random_state (int, optional): Random seed for reproducibility.

    Returns:
        pd.DataFrame: Training data features.
        pd.DataFrame: Testing data features.
        pd.Series: Training data target.
        pd.Series: Testing data target.
    '''
    features = df.drop(columns=[target_column])
    target = df[target_column]

    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=test_size, random_state=random_state)

    return X_train, X_test, y_train, y_test


# @task(retries=3, retry_delay_seconds=2, name='Model Training')
def model_train(X_train, X_test, y_train, y_test, max_depth=10):
    '''
    Train the model and log RMSE using MLflow

    Args:
        X_train (pd.DataFrame): Training data features.
        X_test (pd.DataFrame): Testing data features.
        y_train (pd.Series): Training data labels.
        y_test (pd.Series): Testing data labels.
        max_depth (int, optional): Maximum depth of the RandomForestRegressor.

    Returns:
        None
    '''
    mlflow.set_experiment(EXPERIMENT_NAME)    # Set the tracking URI to your S3 bucket

    with mlflow.start_run():

        mlflow.set_tag("model", "RandomForest")
        mlflow.log_param("max_depth", max_depth)

        pipeline = make_pipeline(
            DictVectorizer(),
            RandomForestRegressor(max_depth=max_depth, random_state=0, n_jobs=-1)
        )
        X_train_dict = X_train.to_dict(orient='records')
        pipeline.fit(X_train_dict, y_train)
        X_test_dict = X_test.to_dict(orient='records')
        y_pred = pipeline.predict(X_test_dict)
        rmse = mean_squared_error(y_test, y_pred, squared=False)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Log metrics
        mlflow.log_metric('rmse', rmse)
        mlflow.log_metric('mse', mse)
        mlflow.log_metric('mae', mae)
        
        # Log artifacts (model file, visualization, etc.)
        mlflow.sklearn.log_model(pipeline, "random_forest_model")

        return rmse, mse, mae



# @task(retries=3, retry_delay_seconds=2, name='Hyperparameter Tunning')
def run_optimization(X_train: pd.DataFrame, X_test: pd.DataFrame,
                     y_train: pd.Series, y_test: pd.Series,
                     num_trials: int) -> None:
    '''
    Utilize Optuna to perform hyperparameter optimization for a machine learning model.

    Args:
        X_train (pd.DataFrame): Training features DataFrame.
        X_test (pd.DataFrame): Testing features DataFrame.
        y_train (pd.Series): Training target Series.
        y_test (pd.Series): Testing target Series.
        num_trials (int): Number of optimization trials to perform.

    Returns:
        None
    '''
    mlflow.set_experiment(HYO_EXPERIMENT_NAME)

    def objective(trial):
        params = {
            'max_depth': trial.suggest_int('max_depth', 1, 30),
            'n_estimators': trial.suggest_int('n_estimators', 50, 500),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 20),
            'min_samples_split': trial.suggest_int('min_samples_split', 2, 30),
            'max_features': trial.suggest_float('max_features', 0.1, 1.0),
            'random_state': 0,
        }

        with mlflow.start_run():
            mlflow.set_tag("model", "RandomForest")
            mlflow.set_tag("run type", "hyperparameter-tuning")
            mlflow.log_params(params)

            pipeline = make_pipeline(
                DictVectorizer(),
                RandomForestRegressor(**params, n_jobs=1)
            )

            X_train_dict = X_train.to_dict(orient='records')
            pipeline.fit(X_train_dict, y_train)
            X_test_dict = X_test.to_dict(orient='records')
            y_pred = pipeline.predict(X_test_dict)
            rmse = mean_squared_error(y_test, y_pred, squared=False)
            mlflow.log_metric('rmse', rmse)
            mse = mean_squared_error(y_test, y_pred)
            mlflow.log_metric('mse', mse)
            mae = mean_absolute_error(y_test, y_pred)
            mlflow.log_metric('mae', mae)
            mlflow.sklearn.log_model(pipeline, "random_forest_model_v1")
            return rmse, mse, mae

    sampler = TPESampler(seed=42)
    # parallel_sampler = ParallelSampler(sampler, n_jobs=-1)
    study = optuna.create_study(direction="minimize", sampler=sampler)
    study.optimize(objective, n_trials=num_trials)


# @task(retries=3,retry_delay_seconds=2, name='Model Evaluation')
def evaluate_model(pipeline, X_test, y_test):
    """
    Evaluate the trained model's performance using RMSE, MSE, and MAE.

    Args:
        pipeline: Trained machine learning pipeline.
        X_test (pd.DataFrame): Testing data features.
        y_test (pd.Series): Testing data labels.

    Returns:
        dict: A dictionary containing calculated metrics.
    """
    X_test_dict = X_test.to_dict(orient='records')
    y_pred = pipeline.predict(X_test_dict)
    
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    evaluation_metrics = {
        'rmse': rmse,
        'mse': mse,
        'mae': mae
    }

    # Log metrics using MLflow
    with mlflow.start_run():
        for metric_name, metric_value in evaluation_metrics.items():
            mlflow.log_metric(metric_name, metric_value)
    
    return evaluation_metrics


# @task(log_prints=True, name='Model Registry')
def register_best_model(top_n: int) -> ModelVersion:
    '''
    Registers the best model and manages its production stage based on the lowest RMSE.

    Args:
        top_n (int): The number of top runs to consider for selecting the best model.

    Returns:
        ModelVersion: The registered model version in MLflow's model registry.
    '''
    client = MlflowClient()
    experiment = client.get_experiment_by_name(HYO_EXPERIMENT_NAME)
    runs = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=top_n,
        order_by=['metrics.rmse ASC']
    )

    # Fetch the best run ID
    best_run_id = runs[0].info.run_id

    # Register the best model
    model_uri = f"runs:/{best_run_id}/model"
    model_name = MODEL_NAME  # Change the model name as per your preference
    mv = mlflow.register_model(model_uri, name=model_name)

    # Get the production model's run ID (if any)
    registered_model = client.search_registered_models(filter_string=f"name='{model_name}'")
    production_run_id = [
        model.run_id
        for model in registered_model[0].latest_versions
        if model.current_stage == 'Production'
    ]

    if len(production_run_id) > 0:
        # Get RMSE of both the best run and the production run
        best_run = client.get_run(best_run_id)
        best_run_rmse = best_run.data.metrics['rmse']

        production_run = client.get_run(production_run_id[0])
        production_run_rmse = production_run.data.metrics['rmse']

        # If best model is better than production model, promote it to production and archive the production model
        if best_run_rmse < production_run_rmse:
            # Archive the previous production model
            previous_production_run_id = production_run_id[0]
            client.transition_model_version_stage(
                name=model_name,
                version=client.get_run(previous_production_run_id).info.artifact_uri.split("/")[-1],
                stage="Archived",
                archive_existing_versions=True,
            )

            # Transition the new best model to 'Production' stage
            model_version = mv.version
            new_stage = "Production"
            client.transition_model_version_stage(
                name=model_name,
                version=model_version,
                stage=new_stage,
                archive_existing_versions=False,
            )

        else:
            # If best model is not better than production, archive the best model
            model_version = mv.version
            new_stage = "Archived"
            client.transition_model_version_stage(
                name=model_name,
                version=model_version,
                stage=new_stage,
                archive_existing_versions=False,
            )
            
    else:
        # If no production model exists, set the new model as production
        model_version = mv.version
        new_stage = "Production"
        client.transition_model_version_stage(
            name=model_name,
            version=model_version,
            stage=new_stage,
            archive_existing_versions=False,
        )

    # Return the best run details
    best_run = client.get_run(best_run_id)
    return best_run


# @Flow
def main_flow(
        zip_file: str = './data/ds_sal.zip',
        file_name: str = 'ds_salaries.csv',
        num_trials: int = 20) -> None:   #change to the number of runs
    """
    The main training pipeline.

    This function orchestrates the end-to-end machine learning operations (MLOps) pipeline,
    including data loading, preprocessing, model training, hyperparameter optimization,
    model saving to S3, and model registration in MLflow's model registry.

    Args:
        zip_file (str): The path to the ZIP file containing the dataset.
        file_name (str): The name of the CSV file within the ZIP archive.

    Returns:
        None
    """
    setup_experiment()
    df = load_data(zip_file, file_name)
    df = preprocess(df)
    # Split the data into train and test sets
    X_train, X_test, y_train, y_test = split_data(df, target_column='salary_in_usd', test_size=0.2, random_state=42)
    model_train(X_train, X_test, y_train, y_test)
    best_params = run_optimization(X_train, X_test, y_train, y_test, num_trials=num_trials)
    register_best_model(top_n=10)    #change if needed

if __name__ == '__main__':
    main_flow()

deployment = Deployment.build_from_flow(
    flow=main_flow,
    name="ds_salaries_training",
    schedule=IntervalSchedule(interval=timedelta(minutes=120)), #480
    work_queue_name="ml"
)

deployment.apply()


# mlflow server backend-store-uri sqlite:///mlflow1.db default-artifact-root s3://artifactss31991/models/
