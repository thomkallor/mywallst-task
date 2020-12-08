from django.urls import path, re_path
from stripeapp.subscription import views

subscription_urls = [
    path('paymentmethod/<str:user_id>', views.PaymentDetails.as_view()),
    path('customer/<str:user_id>/<str:method_id>',
         views.CustomerDefaultPayment.as_view()),
    path('subscription/<str:user_id>/<str:method_id>',
         views.SubscriptionDetails.as_view()),
    path('webhook',
         views.WebHook.as_view()),
]
