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


@receiver(post_save, sender='accounts.CustomUser')
def set_default_styles(sender, instance, created, **kwargs):
    if created:
        Style = apps.get_model('studio', 'Style')
        all_styles = Style.objects.all()

        # Save the instance before setting ManyToMany fields
        instance.save()

        # Now set the ManyToMany fields
        instance.trending_styles.set(all_styles)
        instance.studio_styles.set(all_styles)
        instance.bio = 'penis'

        # Debugging output
        print('\n\n\n\n\n\nALL_STYLES:', all_styles)
        print('\n\n\n\n\n\ninstance.trending_styles:', instance.trending_styles.all())
        print('\n\n\n\n\n\ninstance.studio_styles:', instance.studio_styles.all())
        print('\n\n\n\n\n\ninstance.username:', instance.username)
        print('\n\n\n\n\n\ninstance.bio:', instance.bio)
