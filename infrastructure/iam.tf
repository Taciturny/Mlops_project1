resource "aws_iam_policy" "mlflow_policy" {
  name        = "MLflow_Policy"
  description = "IAM policy for MLflow backend with RDS and S3 bucket for tracking and database management"

  policy = jsonencode({
    Version : "2012-10-17",
    Statement : [
      {
        Effect   : "Allow",
        Action   : [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
          "ec2:DescribeInstances",
          "ec2:DescribeInstanceStatus",
          "rds:DescribeDBInstances",
          "rds:CreateDBInstance",
          "rds:DeleteDBInstance",
          "rds:ModifyDBInstance",
          "rds:RestoreDBInstanceFromDBSnapshot",
          "rds:RebootDBInstance",
          "rds:ListTagsForResource",
          "rds:AddTagsToResource",
          "rds:RemoveTagsFromResource"
        ],
        Resource : [
          "arn:aws:s3:::mlflow-artifact-storage-name20/*",
          "arn:aws:rds:us-east-1::db:mlflowdb"
        ]
      }
    ]
  })
}
