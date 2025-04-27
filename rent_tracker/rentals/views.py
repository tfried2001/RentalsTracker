from django.shortcuts import render, redirect, get_object_or_404 # Import redirect
from django.contrib.auth.decorators import login_required, permission_required # Import login_required
from django.db import IntegrityError, transaction # For handling potential errors
from django.db.models import ProtectedError # To handle deletion protection

from .models import LLC, Property # Import the LLC model
from .forms import LLCForm, PropertyForm, TenantForm, PaymentForm # Import the forms

# Public homepage view
def home(request):
    # You can pass context data to the template if needed
    context = {
        'message': "Welcome to RentTracker!"
    }
    return render(request, 'home.html', context)

@login_required
def dashboard(request):
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

@login_required
@permission_required('rentals.view_tenant', login_url='/login/', raise_exception=True)
def tenant_list(request):
    tenants = Tenant.objects.all().order_by('last_name', 'first_name')
    context = {'tenants': tenants}
    return render(request, 'rentals/tenant_list.html', context)

@login_required
@permission_required('rentals.view_payment', login_url='/login/', raise_exception=True)
def payment_list(request):
    payments = Payment.objects.select_related('tenant', 'property').all().order_by('-payment_date')
    context = {'payments': payments}
    return render(request, 'rentals/payment_list.html', context)



# --- LLC CRUD Views ---
@login_required
@permission_required('rentals.add_llc', login_url='/login/', raise_exception=True)
def llc_add(request):
    if request.method == 'POST':
        form = LLCForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"LLC '{form.cleaned_data['name']}' added successfully.")
                return redirect('rentals:llc_list')
            except IntegrityError: # Handle potential unique constraint errors
                 messages.error(request, "An LLC with this name already exists.")
            except Exception as e:
                 messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = LLCForm()
    context = {'form': form, 'form_title': 'Add New LLC'}
    return render(request, 'rentals/generic_form.html', context)

@login_required
@permission_required('rentals.change_llc', login_url='/login/', raise_exception=True)
def llc_edit(request, pk):
    llc = get_object_or_404(LLC, pk=pk)
    if request.method == 'POST':
        form = LLCForm(request.POST, instance=llc)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"LLC '{llc.name}' updated successfully.")
                return redirect('rentals:llc_list')
            except IntegrityError:
                 messages.error(request, "An LLC with this name already exists.")
            except Exception as e:
                 messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = LLCForm(instance=llc)
    context = {'form': form, 'form_title': f'Edit LLC: {llc.name}', 'instance': llc}
    return render(request, 'rentals/generic_form.html', context)

@login_required
@permission_required('rentals.delete_llc', login_url='/login/', raise_exception=True)
def llc_delete(request, pk):
    llc = get_object_or_404(LLC, pk=pk)
    if request.method == 'POST':
        try:
            llc_name = llc.name # Get name before deleting
            llc.delete()
            messages.success(request, f"LLC '{llc_name}' deleted successfully.")
            return redirect('rentals:llc_list')
        except ProtectedError:
            messages.error(request, f"Cannot delete LLC '{llc.name}' because it still owns properties. Please reassign or delete the properties first.")
            return redirect('rentals:llc_list') # Or redirect to llc detail page
        except Exception as e:
            messages.error(request, f"An error occurred while deleting: {e}")
            return redirect('rentals:llc_list')
    context = {'object': llc, 'object_type': 'LLC'}
    return render(request, 'rentals/generic_confirm_delete.html', context)


