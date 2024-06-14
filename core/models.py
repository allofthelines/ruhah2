import io

from PIL import Image
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Count, Q
from django.utils.timezone import now
from django.utils import timezone
# from accounts.models import CustomUser
# from box.models import Ticket
# lynei to circular import ypotithetai error
from django.apps import apps
from django.conf import settings
import os
import random
from django.db.models.signals import pre_save

def get_image_upload_path(instance, filename):
    return os.path.join('outfits/', filename)

def get_portrait_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"portrait_{instance.id}.{ext}"
    return os.path.join('portraits/', filename)






class Outfit(models.Model):
    rating = models.IntegerField(default=1000)
    image = models.ImageField(upload_to="outfits/", default="outfits/default_img.jpg")
    portrait = models.ImageField(upload_to="portraits/", default="portraits/default_img.jpg", blank=True, null=True)
    ticket_id = models.ForeignKey('box.Ticket', on_delete=models.SET_NULL, null=True, blank=True)
    maker_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    items = models.ManyToManyField('studio.Item', blank=True)

    def __str__(self):
        return f"pk={self.pk}, rating={self.rating}"

    @property
    def rank(self):
        return Outfit.objects.aggregate(rank=Count("rating", filter=Q(rating__gt=self.rating), distinct=True) + 1)["rank"]

    def save(self, *args, **kwargs):
        # Check if a new file has been uploaded to the portrait field
        if self.pk and self._state.adding is False:
            old_instance = Outfit.objects.get(pk=self.pk)
            if self.portrait and self.portrait != old_instance.portrait:
                # Rename and process new portrait file
                self.portrait.name = self._get_portrait_upload_path(self.portrait.name)
                super().save(update_fields=['portrait'])
                self._process_portrait_image()

        # Always process the image field
        super().save(*args, **kwargs)
        self._resize_image(500, 500)

    def _get_portrait_upload_path(self, filename):
        ext = filename.split('.')[-1]
        base_filename = f"portrait_{self.pk}"
        filename = f"{base_filename}.{ext}"

        counter = 1
        while os.path.exists(os.path.join(settings.MEDIA_ROOT, 'portraits/', filename)):
            filename = f"{base_filename}_{counter}.{ext}"
            counter += 1

        filepath = os.path.join('portraits/', filename)
        return filepath

    def _resize_image(self, width, height):
        if self.image.width < width and self.image.height < height:
            return

        with self.image.open() as f:
            image = Image.open(f)
            image.load()

        if image.width > width:
            aspect_ratio = image.width / image.height
            image = image.resize((width, round(width / aspect_ratio)))

        if image.height > height:
            image = image.crop((0, image.height - height, width, image.height))

        with self.image.open("wb") as f:
            image.save(f, 'JPEG')

    def _process_portrait_image(self):
        if not self.portrait:
            return

        with self.portrait.open() as f:
            img = Image.open(f).convert("RGBA")

        new_size = (700, 700)
        background = Image.new("RGBA", new_size, (255, 255, 255, 255))

        scale_factor = random.uniform(0.8, 0.9)
        img.thumbnail((new_size[0] * scale_factor, new_size[1] * scale_factor), Image.ANTIALIAS)

        paste_position = (
            (new_size[0] - img.size[0]) // 2,
            (new_size[1] - img.size[1]) // 2
        )

        background.paste(img, paste_position, img)

        final_image = background.convert("RGB")

        temp_buffer = io.BytesIO()
        final_image.save(temp_buffer, format='JPEG')
        temp_buffer.seek(0)

        self.portrait.save(self.portrait.name, ContentFile(temp_buffer.read()), save=False)

    class Meta:
        db_table = 'outfit_table'
















