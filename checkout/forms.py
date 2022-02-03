from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    """Checkout form"""
    class Meta:
        """only the fields that are not being set automatically"""
        model = Order
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'town_or_city', 'postcode', 'country',
                  'county',)

    def __init__(self, *args, **kwargs):
        """
        override init method
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        # call default init method to set it up as it would be
        super().__init__(*args, **kwargs)
        # then make the adjustments - placeholders instead of labels
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'country': 'Country',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County',
        }
        # autofocus on the first field
        self.fields['full_name'].widget.attrs['autofocus'] = True
        # iterate through the fields to make the updates:
        for field in self.fields:
            # add an asterisk to the required fields placeholder text
            if self.fields[field].required:
                placeholder = f'{placeholders[field]} *'
            else:
                placeholder = placeholders[field]
            # set the placeholder attributes
            self.fields[field].widget.attrs['placeholder'] = placeholder
            # add css class
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            # remove the field labels
            self.fields[field].label = False
