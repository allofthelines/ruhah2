from django import forms
from .models import ShopifyStore
from django.forms import JSONField

class ShopifyStoreForm(forms.ModelForm):
    size_mapping = JSONField(widget=forms.Textarea)

    class Meta:
        model = ShopifyStore
        fields = '__all__'
