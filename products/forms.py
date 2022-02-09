from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    """product form for admin user to add product"""
    class Meta:
        """specify the model and the form"""
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """override init method to make changes to fields"""
        super().__init__(*args, **kwargs)
        # get all categories
        categories = Category.objects.all()
        # put their friendy names in a list
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]
        # update the category field in form to use the friendy names for the dropdown names
        self.fields['category'].choices = friendly_names
        # set class on the fields for css
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
