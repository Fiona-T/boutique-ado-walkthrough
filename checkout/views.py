"""views for checkout app"""
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings

import stripe

from bag.contexts import bag_contents
from products.models import Product
from .forms import OrderForm
from .models import OrderLineItem, Order


def checkout(request):
    """checkout form"""
    # stripe public and private keys - env variables
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        bag = request.session.get('bag', {})
        # form data done manually so as to leave out the save info box
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        # create instance of OrderForm with the above data
        order_form = OrderForm(form_data)
        # if the form is valid, save it, then iterate over items to create lineitem
        if order_form.is_valid():
            order = order_form.save()
            for item_id, item_data in bag.items():
                try:
                    # get the product
                    product = Product.objects.get(id=item_id)
                    # if the item_data is an integer, this is an item without
                    # sizes (item_data is quantity)
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
                # if product not found - should not happen
                except Product.DoesNotExist:
                    # add error msg, delete the empty order, return to bag page
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our "
                        "database. Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))
            # attach whether or not the user wanted to save their info - to the session
            request.session['save_info'] = 'save_info' in request.POST
            # return to success url, with order number passed to it
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')
    else:
        # get request - bag items and empty order form
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


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    # check if user wanted to save info - get from session - will use later
    # this was added to session in post part of checkout view
    save_info = request.session.get('save_info')
    # get the order using the order number
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')
    # delete the shopping bag from session
    if 'bag' in request.session:
        del request.session['bag']
    # template and context to be used
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }
    # render it
    return render(request, template, context)
