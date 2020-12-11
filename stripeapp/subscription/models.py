from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):

    objects = UserManager()

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
