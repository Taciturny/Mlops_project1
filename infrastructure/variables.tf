// region
variable "region" {
  description = "AWS region to create resources in"
  type  = string
  default = "us-east-1"
}

// s3 variable

variable "mlflow-artifact-storage-name10" {
  description = "Name of the mlflow-artifact-storage"
  default     = "my-mlflow-artifact-storage-name"
  type        = string
}

// EC2
# variable "instance_name" {
#   description = "Name of the instance to be created"
#   default     = "awsbuilder-demo"
#   type        = string
# }

variable "ec2_instance_type" {
  default = "t2.large"
  type    = string
}

variable "subnet_id" {
  description = "The VPC subnets the instance(s) will be created in"
  type        = list(string)
  default     = []  # Provide an empty list as the default value
}

variable "ami_id" {
  description = "The AMI to use"
  default     = "ami-053b0d53c279acc90"
  type        = string
}

variable "number_of_instances" {
  description = "Number of instances to be created"
  default     = 1
  type        = number
}

# variable "key_pair_name" {
#   default = "mlops1"
#   type    = string
# }



variable "db_subnet_ids" {
  type        = list(string)
  default     = null
  description = "List of subnets where the RDS database will be deployed"
}



// RDS
variable "rds_database_name" {
  description = "Name of the RDS database"
  default     = "mlflowdb"
  type        = string
}


variable "allocated_storage" {
  default     = 32
  type        = number
  description = "Storage allocated to database instance"
}

variable "engine_version" {
  default     = "13.9"
  type        = string
  description = "Database engine version"
}

variable "rds_instance_type" {
  default     = "db.t3.micro"
  type        = string
  description = "Instance type for database instance"
}

variable "storage_type" {
  default     = "gp2"
  type        = string
  description = "Type of underlying storage for database"
}


variable "db_identifier" {
  description = "The identifier for the RDS instance."
  type        = string
  default     = "my-mlflow-db-instance"
}


variable "database_name" {
  type        = string
  description = "Name of database inside storage engine"
  default = "mydb100"
}

variable "database_username" {
  type        = string
  description = "Name of user inside storage engine"
  default = "mlflow"
}

variable "database_password" {
  type        = string
  description = "Database password inside storage engine"
  default = "tacy12345"
  sensitive   = true
}

variable "database_port" {
  default     = 5432
  type        = number
  description = "Port on which database will accept connections"
}

variable "database_host" {
  type        = string
  description = "Hostname of the database server"
  default = "mlflow1"
}


variable "skip_final_snapshot" {
  default     = true
  type        = bool
  description = "Flag to enable or disable a snapshot if the database instance is terminated"
}


variable "multi_availability_zone" {
  default     = false
  type        = bool
  description = "Flag to enable hot standby in another availability zone"
}

variable "deletion_protection" {
  default     = false
  type        = bool
  description = "Flag to protect the database instance from deletion"
}

