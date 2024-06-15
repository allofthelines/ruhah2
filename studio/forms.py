from django import forms
from .models import EcommerceStore
from django.forms import JSONField

class EcommerceStoreForm(forms.ModelForm):
    size_mapping = JSONField(widget=forms.Textarea)

    class Meta:
        model = EcommerceStore
        fields = '__all__'
