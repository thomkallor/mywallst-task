from django.apps import AppConfig


class SubscriptionConfig(AppConfig):
    name = 'stripeapp.subscription'
    verbose_name = 'An app to create susbtcription with stripe'

    def ready(self):
        import stripeapp.subscription.signals
