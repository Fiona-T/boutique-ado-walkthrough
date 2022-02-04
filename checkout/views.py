"""views for checkout app"""
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

import stripe

from bag.contexts import bag_contents
from .forms import OrderForm


def checkout(request):
    """checkout form"""
    # stripe public and private keys - env variables
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # get bag from session
    bag = request.session.get('bag', {})
    # if nothing in bag, error message and redirect to products page
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))

    # get the bag contents from contexts.py, passing it the request
    current_bag = bag_contents(request)
    # get the grand_total key out of the returned dictionary
    total = current_bag['grand_total']
    # multiply by 100, round to 0 decimal places,as stripe requires an integer
    stripe_total = round(total * 100)
    # set the secret key on stripe
    stripe.api_key = stripe_secret_key
    # create the payment intent
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    # print(intent)

    # empty instance of orderform
    order_form = OrderForm()

    # message alert if public key not set
    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)
