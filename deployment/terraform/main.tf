# Configures the AWS provider and sets the region.
provider "aws" {
  region = "us-east-1"
}

# Defines the S3 bucket for storing all project data and artifacts.
resource "aws_s3_bucket" "dashboard_bucket" {
  bucket = "automation-ai-dashboard-bucket-2025"
}

# Defines the IAM Role that AWS Glue will use for its own operations.
resource "aws_iam_role" "glue_service_role" {
  name = "AI-Dashboard-Glue-Service-Role"

  # Trust policy allowing ONLY the Glue service to use this role.
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      },
    ]
  })
}

# Attaches the AWS-managed policy for general Glue service operations.
resource "aws_iam_role_policy_attachment" "glue_service_policy_attachment" {
  role       = aws_iam_role.glue_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Defines a custom policy to grant specific access to our S3 bucket.
resource "aws_iam_policy" "s3_access_policy" {
  name        = "AI-Dashboard-S3-Access-Policy"
  description = "Allows access to the AI Dashboard S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = "${aws_s3_bucket.dashboard_bucket.arn}/*" # For objects inside the bucket
      },
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = aws_s3_bucket.dashboard_bucket.arn # For the bucket itself
      }
    ]
  })
}

# Attaches our custom S3 access policy to the Glue role.
resource "aws_iam_role_policy_attachment" "s3_access_attachment" {
  role       = aws_iam_role.glue_service_role.name
  policy_arn = aws_iam_policy.s3_access_policy.arn
}

# Uploads the Spark ETL script from our local machine to S3.
resource "aws_s3_object" "spark_etl_script" {
  bucket = aws_s3_bucket.dashboard_bucket.id
  key    = "scripts/cloud_spark_etl.py" # Using the dedicated cloud script
  source = "../../data_processing/glue_jobs/cloud_spark_etl.py"
  etag   = filemd5("../../data_processing/glue_jobs/cloud_spark_etl.py")
}

# Creates a database in the AWS Glue Data Catalog.
resource "aws_glue_catalog_database" "ai_dashboard_database" {
  name = "ai_dashboard_db"
}

# Creates the Glue Crawler to scan S3 data and create tables.
resource "aws_glue_crawler" "s3_crawler" {
  name          = "AI-Dashboard-S3-Crawler"
  database_name = aws_glue_catalog_database.ai_dashboard_database.name
  role          = aws_iam_role.glue_service_role.arn

  s3_target {
    path = "s3://${aws_s3_bucket.dashboard_bucket.id}/processed/users/"
  }
}

# Defines the Glue Job to run our Spark script in the cloud.
resource "aws_glue_job" "spark_etl_job" {
  name     = "AI-Dashboard-Spark-ETL-Job"
  role_arn = aws_iam_role.glue_service_role.arn

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.dashboard_bucket.id}/${aws_s3_object.spark_etl_script.key}"
    python_version  = "3"
  }
  
  default_arguments = {
    "--S3_INPUT_PATH"  = "s3://${aws_s3_bucket.dashboard_bucket.id}/raw/api_users_data.json"
    "--S3_OUTPUT_PATH" = "s3://${aws_s3_bucket.dashboard_bucket.id}/processed/users/"
  }

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 5
}

# --- EventBridge Automation Section ---

# This policy gives permission to START a crawler.
resource "aws_iam_policy" "start_crawler_policy" {
  name   = "AI-Dashboard-Start-Crawler-Policy"
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "glue:StartCrawler"
      Resource = aws_glue_crawler.s3_crawler.arn
    }]
  })
}

# This is a NEW, DEDICATED role for EventBridge to use.
resource "aws_iam_role" "eventbridge_glue_role" {
  name = "AI-Dashboard-EventBridge-Glue-Role"

  # This role can ONLY be assumed by the EventBridge service.
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "events.amazonaws.com" }
    }]
  })
}

# Attaches the "start crawler" policy to our new EventBridge role.
resource "aws_iam_role_policy_attachment" "eventbridge_start_crawler_attachment" {
  role       = aws_iam_role.eventbridge_glue_role.name
  policy_arn = aws_iam_policy.start_crawler_policy.arn
}

# This defines the rule that listens for a successful Glue job run.
resource "aws_cloudwatch_event_rule" "run_crawler_on_job_success" {
  name        = "RunCrawlerAfterGlueJobSuccess"
  description = "Triggers the Glue Crawler when the ETL job succeeds"

  event_pattern = jsonencode({
    source      = ["aws.glue"],
    "detail-type" = ["Glue Job State Change"],
    detail      = {
      jobName = [aws_glue_job.spark_etl_job.name],
      state   = ["SUCCEEDED"]
    }
  })
}

# EventBridge target updated to invoke Lambda, not Glue Crawler
resource "aws_cloudwatch_event_target" "trigger_lambda_target" {
  rule      = aws_cloudwatch_event_rule.run_crawler_on_job_success.name
  arn       = "arn:aws:lambda:us-east-1:654654515599:function:Start-Crawler-Lambda"
  role_arn  = aws_iam_role.eventbridge_glue_role.arn
}



output "glue_crawler_arn_debug" {
  value = aws_glue_crawler.s3_crawler.arn
}

# Grant EventBridge permission to invoke the Lambda
resource "aws_lambda_permission" "allow_eventbridge_to_invoke_lambda" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = "S3-Ingestion-Trigger"  # OR use aws_lambda_function.<name>.function_name if you created Lambda in Terraform
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.run_crawler_on_job_success.arn
}
