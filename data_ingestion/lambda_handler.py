import json
import urllib.parse

def lambda_handler(event, context):
    """
    This function is triggered when a new file is uploaded to S3.
    It logs the metadata of the uploaded file.
    """
    try:
        # Get the bucket name from the S3 event record
        bucket = event['Records'][0]['s3']['bucket']['name']
        
        # Get the file key (name), handling spaces or special characters
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        
        # Print a log message that will appear in Amazon CloudWatch
        print(f"✅ Success! A file named '{key}' was uploaded to the bucket '{bucket}'.")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Lambda function executed successfully!')
        }
    except Exception as e:
        print(f"❌ Error processing event: {e}")
        raise e