import boto3
from django.core.management.base import BaseCommand
from chatai.models import Product  # Adjust if your model path differs

class Command(BaseCommand):
    help = 'Update Product model JSONFields with URLs from S3 products/ prefix'

    def handle(self, *args, **options):
        bucket_name = 'ruhahbucket'
        s3_prefix = 'products/'
        region = 'eu-north-1'
        base_s3_url = f'https://{bucket_name}.s3.{region}.amazonaws.com/'

        # Step 1: Fetch list of S3 objects in products/ and build number-to-URL map
        s3_client = boto3.client('s3')
        uploaded_numbers_to_urls = {}  # e.g., {'1684235190159': 'https://.../products/1684235190159.jpg'}

        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_prefix)
            if 'Contents' not in response:
                self.stdout.write(self.style.ERROR('No objects found in S3 products/ prefix.'))
                return

            for obj in response['Contents']:
                key = obj['Key']
                if key.endswith(('.jpg', '.jpeg', '.png')):  # Filter for images
                    filename = key.split('/')[-1]  # e.g., '1684235190159.jpg'
                    number = os.path.splitext(filename)[0]  # e.g., '1684235190159'
                    s3_url = base_s3_url + key
                    uploaded_numbers_to_urls[number] = s3_url
                    self.stdout.write(f'Found S3 image: {number} -> {s3_url}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to list S3 objects: {str(e)}'))
            return

        if not uploaded_numbers_to_urls:
            self.stdout.write(self.style.ERROR('No matching images found in S3. Skipping updates.'))
            return

        self.stdout.write(f'Found {len(uploaded_numbers_to_urls)} S3 images. Proceed with model updates? (y/n)')
        if input().lower() != 'y':
            return

        # Step 2: Update Product models
        products = Product.objects.all()
        updated_count = 0

        for product in products:
            if not product.product_images:
                continue  # Skip if empty

            try:
                images_list = product.product_images  # Assume list of dicts
                if not isinstance(images_list, list):
                    raise ValueError('product_images is not a list')

                modified = False
                for img_dict in images_list:
                    if not isinstance(img_dict, dict) or len(img_dict) != 1:
                        continue  # Skip invalid dicts

                    original_url = next(iter(img_dict))  # The URL key
                    description = img_dict[original_url]  # The value

                    # Check for any uploaded number as substring in the URL
                    for number, s3_url in uploaded_numbers_to_urls.items():
                        if number in original_url:  # Substring match, per your example
                            # Replace the key with S3 URL, keep description
                            del img_dict[original_url]
                            img_dict[s3_url] = description
                            modified = True
                            self.stdout.write(self.style.SUCCESS(f'Replaced URL in product {product.id}: {original_url} -> {s3_url}'))
                            break  # Assume one match per URL; remove if you want to check all

                if modified:
                    product.save()
                    updated_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating product {product.id}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'Updated {updated_count} products successfully.'))