# vpc
resource "aws_vpc" "vpc_mlops" {
  cidr_block           = "172.16.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "vpc_mlflow"
  }
}

# Create the first Subnet 
resource "aws_subnet" "mlflow_public_subnet1" {
  vpc_id                  = aws_vpc.vpc_mlops.id
  cidr_block              = "172.16.0.0/24"  # Use a /24 subnet (256 IP addresses)
  availability_zone       = "us-east-1a"

  tags = {
    Name = "mlflow-public-subnet1"
  }
}

# Create the 2nd Subnet 
resource "aws_subnet" "mlflow_public_subnet2" {
  vpc_id                  = aws_vpc.vpc_mlops.id
  cidr_block              = "172.16.1.0/24"  # Use a different /24 subnet for the 2nd subnet
  availability_zone       = "us-east-1b"

  tags = {
    Name = "mlflow-public-subnet2"
  }
}


resource "aws_security_group" "mlops" {
  name        = "mlflow-sg"
  description = "security group with terraform"
  vpc_id      = aws_vpc.vpc_mlops.id 

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Mlflow incoming traffic"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Prefect incoming traffic"
    from_port   = 4200
    to_port     = 4200
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Prefect incoming traffic"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "Mlops"
  }
}

# Create an internet gateway
resource "aws_internet_gateway" "custom_igw" {
  vpc_id = aws_vpc.vpc_mlops.id
}

# Create the main route table for the custom VPC
resource "aws_route_table" "main_route_table" {
  vpc_id = aws_vpc.vpc_mlops.id
}

# Create a default route for the main route table to direct internet traffic to the internet gateway
resource "aws_route" "internet_gateway_route" {
  route_table_id            = aws_route_table.main_route_table.id
  destination_cidr_block    = "0.0.0.0/0"
  gateway_id                = aws_internet_gateway.custom_igw.id
}

# Associate the main route table with the public subnets
resource "aws_route_table_association" "public_subnet_association_1" {
  subnet_id      = aws_subnet.mlflow_public_subnet1.id
  route_table_id = aws_route_table.main_route_table.id
}

resource "aws_route_table_association" "public_subnet_association_2" {
  subnet_id      = aws_subnet.mlflow_public_subnet2.id
  route_table_id = aws_route_table.main_route_table.id
}

resource "aws_security_group" "postgresql" {
  name            = "postgresql-sg"
  description      = "Security group for PostgreSQL RDS"
  vpc_id           = aws_vpc.vpc_mlops.id 

  ingress {
    description = "PostgreSQL incoming traffic"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "Postgresql"
  }
}
