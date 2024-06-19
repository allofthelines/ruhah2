# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Customer

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)







from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps

print('\n\n\n\n\n\n', '1111111111111', '\n\n\n\n\n\n')
@receiver(post_save, sender='accounts.CustomUser')
def set_default_styles(sender, instance, created, **kwargs):
    print('\n\n\n\n\n\n', '222222222222', '\n\n\n\n\n\n')
    if created:
        Style = apps.get_model('studio', 'Style')
        all_styles = Style.objects.all()
        instance.trending_styles.set(all_styles)
        instance.studio_styles.set(all_styles)
