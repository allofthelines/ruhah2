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


class Outfit(models.Model):
    rating = models.IntegerField(default=1000)
    image = models.ImageField(upload_to="outfits/", default="outfits/default_img.jpg")
    portrait = models.ImageField(upload_to="portraits/", default="portraits/default_img.jpg")
    ticket_id = models.ForeignKey('box.Ticket', on_delete=models.SET_NULL, null=True, blank=True)
    maker_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    items = models.ManyToManyField('studio.Item', blank=True)
    hidden = models.BooleanField(default=False)  # portrait otan sto profile

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