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

    STYLIST_CHOICES = [
        ('everyone', 'Everyone'),
        ('following', 'Following')
    ]

    try:
        casual_style = Style.objects.get(style_name='casual')
    except Style.DoesNotExist:
        casual_style = None

    style1 = forms.ModelChoiceField(queryset=Style.objects.all(), label='Style', initial=casual_style)
    stylist_type = forms.ChoiceField(choices=STYLIST_CHOICES, label='Stylist', initial='everyone')
    catalogue = forms.ChoiceField(choices=CATALOGUE_CHOICES, label='Catalogue', required=False)
    notes = forms.CharField(max_length=200, label='Note to Stylist', widget=forms.Textarea(attrs={
        'rows': 4,
        'cols': 30
        # 'style': 'background-color: #F5F5F5;'
        # 'placeholder': '"experiment with patterns"\n"use pastel palette"\n"make it comfy"\n"do not include footwear"'
    }), required=True)

class PrivateAskFitForm(forms.Form):

    try:
        casual_style = Style.objects.get(style_name='casual')
    except Style.DoesNotExist:
        casual_style = None

    style1 = forms.ModelChoiceField(queryset=Style.objects.all(), label='Style', initial=casual_style)
    stylist_type = forms.CharField(
        label='Stylist',
        initial='Private',
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})  # Read-only to indicate it's private
    )
    stylist_username = forms.CharField(label='Stylist', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    private_ask_price_display = forms.CharField(label='Price (Credits)', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    notes = forms.CharField(max_length=200, label='Note to Stylist', widget=forms.Textarea(attrs={
        'rows': 4,
        'cols': 30
        # 'style': 'background-color: #FFFFCC;'
    }), required=True)

    def __init__(self, *args, **kwargs):
        # Accept additional keyword arguments for stylist and price
        stylist_username = kwargs.pop('stylist_username', None)
        private_ask_price = kwargs.pop('private_ask_price', None)
        super().__init__(*args, **kwargs)

        # Set initial values for display-only fields
        self.fields['stylist_username'].initial = stylist_username
        self.fields['stylist_type'].initial = 'private'
        if private_ask_price == 0:
            self.fields['private_ask_price_display'].initial = "Free"
        else:
            self.fields['private_ask_price_display'].initial = f"{private_ask_price} Credits"


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

    STYLIST_CHOICES = [
        ('everyone', 'Everyone'),
        ('following', 'Following')
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
    stylist_type = forms.ChoiceField(choices=STYLIST_CHOICES, label='Stylist', initial='everyone')
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