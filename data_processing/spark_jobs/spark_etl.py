import os
import sys

# --- Part 1: Setup Spark Environment ---
def setup_spark_environment():
    print("Configuring environment for Spark...")

    # Hardcoded correct paths (no need for java_home / hadoop_home variables)
    os.environ['JAVA_HOME'] = 'C:\\Program Files\\Amazon Corretto\\jdk11.0.27.6.1'
    os.environ['HADOOP_HOME'] = 'C:\\Hadoop'

    # Add them to PATH for this process
    os.environ["PATH"] = f"{os.environ['JAVA_HOME']}\\bin;{os.environ['HADOOP_HOME']}\\bin;{os.environ['PATH']}"

    print(f"JAVA_HOME set to: {os.environ['JAVA_HOME']}")
    print(f"HADOOP_HOME set to: {os.environ['HADOOP_HOME']}")
    print("Environment configured successfully.\n")

# Call setup before importing pyspark
setup_spark_environment()

# --- Part 2: Spark Application ---
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def process_data_with_spark():
    print("Initializing Spark session...")
    spark = SparkSession.builder \
        .appName("UserDataTransformation") \
        .master("local[2]") \
        .config("spark.driver.host", "127.0.0.1") \
        .getOrCreate()

    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    INPUT_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "api_users_data.json")
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, "users.parquet")

    print(f"Reading raw data from {INPUT_PATH}")
    df = spark.read.option("multiLine", True).json(INPUT_PATH)

    print("Transforming data with Spark...")
    df_transformed = df.select(
        col("id"), col("name"), col("username"), col("email"), 
        col("phone"), col("website"), col("company.name").alias("company_name")
    )

    print(f"Saving processed data to {OUTPUT_FILE}")
    df_transformed.write.mode("overwrite").parquet(OUTPUT_FILE)

    print("✅ Spark job complete. Stopping Spark session.")
    spark.stop()

if __name__ == "__main__":
    process_data_with_spark()
