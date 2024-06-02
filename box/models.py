from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from core.models import Outfit
from django.conf import settings
# from studio.models import Item
# lynei to circular import error ypotithetai
from django.apps import apps
from django.conf import settings




class Ticket(models.Model):
    style1 = models.CharField(max_length=100)
    style2 = models.CharField(max_length=100, blank=True, null=True)
    occasion = models.CharField(max_length=100)
    condition = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    notes = models.TextField(blank=True, default='')

    STATUS_CHOICES = [
        ('notpaid', 'notpaid'),
        ('open', 'open'),
        ('closed', 'closed'),
        ('boxed', 'boxed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='notpaid')
    timestamp = models.DateTimeField(default=timezone.now)
    creator_id = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    outfit1 = models.ForeignKey(Outfit, on_delete=models.SET_NULL, null=True, blank=True, related_name='ticket_outfit1')
    outfit2 = models.ForeignKey(Outfit, on_delete=models.SET_NULL, null=True, blank=True, related_name='ticket_outfit2')
    outfits_all = models.ManyToManyField('core.Outfit', blank=True)
    stylists_all = models.ManyToManyField(CustomUser, blank=True, related_name='stylist_tickets')

    SIZE_CHOICES = [('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')]

    size_top_xyz = models.CharField(max_length=3, choices=SIZE_CHOICES, blank=True, null=True)
    size_bottom_xyz = models.CharField(max_length=3, choices=SIZE_CHOICES, blank=True, null=True)
    size_waist_inches = models.IntegerField(blank=True, null=True)
    size_shoe_eu = models.FloatField(blank=True, null=True)

    maximum_outfits = models.IntegerField(default=5)
    current_outfits = models.IntegerField(default=0)

    def __str__(self):
        return f"Ticket {self.id} - Status: {self.status}"

class Order(models.Model):
    TYPE_CHOICES = [
        ('box', 'box'),
        ('item', 'item'),
    ]

    STATUS_CHOICES = [
        ('preparing', 'preparing'),
        ('shipped', 'shipped'),
        ('delivered', 'delivered'),
    ]

    type = models.CharField(max_length=5, choices=TYPE_CHOICES)
    ticket_id = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, blank=True)
    money = models.FloatField(blank=True, null=True)
    creator_id = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=True, null=True)
    items = models.ManyToManyField('studio.Item')
    address_customer = models.CharField(max_length=100, blank=True, null=True)
    address_fumio = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} - {self.get_type_display()}"

    def hours_preparing(self):
        if not self.timestamp:
            return 0
        now = timezone.now()
        elapsed_time = now - self.timestamp
        hours_elapsed = elapsed_time.total_seconds() // 3600
        return int(hours_elapsed)

    hours_preparing.short_description = 'Hours Preparing'
    hours_preparing.admin_order_field = 'timestamp'  # This allows sorting by this method



class Return(models.Model):
    STATUS_CHOICES = [
        ('preparing', 'preparing'),
        ('shipped', 'shipped'),
        ('delivered', 'delivered'),
    ]

    order_id = models.ForeignKey('box.Order', on_delete=models.SET_NULL, null=True, blank=True)
    returner_id = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='returns')
    timestamp = models.DateTimeField(auto_now_add=True)
    money = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    address_customer = models.CharField(max_length=100, blank=True, null=True)
    address_fumio = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Return {self.id} for Order {self.order_id}"
