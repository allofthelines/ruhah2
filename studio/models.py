from django.db import models
from accounts.models import CustomUser
from django.conf import settings
import jsonfield
from pgvector.django import VectorField
# from multiselectfield import MultiSelectField
# ALLAKSE TO SIZE_XYZ SE MULTIPLE


class Style(models.Model):
    style_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.style_name

class Tag(models.Model):
    tag_name = models.CharField(max_length=100, blank=True)
    tag_type = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.tag_name

class SizeCategory(models.Model):
    SIZE_CHOICES = [('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('one_size', 'One Size')]

    name = models.CharField(max_length=10, choices=SIZE_CHOICES, unique=True)

    def __str__(self):
        return self.name

class SizeShoeUkCategory(models.Model):
    SIZE_CHOICES = [('2', '2'), ('2.5', '2.5'), ('3', '3'), ('3.5', '3.5'), ('4', '4'), ('4.5', '4.5'),
                    ('5', '5'), ('5.5', '5.5'), ('6', '6'), ('6.5', '6.5'), ('7', '7'), ('7.5', '7.5'),
                    ('8', '8'), ('8.5', '8.5'), ('9', '9'), ('9.5', '9.5'), ('10', '10'), ('10.5', '10.5'),
                    ('11', '11'), ('11.5', '11.5'), ('12', '12'), ('12.5', '12.5'), ('13', '13'), ('13.5', '13.5')]

    size = models.CharField(max_length=10, choices=SIZE_CHOICES, unique=True)

    def __str__(self):
        return self.size

class SizeShoeEuCategory(models.Model):
    SIZE_CHOICES = [('34', '34'), ('34.5', '34.5'), ('35', '35'), ('35.5', '35.5'), ('36', '36'), ('36.5', '36.5'),
                    ('37', '37'), ('37.5', '37.5'), ('38', '38'), ('38.5', '38.5'), ('39', '39'), ('39.5', '39.5'),
                    ('40', '40'), ('40.5', '40.5'), ('41', '41'), ('41.5', '41.5'), ('42', '42'), ('42.5', '42.5'),
                    ('43', '43'), ('43.5', '43.5'), ('44', '44'), ('44.5', '44.5'), ('45', '45'), ('45.5', '45.5'),
                    ('46', '46'), ('46.5', '46.5'), ('47', '47'), ('47.5', '47.5'), ('48', '48')]

    size = models.CharField(max_length=10, choices=SIZE_CHOICES, unique=True)

    def __str__(self):
        return self.size

class SizeWaistInchCategory(models.Model):
    SIZE_CHOICES = [('23', '23'), ('24', '24'), ('25', '25'), ('26', '26'), ('27', '27'),
                    ('28', '28'), ('29', '29'), ('30', '30'), ('31', '31'), ('32', '32'),
                    ('33', '33'), ('34', '34'), ('35', '35'), ('36', '36'), ('37', '37')]

    size = models.CharField(max_length=10, choices=SIZE_CHOICES, unique=True)

    def __str__(self):
        return self.size

class EcommerceStore(models.Model):
    # rename to EcommerceStore
    name = models.CharField(max_length=255, null=True, blank=True)
    shop_url = models.CharField(max_length=255, null=True, blank=True)

    PLATFORM_CHOICES = [
        ('shopify', 'Shopify'),
        ('bigcommerce', 'BigCommerce'),
        ('woocommerce', 'WooCommerce'),
        ('magento', 'Magento'),
        ('squarespace', 'Squarespace'),
    ]

    # address
    address_street_1 = models.CharField(max_length=255, null=True, blank=True)
    address_street_2 = models.CharField(max_length=255, null=True, blank=True)
    address_postal_code = models.CharField(max_length=50, null=True, blank=True)
    address_city = models.CharField(max_length=50, null=True, blank=True)
    address_country = models.CharField(max_length=50, null=True, blank=True)

    # api
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, null=True, blank=True)
    api_store_id = models.CharField(max_length=255, null=True, blank=True)
    api_key = models.CharField(max_length=255, null=True, blank=True)
    api_secret = models.CharField(max_length=255, null=True, blank=True)
    api_access_token = models.CharField(max_length=255, null=True, blank=True)

    size_mapping = jsonfield.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    CONDITION_CHOICES = [
        ('new', 'new'),
        ('pre-owned', 'pre-owned'),
    ]
    CAT_CHOICES = [
        ('top', 'top'),
        ('bottom', 'bottom'),
        ('accessory', 'accessory'),
        ('footwear', 'footwear'),
        ('dress', 'dress')
    ]

    # SHOPIFY API
    name = models.CharField(max_length=255, blank=True, null=True)
    price = models.FloatField(null=True, blank=True)
    sizes_xyz = models.ManyToManyField(SizeCategory, blank=True)
    sizes_shoe_uk = models.ManyToManyField(SizeShoeUkCategory, blank=True)
    sizes_shoe_eu = models.ManyToManyField(SizeShoeEuCategory, blank=True)
    sizes_waist_inches = models.ManyToManyField(SizeWaistInchCategory, blank=True)

    # SHOPIFY STORE DB
    location = models.CharField(max_length=255, blank=True, null=True) # location_country or location_city?

    # TYPE ME XERI DJANGO-ADMIN-MANUAL vs AWS-JSON-BATCH
    ecommerce_store = models.ForeignKey(EcommerceStore, on_delete=models.SET_NULL, blank=True, null=True)
    ecommerce_product_id = models.CharField(max_length=255, blank=True, null=True)
    cat = models.CharField(max_length=20, choices=CAT_CHOICES, blank=True)
    modality = models.CharField(max_length=20, choices=[('physical', 'physical'), ('virtual', 'virtual')], blank=True)
    taglist = models.ManyToManyField('studio.Tag', blank=True)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, blank=True, null=True)

    # AUTO GEN ME SCRIPT
    tags = models.CharField(max_length=255, blank=True, null=True)
    itemid = models.CharField(max_length=30, blank=True, null=True)

    # DJANGO-ADMIN-MANUAL vs AWS-JSON-BATCH
    image = models.ImageField(upload_to="items/", default='items/default.jpg', blank=True, null=True)
    embedding = VectorField(dimensions=768, blank=True, null=True)

    def __str__(self):
        return self.itemid

    @classmethod
    def find_similar(cls, vector, limit=10):
        """Find similar products using pgvector cosine similarity"""
        return cls.objects.annotate(
            similarity=1 - CosineDistance('embedding', vector)
        ).order_by('-similarity')[:limit]

class StudioOutfitTemp(models.Model):
    # etsi wste otan kanw refresh na krathsw to idio
    ticket = models.ForeignKey('box.Ticket', on_delete=models.CASCADE, null=True, blank=True)  # box.Ticket lynei circular import
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
