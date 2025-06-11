from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.timezone import now
from PIL import Image, ExifTags
import os
from django.core.files.storage import default_storage
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils import timezone
# an kanw import apo studio.Style tha exw CYCLIC IMPORT ERROR
# solution grapsto san studio.Style kai kane to apo katw gia to new_user
from django.apps import apps
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    PROFILE_VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('followers', 'Followers'),
    ]
    TRENDING_MODE_CHOICES = [
        ('discover', 'Discover'),
        ('following', 'Following'),
    ]
    LIFEFORM_CHOICES = [
        ('angel', 'angel'),
        ('human', 'human'),
        ('bot', 'bot'),
    ]
    STUDIO_VISIBILITY_CHOICES = [
        ('discover', 'Discover'),
        ('following', 'Following'),
    ]

    ACCEPT_PRIVATE_ASKS_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    # delete these
    is_stylist = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    is_customer = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    is_seller = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No')], default='no')

    lifeform = models.CharField(max_length=10, choices=LIFEFORM_CHOICES, default='human')

    bio = models.CharField(max_length=150, blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True)
    pfp = models.ImageField(upload_to='pfps/', blank=True, null=True, default='pfps/default_img.jpg')
    credits = models.IntegerField(default=0)

    is_email_confirmed = models.BooleanField(default=False)
    new_email = models.EmailField(_('new email address'), blank=True, null=True)
    email_change_requested_at = models.DateTimeField(_('email change requested at'), blank=True, null=True)

    profile_visibility = models.CharField(max_length=20, choices=PROFILE_VISIBILITY_CHOICES, default='public')
    trending_mode = models.CharField(max_length=10, choices=TRENDING_MODE_CHOICES, default='discover')
    trending_styles = models.ManyToManyField('studio.Style', blank=True, related_name='users_with_trending_styles')
    studio_styles = models.ManyToManyField('studio.Style', blank=True, related_name='users_with_studio_styles')
    studio_visibility = models.CharField(max_length=15, choices=STUDIO_VISIBILITY_CHOICES, default='discover')
    accept_private_asks = models.CharField(max_length=3, choices=ACCEPT_PRIVATE_ASKS_CHOICES, default='yes',help_text="Indicates if the user accepts private asks.")
    private_ask_price = models.IntegerField(default=0,help_text="The price in credits for a private ask.")

    followers_list = models.ManyToManyField(
        'self',
        through='UserFollows',
        symmetrical=False,
        related_name='following_list'
    )

    @property
    def followers_num(self):
        return UserFollows.objects.filter(user_to=self).count()

    @property
    def following_num(self):
        return UserFollows.objects.filter(user_from=self).count()

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to include image processing
        for the profile picture (pfp). The image is cropped to a square
        and resized to 300x300 pixels before being saved.
        """
        new_user = self.pk is None
        super().save(*args, **kwargs)

        # Create 3 invite codes for new users
        if new_user:
            for _ in range(3):
                InviteCode.objects.create(inviter=self)


        """ thaprepe na doulevei alla den doulevei, lysh me signal
        if new_user:
            Style = apps.get_model('studio', 'Style')
            all_styles = Style.objects.all()
            self.trending_styles.set(all_styles)
            self.studio_styles.set(all_styles)"""

        if self.pfp:
            img = Image.open(self.pfp)

            # Rotate image based on EXIF orientation
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break

                exif = img._getexif()
                if exif is not None:
                    orientation = exif.get(orientation, 1)
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
            except (AttributeError, KeyError, IndexError):
                # If the image doesn't have EXIF data or it can't be accessed
                pass

            # Ensure the image is a square
            width, height = img.size
            min_dim = min(width, height)
            left = (width - min_dim) / 2
            top = (height - min_dim) / 2
            right = (width + min_dim) / 2
            bottom = (height + min_dim) / 2

            # Crop the image to a square
            img = img.crop((left, top, right, bottom))
            img = img.resize((300, 300), Image.ANTIALIAS)

            # Convert image to RGB if it's in RGBA mode
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Save the processed image to a BytesIO object
            img_io = BytesIO()
            img.save(img_io, format='JPEG')
            img_content = ContentFile(img_io.getvalue(), os.path.basename(self.pfp.name))  # path apofevgei pfps/pfps bug

            # Save the processed image back to the model field
            self.pfp.save(os.path.basename(self.pfp.name), img_content, save=False)

        super().save(*args, **kwargs)



class UserFollows(models.Model):
    user_from = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='following',
        on_delete=models.CASCADE
    )
    user_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='followers',
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'UserFollows'
        unique_together = ('user_from', 'user_to')

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'

class UserItemLikes(models.Model):
    liker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='liker_likes', blank=True, null=True)
    item = models.ForeignKey('studio.Item', on_delete=models.CASCADE, blank=True, null=True)
    styler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='styler_likes', blank=True, null=True)
    liked_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"Liker: {self.liker.username}, Item: {self.item}, Styler: {self.styler.username if self.styler else 'None'}"

    class Meta:
        verbose_name = 'UserItemLikes'
        verbose_name_plural = 'UserItemLikes'


class UserItemCart(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_cart', blank=True, null=True)
    item = models.ForeignKey('studio.Item', on_delete=models.CASCADE, blank=True, null=True)
    styler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='styler_cart', blank=True, null=True)
    price = models.FloatField(blank=True, null=True)  # New field
    size = models.CharField(max_length=10, blank=True, null=True)  # New field

    def __str__(self):
        return f"Buyer: {self.buyer.username if self.buyer else 'None'}, Item: {self.item}, Styler: {self.styler.username if self.styler else 'None'}"

    class Meta:
        verbose_name = 'UserItemCart'
        verbose_name_plural = 'UserItemCarts'


class PortraitUpload(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('notified', 'Notified'),
    ]

    portrait_img = models.ImageField(upload_to='portraituploads/')
    wearer_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ticket_id_int = models.IntegerField(null=True, blank=True)
    outfit_id = models.ForeignKey('core.Outfit', on_delete=models.SET_NULL, null=True, blank=True)
    timedate_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.wearer_id.username}'s portrait upload"


from studio.models import Item  # Make sure this import is present
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class GridPicUpload(models.Model):
    DELETED_BY_UPLOADER_CHOICES = [
        ('no', 'no'),
        ('yes', 'yes'),
    ]

    TRYON_STATE_CHOICES = [
        ('original', 'Original'),
        ('temp', 'Temporary'),
        ('virtual', 'Virtual'),
    ]

    gridpic_img = models.ImageField(upload_to='gridpicuploads/')
    gridpic_processed_img = models.ImageField(upload_to='gridpicuploads/processed/', blank=True, null=True)
    uploader_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timedate_uploaded = models.DateTimeField(auto_now_add=True)
    deleted_by_uploader = models.CharField(max_length=10, choices=DELETED_BY_UPLOADER_CHOICES, default='no')
    timedate_deleted_by_uploader = models.DateTimeField(null=True, blank=True)

    gridpic_tryon_img = models.ImageField(upload_to='gridpicuploads/processed/tryons/', blank=True, null=True)
    gridpic_temp_img = models.ImageField(upload_to='gridpicuploads/processed/temps/', blank=True, null=True)
    # gridpic_tryon_item_id = models.ManyToManyField(Item, blank=True)
    gridpic_tryon_item = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True)
    tryon_state = models.CharField(max_length=10, choices=TRYON_STATE_CHOICES, default='original')

    def __str__(self):
        return f"GridPic {self.id} uploaded by {self.uploader_id}"

    def save(self, *args, **kwargs):
        if not self.gridpic_processed_img:
            self.process_image()
        super().save(*args, **kwargs)

    def process_image(self):
        # Open the image
        img = Image.open(self.gridpic_img)

        # Convert non-RGB images to RGB
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')

        width, height = img.size

        if width > height:
            # Horizontal image
            left = (width - height) / 2
            top = 0
            right = (width + height) / 2
            bottom = height
        else:
            # Vertical image
            left = 0
            top = (height - width) / 2
            right = width
            bottom = (height + width) / 2

        # Crop and resize the image
        img = img.crop((left, top, right, bottom))
        img = img.resize((600, 600), Image.ANTIALIAS)

        # Save the processed image to BytesIO buffer
        output = BytesIO()
        img.save(output, format='JPEG', quality=85)
        output.seek(0)

        # Save the image to the gridpic_processed_img field
        self.gridpic_processed_img.save(
            f"{self.gridpic_img.name.split('/')[-1].split('.')[0]}_processed.jpg",
            ContentFile(output.read()),
            save=False
        )

    """
    def process_image(self):
        img = Image.open(self.gridpic_img)

        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        width, height = img.size

        if width > height:
            # Horizontal image
            left = (width - height) / 2
            top = 0
            right = (width + height) / 2
            bottom = height
        else:
            # Vertical image
            left = 0
            top = (height - width) / 2
            right = width
            bottom = (height + width) / 2

        img = img.crop((left, top, right, bottom))
        img = img.resize((600, 600), Image.ANTIALIAS)

        output = BytesIO()
        img.save(output, format='JPEG', quality=85)
        output.seek(0)

        self.gridpic_processed_img.save(
            f"{self.gridpic_img.name.split('/')[-1].split('.')[0]}_processed.jpg",
            ContentFile(output.read()),
            save=False
        )
    """



class Stylist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    credits = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Stylist Profile"



class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    SIZE_CHOICES = [('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')]
    SHOE_SIZE_EU_CHOICES = [(str(size), str(size)) for size in range(34, 49)] + \
                           [(str(size + 0.5), str(size + 0.5)) for size in range(34, 48)]
    SIZE_WAIST_INCHES_CHOICES = [(str(size), str(size)) for size in range(24, 39)]
    SHOE_SIZE_UK_CHOICES = [(str(size), str(size)) for size in range(2, 14)] + \
                           [(str(size + 0.5), str(size + 0.5)) for size in range(2, 13)]

    top_size_xyz = models.CharField(max_length=10, choices=SIZE_CHOICES, null=True, blank=True)
    bottom_size_xyz = models.CharField(max_length=10, choices=SIZE_CHOICES, null=True, blank=True)
    size_waist_inches = models.CharField(max_length=10, choices=SIZE_WAIST_INCHES_CHOICES, null=True, blank=True)
    shoe_size_eu = models.CharField(max_length=10, choices=SHOE_SIZE_EU_CHOICES, null=True, blank=True)
    shoe_size_uk = models.CharField(max_length=10, choices=SHOE_SIZE_UK_CHOICES, null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    birth_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}"

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'




import random

class InviteCode(models.Model):
    invite_code = models.CharField(max_length=20, unique=True, blank=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    inviter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='invite_codes_given', on_delete=models.SET_NULL, null=True, blank=True)
    invitee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='invite_code_used', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        while True:
            code = ''.join(random.choices('0123456789', k=10))
            if not InviteCode.objects.filter(invite_code=code).exists():
                return code