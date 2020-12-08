from django.db.models.signals import pre_save
from django.dispatch import receiver

from stripeapp.subscription.models import PaymentMethod


@receiver(pre_save, sender=PaymentMethod)
def save_payment_method(sender, instance, **kwargs):
    if (instance.is_default):

        try:
            default_method = PaymentMethod.objects.get(
                user_id=instance.user_id, is_default=True)
            default_method.is_default = False
            return default_method.save()

        except PaymentMethod.DoesNotExist:
            pass
