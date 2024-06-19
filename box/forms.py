from django import forms
from .models import Ticket
from studio.models import Style

class TicketForm(forms.Form):
    # Multiple choice fields

    STYLE_CHOICES = [
        ('casual', 'casual'),
        ('boho', 'boho'),
        ('gorpcore', 'gorpcore'),
        ('indie', 'indie'),
        ('loungewear', 'loungewear'),
        ('preppy', 'preppy'),
        ('streetwear', 'streetwear'),
        ('y2k', 'y2k'),
    ]

    OCCASION_CHOICES = [
        ('everyday', 'everyday'),
        ('special', 'special'),
    ]

    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
    ]

    TYPE_CHOICES = [
        ('styled_outfits', 'styled_outfits'),
        ('liked_outfits', 'styled_outfits'),
    ]

    SHOE_SIZE_EU_CHOICES = [(str(size), str(size)) for size in range(34, 49)] + \
                           [(str(size + 0.5), str(size + 0.5)) for size in range(34, 48)]
    SIZE_WAIST_INCHES_CHOICES = [(str(size), str(size)) for size in range(23, 37)]
    SHOE_SIZE_UK_CHOICES = [(str(size), str(size)) for size in range(2, 14)] + \
                           [(str(size + 0.5), str(size + 0.5)) for size in range(2, 13)]

    # style1 = forms.ChoiceField(choices=STYLE_CHOICES, label='Base')
    style1 = forms.ModelChoiceField(queryset=Style.objects.all(), label='Style 1')
    style2 = forms.ModelChoiceField(queryset=Style.objects.all(), label='Style 2')
    type = forms.ModelChoiceField(queryset=Style.objects.all(), label='Type')
    occasion = forms.ChoiceField(choices=OCCASION_CHOICES, label='Occasion')
    condition = forms.ChoiceField(choices=[('whatever', 'whatever'), ('new', 'new'), ('pre-owned', 'pre-owned')], label='Condition')
    price = forms.ChoiceField(choices=[('whatever', 'whatever'), ('under 40', 'under 40'), ('under 80', 'under 80')], label='Price')
    notes = forms.CharField(max_length=200, label='Note to Stylist', widget=forms.Textarea(attrs={
        'rows': 4,
        'cols': 20,
        'placeholder': '"play with layering"\n"pastel palette"\n"emphasize my shoulders"\n"for a trip to greece"'}), required=False)

    size_top_xyz = forms.ChoiceField(choices=SIZE_CHOICES, label='Top Size')
    size_bottom_xyz = forms.ChoiceField(choices=SIZE_CHOICES, label='Bottom Size')
    size_waist_inches = forms.ChoiceField(choices=SIZE_WAIST_INCHES_CHOICES, label='Waist (inches)')
    size_shoe_eu = forms.ChoiceField(choices=SHOE_SIZE_EU_CHOICES, label='Shoe Size (EU)')
    size_shoe_uk = forms.ChoiceField(choices=SHOE_SIZE_UK_CHOICES, label='Shoe Size (UK)')