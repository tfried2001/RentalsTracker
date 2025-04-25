# /workspaces/python/rent_tracker/rentals/signals.py
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User # Assuming standard User model

from .models import LLC, Property, Tenant, Payment
from .middleware import get_current_user # Import the function to get the user

# Get an instance of a logger (we'll configure this in settings.py)
action_logger = logging.getLogger('rentals.actions')

# List of models we want to log actions for
LOGGED_MODELS = [LLC, Property, Tenant, Payment]

@receiver(post_save)
def log_post_save(sender, instance, created, **kwargs):
    """
    Logs when an instance of a tracked model is saved (created or updated).
    """
    if sender in LOGGED_MODELS:
        user = get_current_user()
        user_str = str(user) if user and user.is_authenticated else "System/Unknown"

        action = "Added" if created else "Changed"

        # Log the action
        action_logger.info(
            f"User '{user_str}' {action} {sender.__name__}: '{str(instance)}' (ID: {instance.pk})"
        )
        # You could add more details here if needed, like changed fields (more complex)

@receiver(post_delete)
def log_post_delete(sender, instance, **kwargs):
    """
    Logs when an instance of a tracked model is deleted.
    """
    if sender in LOGGED_MODELS:
        user = get_current_user()
        user_str = str(user) if user and user.is_authenticated else "System/Unknown"

        # Log the action
        action_logger.info(
            f"User '{user_str}' Deleted {sender.__name__}: '{str(instance)}' (ID: {instance.pk})"
        )