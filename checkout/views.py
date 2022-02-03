from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import OrderForm


def checkout(request):
    # get bag from session
    bag = request.session.get('bag', {})
    # if nothing in bag, error message and redirect to products page
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))
    # empty instance of orderform
    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51KP8RIJcyb9kw8knJ00106H7hMXWjhFXBnCGXazewELzdZsmAHfLgvpKGBOPaKNeFtMv4hmLy4K7tDW7Z1SgotPb00BoS7eNQa',
        'client_secret': 'test client secret',
    }

    return render(request, template, context)
