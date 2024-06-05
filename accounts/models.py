from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.timezone import now
from PIL import Image, ExifTags
import os
from django.core.files.storage import default_storage
from io import BytesIO
from django.core.files.base import ContentFile

class CustomUser(AbstractUser):
    is_stylist = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    is_customer = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    is_seller = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No')], default='no')

    bio = models.CharField(max_length=150, blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True)
    pfp = models.ImageField(upload_to='pfps/', blank=True, null=True, default='pfps/default_img.jpg')

    followers_list = models.ManyToManyField(
        'self',
        through='UserFollows',
        symmetrical=False,
        related_name='following_list'
    )

    @property
    def followers_num(self):
        # return self.followers_list.count()
        return UserFollows.objects.filter(user_to=self).count()

    @property
    def following_num(self):
        # return self.following_list.count()
        return UserFollows.objects.filter(user_from=self).count()

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to include image processing
        for the profile picture (pfp). The image is cropped to a square
        and resized to 300x300 pixels before being saved.
        """
        super().save(*args, **kwargs)

        if self.pfp:
            img = Image.open(self.pfp)

            # Rotate image based on EXIF orientation
            # lynei to provlhma sto mobile sideways upload
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

            # Save the processed image to a BytesIO object
            img_io = BytesIO()
            img.save(img_io, format='JPEG')
            img_content = ContentFile(img_io.getvalue(), os.path.basename(self.pfp.name)) # path apofevgei pfps/pfps bug

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






class Stylist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    credits = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Stylist Profile"



class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    SIZE_CHOICES = [('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')]

    top_size_xyz = models.CharField(max_length=10, choices=SIZE_CHOICES, null=True, blank=True)
    bottom_size_xyz = models.CharField(max_length=10, choices=SIZE_CHOICES, null=True, blank=True)
    size_waist_inches = models.IntegerField(default=0, null=True, blank=True)
    size_chest_inches = models.IntegerField(default=0, null=True, blank=True)
    shoe_size_eu = models.FloatField(null=True, blank=True)
    shoe_size_uk = models.FloatField(null=True, blank=True)
    shoe_size_us = models.FloatField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    birth_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}"

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'




class Seller(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    items_uploaded = models.ManyToManyField('studio.Item', blank=True)
    items_sold = models.IntegerField(blank=True, null=True, default=0)
    total_sales = models.IntegerField(blank=True, null=True, default=0)
    fumio_profit = models.IntegerField(blank=True, null=True, default=0)
    seller_profit = models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        verbose_name = 'Seller'
        verbose_name_plural = 'Sellers'








class Supplier(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=50, blank=True, null=True)
    items_catalogue = models.ManyToManyField('studio.Item', blank=True)
    timestamp = models.DateTimeField(default=now)
    items_sold = models.IntegerField(blank=True, null=True, default=0)
    items_boxed = models.IntegerField(blank=True, null=True, default=0)
    total_sales = models.IntegerField(blank=True, null=True, default=0)
    fumio_profit = models.IntegerField(blank=True, null=True, default=0)
    supplier_profit = models.IntegerField(blank=True, null=True, default=0)
    notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'

    def __str__(self):
        return f'Supplier {self.id}'