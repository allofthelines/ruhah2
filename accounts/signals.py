# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Customer

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)







"""from django.db.models.signals import post_save
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
        print('\n\n\n\n\n\ninstance.trending_styles:', type(instance.trending_styles.all()))
        print('\n\n\n\n\n\ninstance.studio_styles:', instance.studio_styles.all())
        print('\n\n\n\n\n\ninstance.username:', instance.username)
        print('\n\n\n\n\n\ninstance.bio:', instance.bio)"""



from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.apps import apps
from .models import CustomUser
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender='accounts.CustomUser')
def set_bio(sender, instance, created, **kwargs):
    if created:
        # Set the bio field and save the instance
        instance.bio = 'penis'
        instance.save()
        logger.debug('\n\n\n\n\nBIO SET AND INSTANCE SAVED\n\n\n\n\n')
        print('\n\n\n\n\nBIO SET AND INSTANCE SAVED\n\n\n\n\n')

@receiver(m2m_changed, sender=CustomUser.trending_styles.through)
def set_default_styles(sender, instance, action, **kwargs):
    if action == 'post_add':
        Style = apps.get_model('studio', 'Style')
        all_styles = Style.objects.all()

        # Now set the ManyToMany fields
        instance.trending_styles.set(all_styles)
        instance.studio_styles.set(all_styles)

        # Debugging output
        logger.debug('\n\n\n\n\nALL_STYLES: %s\n\n\n\n\n', all_styles)
        logger.debug('\n\n\n\n\ninstance.trending_styles: %s\n\n\n\n\n', instance.trending_styles.all())
        logger.debug('\n\n\n\n\ninstance.studio_styles: %s\n\n\n\n\n', instance.studio_styles.all())
        print('\n\n\n\n\nALL_STYLES:', all_styles)
        print('\n\n\n\n\ninstance.trending_styles:', instance.trending_styles.all())
        print('\n\n\n\n\ninstance.studio_styles:', instance.studio_styles.all())
        print('\n\n\n\n\ninstance.username:', instance.username)
        print('\n\n\n\n\ninstance.bio:', instance.bio)

