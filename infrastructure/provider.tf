# create the state bucket mlops-dtc-project011
terraform {
  required_version = ">= 1.0"
  backend "s3" {
    bucket  = "mlops-dtc-project011"
    key     = "mlops-zoomcamp-stg.tfstate"
    region = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.region
}

