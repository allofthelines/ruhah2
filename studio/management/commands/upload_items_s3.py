import os
import boto3
from botocore.exceptions import NoCredentialsError
from django.core.management.base import BaseCommand
from django.conf import settings
import django

"""
vale eikones photoshoparismenes ston LOCAL fakelo /media/items-temp
me onomata 1.png 2.png 3.png etc
apla anevazei aftes tis fwtografies sto s3 me afta ta onomata
"""

# Initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ruhah.settings')
django.setup()

AWS_ACCESS_KEY = settings.AWS_ACCESS_KEY_ID
AWS_SECRET_KEY = settings.AWS_SECRET_ACCESS_KEY
BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME
LOCAL_DIRECTORY = os.path.join(settings.BASE_DIR, 'media', 'items-temp')
S3_FOLDER = 'items/'

class Command(BaseCommand):
    help = 'Upload all .png files from local directory to AWS S3'

    def upload_files(self, directory, bucket, s3_folder):
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

    def handle(self, *args, **kwargs):
        self.upload_files(LOCAL_DIRECTORY, BUCKET_NAME, S3_FOLDER)












import os
import json
import csv
import random
from django.core.management.base import BaseCommand
from django.conf import settings
import django

# Initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ruhah.settings')
django.setup()

LOCAL_DIRECTORY = os.path.join(settings.BASE_DIR, 'media', 'items-temp')
CSV_FILE_NAME = 'itemids.csv'
LOCAL_CSV_FILE = 'local_itemids.csv'
JSON_FILE_PATH = os.path.join(settings.BASE_DIR, 'studio', 'static', 'studio', 'new_items.json')

class Command(BaseCommand):
    help = 'Rename images to unique 8-digit numbers and update the JSON file'

    def download_csv(self):
        # In this implementation, the CSV is assumed to be local and already present as LOCAL_CSV_FILE.
        pass

    def rename_files(self, directory, existing_ids):
        new_names = {}

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.png'):
                    new_name = self.generate_unique_id(existing_ids)
                    old_path = os.path.join(root, file)
                    new_path = os.path.join(root, f"{new_name}.png")
                    os.rename(old_path, new_path)
                    existing_ids.add(new_name)  # Add new name to existing_ids
                    new_names[file] = f"{new_name}.png"
                    print(f"Renamed {old_path} to {new_path}")

        return new_names

    def generate_unique_id(self, existing_ids):
        while True:
            new_id = random.randint(10000000, 99999999)
            if new_id not in existing_ids:
                return new_id

    def update_json_file(self, json_file_path, new_names):
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        for item in data:
            temp_upload_id = item.get('temp_upload_id')
            if temp_upload_id and f"{temp_upload_id}.png" in new_names:
                new_image_name = new_names[f"{temp_upload_id}.png"]
                item['temp_upload_id'] = new_image_name.split('.')[0]
                item['image'] = f'items/{new_image_name}'

        with open(json_file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def append_item_id_to_csv(self, item_id):
        with open(LOCAL_CSV_FILE, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow([item_id])

    def handle(self, *args, **kwargs):
        # Download the current CSV file (if needed)
        self.download_csv()

        # Read existing item IDs from CSV file
        existing_ids = set()
        if os.path.exists(LOCAL_CSV_FILE):
            with open(LOCAL_CSV_FILE, 'r') as csvfile:
                csv_reader = csv.reader(csvfile)
                for row in csv_reader:
                    if row:
                        existing_ids.add(int(row[0]))

        # Rename files and get new names mapping
        new_names = self.rename_files(LOCAL_DIRECTORY, existing_ids)

        # Update JSON file with new names
        self.update_json_file(JSON_FILE_PATH, new_names)

        # Append new item IDs to the CSV
        for new_name in new_names.values():
            self.append_item_id_to_csv(new_name.split('.')[0])

        self.stdout.write(self.style.SUCCESS('Finished renaming images and updating JSON file.'))
