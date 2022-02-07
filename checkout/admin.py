from django.contrib import admin
from .models import Order, OrderLineItem


class OrderLineItemAdminInline(admin.TabularInline):
    """
    This means the line items will be in the relevant Order
    - can be added/edited there instead of going to separate
    OderLineItem section
    """
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)


class OrderAdmin(admin.ModelAdmin):
    """admin set up for Order model"""
    inlines = (OrderLineItemAdminInline,)
    readonly_fields = (
        'order_number', 'date', 'delivery_cost', 'order_total', 'grand_total',
        'original_bag', 'stripe_pid',
        )
    # specifiying the fields so that the order of fields can be set
    # as the order would be adjusted because of the read only fields
    # order of fields same as they appear in the model
    fields = ('order_number', 'date', 'full_name',
              'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'delivery_cost',
              'order_total', 'grand_total','original_bag', 'stripe_pid',)
    # fields that will show up in the list view
    list_display = ('order_number', 'date', 'full_name',
                    'order_total', 'delivery_cost',
                    'grand_total',)
    # recent orders at top - reverse chronological order
    ordering = ('-date',)


# no need to register OrderLineItem as it is an inline in OrderAdmin
admin.site.register(Order, OrderAdmin)
