from django.db import models
from django.contrib.auth.models import User
# for signals - post_save (after save) we create instance of userProfile
from django.db.models.signals import post_save
# to rececive the signals
from django.dispatch import receiver

from django_countries.fields import CountryField


class UserProfile(models.Model):
    """
    user profile
    1. place to save default delivery info
    2. provide user with record of their order history
    """
    # one to one - like foreign key but only one i.e. only one user profile
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # delivery info that user can provide defaults for
    default_phone_number = models.CharField(max_length=20, null=True, blank=True)
    default_country = CountryField(blank_label='Country *', null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_town_or_city = models.CharField(max_length=40, null=True, blank=True)
    default_street_address1 = models.CharField(max_length=80, null=True, blank=True)
    default_street_address2 = models.CharField(max_length=80, null=True, blank=True)
    default_county = models.CharField(max_length=80, null=True, blank=True)

    def __str__(self):
        """return username"""
        return self.user.username


# similar to signals in signals.py in checkout app but just including
# them here instead of in separate file because there's only one
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile each time user object is saved
    """
    if created:
        UserProfile.objects.create(user=instance)
    # Existing users: just save the profile
    instance.userprofile.save()
