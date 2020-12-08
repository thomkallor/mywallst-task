from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated

from stripeapp.subscription.serializers import CustomerRequestSerializer, PaymentMethodRequestSerializer, PaymentMethodSerializer, SubscriptionSerializer, SubscriptionRequestSerializer
from stripeapp.subscription.models import PaymentMethod, Subscription, User
from stripeapp.subscription.permissions import IsSameUser
from stripeapp.config import STRIPE_API_KEY

from datetime import datetime
import json
import stripe

from drf_yasg.utils import swagger_auto_schema, no_body
from drf_yasg import openapi

stripe.api_key = STRIPE_API_KEY


class WebHook(GenericAPIView):

    def get_serializer(self):
        pass

    def update_status(self, id, status):

        subscription = Subscription.objects.get(stripe_id=id)
        subscription.status = status
        subscription.save()

    def post(self, request):
        """
            Web hoook that handles subscription created and updated event.
        """
        payload = request.body
        event = None

        try:
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
        except ValueError as e:
            # Invalid payload
            return Response(status=400)

        # Handle the event
        if event.type == 'customer.subscription.created':

            subscription = event.data.object  # contains a stripe.PaymentIntent
            # Then define and call a method to handle the successful payment intent.
            # handle_payment_intent_succeeded(payment_intent)

            try:
                self.update_status(subscription.get(
                    'id'), subscription.get('status'))
            except:
                return Response(status=400)

        elif event.type == 'customer.subscription.updated':

            subscription = event.data.object  # contains a stripe.PaymentMethod
            # Then define and call a method to handle the successful attachment of a PaymentMethod.
            # handle_payment_method_attached(payment_method)
        # ... handle other event types
            try:
                self.update_status(subscription.get(
                    'id'), subscription.get('status'))
            except:
                return Response(status=400)

        else:
            print('Unhandled event type {}'.format(event.type))

        return Response(status=200)


class PaymentDetails(CreateAPIView):

    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated, IsSameUser]

    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @swagger_auto_schema(request_body=PaymentMethodRequestSerializer, responses={'200': PaymentMethodSerializer})
    def post(self, request, user_id):
        """
            Creates new payment method for a customer.
            When the user creates a payment method for the first time it create a new customer in stripe and makes the card default.
        """
        req_serializer = PaymentMethodRequestSerializer(data=request.data)
        if(req_serializer.is_valid()):

            try:
                user = self.get_user(user_id)

            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            try:

                # create the payment method and update in database

                payment_method = stripe.PaymentMethod.create(
                    **req_serializer.validated_data)
                method_id = payment_method.get('id')
                holder_name = payment_method.get('billing_details').get(
                    'name') if payment_method.get('billing_details') else None
                last4 = payment_method.get('card').get(
                    'last4') if payment_method.get('card') else None
                brand = payment_method.get('card').get(
                    'brand') if payment_method.get('card') else None
                is_default = False
                cust_id = user.stripe_id
                _type = payment_method.get('type')

                # if there is no customer create one
                # And make the payment method default
                if(not cust_id or cust_id == ''):
                    full_name = user.first_name + ' ' + user.last_name
                    stripe_cust = {'name': full_name, 'email': user.email, 'payment_method': method_id,
                                   'invoice_settings': {'default_payment_method': method_id}}
                    created_cust = stripe.Customer.create(**stripe_cust)
                    user.stripe_id = created_cust.get('id')
                    is_default = True
                    user.save()
                    cust_id = created_cust.get('id')

                # update the payment method with the customer_id

                stripe.PaymentMethod.attach(
                    method_id, customer=cust_id)

                data = {'stripe_id': method_id, 'holder_name': holder_name,
                        'last4': last4, 'brand': brand, 'user': user.id, 'type': _type, 'is_default': is_default}

                # save payment method in database
                payment_details = self.get_serializer(data=data)
                if(payment_details.is_valid()):
                    payment_details.save()

                    return Response(payment_details.data, status=status.HTTP_201_CREATED)

                return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            except Exception as err:
                exception_type = type(err).__name__
                body = {'error': exception_type}
                return Response(body, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDefaultPayment(GenericAPIView):

    permission_classes = [IsAuthenticated, IsSameUser]
    serializer_class = PaymentMethodSerializer

    def get_method(self, user_id, method_id):
        return PaymentMethod.objects.select_related('user').get(stripe_id=method_id, user_id=user_id)

    @swagger_auto_schema(request_body=no_body)
    def put(self, request, user_id, method_id):
        """
            Updates the default payment method for a customer.
        """

        try:
            # check if method belongs to user
            method = self.get_method(user_id, method_id)

        except PaymentMethod.DoesNotExist:
            return Response({'error': 'Payment method not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            user = method.user

            # Update default payment method
            stripe.Customer.modify(user.stripe_id, invoice_settings={
                                   'default_payment_method': method.stripe_id})

            if(method.is_default):
                return Response('No changes.', status=status.HTTP_200_OK)

            method.is_default = True
            method.save()
            method_serializer = self.get_serializer(method)
            return Response(method_serializer.data, status=status.HTTP_200_OK)

        except Exception as err:
            exception_type = type(err).__name__
            body = {'error': exception_type}
            return Response(body, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionDetails(CreateAPIView):

    permission_classes = [IsAuthenticated, IsSameUser]
    serializer_class = SubscriptionSerializer

    def get_method(self, user_id, method_id):
        return PaymentMethod.objects.select_related('user').get(stripe_id=method_id, user_id=user_id)

    @swagger_auto_schema(request_body=SubscriptionRequestSerializer)
    def post(self, request, user_id, method_id):
        """
            Create a new subscription for a customer.
        """

        try:
            # check if method belongs to user
            method = self.get_method(user_id, method_id)

        except PaymentMethod.DoesNotExist:
            return Response({'error': 'Payment method not found.'}, status=status.HTTP_404_NOT_FOUND)

        req_serializer = SubscriptionRequestSerializer(data=request.data)

        if(req_serializer.is_valid()):

            try:
                price_id = req_serializer.validated_data.get('price_id')
                created_sub = stripe.Subscription.create(
                    customer=method.user.stripe_id, items=[{"price": price_id}])
                subscription = {'stripe_id': created_sub.get('id'),
                                'payment_method': method_id, 'price_id': price_id, 'status': 'pending',
                                'start': datetime.fromtimestamp(created_sub.get('current_period_start')),
                                'end': datetime.fromtimestamp(created_sub.get('current_period_end'))}

                sub_serializer = self.get_serializer(data=subscription)
                if(sub_serializer.is_valid()):
                    sub_serializer.save()
                    return Response(sub_serializer.data, status=status.HTTP_201_CREATED)

                return Response(sub_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as err:
                exception_type = type(err).__name__
                body = {'error': exception_type}
                return Response(body, status=status.HTTP_400_BAD_REQUEST)

        return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
