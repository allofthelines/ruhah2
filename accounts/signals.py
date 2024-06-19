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
from .models import CustomUser

print('\n\n\n\n\n\n', '1111111111111', '\n\n\n\n\n\n')
def set_default_styles(sender, instance, created, **kwargs):
    print('\n\n\n\n\n\n', '222222222222', '\n\n\n\n\n\n')
    if created:
        print('\n\n\n\n\n\n', '33333333333', '\n\n\n\n\n\n')
        Style = apps.get_model('studio', 'Style')
        all_styles = Style.objects.all()
        instance.trending_styles.set(all_styles)
        instance.studio_styles.set(all_styles)
        print('\n\n\n\n\n\n', '44444444444', '\n\n\n\n\n\n')
