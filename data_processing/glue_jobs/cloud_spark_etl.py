import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from awsglue.utils import getResolvedOptions

# --- Get Job Arguments from AWS Glue ---
# This special Glue utility reads arguments passed to the job when it runs.
args = getResolvedOptions(sys.argv, [
    'S3_INPUT_PATH',
    'S3_OUTPUT_PATH'
])
s3_input_path = args['S3_INPUT_PATH']
s3_output_path = args['S3_OUTPUT_PATH']


# --- Spark Application ---
def process_data_with_spark():
    """
    Initializes a Spark session, reads raw data from a given S3 path, 
    transforms it, and saves it to a given S3 output path.
    """
    print("Initializing Spark session in the cloud...")
    spark = SparkSession.builder.appName("AI-Dashboard-Cloud-ETL").getOrCreate()

    # The script now uses the S3 path it received as an argument.
    print(f"Reading raw data from {s3_input_path}")
    df = spark.read.option("multiLine", True).json(s3_input_path)

    print("Transforming data...")
    df_transformed = df.select(
        col("id"), col("name"), col("username"), col("email"), 
        col("phone"), col("website"), col("company.name").alias("company_name")
    )
    
    # The script now writes the output directly back to S3.
    print(f"Saving processed data to {s3_output_path}")
    df_transformed.write.mode("overwrite").parquet(s3_output_path)

    print("✅ Cloud Spark ETL job complete.")
    spark.stop()


if __name__ == "__main__":
    process_data_with_spark()