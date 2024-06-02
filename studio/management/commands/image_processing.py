import os
import random
import numpy as np
from PIL import Image
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def pad_to_square(image):
    width, height = image.size
    max_dim = max(width, height)
    new_image = Image.new('RGBA', (max_dim, max_dim), (255, 255, 255, 0))
    new_image.paste(image, ((max_dim - width) // 2, ((max_dim - height) // 2)))
    return new_image

def expand_image(image, expansion_percent):
    width, height = image.size
    expansion_width = int(width * expansion_percent / 100)
    expansion_height = int(height * expansion_percent / 100)
    expanded_image = image.resize((width + expansion_width, height + expansion_height), Image.ANTIALIAS)
    return expanded_image

def create_canvas(total_area):
    side_length = int(np.sqrt(total_area) * 1.3)
    print(f"Canvas side length: {side_length}")  # Debugging line
    canvas = Image.new('RGBA', (side_length, side_length), (0, 0, 0, 0))  # Transparent canvas
    return canvas

def calculate_overlap_area(box1, box2):
    left = max(box1[0], box2[0])
    upper = max(box1[1], box2[1])
    right = min(box1[2], box2[2])
    lower = min(box1[3], box2[3])
    if left < right and upper < lower:
        return (right - left) * (lower - upper)
    return 0

def calculate_non_empty_area(image):
    alpha = image.split()[-1]
    non_empty_pixels = np.array(alpha).astype(bool).sum()
    return non_empty_pixels

def resize_image_to_non_empty_area(image, target_non_empty_area):
    non_empty_area = calculate_non_empty_area(image)
    if non_empty_area == 0:
        return image
    scale_factor = np.sqrt(target_non_empty_area / non_empty_area)
    new_width = int(image.width * scale_factor)
    new_height = int(image.height * scale_factor)
    resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)
    return resized_image

def pack_images(images, canvas):
    canvas_width, canvas_height = canvas.size
    positions = []
    top_images = [img for img in images if img['category'] == 'top']
    bottom_images = [img for img in images if img['category'] == 'bottom']
    footwear_images = [img for img in images if img['category'] == 'footwear']
    other_images = [img for img in images if img['category'] not in ['top', 'bottom', 'footwear']]

    # Resize top and bottom images to have the same height equal to half the height of the canvas
    if top_images:
        top_image = top_images[0]['image']
        target_height = canvas_height // 2
        scale_factor = target_height / top_image.height
        new_width = int(top_image.width * scale_factor)
        new_height = int(top_image.height * scale_factor)
        top_image = top_image.resize((new_width, new_height), Image.ANTIALIAS)

        # Center the image and apply a random shift
        x_center = (canvas_width - top_image.width) // 2
        x_shift = random.randint(-int(canvas_width * 0.1), int(canvas_width * 0.1))
        x = x_center + x_shift

        # Allow placement in the top 60% of the canvas height
        y = random.randint(0, int(canvas_height * 0.6) - new_height)

        canvas.paste(top_image, (x, y), top_image)
        positions.append((x, y, top_image.width, top_image.height))

    if bottom_images:
        bottom_image = bottom_images[0]['image']
        target_height = canvas_height // 2
        scale_factor = target_height / bottom_image.height
        new_width = int(bottom_image.width * scale_factor)
        new_height = int(bottom_image.height * scale_factor)
        bottom_image = bottom_image.resize((new_width, new_height), Image.ANTIALIAS)

        # Center the image and apply a random shift
        x_center = (canvas_width - bottom_image.width) // 2
        x_shift = random.randint(-int(canvas_width * 0.1), int(canvas_width * 0.1))
        x = x_center + x_shift

        # Allow placement in the bottom 60% of the canvas height
        y = random.randint(int(canvas_height * 0.4), canvas_height - new_height)

        canvas.paste(bottom_image, (x, y), bottom_image)
        positions.append((x, y, bottom_image.width, bottom_image.height))

    for img_data in footwear_images + other_images:
        image = img_data['image']
        category = img_data['category']
        max_dim = int(0.4 * canvas_height)
        scale_factor = min(max_dim / image.width, max_dim / image.height)
        new_width = int(image.width * scale_factor)
        new_height = int(image.height * scale_factor)
        image = image.resize((new_width, new_height), Image.ANTIALIAS)
        placed = False
        attempts = 0

        while not placed and attempts < 100:
            if category == 'footwear':
                x = random.randint(0, canvas_width - new_width)
                y = random.randint(canvas_height // 2, canvas_height - new_height)
            else:
                x = random.randint(0, canvas_width - new_width)
                y = random.randint(0, canvas_height // 2 - new_height)

            overlap_area = 0

            for pos in positions:
                bbox1 = (x, y, x + new_width, y + new_height)
                bbox2 = (pos[0], pos[1], pos[0] + pos[2], pos[1] + pos[3])
                overlap_area += calculate_overlap_area(bbox1, bbox2)

            total_occupied_area = sum([pos[2] * pos[3] for pos in positions])
            overlap_percentage = overlap_area / total_occupied_area if total_occupied_area > 0 else 0

            if overlap_percentage <= 0.15:
                canvas.paste(image, (x, y), image)
                positions.append((x, y, new_width, new_height))
                placed = True

            attempts += 1

        if not placed:
            print("Too many attempts to place image without excessive overlap.")
            break

    return canvas

def create_composite_image(outfit):
    items = outfit.items.all()
    images = []

    for item in items:
        img_path = item.image.name
        print(f"Loading image from: {img_path}")  # Debugging line
        if default_storage.exists(img_path):
            with default_storage.open(img_path) as img_file:
                image = Image.open(img_file).convert('RGBA')
                padded_image = pad_to_square(image)
                expanded_image = expand_image(padded_image, 10)
                images.append({'image': expanded_image, 'category': item.cat})
        else:
            print(f"Image not found: {img_path}")  # Debugging line

    if not images:
        print("No images to process.")  # Debugging line
        return None

    # Calculate the total non-empty area of all images
    total_non_empty_area = sum([calculate_non_empty_area(img['image']) for img in images])
    print(f"Total non-empty area of images: {total_non_empty_area}")  # Debugging line

    # Calculate the target non-empty area for each image
    target_non_empty_area = total_non_empty_area / len(images)
    print(f"Target non-empty area per image: {target_non_empty_area}")  # Debugging line

    # Resize each image to have the same non-empty area
    resized_images = [
        {'image': resize_image_to_non_empty_area(img['image'], target_non_empty_area), 'category': img['category']} for
        img in images]

    total_area = sum([img['image'].size[0] * img['image'].size[1] for img in resized_images])
    canvas = create_canvas(total_area)

    composite_image = pack_images(resized_images, canvas)

    # Create a white background image
    white_background = Image.new("RGB", composite_image.size, (255, 255, 255))
    # Paste the composite image on the white background
    white_background.paste(composite_image, (0, 0), composite_image)

    output_path = os.path.join('outfits', f'outfit_{outfit.id}.jpeg')
    output_content = ContentFile(white_background.tobytes(), name=output_path)
    default_storage.save(output_path, output_content)

    return output_path
