from django.db import models
from pgvector.django import VectorField
from accounts.models import CustomUser
from studio.models import Item




class Product(models.Model):
    product_name = models.CharField(max_length=255)
    product_brand = models.CharField(max_length=100, default='unknown')
    product_link = models.URLField()
    product_images = models.JSONField()  # Stores list of dicts like [{'url': 'https://...', 'desc': 'Image 0'}]
    product_main_image = models.URLField(null=True, blank=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_details = models.TextField()
    product_created_at = models.DateTimeField(auto_now_add=True)

    product_embedding = VectorField(dimensions=768, blank=True, null=True)

    def __str__(self):
        return self.product_name



import secrets

def generate_chat_id():
    return secrets.token_urlsafe(10)

class ChatSession(models.Model):
    chat_id = models.CharField(max_length=32, unique=True, null=True, blank=True)  # temporarily allow null
    chat_user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL)  # Updated to CustomUser; optional for guests
    chat_reference_item = models.ForeignKey(Item, null=True, blank=True, on_delete=models.SET_NULL)  # For mode 1; uses studio Item
    chat_reference_outfit_id = models.IntegerField(null=True, blank=True)  # Metadata for "Go Back" (outfit ID)
    chat_main_embedding = VectorField(dimensions=768, blank=True, null=True)  # Single reference embedding for similarity (initially from item; updatable in future)
    chat_created_at = models.DateTimeField(auto_now_add=True)
    chat_status = models.CharField(max_length=20, default='active')  # Future: 'active', 'closed' for limits

    def __str__(self):
        return f"Session {self.id} for user {self.user or 'Guest'}"





class ChatMessage(models.Model):
    msg_chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    msg_is_from_user = models.BooleanField(default=True)  # True: user, False: Ruhah
    msg_text = models.TextField(blank=True)  # For text messages
    msg_image = models.ImageField(upload_to='chat_uploads/', null=True, blank=True)  # For uploaded images (temp local storage; easy to switch to S3)
    msg_image_url = models.URLField(null=True, blank=True)  # Alternative for item image URLs
    msg_recommendations = models.JSONField(null=True, blank=True)  # List of {'product_id': int, 'main_image': url, 'price': decimal} for display
    msg_created_at = models.DateTimeField(auto_now_add=True)
    msg_message_type = models.CharField(max_length=20, default='text')  # Future: 'text', 'image', 'recommendation', 'item'

    """ VALTO STO MELLON
    class Meta:
        ordering = ['created_at']
    """

    def __str__(self):
        return f"Message {self.id} in session {self.session.id}"