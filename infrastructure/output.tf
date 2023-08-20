output "mlflow-model-artifact" {
  value = "s3://${var.mlflow-artifact-storage-name10}"
}

output "ec2_public_ip" {
  value = aws_instance.ec2_instance.public_ip
}

output "rds_endpoint" {
  value = aws_db_instance.postgresql[*].endpoint
}

output "mlflow_server_url" {
  value = "http://${aws_instance.ec2_instance.public_ip}:5000/"
}

# output "prefect_server_url" {
#   value = "http://${aws_instance.ec2_instance.public_ip}:8080/"
# }

output "prefect_server_url" {
  value = "http://${aws_instance.ec2_instance.public_ip}:4200/"
}
