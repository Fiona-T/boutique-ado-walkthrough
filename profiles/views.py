from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from checkout.models import Order
from .models import UserProfile
from .forms import UserProfileForm


@login_required
def profile(request):
    """profile page - display user profile"""
    profile = get_object_or_404(UserProfile, user=request.user)

    # if request method is post, create instance of form with post data
    if request.method == 'POST':
        # tell it instance we are updating with the data is the profile from above
        form = UserProfileForm(request.POST, instance=profile)
        # if form valid, save it and send success msg
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Update failed. Please ensure form is valid.')
    else:
        form = UserProfileForm(instance=profile)
    orders = profile.orders.all()

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True,
    }

    return render(request, template, context)


def order_history(request, order_number):
    """
    order history view
    """
    # get order
    order = get_object_or_404(Order, order_number=order_number)
    # so user knows they are looking at a past order confirmation
    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))
    # using the checkout success template (re-using it as layout works for this)
    template = 'checkout/checkout_success.html'
    # from profile variable so will know if coming from order history view
    context = {
        'order': order,
        'from_profile': True,
    }

    return render(request, template, context)