'''
class Outfit(models.Model):
    rating = models.IntegerField(default=1000)
    image = models.ImageField(upload_to="outfits/", default="outfits/default_img.jpg")
    portrait = models.ImageField(upload_to="portraits/", default="portraits/default_img.jpg", blank=True, null=True)
    ticket_id = models.ForeignKey('box.Ticket', on_delete=models.SET_NULL, null=True, blank=True)
    maker_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    items = models.ManyToManyField('studio.Item', blank=True)

    def __str__(self):
        return f"pk={self.pk}, rating={self.rating}"

    @property
    def rank(self):
        return Outfit.objects.aggregate(rank=Count("rating", filter=Q(rating__gt=self.rating), distinct=True) + 1)["rank"]

    def save(self, *args, **kwargs):
        # Check if a new file has been uploaded to the portrait field
        if self.pk and self._state.adding is False:
            old_instance = Outfit.objects.get(pk=self.pk)
            if self.portrait and self.portrait != old_instance.portrait:
                # Process new portrait file
                self.portrait.name = self._get_portrait_upload_path(self.portrait.name)
                super().save(update_fields=['portrait'])
                self._resize_portrait(500, 500)

        # Always process the image field
        super().save(*args, **kwargs)
        self._resize_image(500, 500)

    def _get_portrait_upload_path(self, filename):
        ext = filename.split('.')[-1]
        base_filename = f"portrait_{self.pk}"
        filename = f"{base_filename}.{ext}"
        filepath = os.path.join('portraits/', filename)

        counter = 1
        while os.path.exists(os.path.join(settings.MEDIA_ROOT, filepath)):
            filename = f"{base_filename}_{counter}.{ext}"
            filepath = os.path.join('portraits/', filename)
            counter += 1

        return filepath

    def _resize_image(self, width, height):
        if self.image.width < width and self.image.height < height:
            return

        with self.image.open() as f:
            image = Image.open(f)
            image.load()

        if image.width > width:
            aspect_ratio = image.width / image.height
            image = image.resize((width, round(width / aspect_ratio)))

        if image.height > height:
            image = image.crop((0, image.height - height, width, image.height))

        with self.image.open("wb") as f:
            image.save(f, 'JPEG')

    def _resize_portrait(self, width, height):
        if not self.portrait:
            return

        with self.portrait.open() as f:
            portrait = Image.open(f)
            portrait.load()

        if portrait.width > width:
            aspect_ratio = portrait.width / portrait.height
            portrait = portrait.resize((width, round(width / aspect_ratio)))

        if portrait.height > height:
            portrait = portrait.crop((0, portrait.height - height, width, portrait.height))

        with self.portrait.open("wb") as f:
            portrait.save(f, 'JPEG')

    class Meta:
        db_table = 'outfit_table'






class Outfit(models.Model):
    rating = models.IntegerField(default=1000)
    image = models.ImageField(upload_to="outfits/", default="outfits/default_img.jpg")
    portrait = models.ImageField(upload_to="portraits/", default="portraits/default_img.jpg")
    ticket_id = models.ForeignKey('box.Ticket', on_delete=models.SET_NULL, null=True, blank=True)
    maker_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    items = models.ManyToManyField('studio.Item', blank=True)

    def __str__(self):
        return f"pk={self.pk}, rating={self.rating}"

    @property
    def rank(self):
        return Outfit.objects.aggregate(rank=Count("rating", filter=Q(rating__gt=self.rating), distinct=True) + 1)["rank"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._resize_image(500, 500)
        self._resize_portrait(500, 500)

    def _resize_image(self, width, height):
        if self.image.width < width and self.image.height < height:
            return

        with self.image.open() as f:
            image = Image.open(f)
            image.load()

        if image.width > width:
            aspect_ratio = image.width / image.height
            image = image.resize((width, round(width / aspect_ratio)))

        if image.height > height:
            image = image.crop((0, image.height - height, width, image.height))

        with self.image.open("wb") as f:
            image.save(f, 'JPEG')

    def _resize_portrait(self, width, height):
        if self.portrait.width < width and self.portrait.height < height:
            return

        with self.portrait.open() as f:
            portrait = Image.open(f)
            portrait.load()

        if portrait.width > width:
            aspect_ratio = portrait.width / portrait.height
            portrait = portrait.resize((width, round(width / aspect_ratio)))

        if portrait.height > height:
            portrait = portrait.crop((0, portrait.height - height, width, portrait.height))

        with self.portrait.open("wb") as f:
            portrait.save(f, 'JPEG')

    class Meta:
        db_table = 'outfit_table'
'''