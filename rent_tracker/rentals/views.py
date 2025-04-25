from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required # Import login_required
from .models import LLC, Property # Import the LLC model

# Public homepage view
def home(request):
    # You can pass context data to the template if needed
    context = {
        'message': "Welcome to RentTracker!"
    }
    return render(request, 'home.html', context)

# Example view that requires login
@login_required
@permission_required('rentals.view_llc', login_url='/login/', raise_exception=True)
def dashboard(request):
    # This view can only be accessed by logged-in users
    # You would typically fetch user-specific data here

    # Fetch all LLCs to pass to the template
    llcs = LLC.objects.all().order_by('name')

    context = {
        'user_first_name': request.user.first_name or request.user.username,
        'llcs': llcs, # <-- Add llcs to the context
    }
    return render(request, 'rentals/dashboard.html', context)

@login_required # Protect this view
@permission_required('rentals.view_llc', login_url='/login/', raise_exception=True)
def llc_list(request):
    """Displays a list of all LLCs and their filing status."""
    llcs = LLC.objects.all().order_by('name') # Get all LLCs, ordered by name
    context = {
        'llcs': llcs,
    }
    return render(request, 'rentals/llc_list.html', context)

@login_required # Protect this view
@permission_required('rentals.view_property', login_url='/login/', raise_exception=True)
def property_list(request):
    """Displays a list of all properties."""
    properties = Property.objects.all().order_by('llc', 'street_number', 'street_name') # Get all properties, ordered by LLC, address
    context = {
        'properties': properties,
    }
    return render(request, 'rentals/property_list.html', context)


# Add views for LLCs, Properties, Tenants, Payments later
# Example for adding a property (you'll need a form and template later)
# @login_required
# @permission_required('rentals.add_property', login_url='/login/', raise_exception=True)
# def property_add(request):
#     # ... view logic for adding a property ...
#     pass

# Example for editing a property
# @login_required
# @permission_required('rentals.change_property', login_url='/login/', raise_exception=True)
# def property_edit(request, property_id):
#     # ... view logic for editing a specific property ...
#     pass

# Example for deleting a property
# @login_required
# @permission_required('rentals.delete_property', login_url='/login/', raise_exception=True)
# def property_delete(request, property_id):
#     # ... view logic for deleting a specific property ...
#     pass