import os
from PIL import Image, ImageOps
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Make PNG images square, extend them by 10% with transparent border, ' \
           'and adjust their alpha values in the media/items-temp directory'

    def adjust_alpha(self, img):
        # Convert the image to RGBA mode (if not already in RGBA)
        img = img.convert("RGBA")

        # Get the alpha channel
        alpha = img.split()[3]

        # Get the size of the image
        width, height = img.size

        # Create a new image to store the adjusted alpha values
        new_img = Image.new("RGBA", img.size)

        # Iterate over each pixel in the image
        for y in range(height):
            for x in range(width):
                # Get the current alpha value
                current_alpha = alpha.getpixel((x, y))

                # Adjust alpha value (if below 100, set it to 0)
                new_alpha = 0 if current_alpha < 100 else current_alpha

                # Set the pixel's alpha value
                r, g, b, _ = img.getpixel((x, y))
                new_img.putpixel((x, y), (r, g, b, new_alpha))

        return new_img

    def make_square_and_extend(self, img):
        # Determine the dimensions to achieve a square image
        max_side = max(img.size)

        # Convert image to RGBA to ensure it's using alpha channel
        img = img.convert("RGBA")

        # Make the image square by adding transparent pixels to smaller side
        img_square = ImageOps.pad(img, (max_side, max_side), color=(0, 0, 0, 0))

        # Calculate the border to add based on 10% of the new dimension
        border = int(max_side * 0.1)

        # Add calculated border around the square image
        img_extended = ImageOps.expand(img_square, border=border, fill=(0, 0, 0, 0))

        return img_extended

    def handle(self, *args, **kwargs):
        # Specify the directory containing the images
        directory_path = os.path.join(settings.BASE_DIR, 'media', 'items-temp')

        # Get a list of all PNG files in the directory
        file_list = [f for f in os.listdir(directory_path) if f.endswith('.png')]

        # Process each image in the directory
        for file_name in file_list:
            file_path = os.path.join(directory_path, file_name)

            # Open the image
            img = Image.open(file_path)

            # Adjust alpha values
            img = self.adjust_alpha(img)

            # Convert the image to square and extend it by 10%
            img_extended = self.make_square_and_extend(img)

            # Save the modified image with the same name
            img_extended.save(file_path)

            print(f"Processed {file_name}")

        self.stdout.write(self.style.SUCCESS('Finished processing and extending PNG images.'))
