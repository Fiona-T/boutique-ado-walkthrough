"""custom template filter for subtotal"""
from django import template

# variable register which is an instance of template.library
register = template.Library()


# add the decorator to register the function as a template filter
@register.filter(name='calc_subtotal')
def calc_subtotal(price, quantity):
    """take price and quantity and return the product of the two"""
    return price * quantity
