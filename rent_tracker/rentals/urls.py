# rentals/urls.py
from django.urls import path
from . import views # Import views from the current directory

# Define an app name for namespacing (optional but good practice)
app_name = 'rentals'

urlpatterns = [
    # Map the root URL of the app ('/') to the home view
    path('', views.home, name='home'),
    # Add other app-specific URLs here later (e.g., for properties, tenants)
    path('dashboard/', views.dashboard, name='dashboard'), # Example protected view
    # LLC URLs
    path('llcs/', views.llc_list, name='llc_list'),
    path('llcs/add/', views.llc_add, name='llc_add'),
    path('llcs/<int:pk>/edit/', views.llc_edit, name='llc_edit'),
    path('llcs/<int:pk>/delete/', views.llc_delete, name='llc_delete'),

    # Property URLs
    path('properties/', views.property_list, name='property_list'),
    path('properties/add/', views.property_add, name='property_add'),
    path('properties/<int:pk>/edit/', views.property_edit, name='property_edit'),
    path('properties/<int:pk>/delete/', views.property_delete, name='property_delete'),

    # Tenant URLs
    path('tenants/', views.tenant_list, name='tenant_list'),
    path('tenants/add/', views.tenant_add, name='tenant_add'),
    path('tenants/<int:pk>/edit/', views.tenant_edit, name='tenant_edit'),
    path('tenants/<int:pk>/delete/', views.tenant_delete, name='tenant_delete'),

    # Payment URLs
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/add/', views.payment_add, name='payment_add'),
    path('payments/<int:pk>/edit/', views.payment_edit, name='payment_edit'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),
]
