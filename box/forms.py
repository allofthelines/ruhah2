from django import forms
from .models import Ticket
from studio.models import Style

class TicketForm(forms.Form):
    # Multiple choice fields

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

    CATALOGUE_CHOICES = [
        ('all_items', 'all items'),
        ('liked_only', 'liked items only'),
    ]

    SHOE_SIZE_EU_CHOICES = [(str(size), str(size)) for size in range(34, 49)] + \
                           [(str(size + 0.5), str(size + 0.5)) for size in range(34, 48)]
    SIZE_WAIST_INCHES_CHOICES = [(str(size), str(size)) for size in range(23, 37)]
    SHOE_SIZE_UK_CHOICES = [(str(size), str(size)) for size in range(2, 14)] + \
                           [(str(size + 0.5), str(size + 0.5)) for size in range(2, 13)]

    try:
        casual_style = Style.objects.get(style_name='casual')
    except Style.DoesNotExist:
        casual_style = None

    # style1 = forms.ChoiceField(choices=STYLE_CHOICES, label='Base')
    style1 = forms.ModelChoiceField(queryset=Style.objects.all(), label='Style', initial=casual_style)
    style2 = forms.ModelChoiceField(queryset=Style.objects.all(), label='Style 2', required=False)
    catalogue = forms.ChoiceField(choices=CATALOGUE_CHOICES, label='Catalogue')
    occasion = forms.ChoiceField(choices=OCCASION_CHOICES, label='Occasion', required=False)
    condition = forms.ChoiceField(choices=[('new_or_like_new', 'new or like new'), ('new', 'new'), ('like_new', 'like new')], label='Condition')
    price = forms.ChoiceField(choices=[('no limit', 'no limit'), ('max $59', 'max $59'), ('max $99', 'max $99')], label='Price')
    notes = forms.CharField(max_length=200, label='Note to Stylist', widget=forms.Textarea(attrs={
        'rows': 4,
        'cols': 40,
        'placeholder': '"for a birthday party"\n"use a neutral palette"\n"make it extra comfy"\n"do not include footwear"'}), required=False)

    size_top_xyz = forms.ChoiceField(choices=SIZE_CHOICES, label='Top Size')
    size_bottom_xyz = forms.ChoiceField(choices=SIZE_CHOICES, label='Bottom Size')
    size_waist_inches = forms.ChoiceField(choices=SIZE_WAIST_INCHES_CHOICES, label='Waist (inches)')
    size_shoe_eu = forms.ChoiceField(choices=SHOE_SIZE_EU_CHOICES, label='Shoe Size (EU)')
    size_shoe_uk = forms.ChoiceField(choices=SHOE_SIZE_UK_CHOICES, label='Shoe Size (UK)')


class AskFitForm(forms.Form):

    CATALOGUE_CHOICES = [
        ('all_items', 'all items'),
        ('liked_only', 'liked items only'),
    ]

    try:
        casual_style = Style.objects.get(style_name='casual')
    except Style.DoesNotExist:
        casual_style = None

    style1 = forms.ModelChoiceField(queryset=Style.objects.all(), label='Style', initial=casual_style)
    catalogue = forms.ChoiceField(choices=CATALOGUE_CHOICES, label='Catalogue', required=False)
    notes = forms.CharField(max_length=200, label='Note to Stylist', widget=forms.Textarea(attrs={
        'rows': 4,
        'cols': 30
        # 'placeholder': '"experiment with patterns"\n"use pastel palette"\n"make it comfy"\n"do not include footwear"'
    }), required=False)


class AskBoxForm(forms.Form):

    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
    ]

    CATALOGUE_CHOICES = [
        ('all_items', 'all items'),
        ('liked_only', 'liked items only'),
    ]

    CURATED_BY_CHOICES = [
        ('human_stylist', 'human stylist'),
        ('personalized_algorithm', 'personalized algorithm')
    ]

    SHOE_SIZE_EU_CHOICES = [(str(size), str(size)) for size in range(34, 49)] + \
                           [(str(size + 0.5), str(size + 0.5)) for size in range(34, 48)]
    SIZE_WAIST_INCHES_CHOICES = [(str(size), str(size)) for size in range(23, 37)]
    SHOE_SIZE_UK_CHOICES = [(str(size), str(size)) for size in range(2, 14)] + \
                           [(str(size + 0.5), str(size + 0.5)) for size in range(2, 13)]

    try:
        casual_style = Style.objects.get(style_name='casual')
    except Style.DoesNotExist:
        casual_style = None

    # style1 = forms.ChoiceField(choices=STYLE_CHOICES, label='Base')
    style1 = forms.ModelChoiceField(queryset=Style.objects.all(), label='Style', initial=casual_style)
    curated_by = forms.ChoiceField(choices=CURATED_BY_CHOICES, label='Curated by', initial='human_stylist', required=False)
    catalogue = forms.ChoiceField(choices=CATALOGUE_CHOICES, label='Catalogue', required=False)
    condition = forms.ChoiceField(choices=[('new_or_like_new', 'new or like new'), ('new', 'new'), ('like_new', 'like new')], label='Condition', required=False)
    price = forms.ChoiceField(choices=[('no limit', 'no limit'), ('max $59', 'max $59'), ('max $99', 'max $99')], label='Price', required=False)
    notes = forms.CharField(max_length=200, label='Note to Stylist', widget=forms.Textarea(attrs={
        'rows': 4,
        'cols': 30
        # 'placeholder': '"experiment with patterns"\n"use pastel palette"\n"make it comfy"\n"do not include footwear"'
    }), required=False)

    size_top_xyz = forms.ChoiceField(choices=SIZE_CHOICES, label='Top Size', required=False)
    size_bottom_xyz = forms.ChoiceField(choices=SIZE_CHOICES, label='Bottom Size', required=False)
    size_waist_inches = forms.ChoiceField(choices=SIZE_WAIST_INCHES_CHOICES, label='Waist (inches)', required=False)
    size_shoe_eu = forms.ChoiceField(choices=SHOE_SIZE_EU_CHOICES, label='Shoe Size (EU)', required=False)
    size_shoe_uk = forms.ChoiceField(choices=SHOE_SIZE_UK_CHOICES, label='Shoe Size (UK)', required=False)
