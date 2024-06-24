import os
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings
import django

# Initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ruhah.settings')
django.setup()

AWS_ACCESS_KEY = settings.AWS_ACCESS_KEY_ID
AWS_SECRET_KEY = settings.AWS_SECRET_ACCESS_KEY
BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME
LOCAL_DIRECTORY = os.path.join(settings.BASE_DIR, 'media', 'items-temp')
S3_FOLDER = 'items/'

def upload_files(directory, bucket, s3_folder):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.png'):
                local_path = os.path.join(root, file)
                s3_path = os.path.join(s3_folder, file)

                try:
                    s3.upload_file(local_path, bucket, s3_path)
                    print(f"Upload Successful: {s3_path}")
                except FileNotFoundError:
                    print(f"The file was not found: {local_path}")
                except NoCredentialsError:
                    print("Credentials not available")

if __name__ == "__main__":
    upload_files(LOCAL_DIRECTORY, BUCKET_NAME, S3_FOLDER)
