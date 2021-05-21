from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

print('~~~top of users/signals.py~~~')

from django.contrib.auth import get_user_model
User = get_user_model()
from django.conf import settings


from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=get_user_model())
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=get_user_model())
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

print('~~~bottom of users/signals.py~~~')
