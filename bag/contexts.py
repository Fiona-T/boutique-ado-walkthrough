from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product


def bag_contents(request):
    """
    context processor
    return context dictionary which will be available to all templates
    """
    bag_items = []
    total = 0
    product_count = 0
    # get the bag session variable if it exists, or initialise empty dictionary for it if not there
    bag = request.session.get('bag', {})

    # for each item and quantity in session variable bag dict items
    for item_id, quantity in bag.items():
        # get the product from Product table using id of item
        product = get_object_or_404(Product, pk=item_id)
        # multiply its price by quantity and add this to total variable
        total += quantity * product.price
        # increase product_count varibale by the quantity
        product_count += quantity
        # add the below dictionary to bag_items list
        # item id, quantity, and the product object (so that other attributes of product will be available in template)
        bag_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'product': product,
        })



    if total < settings.FREE_DELIVERY_THRESHOLD:
        # calc delivery cost if total is less than free delivery amt
        # using decimal instead of float to avoid rounding issues with float
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        # how much more the customer would have to spend for free delivery
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0

    grand_total = total + delivery

    # context which can be used in every template in all apps across the project
    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context