# --- Property CRUD Views ---
@login_required
@permission_required('rentals.add_property', login_url='/login/', raise_exception=True)
def property_add(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Property '{form.instance}' added successfully.")
                return redirect('rentals:property_list')
            except IntegrityError as e:
                 messages.error(request, f"Could not add property. Check for duplicate VIN or other constraints. Error: {e}")
            except Exception as e:
                 messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = PropertyForm()
    context = {'form': form, 'form_title': 'Add New Property'}
    return render(request, 'rentals/generic_form.html', context)

@login_required
@permission_required('rentals.change_property', login_url='/login/', raise_exception=True)
def property_edit(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=prop)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Property '{prop}' updated successfully.")
                return redirect('rentals:property_list')
            except IntegrityError as e:
                 messages.error(request, f"Could not update property. Check for duplicate VIN or other constraints. Error: {e}")
            except Exception as e:
                 messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = PropertyForm(instance=prop)
    context = {'form': form, 'form_title': f'Edit Property: {prop}', 'instance': prop}
    return render(request, 'rentals/generic_form.html', context)

@login_required
@permission_required('rentals.delete_property', login_url='/login/', raise_exception=True)
def property_delete(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        try:
            prop_str = str(prop)
            prop.delete()
            messages.success(request, f"Property '{prop_str}' deleted successfully.")
            return redirect('rentals:property_list')
        except ProtectedError:
            messages.error(request, f"Cannot delete Property '{prop}' because it has related Tenants or Payments. Please reassign or delete them first.")
            return redirect('rentals:property_list')
        except Exception as e:
            messages.error(request, f"An error occurred while deleting: {e}")
            return redirect('rentals:property_list')
    context = {'object': prop, 'object_type': 'Property'}
    return render(request, 'rentals/generic_confirm_delete.html', context)


# --- Tenant CRUD Views ---
@login_required
@permission_required('rentals.add_tenant', login_url='/login/', raise_exception=True)
def tenant_add(request):
    if request.method == 'POST':
        form = TenantForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Tenant '{form.instance}' added successfully.")
                return redirect('rentals:tenant_list')
            except Exception as e:
                 messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = TenantForm()
    context = {'form': form, 'form_title': 'Add New Tenant'}
    return render(request, 'rentals/generic_form.html', context)

@login_required
@permission_required('rentals.change_tenant', login_url='/login/', raise_exception=True)
def tenant_edit(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk)
    if request.method == 'POST':
        form = TenantForm(request.POST, instance=tenant)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Tenant '{tenant}' updated successfully.")
                return redirect('rentals:tenant_list')
            except Exception as e:
                 messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = TenantForm(instance=tenant)
    context = {'form': form, 'form_title': f'Edit Tenant: {tenant}', 'instance': tenant}
    return render(request, 'rentals/generic_form.html', context)

@login_required
@permission_required('rentals.delete_tenant', login_url='/login/', raise_exception=True)
def tenant_delete(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk)
    if request.method == 'POST':
        try:
            tenant_str = str(tenant)
            tenant.delete()
            messages.success(request, f"Tenant '{tenant_str}' deleted successfully.")
            return redirect('rentals:tenant_list')
        except ProtectedError:
            messages.error(request, f"Cannot delete Tenant '{tenant}' because they have related Payments. Please delete the payments first.")
            return redirect('rentals:tenant_list')
        except Exception as e:
            messages.error(request, f"An error occurred while deleting: {e}")
            return redirect('rentals:tenant_list')
    context = {'object': tenant, 'object_type': 'Tenant'}
    return render(request, 'rentals/generic_confirm_delete.html', context)


# --- Payment CRUD Views ---
@login_required
@permission_required('rentals.add_payment', login_url='/login/', raise_exception=True)
def payment_add(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Payment added successfully.")
                return redirect('rentals:payment_list')
            except Exception as e:
                 messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = PaymentForm()
    context = {'form': form, 'form_title': 'Add New Payment'}
    return render(request, 'rentals/generic_form.html', context)

@login_required
@permission_required('rentals.change_payment', login_url='/login/', raise_exception=True)
def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Payment updated successfully.")
                return redirect('rentals:payment_list')
            except Exception as e:
                 messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = PaymentForm(instance=payment)
    context = {'form': form, 'form_title': f'Edit Payment: {payment}', 'instance': payment}
    return render(request, 'rentals/generic_form.html', context)

@login_required
@permission_required('rentals.delete_payment', login_url='/login/', raise_exception=True)
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        try:
            payment_str = str(payment)
            payment.delete()
            messages.success(request, f"Payment '{payment_str}' deleted successfully.")
            return redirect('rentals:payment_list')
        # No ProtectedError expected here based on current models, but keep general exception handling
        except Exception as e:
            messages.error(request, f"An error occurred while deleting: {e}")
            return redirect('rentals:payment_list')
    context = {'object': payment, 'object_type': 'Payment'}
    return render(request, 'rentals/generic_confirm_delete.html', context)


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