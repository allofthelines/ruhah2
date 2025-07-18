# utils.py (updated to fix the ValueError)

from pgvector.django import CosineDistance
from django.db.models import F
from chatai.models import Product


def get_similar_products(main_embedding, limit=6):
    """
    Find similar products based on cosine distance of main_embedding.
    Future: Add params for filters (e.g., color, size) or sorting (e.g., by price).
    """
    # Fixed check: Use 'is None' instead of 'not' to avoid truth value ambiguity on arrays
    if main_embedding is None:
        return []

    # Use pgvector to order by similarity (lower distance = more similar)
    similar = Product.objects.annotate(
        distance=CosineDistance('product_embedding', main_embedding)
    ).filter(distance__lt=0.5)  # Threshold for "similar"; adjustable
    similar = similar.order_by('distance')[:limit]

    # Return list of dicts for easy rendering (expandable for future details)
    return [
        {
            'id': p.id,
            'main_image': p.product_main_image,
            'price': p.product_price,
            'name': p.product_name,  # Future: Use for pop-ups
            'link': p.product_link  # Future: For details
        } for p in similar
    ]