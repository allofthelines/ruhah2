# utils.py (updated to fix JSON serialization)

from pgvector.django import CosineDistance
from django.db.models import F
from chatai.models import Product


def get_similar_products(main_embedding, category=None, limit=6):
    """
    Find similar products based on cosine distance of main_embedding.
    Optionally filter by product_category (must match exactly, e.g., 'top').
    Future: Add params for filters (e.g., color, size) or sorting (e.g., by price).
    """
    if main_embedding is None:
        return []

    # Use pgvector to order by similarity (lower distance = more similar)
    similar = Product.objects.annotate(
        distance=CosineDistance('product_embedding', main_embedding)
    ).filter(distance__lt=0.5)  # Threshold for "similar"; adjustable

    # Apply category filter if provided
    if category:
        similar = similar.filter(product_category=category)

    similar = similar.order_by('distance')[:limit]

    # Return list of dicts for easy rendering (expandable for future details)
    return [
        {
            'id': p.id,
            'main_image': get_first_image_url(p),  # Use first image from product_images
            'price': float(p.product_price),  # Convert Decimal to float for JSON serialization
            'name': p.product_name,  # Future: Use for pop-ups
            'link': p.product_link  # Future: For details
        } for p in similar
    ]

def get_first_image_url(product):
    """
    Helper to extract the first image URL from product_images JSONField.
    Returns the key (URL) of the first dict if available, else None.
    """
    images = product.product_images
    if isinstance(images, list) and len(images) > 0:
        first_image = images[0]
        if isinstance(first_image, dict) and len(first_image) > 0:
            # Get the first key (which is the URL)
            return next(iter(first_image))
    return None  # Or fallback to product_main_image if desired: product.product_main_image