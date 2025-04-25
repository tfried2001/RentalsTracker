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
    path('llcs/', views.llc_list, name='llc_list'),
    path('properties/', views.property_list, name='property_list'),
]
