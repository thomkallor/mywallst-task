from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from stripeapp.subscription.models import User, PaymentMethod, Subscription
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms


class MyUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('stripe_id',)}),
    )


admin.site.register(User, MyUserAdmin)
admin.site.register(PaymentMethod)
admin.site.register(Subscription)
