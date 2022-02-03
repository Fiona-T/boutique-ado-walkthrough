import uuid
from django.db import models
from django.db.models import Sum
from django.conf import settings
from products.models import Product


class Order(models.Model):
    """Order as a whole"""
    # order number not editable - unique and permanent number
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = models.CharField(max_length=40, null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)  # not required
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)  # not required
    date = models.DateTimeField(auto_now_add=True)  # set order date and time
    # below three will be calculated when order saved, using a model method
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)

    def _generate_order_number(self):
        """
        Private method, only used inside this class (_ denotes this)
        Generate a random unique string of 32 chars using UUID
        Will be used as an order number
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        # Sum function across all lineitem_total fields - in lineitem_total__sum
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum']
        # then calculate the deliverly costs
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        else:
            self.delivery_cost = 0
        # grand total is the order total + delivery costs - save the instance then
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        # then execute the original save method
        super().save(*args, **kwargs)

    def __str__(self):
        """string method - return order number"""
        return self.order_number


class OrderLineItem(models.Model):
    """
    Individual shopping bag item
    After Order instance is created, iterate through the shopping bag, create
    order line item for each item, and attach these to the Order
    Doing this, update the three items above at the same time
    """
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)
    product_size = models.CharField(max_length=2, null=True, blank=True) # XS, S, M, L, XL, blank if no sizes
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem_total
        and update the order total.
        """
        # set the total for each line item to product price by quantity
        self.lineitem_total = self.product.price * self.quantity
        # then execute the original save method
        super().save(*args, **kwargs)

    def __str__(self):
        """string method - return sku plus order number"""
        return f'SKU {self.product.sku} on order {self.order.order_number}'
