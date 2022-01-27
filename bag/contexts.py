from decimal import Decimal
from django.conf import settings


def bag_contents(request):
    """
    context processor
    return context dictionary which will be available to all templates
    """
    bag_items = []
    total = 0
    product_count = 0

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
