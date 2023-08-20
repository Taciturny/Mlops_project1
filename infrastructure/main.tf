data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_db_subnet_group" "rds" {
  name       = "rds-subnet-group"
  subnet_ids = ["${aws_subnet.mlflow_public_subnet1.id}","${aws_subnet.mlflow_public_subnet2.id}"]
}


// EC2 instance
resource "tls_private_key" "mlops1_rsa" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "local_file" "mlops1_dtc" {
  content  = tls_private_key.mlops1_rsa.private_key_pem
  filename = "mlops1.pem"
}

resource "aws_key_pair" "mlops_keypair" {
  key_name   = "mlops1"  # keypair
  public_key = tls_private_key.mlops1_rsa.public_key_openssh
}



resource "aws_instance" "ec2_instance" {
  ami                          = var.ami_id
  subnet_id                    = aws_subnet.mlflow_public_subnet1.id
  instance_type                = var.ec2_instance_type
  key_name                     = aws_key_pair.mlops_keypair.key_name
  vpc_security_group_ids       = [aws_security_group.mlops.id] 
  associate_public_ip_address  = true
  user_data                    = file("docker_mlflow.sh")

  tags = {
    Name = "Mlops"
  }
}


// RDS

resource "aws_db_instance" "postgresql" {
allocated_storage               = var.allocated_storage
engine                          = "postgres"
engine_version                  = var.engine_version
instance_class                  = var.rds_instance_type
storage_type                    = var.storage_type
identifier                      = var.db_identifier
db_name                         = var.database_name
password                        = var.database_password
username                        = var.database_username
multi_az                        = var.multi_availability_zone
port                            = var.database_port
skip_final_snapshot             = var.skip_final_snapshot
vpc_security_group_ids          = [aws_security_group.postgresql.id]    
db_subnet_group_name            = aws_db_subnet_group.rds.name
deletion_protection             = var.deletion_protection
}


resource "aws_s3_bucket" "b" {
  bucket = var.mlflow-artifact-storage-name10
  acl    = "private"
  force_destroy = true

  tags = {
    Name = "mlflow_artifact_bucket"
  }
}


