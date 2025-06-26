import sys
import os
from pyspark.sql import SparkSession
from awsglue.utils import getResolvedOptions

# --- Get Job Arguments from AWS Glue ---
args = getResolvedOptions(sys.argv, [
    'S3_INPUT_PATH',
    'S3_OUTPUT_PATH'
])
s3_input_path = args['S3_INPUT_PATH']
s3_output_path = args['S3_OUTPUT_PATH']


def process_generic_data():
    """
    Reads any supported file format (CSV, JSON, Parquet) from S3,
    logs its schema, and saves it as Parquet without errors.
    """
    print("Initializing generic Spark ETL job...")
    spark = SparkSession.builder.appName("Generic-Cloud-ETL").getOrCreate()

    # --- 1. DYNAMICALLY READ DATA ---
    print(f"Reading raw data from {s3_input_path}")
    file_format = s3_input_path.split('.')[-1].lower()

    try:
        if file_format == 'json':
            df = spark.read.option("multiLine", True).json(s3_input_path)
        elif file_format == 'csv':
            df = spark.read.option("header", True).option("inferSchema", True).csv(s3_input_path)
        elif file_format == 'parquet':
            df = spark.read.parquet(s3_input_path)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
    except Exception as e:
        print(f"❌ ERROR: Failed to read input file. It might be corrupted or in the wrong format.")
        print(e)
        sys.exit(1)

    # --- 2. LOG SCHEMA AND VALIDATE ---
    print("\n--- Inferred Input Schema ---")
    df.printSchema()

    input_count = df.count()
    print(f"Input record count: {input_count}")
    if input_count == 0:
        print("❌ ERROR: Input file contains no data. Aborting job.")
        sys.exit(1)

    # --- 3. DYNAMIC TRANSFORMATION ---
    print("\nPerforming generic transformation (ensuring clean column names)...")
    
    # This is a generic transformation that works on ANY DataFrame.
    # It replaces characters that are not allowed in Parquet column names.
    cleaned_columns = [c.replace(' ', '_').replace(';', '').replace('}', '').replace('{', '').replace(')', '').replace('(', '').replace('=', '') for c in df.columns]
    df_transformed = df.toDF(*cleaned_columns)

    print("\n--- Output Data Schema ---")
    df_transformed.printSchema()
    
    # --- 4. LOAD ---
    print(f"\nSaving processed data to {s3_output_path}")
    # We will save the output in a sub-folder named after the original file to keep things organized
    # output_filename = os.path.basename(s3_input_path)
    # final_output_path = os.path.join(s3_output_path, output_filename)
    # df_transformed.write.mode("overwrite").parquet(s3_output_path)

    # print(f"✅ Generic ETL job complete. Output saved to {final_output_path}")
    # spark.stop()

    
    print(f"\nSaving processed data to {s3_output_path}")
    df_transformed.write.mode("overwrite").parquet(s3_output_path)
    print(f"✅ Generic ETL job complete. Output saved to {s3_output_path}")
    spark.stop()



if __name__ == "__main__":
    process_generic_data()