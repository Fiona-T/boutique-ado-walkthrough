"""for stripe webhooks"""
import json
import time
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from products.models import Product
from profiles.models import UserProfile
from .models import Order, OrderLineItem


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        """
        assign the request as an attribute
        so that attributes of the request from stripe can be accessed
        """
        # set up method, called every time an instance is created
        self.request = request
    
    def _send_confirmation_email(self, order):
        """Send the user a confirmation email. private method"""
        cust_email = order.email
        # 1st parameter is file to render, second is the context
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        # the default from email will be added to settings file
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})
        # use send mail function
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]  # list of emails we are sending to - only one in this case
        )

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        Take the event from stripe, return http response indicating
        it was received
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from stripe
        each time user completes the payment process
        """
        # payment intent from stripe saved in key event.data.object
        intent = event.data.object
        # create an order, in case the form isn't submitted for some reason
        # get the payment intent id
        pid = intent.id
        # get bag + save info boolean from the metadata added to the intent in cache view
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info
        # get the billing, shipping etc from intent data also
        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)

        # Clean data in the shipping details - replace empty with None
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # update the user profile if save info box was ticked
        profile = None
        # get username, if they're not anonymous then they're logged in
        username = intent.metadata.username
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)
            if save_info:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = shipping_details.address.line1
                profile.default_street_address2 = shipping_details.address.line2
                profile.default_county = shipping_details.address.state
                profile.save()

        # usually the form will be submitted and therefore the order created
        # so order already in db when we receive the webhook
        # check if the order exists, if it does, return response
        order_exists = False
        # allow for delays by using a while loop with 5 attempts
        attempt = 1
        while attempt <= 5:
            # try to get the order (iexact means exact but case insensitive)
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                # if the order is found, break out of loop (return status below)
                order_exists = True
                # break out of loop as order is found
                break
            # if it doesn't exist then we create the order here, using mostly the
            # same code as from the checkout view
            except Order.DoesNotExist:
                # if order doesn't exist, increment attempt, sleep for 1 second
                attempt += 1
                time.sleep(1)
        # outside the loop - if order exists, return 200 response to stripe with message
        if order_exists:
            # send confirmation email
            self._send_confirmation_email(order)
            return HttpResponse(
                    content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                    status=200)
        # otherwise, try to create the order
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for item_id, item_data in json.loads(bag).items():
                    # get the product
                    product = Product.objects.get(id=item_id)
                    # if the item_data is an integer, this is an item without sizes
                    if isinstance(item_data, int):
                        # create the lineitem
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        # if the item has sizes, then iterate through each size
                        for size, quantity in item_data['items_by_size'].items():
                            # and create each lineitem
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
            except Exception as error:
                # if anything goes wrong trying to create the order,delete it
                if order:
                    order.delete()
                # send 500 to stripe, means it will try the webhook again later
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {error}',
                    status=500)
        # order must have been created, at this point in code, return response to stripe
        # send confirmation email
        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
