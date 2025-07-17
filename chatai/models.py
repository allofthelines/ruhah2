from django.db import models

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    product_link = models.URLField()
    product_images = models.JSONField()  # Stores list of dicts like [{'url': 'https://...', 'desc': 'Image 0'}]
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_details = models.TextField()
    product_created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name