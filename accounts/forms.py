from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser, Customer, PortraitUpload, InviteCode, GridPicUpload
from django.contrib.auth.models import User
import re





class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')



class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    # invite_code = forms.CharField(max_length=20, required=settings.INVITE_CODE_REQUIRED, help_text='Enter your invite code')
    # to evala pio katw sto __init__ wste otan einai false na mhn fainetai kan san pedio.

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

        widgets = {
            'username': forms.TextInput(attrs={'maxlength': 30}),
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }
        help_texts = {
            'username': None,
            'password1': None,
            'password2': None,
            'email': None,
        }
        labels = {
            'email': 'Email',  # This will ensure the label doesn't say "Required"
        }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        if settings.INVITE_CODE_REQUIRED:
            self.fields['invite_code'] = forms.CharField(max_length=20, required=True, help_text='')

        # Customize username field
        self.fields['username'].validators[0].limit_value = 30
        self.fields['username'].help_text = None
        self.fields['username'].error_messages = {
            'invalid': 'Username can only contain letters digits _ . -',
        }

        # Remove 'Enter the same password as before, for verification.' text
        self.fields['password2'].label = 'Password confirmation'
        self.fields['password2'].help_text = None

        # Remove "required" label from email field
        self.fields['email'].label = 'Email'
        self.fields['email'].help_text = None

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) > 30:
            raise forms.ValidationError('Username must be 30 characters or fewer.')
        if not re.match(r'^[\w.-]+$', username):
            raise forms.ValidationError('Username can only contain letters, digits, _ . -')
        return username

    def clean_invite_code(self):
        if settings.INVITE_CODE_REQUIRED:
            code = self.cleaned_data.get('invite_code')
            if not code:
                raise forms.ValidationError('Invite code is required.')
            if not InviteCode.objects.filter(invite_code=code, is_used=False).exists():
                raise forms.ValidationError('Invalid or already used invite code.')
            return code
        return None







class UserProfileForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'name', 'bio', 'pfp']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email
            self.fields['username'].initial = user.username
            self.fields['name'].initial = user.name
            self.fields['bio'].initial = user.bio
            self.fields['pfp'].initial = user.pfp

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Username already exists.')
        return username

    def save(self, commit=True, user=None):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        user.name = self.cleaned_data['name']
        user.bio = self.cleaned_data['bio']
        if 'pfp' in self.cleaned_data:
            user.pfp = self.cleaned_data['pfp']

        if commit:
            user.save()
        return user




class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'top_size_xyz', 'bottom_size_xyz', 'size_waist_inches',
            'shoe_size_eu', 'shoe_size_uk', 'height', 'weight'
        ]

    def __init__(self, *args, **kwargs):
        customer = kwargs.pop('customer', None)
        super().__init__(*args, **kwargs)
        if customer:
            self.fields['top_size_xyz'].initial = customer.top_size_xyz
            self.fields['bottom_size_xyz'].initial = customer.bottom_size_xyz
            self.fields['size_waist_inches'].initial = customer.size_waist_inches
            self.fields['shoe_size_eu'].initial = customer.shoe_size_eu
            self.fields['shoe_size_uk'].initial = customer.shoe_size_uk
            self.fields['height'].initial = customer.height
            self.fields['weight'].initial = customer.weight

    def save(self, commit=True, customer=None):
        customer = super().save(commit=False)
        customer.top_size_xyz = self.cleaned_data['top_size_xyz']
        customer.bottom_size_xyz = self.cleaned_data['bottom_size_xyz']
        customer.size_waist_inches = self.cleaned_data['size_waist_inches']
        customer.shoe_size_eu = self.cleaned_data['shoe_size_eu']
        customer.shoe_size_uk = self.cleaned_data['shoe_size_uk']
        customer.height = self.cleaned_data['height']
        customer.weight = self.cleaned_data['weight']
        if commit:
            customer.save()
        return customer





class PortraitUploadForm(forms.ModelForm):
    ticket_id_int = forms.IntegerField()

    class Meta:
        model = PortraitUpload
        fields = ['portrait_img', 'ticket_id_int']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.wearer_id = self.user  # Automatically assign the wearer_id
        instance.status = 'pending'  # Automatically assign status to 'pending'
        if commit:
            instance.save()
        return instance


class GridPicUploadForm(forms.ModelForm):
    class Meta:
        model = GridPicUpload
        fields = ['gridpic_img']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.uploader_id = self.user
        if commit:
            instance.save()
        return instance


class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_visibility', 'trending_mode', 'trending_styles', 'studio_styles', 'studio_visibility']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['profile_visibility'].initial = user.profile_visibility
            self.fields['trending_mode'].initial = user.trending_mode
            self.fields['studio_visibility'].initial = user.studio_visibility
            self.fields['trending_styles'].initial = user.trending_styles.all()
            self.fields['studio_styles'].initial = user.studio_styles.all()

    def save(self, commit=True, user=None):
        user = super().save(commit=False)
        user.profile_visibility = self.cleaned_data['profile_visibility']
        user.trending_mode = self.cleaned_data['trending_mode']
        user.studio_visibility = self.cleaned_data['studio_visibility']
        user.trending_styles.set(self.cleaned_data['trending_styles'])
        user.studio_styles.set(self.cleaned_data['studio_styles'])
        user.save()
        return user



class EmailChangeForm(forms.ModelForm):
    new_email = forms.EmailField(label='New Email', required=True)

    class Meta:
        model = CustomUser
        fields = ['new_email']