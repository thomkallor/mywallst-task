from django.db import models

# from django.contrib.auth.models import User

from django.contrib.auth.models import AbstractUser

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):

    def create_user(self, username, password, **extra_fields):
        """
        Create and save a User with the given username and password.
        """
        if not username:
            raise ValueError(_('The username must be set'))
        username = username.strip().lower()
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given username and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):

    objects = CustomUserManager()

    stripe_id = models.CharField(max_length=255, unique=True, null=True)


class PaymentMethod(models.Model):
    stripe_id = models.CharField(max_length=255, primary_key=True)
    last4 = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=128)
    brand = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    holder_name = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    is_default = models.BooleanField(default=False)


class Subscription(models.Model):
    stripe_id = models.CharField(max_length=255, primary_key=True)
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.DO_NOTHING)
    price_id = models.CharField(max_length=255)
    status = models.CharField(max_length=128)
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField()
