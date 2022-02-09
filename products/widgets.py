from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _


class CustomClearableFileInput(ClearableFileInput):
    """inherit django ClearableFileInput and make some overrides"""
    # put new values for the checkbox label, initial text and input text
    clear_checkbox_label = _('Remove')
    initial_text = _('Current Image')
    input_text = _('')
    # use our own template
    template_name = 'products/custom_widget_templates/custom_clearable_file_input.html'
