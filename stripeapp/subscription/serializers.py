from rest_framework import serializers
from stripeapp.subscription.models import User, PaymentMethod, Subscription


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = User


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = PaymentMethod


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Subscription


class AddressSerializer(serializers.Serializer):
    city = serializers.CharField(
        max_length=128, required=False, allow_null=True)
    country = serializers.CharField(
        max_length=128, required=False, allow_null=True)
    line1 = serializers.CharField(
        max_length=256, required=False, allow_null=True)
    line2 = serializers.CharField(
        max_length=256, required=False, allow_null=True)
    postal_code = serializers.CharField(
        max_length=64, required=False, allow_null=True)
    state = serializers.CharField(
        max_length=128, required=False, allow_null=True)


class BillingDetailsSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=128, required=False, allow_null=True)
    address = AddressSerializer()
    email = serializers.EmailField(required=False, allow_null=True)
    phone = serializers.CharField(
        max_length=15, required=False, allow_null=True)


class CardSerializer(serializers.Serializer):
    number = serializers.IntegerField(required=False, allow_null=True)
    exp_month = serializers.IntegerField(required=False, allow_null=True)
    exp_year = serializers.IntegerField(required=False, allow_null=True)
    cvc = serializers.IntegerField(required=False, allow_null=True)


class PaymentMethodRequestSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=128)
    card = CardSerializer()
    billing_details = BillingDetailsSerializer(required=False, allow_null=True)
    customer = serializers.CharField(
        max_length=128, required=False, allow_null=True)


class CustomerRequestSerializer(serializers.Serializer):
    address = AddressSerializer()
    email = serializers.EmailField(required=False, allow_null=True)
    payment_method = serializers.CharField(
        max_length=255, required=False, allow_null=True)
    phone = serializers.CharField(
        max_length=15, required=False, allow_null=True)
    description = serializers.CharField(
        max_length=255, required=False, allow_null=True)


class SubscriptionRequestSerializer(serializers.Serializer):
    price_id = serializers.CharField(max_length=255, required=True)
