# signals are sent after (post) a model is saved or deleted
from django.db.models.signals import post_save, post_delete
# to rececive the signals
from django.dispatch import receiver
# we are listening for signals from the below model
from .models import OrderLineItem


@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    Handles signals from the post_save event
    Update order total on lineitem update/create
    """
    # sender is the sender of the signal - OrderLineItem
    # instance is instance of the model that sent it
    # created is Boolean sent by Django - new instance or an instance being updated
    # call the update_total method (from the model) on the instance of the order
    # that this line item is related to
    instance.order.update_total()

@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    """
    Handles signals from the post_delete event
    Update order total on lineitem delete
    """
    # sender is the sender of the signal - OrderLineItem
    # instance is instance of the model that sent it
    # no created parameter this time as it is not sent by this signal
    # call the update_total method (from the model) on the instance of the order
    # that this line item is related to
    instance.order.update_total()
