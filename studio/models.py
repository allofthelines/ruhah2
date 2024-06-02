from django.db import models
from accounts.models import CustomUser
from django.conf import settings
from box.models import Ticket
# from multiselectfield import MultiSelectField
# ALLAKSE TO SIZE_XYZ SE MULTIPLE


class Tag(models.Model):
    tag_name = models.CharField(max_length=100, blank=True)
    tag_type = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.tag_name


class Item(models.Model):
    CONDITION_CHOICES = [
        ('new', 'new'),
        ('pre-owned', 'pre-owned'),
    ]
    SHIP_READY_CHOICES = [
        ('yes', 'yes'),
        ('no', 'no'),
    ]
    CAT_CHOICES = [
        ('top', 'top'),
        ('bottom', 'bottom'),
        ('accessory', 'accessory'),
        ('footwear', 'footwear'),
        ('dress', 'dress')
    ]

    name = models.CharField(max_length=255, blank=True, null=True)
    price = models.FloatField(null=True, blank=True)
    cat = models.CharField(max_length=20, choices=CAT_CHOICES, blank=True)
    itemid = models.CharField(max_length=30, blank=True, null=True)
    sku = models.CharField(max_length=30, blank=True, null=True)
    brand = models.CharField(max_length=100, default='nologo', blank=True, null=True)
    owner = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, blank=True, null=True)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    is_ship_ready = models.CharField(max_length=3, choices=SHIP_READY_CHOICES, blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True)
    taglist = models.ManyToManyField('studio.Tag', blank=True)
    image = models.ImageField(upload_to="items/", default='items/default.jpg', blank=True, null=True)
    stock = models.IntegerField(blank=True, null=True)

    SIZE_CHOICES = [('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')]

    size_xyz = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True, null=True)
    size_uk = models.FloatField(null=True, blank=True)
    size_us = models.FloatField(null=True, blank=True)
    size_eu = models.FloatField(null=True, blank=True)
    size_chest_inches = models.FloatField(null=True, blank=True)
    size_waist_inches = models.FloatField(null=True, blank=True)
    shoe_mw = models.CharField(max_length=10, choices=[('man', 'man'), ('woman', 'woman'), ('unisex', 'unisex')],
                               blank=True, null=True)

    def __str__(self):
        return self.itemid

class StudioOutfitTemp(models.Model):
    # etsi wste otan kanw refresh na krathsw to idio
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    item1img = models.ImageField(upload_to='studiooutfittemps/', default='studiooutfittemps/default_img1.jpg')
    item1id = models.CharField(max_length=20, blank=True)
    item2img = models.ImageField(upload_to='studiooutfittemps/', default='studiooutfittemps/default_img2.jpg')
    item2id = models.CharField(max_length=20, blank=True)
    item3img = models.ImageField(upload_to='studiooutfittemps/', default='studiooutfittemps/default_img3.jpg')
    item3id = models.CharField(max_length=20, blank=True)
    item4img = models.ImageField(upload_to='studiooutfittemps/', default='studiooutfittemps/default_img4.jpg')
    item4id = models.CharField(max_length=20, blank=True)

    def get_image_url(self, index):
        attr = f'item{index}img'
        return getattr(self, attr, None).url if getattr(self, attr, None) else None

    def __str__(self):
        return f"Studio Outfit Temp {self.id}"