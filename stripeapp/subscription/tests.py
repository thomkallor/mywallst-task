from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate

from stripeapp.subscription.models import User
from stripeapp.subscription.views import CustomerDefaultPayment, PaymentDetails, SubscriptionDetails, WebHook
from stripeapp.subscription.testmocks import pay_req, sub_req

import copy
import json

admin = User.objects.get(username='admin')
client = APIClient()
# force the authentication of users
client.force_authenticate(user=admin)


class PaymentDetailsTest(APITestCase):

    def setUp(self):

        self.req_body = pay_req

    def test_success(self):

        global payment_id

        response = client.post(
            f'/paymentmethod/{admin.id}', self.req_body, format='json')

        payment_id = json.loads(
            response.content.decode('utf-8')).get('stripe_id')

        self.assertEqual(201, response.status_code)

    def test_faliure(self):

        req_fail = copy.deepcopy(self.req_body)
        req_fail['card'] = None
        response = client.post(
            f'/paymentmethod/{admin.id}', req_fail, format='json')

        assert response.status_code == 400


class DefaultPaymentTest(APITestCase):

    def setUp(self):

        # create a payment method

        response = client.post(
            f'/paymentmethod/{admin.id}', pay_req, format='json')

        self.payment_id = json.loads(
            response.content.decode('utf-8')).get('stripe_id')

    def test_success(self):

        response = client.put(
            f'/customer/{admin.id}/{self.payment_id}', format='json')

        self.assertEqual(200, response.status_code)

    def test_failure(self):

        response = client.put(
            f'/paymentmethod/{admin.id}/01', format='json')

        self.assertEqual(404, response.status_code)


class SubscriptionTest(APITestCase):

    def setUp(self):

        self.req_body = sub_req

        # create a payment method

        response = client.post(
            f'/paymentmethod/{admin.id}', pay_req, format='json')

        self.payment_id = json.loads(
            response.content.decode('utf-8')).get('stripe_id')

    def test_success(self):

        response = client.post(
            f'/subscription/{admin.id}/{self.payment_id}', self.req_body, format='json')

        subscription_id = json.loads(
            response.content.decode('utf-8')).get('stripe_id')

        self.assertEqual(201, response.status_code)

    def test_failure(self):

        response = client.post(
            f'/subscription/{admin.id}/01', self.req_body, format='json')

        self.assertEqual(404, response.status_code)


class WebHookTest(APITestCase):

    def setUp(self):

        # create a payment method

        response = client.post(
            f'/paymentmethod/{admin.id}', pay_req, format='json')

        payment_id = json.loads(
            response.content.decode('utf-8')).get('stripe_id')

        # create a subscription

        response = client.post(
            f'/subscription/{admin.id}/{payment_id}', sub_req, format='json')

        subscription_id = json.loads(
            response.content.decode('utf-8')).get('stripe_id')

        self.req_body = {
            "id": "evt_00000000000000",
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": subscription_id,
                    "status": "active"
                }
            }

        }

    def subscription_created(self):

        response = client.post(
            f'/webhook', self.req_body, format='json')

        self.assertEqual(200, response.status_code)

    def subscription_updated(self):

        req_updated = copy.deepcopy(self.req_body)
        req_updated['type'] = 'customer.subscription.updated'

        response = client.post(
            f'/webhook', self.req_body, format='json')

        self.assertEqual(200, response.status_code)
