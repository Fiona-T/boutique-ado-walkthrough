"""for stripe webhooks"""
from django.http import HttpResponse


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        """
        assign the request as an attribute
        so that attributes of the request from stripe can be accessed
        """
        # set up method, called every time an instance is created
        self.request = request

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
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
