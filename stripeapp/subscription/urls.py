from django.urls import path, re_path
from stripeapp.subscription import views

app_name = 'stripeapp.subscription'

subscription_urls = [
    path('paymentmethod/<str:user_id>',
         views.PaymentDetails.as_view(), name='newpayment'),
    path('customer/<str:user_id>/<str:method_id>',
         views.CustomerDefaultPayment.as_view(), name='defaultpayment'),
    path('subscription/<str:user_id>/<str:method_id>',
         views.SubscriptionDetails.as_view(), name='newsubscription'),
    path('webhook',
         views.WebHook.as_view(), name='webhook'),
]
