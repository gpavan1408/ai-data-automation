# This block configures the AWS provider, telling Terraform we are working with AWS.
provider "aws" {
  region = "us-east-1"
}

# This block defines the S3 bucket we created earlier.
# Make sure the bucket name is the same unique name you used before.
resource "aws_s3_bucket" "dashboard_bucket" {
  bucket = "automation-ai-dashboard-bucket-2025"
}

# This block defines a new resource: an object (a file) to be placed in our S3 bucket.
resource "aws_s3_object" "model_upload" {
  # This links the object to the bucket we defined above.
  bucket = aws_s3_bucket.dashboard_bucket.id

  # This is the name and path the file will have inside the S3 bucket.
  key    = "models/fraud_detection_model.joblib"

  # This is the path to the local file on your computer that you want to upload.
  # Terraform needs a relative path from this main.tf file's location.
  source = "../../models/fraud_detection_model.joblib"

  # The etag helps Terraform know if the file has changed and needs to be re-uploaded.
  etag = filemd5("../../models/fraud_detection_model.joblib")
}