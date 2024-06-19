# signals.py in your accounts app
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def set_default_styles(sender, instance, created, **kwargs):
    if created:
        Style = apps.get_model('studio', 'Style')
        all_styles = Style.objects.all()
        instance.trending_styles.set(all_styles)
        instance.studio_styles.set(all_styles)
