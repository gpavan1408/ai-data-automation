import subprocess
import sys
import os

def run_step(command, description):
    """
    Runs an external command, prints its status, and exits the script if the command fails.
    """
    print(f"🚀 STARTING: {description}")
    try:
        # We use subprocess.run() to execute the command.
        # 'shell=True' allows us to run complex shell commands.
        # 'check=True' will automatically raise an exception if the command fails (returns a non-zero exit code).
        subprocess.run(command, shell=True, check=True)
        print(f"✅ COMPLETED: {description}\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ FAILED: {description}")
        print(f"Error: {e}")
        # Exit the entire pipeline script with an error code.
        sys.exit(1)

def main():
    """
    Main function to run the entire data and ML pipeline in sequence.
    """
    # Get the project's root directory, which is one level up from this script's folder.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # --- Main Pipeline Steps ---

    # Step 1: Run the Spark data processing job.
    process_script_path = os.path.join(project_root, "data_processing", "spark_jobs", "spark_etl.py")
    run_step(f"python {process_script_path}", "Running Spark data processing job")

    # Step 2: Run the model training script.
    train_script_path = os.path.join(project_root, "model_training", "train_model.py")
    run_step(f"python {train_script_path}", "Training the fraud detection model")
    
    # Step 3: Run the Terraform deployment.
    terraform_dir = os.path.join(project_root, "deployment", "terraform")
    # We construct a single command that first changes directory to the terraform folder,
    # and then runs 'terraform apply'. The '-auto-approve' flag is for automation.
    terraform_command = f"cd {terraform_dir} && terraform apply -auto-approve"
    run_step(terraform_command, "Deploying model to S3 via Terraform")

    print("🎉🎉🎉 --- Full pipeline completed successfully! --- 🎉🎉🎉")

if __name__ == "__main__":
    main()