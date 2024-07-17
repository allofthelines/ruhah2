import os
import json
import csv
import random
from django.core.management.base import BaseCommand
from django.conf import settings
import django
import boto3
from botocore.exceptions import NoCredentialsError

"""
1.png 2.png klp se /media/item-temps
{1 2 klp} json se /studio/static/studio/new_items.json
aws/itemids.csv

metonomase ta 1 2 se 12345678 23456789, kainourgious kwdikous
"""

# Initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ruhah.settings')
django.setup()

LOCAL_DIRECTORY = os.path.join(settings.BASE_DIR, 'media', 'items-temp')
CSV_FILE_NAME = 'itemids.csv'
LOCAL_CSV_FILE = 'local_itemids.csv'
JSON_FILE_PATH = os.path.join(settings.BASE_DIR, 'studio', 'static', 'studio', 'new_items.json')



class Command(BaseCommand):
    help = 'Rename images to unique 8-digit numbers and update the JSON file'

    AWS_ACCESS_KEY = 'AKIA3FLD37VQC5XLDFVV'
    AWS_SECRET_KEY = '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'
    BUCKET_NAME = 'ruhahbucket'

    def download_csv(self):
        s3 = boto3.client('s3', aws_access_key_id=self.AWS_ACCESS_KEY, aws_secret_access_key=self.AWS_SECRET_KEY)
        try:
            s3.download_file(self.BUCKET_NAME, CSV_FILE_NAME, LOCAL_CSV_FILE)
            print("Download Successful")
        except FileNotFoundError:
            print("The file was not found")
        except NoCredentialsError:
            print("Credentials not available")

    def upload_csv(self):
        s3 = boto3.client('s3', aws_access_key_id=self.AWS_ACCESS_KEY, aws_secret_access_key=self.AWS_SECRET_KEY)
        try:
            s3.upload_file(LOCAL_CSV_FILE, self.BUCKET_NAME, CSV_FILE_NAME)
            print("Upload Successful")
        except FileNotFoundError:
            print("The file was not found")
        except NoCredentialsError:
            print("Credentials not available")

    def rename_files(self, directory, existing_ids):
        new_names = {}

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.png'):
                    temp_upload_id = os.path.splitext(file)[0]  # Get the part before .png
                    new_name = self.generate_unique_id(existing_ids)
                    old_path = os.path.join(root, file)
                    new_path = os.path.join(root, f"{new_name}.png")
                    os.rename(old_path, new_path)
                    existing_ids.add(new_name)  # Add new name to existing_ids
                    new_names[temp_upload_id] = f"{new_name}.png"
                    print(f"Renamed {old_path} to {new_path}")

        return new_names

    def generate_unique_id(self, existing_ids):
        while True:
            new_id = random.randint(10000000, 99999999)
            if new_id not in existing_ids:
                return new_id

    def update_json_file(self, json_file_path, new_names):
        try:
            with open(json_file_path, 'r') as file:
                content = file.read().strip()
                if not content:
                    raise ValueError("The JSON file is empty.")
                data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

        for item in data:
            temp_upload_id = item.get('temp_upload_id')
            if temp_upload_id in new_names:
                new_image_name = new_names[temp_upload_id]
                item['itemid'] = new_image_name.split('.')[0]
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

        # Upload the updated CSV file back to S3
        self.upload_csv()

        self.stdout.write(self.style.SUCCESS('Finished renaming images and updating JSON file.'))
