import os
from PIL import Image
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Crop PNG images in the media/items-temp directory and adjust their alpha values'

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

    def crop_image(self, img):
        # Find bounding box of non-transparent region
        bbox = img.getbbox()

        # Crop the image to the bounding box
        cropped_img = img.crop(bbox)

        return cropped_img

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

            # Crop the image
            cropped_img = self.crop_image(img)

            # Save the cropped image with the new name
            cropped_path = os.path.splitext(file_path)[0] + ".png"
            cropped_img.save(cropped_path)

            print(f"Processed {file_name}")

        self.stdout.write(self.style.SUCCESS('Finished processing and cropping PNG images.'))
