import os
import boto3
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Upload images from local folder to S3 bucket under products/ prefix'

    def handle(self, *args, **options):
        local_folder = '/Users/aris/Documents/1-RUHAH/1-website/ruhah-heroku/ruhah2/zara-pics'
        bucket_name = 'ruhahbucket'
        s3_prefix = 'products/'
        region = 'eu-north-1'
        base_s3_url = f'https://{bucket_name}.s3.{region}.amazonaws.com/'

        # Get list of local files (filter for images)
        files_to_upload = [f for f in os.listdir(local_folder) if os.path.isfile(os.path.join(local_folder, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        if not files_to_upload:
            self.stdout.write(self.style.ERROR('No images found in local folder.'))
            return

        self.stdout.write(f'Found {len(files_to_upload)} images to upload. Proceed? (y/n)')
        if input().lower() != 'y':
            return

        s3_client = boto3.client('s3')
        uploaded_count = 0

        for filename in files_to_upload:
            local_path = os.path.join(local_folder, filename)
            s3_key = s3_prefix + filename

            try:
                s3_client.upload_file(
                    local_path,
                    bucket_name,
                    s3_key,
                    ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'}  # Adjust ContentType if needed
                )
                s3_url = base_s3_url + s3_key
                self.stdout.write(self.style.SUCCESS(f'Uploaded: {filename} to {s3_url}'))
                uploaded_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to upload {filename}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully uploaded {uploaded_count} images.'))