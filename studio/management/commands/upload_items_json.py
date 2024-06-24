import json
import os
import boto3
import csv
from botocore.exceptions import NoCredentialsError
from django.core.management.base import BaseCommand
from studio.models import Item, SizeCategory, SizeShoeUkCategory, SizeShoeEuCategory, SizeWaistInchCategory, EcommerceStore
from django.conf import settings

class Command(BaseCommand):
    help = 'Upload items from JSON file to the Item model'

    AWS_ACCESS_KEY = 'AKIA3FLD37VQC5XLDFVV'
    AWS_SECRET_KEY = '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'
    BUCKET_NAME = 'ruhahbucket'
    FILE_NAME = 'itemids.csv'
    LOCAL_FILE_NAME = 'local_itemids.csv'

    def download_csv_from_s3(self):
        s3 = boto3.client('s3', aws_access_key_id=self.AWS_ACCESS_KEY, aws_secret_access_key=self.AWS_SECRET_KEY)
        try:
            s3.download_file(self.BUCKET_NAME, self.FILE_NAME, self.LOCAL_FILE_NAME)
            print("Download Successful")
        except FileNotFoundError:
            print("The file was not found")
        except NoCredentialsError:
            print("Credentials not available")

    def upload_csv_to_s3(self):
        s3 = boto3.client('s3', aws_access_key_id=self.AWS_ACCESS_KEY, aws_secret_access_key=self.AWS_SECRET_KEY)
        try:
            s3.upload_file(self.LOCAL_FILE_NAME, self.BUCKET_NAME, self.FILE_NAME)
            print("Upload Successful")
        except FileNotFoundError:
            print("The file was not found")
        except NoCredentialsError:
            print("Credentials not available")

    def append_item_id_to_csv(self, item_id):
        with open(self.LOCAL_FILE_NAME, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow([item_id])

    def handle(self, *args, **kwargs):
        print(f"Database settings: {settings.DATABASES['default']}")

        json_file_path = os.path.join(settings.BASE_DIR, 'studio', 'static', 'studio', 'new_items.json')

        # Download the current CSV file from S3
        self.download_csv_from_s3()

        with open(json_file_path, 'r') as file:
            data = json.load(file)
            for item_data in data:
                item = Item(
                    name=item_data.get('name'),
                    price=item_data.get('price'),
                    location=item_data.get('location'),
                    ecommerce_product_id=item_data.get('ecommerce_product_id'),
                    cat=item_data.get('cat'),
                    formtype=item_data.get('formtype'),
                    condition=item_data.get('condition'),
                    tags=item_data.get('tags'),
                    image=item_data.get('image'),
                    itemid=item_data.get('itemid'),
                )
                print(item)

                # Set foreign key for EcommerceStore if exists
                if item_data.get('ecommerce_store'):
                    try:
                        ecommerce_store = EcommerceStore.objects.get(name=item_data.get('ecommerce_store'))
                        item.ecommerce_store = ecommerce_store
                    except EcommerceStore.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"EcommerceStore '{item_data.get('ecommerce_store')}' does not exist."))

                # Save the item to get an ID for ManyToMany relations
                item.save()

                # Set ManyToMany fields
                if 'sizes_xyz' in item_data:
                    for size_name in item_data['sizes_xyz']:
                        size_category, created = SizeCategory.objects.get_or_create(name=size_name)
                        item.sizes_xyz.add(size_category)

                if 'sizes_shoe_uk' in item_data:
                    for size_name in item_data['sizes_shoe_uk']:
                        size_shoe_uk_category, created = SizeShoeUkCategory.objects.get_or_create(size=size_name)
                        item.sizes_shoe_uk.add(size_shoe_uk_category)

                if 'sizes_shoe_eu' in item_data:
                    for size_name in item_data['sizes_shoe_eu']:
                        size_shoe_eu_category, created = SizeShoeEuCategory.objects.get_or_create(size=size_name)
                        item.sizes_shoe_eu.add(size_shoe_eu_category)

                if 'sizes_waist_inches' in item_data:
                    for size_name in item_data['sizes_waist_inches']:
                        size_waist_inch_category, created = SizeWaistInchCategory.objects.get_or_create(size=size_name)
                        item.sizes_waist_inches.add(size_waist_inch_category)

                item.save()
                self.stdout.write(self.style.SUCCESS(f"Successfully added item '{item.name}' with ID {item.id}."))

                # Append the item ID to the local CSV file
                self.append_item_id_to_csv(item.itemid)

        # Upload the updated CSV file back to S3
        self.upload_csv_to_s3()

        self.stdout.write(self.style.SUCCESS('Finished uploading new items from JSON file.'))
