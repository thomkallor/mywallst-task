from django.urls import reverse

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
        self.pay_url = reverse('newpayment', kwargs={'user_id': admin.id})

    def test_success(self):

        global payment_id

        response = client.post(self.pay_url, self.req_body, format='json')

        payment_id = json.loads(
            response.content.decode('utf-8')).get('stripe_id')

        self.assertEqual(201, response.status_code)

    def test_faliure(self):

        req_fail = copy.deepcopy(self.req_body)
        req_fail['card'] = None
        response = client.post(self.pay_url, req_fail, format='json')

        assert response.status_code == 400


class DefaultPaymentTest(APITestCase):

    def setUp(self):

        # create a payment method

        pay_url = reverse('newpayment', kwargs={'user_id': admin.id})
        response = client.post(pay_url, pay_req, format='json')

        payment_id = json.loads(
            response.content.decode('utf-8')).get('stripe_id')

        self.success_url = reverse('defaultpayment', kwargs={
                                   'user_id': admin.id, 'method_id': payment_id})
        self.fail_url = reverse('defaultpayment', kwargs={
                                'user_id': admin.id, 'method_id': '01'})

    def test_success(self):

        response = client.put(self.success_url, format='json')

        self.assertEqual(200, response.status_code)

    def test_failure(self):

        response = client.put(self.fail_url, format='json')

        self.assertEqual(404, response.status_code)


class SubscriptionTest(APITestCase):

    def setUp(self):

        pay_url = reverse('newpayment', kwargs={'user_id': admin.id})

        # create a payment method

        response = client.post(pay_url, pay_req, format='json')

        payment_id = json.loads(
            response.content.decode('utf-8')).get('stripe_id')

        self.success_url = reverse('newsubscription', kwargs={
                                   'user_id': admin.id, 'method_id': payment_id})
        self.fail_url = reverse('newsubscription', kwargs={
                                'user_id': admin.id, 'method_id': '01'})

        self.req_body = sub_req

    def test_success(self):

        response = client.post(self.success_url, self.req_body, format='json')

        subscription_id = json.loads(
            response.content.decode('utf-8')).get('stripe_id')

        self.assertEqual(201, response.status_code)

    def test_failure(self):

        response = client.post(self.fail_url, self.req_body, format='json')

        self.assertEqual(404, response.status_code)


class WebHookTest(APITestCase):

    def setUp(self):

        pay_url = reverse('newpayment', kwargs={'user_id': admin.id})

        # create a payment method

        response = client.post(pay_url, pay_req, format='json')

        payment_id = json.loads(
            response.content.decode('utf-8')).get('stripe_id')

        # create a subscription
        sub_url = reverse('newsubscription', kwargs={
            'user_id': admin.id, 'method_id': payment_id})

        response = client.post(sub_url, sub_req, format='json')

        subscription_id = json.loads(
            response.content.decode('utf-8')).get('stripe_id')

        self.url = reverse('webhook')

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

        response = client.post(self.url, self.req_body, format='json')

        self.assertEqual(200, response.status_code)

    def subscription_updated(self):

        req_updated = copy.deepcopy(self.req_body)
        req_updated['type'] = 'customer.subscription.updated'

        response = client.post(self.url, self.req_body, format='json')

        self.assertEqual(200, response.status_code)
