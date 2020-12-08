from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import force_authenticate

from stripeapp.subscription.models import User
from stripeapp.subscription.views import CustomerDefaultPayment, PaymentDetails, SubscriptionDetails, WebHook

import copy
import json

# Using the standard RequestFactory API to create a form POST request
admin = User.objects.get(username='admin')
payment_id = ''
subscription_id = ''
client = APIClient()
client.force_authenticate(user=admin)


class PaymentDetailsTest:
    view = PaymentDetails.as_view()
    req_body = {
        "type": "card",
        "card": {
            "number": 4242424242424242,
            "exp_month": 12,
            "exp_year": 2021,
            "cvc": 422
        },
        "billing_details": {
            "name": "fd",
            "address": {
                "city": "New york",
                "country": "US",
                "line1": "line1",
                "line2": "line2",
                "postal_code": "code",
                "state": "New york"
            },
            "email": "email@email.com",
            "phone": 89283021234
        },
        "customer": None
    }

    @classmethod
    def success(cls):
        global payment_id
        response = client.post(
            f'/paymentmethod/{admin.id}', cls.req_body, format='json')
        payment_id = json.loads(
            response.content.decode('utf-8')).get('stripe_id')

        assert response.status_code == 201

    @classmethod
    def failure(cls):
        req_fail = copy.deepcopy(cls.req_body)
        req_fail['card'] = None
        response = client.post(
            f'/paymentmethod/{admin.id}', req_fail, format='json')

        assert response.status_code == 400


class DefaultPaymentTest:

    @classmethod
    def success(cls):
        response = client.put(
            f'/customer/{admin.id}/{payment_id}', format='json')

        assert response.status_code == 200

    @classmethod
    def failure(cls):
        response = client.put(
            f'/paymentmethod/{admin.id}/01', format='json')

        assert response.status_code == 404


class SubscriptionTest:

    req_body = {'price_id': 'price_1Hv5XTEtUponlBUMn4Woapo3'}

    @classmethod
    def success(cls):
        global subscription_id
        response = client.post(
            f'/subscription/{admin.id}/{payment_id}', cls.req_body, format='json')
        subscription_id = json.loads(
            response.content.decode('utf-8')).get('stripe_id')

        assert response.status_code == 201

    @classmethod
    def failure(cls):
        response = client.post(
            f'/subscription/{admin.id}/01', cls.req_body, format='json')

        assert response.status_code == 404


class WebHookTest:

    req_body = {
        "created": 1326853478,
        "livemode": False,
        "id": "evt_00000000000000",
        "type": "customer.subscription.created",
        "object": "event",
        "request": None,
        "pending_webhooks": 1,
        "api_version": "2020-08-27",
        "data": {
            "object": {
                "id": subscription_id,
                "object": "subscription",
                "application_fee_percent": None,
                "billing_cycle_anchor": 1607369142,
                "billing_thresholds": None,
                "cancel_at": None,
                "cancel_at_period_end": False,
                "canceled_at": None,
                "collection_method": "charge_automatically",
                "created": 1607369142,
                "current_period_end": 1610047542,
                "current_period_start": 1607369142,
                "customer": "cus_00000000000000",
                "days_until_due": None,
                "default_payment_method": None,
                "default_source": None,
                "default_tax_rates": [
                ],
                "discount": None,
                "ended_at": None,
                "items": {
                    "object": "list",
                    "data": [
                        {
                            "id": "si_00000000000000",
                            "object": "subscription_item",
                            "billing_thresholds": None,
                            "created": 1607369143,
                            "metadata": {
                            },
                            "price": {
                                "id": "price_00000000000000",
                                "object": "price",
                                "active": True,
                                "billing_scheme": "per_unit",
                                "created": 1607193083,
                                "currency": "eur",
                                "livemode": False,
                                "lookup_key": None,
                                "metadata": {
                                },
                                "nickname": None,
                                "product": "prod_00000000000000",
                                "recurring": {
                                    "aggregate_usage": None,
                                    "interval": "month",
                                    "interval_count": 1,
                                    "usage_type": "licensed"
                                },
                                "tiers_mode": None,
                                "transform_quantity": None,
                                "type": "recurring",
                                "unit_amount": 1000,
                                "unit_amount_decimal": "1000"
                            },
                            "quantity": 1,
                            "subscription": "sub_00000000000000",
                            "tax_rates": [
                            ]
                        }
                    ],
                    "has_more": False,
                    "url": "/v1/subscription_items?subscription=sub_IWt7lOlijKfkVv"
                },
                "latest_invoice": "in_1HvpL8EtUponlBUMA27JzrJc",
                "livemode": False,
                "metadata": {
                },
                "next_pending_invoice_item_invoice": None,
                "pause_collection": None,
                "pending_invoice_item_interval": None,
                "pending_setup_intent": None,
                "pending_update": None,
                "schedule": None,
                "start_date": 1607369142,
                "status": "active",
                "transfer_data": None,
                "trial_end": None,
                "trial_start": None
            },
            "previous_attributes": {
                "plan": {
                    "id": "OLD_00000000000000",
                    "object": "plan",
                    "active": True,
                    "aggregate_usage": None,
                    "amount": 10000,
                    "amount_decimal": "10000",
                    "billing_scheme": "per_unit",
                    "created": 1607193257,
                    "currency": "eur",
                    "interval": "year",
                    "interval_count": 1,
                    "livemode": False,
                    "metadata": {
                    },
                    "nickname": None,
                    "product": "prod_00000000000000",
                    "tiers_mode": None,
                    "transform_usage": None,
                    "trial_period_days": None,
                    "usage_type": "licensed",
                    "name": "Old plan"
                }
            }
        }
    }

    @classmethod
    def subscription_created(cls):
        response = client.post(
            f'/webhook', cls.req_body, format='json')

        assert response.status_code == 200

    @classmethod
    def subscription_updated(cls):
        req_updated = copy.deepcopy(cls.req_body)
        req_updated['type'] = 'customer.subscription.updated'
        response = client.post(
            f'/webhook', cls.req_body, format='json')

        assert response.status_code == 200


PaymentDetailsTest.success()
PaymentDetailsTest.failure()
DefaultPaymentTest.success()
DefaultPaymentTest.failure()
SubscriptionTest.success()
SubscriptionTest.failure()
