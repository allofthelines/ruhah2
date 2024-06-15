# forms.py
from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['top_size_xyz',
                  'bottom_size_xyz',
                  'size_waist_inches',
                  'shoe_size_eu',
                  'height',
                  'weight',
                  'birth_year']
