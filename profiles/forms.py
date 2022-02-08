from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """Checkout form"""
    class Meta:
        """all fields but exclude user as that will not change"""
        model = UserProfile
        exclude = ('user',)

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
            'default_phone_number': 'Phone Number',
            'default_postcode': 'Postal Code',
            'default_town_or_city': 'Town or City',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_county': 'County, State or Locality',
        }
        # autofocus on the first field
        self.fields['default_phone_number'].widget.attrs['autofocus'] = True
        # iterate through the fields to make the updates:
        for field in self.fields:
            # not on country since this is a dropdown box with no placeholder
            if field != 'default_country':
                # add an asterisk to the required fields placeholder text
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                # set the placeholder attributes
                self.fields[field].widget.attrs['placeholder'] = placeholder
            # add css class
            self.fields[field].widget.attrs['class'] = 'border-black rounded-0 profile-form-input'
            # remove the field labels
            self.fields[field].label = False
