from datetime import datetime, timedelta

from django.db import models
from PIL import Image
# from django.contrib.auth import get_user_model
# User = get_user_model()
from django.conf import settings
User = settings.AUTH_USER_MODEL
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

#~~~ CUSTOM USER ~~~
print('~~~top of users/models.py~~~')


# class User(AbstractUser):
#     class Meta:
#         db_table = 'auth_user'


class MyUserManager(BaseUserManager):
    def create_user(self, email, lat, long, travel_radius, username, password=None):
        print('username in UserManager.create_user(): ' + username)

        if not email:
            raise ValueError('Users must have an email address')

        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username, #todo: confirm, is this right?
            lat=lat,
            long=long,
            travel_radius=travel_radius,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    # def create_staffuser(self, email, lat, long, travel_radius, password): # todo: remove
    #     """
    #     Creates and saves a staff user with the given email and password.
    #     """
    #     user = self.create_user(
    #         email,
    #         username=username,
    #         password=password,
    #         lat=lat,
    #         long=long,
    #         travel_radius=travel_radius,
    #     )
    #     user.staff = True
    #     user.save(using=self._db)
    #     return user

    def create_superuser(self, email, username, password):
        print('username in UserManager.create_superuser(): ' + username)
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            username=username,
            password=password,
            lat=None,
            long=None,
            travel_radius=None,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user




class MyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False) # a admin user; non super-user
    admin = models.BooleanField(default=False) # a superuser
    email_confirmed = models.BooleanField(default=False)  # has user confirmed their email?
    confirmed_trade_email_opt_in = models.BooleanField(default=False)  # send user an email if someone confirms a match with them
    first_trade_proposal = models.BooleanField(default=True)  # user has submitted at least 1 trade proposal. Email notif. prompt

    # Location fields:
    lat = models.DecimalField(default=None, null=True, blank=True, max_digits=14, decimal_places=11)
    long = models.DecimalField(default=None, null=True, blank=True, max_digits=14, decimal_places=11)
    travel_radius = models.IntegerField(default=None, null=True, blank=True)
    location_name = models.CharField(max_length=255)

    # Email confirmation fields:
    activation_key = models.CharField(max_length=40, null=True, blank=True) # builds link user goes to for email confirmation/activation
    key_expires = models.DateTimeField(default=datetime.today() + timedelta(days=7))
    email_confirmation_due_date = models.DateTimeField(default=datetime.today() + timedelta(days=7)) # Require login if email not confirmed

    conf_trade_opt_out_key = models.CharField(max_length=40, null=True, blank=True)  # builds link user goes to for easy email opt out

    @property
    def email_confirmation_overdue(self):
        return datetime.now(self.email_confirmation_due_date.tzinfo) > self.email_confirmation_due_date

    # notice the absence of a "Password field", that is built in.
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email'] # Email & Password are required by default.

    objects = MyUserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin






# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     image = models.ImageField(default='default.jpg', upload_to='profile_pics')
#
#     def __str__(self):
#         return f'{self.user.username} Profile'

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)

    #     img = Image.open(self.image.path)

    #     if img.height > 300 or img.width > 300:
    #         output_size = (300, 300)
    #         img.thumbnail(output_size)
    #         img.save(self.image.path)


print('~~~bottom of users/models.py~~~')
