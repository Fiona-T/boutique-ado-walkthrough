"""views for checkout app"""
import json
from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

import stripe

from bag.contexts import bag_contents
from products.models import Product
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from .forms import OrderForm
from .models import OrderLineItem, Order


@require_POST
def cache_checkout_data(request):
    """
    for the save info check box
    Before calling confirmCardPayment in js, make a post request to this view
    Give it the client secret from payment intent, modify payment intent
    """
    try:
        # first part of client secret is the payment intent id
        pid = request.POST.get('client_secret').split('_secret')[0]
        # give stripe the secret key, so we can modify the payment intent
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # call the PaymentIntent.modify, give it pid and info we want to modify
        stripe.PaymentIntent.modify(pid, metadata={
            # json dump of shopping bag contents - required later
            'bag': json.dumps(request.session.get('bag', {})),
            # whether or not the user wanted to save their info
            'save_info': request.POST.get('save_info'),
            # the user
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


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
            order = order_form.save(commit=False)
            # get the payment intent id and the bag, add them to the order details
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()
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
            request.session['save_info'] = 'save-info' in request.POST
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
        # generate order form - either prefilled or empty:
        # Attempt to prefill the form with any info the user maintains in their profile
        if request.user.is_authenticated:
            try:
                # get their profile
                profile = UserProfile.objects.get(user=request.user)
                # set the initial values on the form, with values from account + profile
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                    'town_or_city': profile.default_town_or_city,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'county': profile.default_county,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            # empty instance of orderform if user not logged in
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
    Handle successful checkouts + attach user profile to order
    so that it appears in their order history
    """
    # check if user wanted to save info - get from session - will use later
    # this was added to session in post part of checkout view
    save_info = request.session.get('save_info')
    print(save_info)
    # get the order using the order number
    order = get_object_or_404(Order, order_number=order_number)
    # if the user is logged in, then we want to attach the user to the order
    # and also check if they want their delivery info saved to their profile
    if request.user.is_authenticated:
        print('authenticated user')
        # get the user's profile
        profile = UserProfile.objects.get(user=request.user)
        # Attach it to the order
        order.user_profile = profile
        order.save()

        # if user ticked the save info box
        if save_info:
            print('saving info')
            # get the data to save into the user's profile
            # keys of this dict match the fields on userprofile model
            profile_data = {
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }
            # create instance of userprofileform, using the above data
            # and telling it to update profile variable from above
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

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
