# /workspaces/python/rent_tracker/rentals/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from .models import LLC, Property, Tenant, Payment
from django.contrib.auth.models import User, Group, Permission # Assuming standard Django User model
from django.contrib.contenttypes.models import ContentType # For permissions

# Helper function to create a user for tests
def create_test_user(username='testuser', password='password', groups=None, permissions=None):
    user = User.objects.create_user(username=username, password=password)
    if groups:
        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
    if permissions:
        user.user_permissions.add(*permissions)
    return user

def get_permission(app_label, model_name, codename_prefix):
    content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    codename = f"{codename_prefix}_{model_name}"
    return Permission.objects.get(content_type=content_type, codename=codename)

class NavigationTest(TestCase):
    """Tests related to site navigation defined in base.html"""

    def setUp(self):
        """Set up common test resources"""
        self.client = Client()
        self.user = create_test_user()
        # We need a URL for the link to point to, even if the view doesn't exist yet.
        # Let's assume we'll name it 'property_list' in our urls.py
        self.properties_url = reverse('rentals:property_list') # <<< This will FAIL initially (NoReverseMatch)

    def test_properties_link_visible_when_logged_in(self):
        """Verify 'Properties' link is present for authenticated users."""
        self.client.login(username='testuser', password='password')
        # We can test any page that uses base.html, like the dashboard
        dashboard_url = reverse('rentals:dashboard')
        response = self.client.get(dashboard_url)
        self.assertEqual(response.status_code, 200)
        # Check if the link HTML is present in the response content
        # Use assertContains for checking substrings in HTML response
        self.assertContains(response, f'<a class="nav-link" href="{self.properties_url}">Properties</a>') # <<< This will FAIL initially

    def test_properties_link_not_visible_when_logged_out(self):
        """Verify 'Properties' link is NOT present for anonymous users."""
        # Access a page that uses base.html, like the home page
        home_url = reverse('rentals:home')
        response = self.client.get(home_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, f'<a class="nav-link" href="{self.properties_url}">Properties</a>') # <<< This might PASS initially if the URL doesn't resolve, but will FAIL correctly once the URL exists but the link isn't there.

class PropertyListViewTest(TestCase):
    """Tests for the Property List View"""

    def setUp(self):
        self.client = Client()
        self.user = create_test_user()
        self.properties_url = reverse('rentals:property_list') # <<< This will FAIL initially (NoReverseMatch)

    def test_property_list_view_requires_login(self):
        """Verify accessing the property list page redirects if not logged in."""
        response = self.client.get(self.properties_url)
        # Expect a redirect (302) to the login page
        login_url = reverse('login')
        self.assertRedirects(response, f'{login_url}?next={self.properties_url}') # <<< This will FAIL initially (404 or NoReverseMatch)

    def test_property_list_view_accessible_when_logged_in(self):
        """Verify logged-in users can access the property list page."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.properties_url)
        self.assertEqual(response.status_code, 200) # <<< This will FAIL initially (404 or NoReverseMatch)

    def test_property_list_view_uses_correct_template(self):
        """Verify the correct template is used for the property list page."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.properties_url)
        self.assertTemplateUsed(response, 'rentals/property_list.html') # <<< This will FAIL initially
        # Also check it uses the base template implicitly
        self.assertTemplateUsed(response, 'base.html') # <<< This will FAIL initially

    def test_property_list_view_contains_base_elements(self):
        """Verify the page includes elements from base.html like navbar and title."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.properties_url)
        self.assertContains(response, '<nav class="navbar') # Check for navbar
        self.assertContains(response, 'RentTracker') # Check for brand/title in navbar/footer
        self.assertContains(response, '<h1>Properties</h1>') # Check for expected content <<< This will FAIL initially

class NavigationPermissionTest(TestCase):
    """Tests related to site navigation visibility based on permissions"""

    @classmethod
    def setUpTestData(cls):
        # Create permissions
        cls.view_llc_perm = get_permission('rentals', 'llc', 'view')
        cls.view_prop_perm = get_permission('rentals', 'property', 'view')
        cls.add_prop_perm = get_permission('rentals', 'property', 'add')

        # Create groups and assign permissions
        viewer_group, _ = Group.objects.get_or_create(name='Viewers')
        viewer_group.permissions.add(cls.view_llc_perm, cls.view_prop_perm)

        manager_group, _ = Group.objects.get_or_create(name='Property Managers')
        manager_group.permissions.add(cls.view_llc_perm, cls.view_prop_perm, cls.add_prop_perm) # Add more perms as needed

        # Create users
        cls.viewer_user = create_test_user(username='viewer', password='password', groups=['Viewers'])
        cls.manager_user = create_test_user(username='manager', password='password', groups=['Property Managers'])
        cls.no_perms_user = create_test_user(username='noperms', password='password') # Logged in, but no specific group/perms

        # URLs
        cls.dashboard_url = reverse('rentals:dashboard')
        cls.llc_list_url = reverse('rentals:llc_list')
        cls.property_list_url = reverse('rentals:property_list')

    def test_nav_links_for_viewer(self):
        """Verify nav links visible to users with only view permissions."""
        self.client.login(username='viewer', password='password')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{self.llc_list_url}"')
        self.assertContains(response, f'href="{self.property_list_url}"')
        # Assuming 'Add Property' link is NOT in base nav, but on property list page
        response_props = self.client.get(self.property_list_url)
        self.assertNotContains(response_props, "Add New Property") # Viewers shouldn't see Add button

    def test_nav_links_for_manager(self):
        """Verify nav links visible to users with manager permissions."""
        self.client.login(username='manager', password='password')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{self.llc_list_url}"')
        self.assertContains(response, f'href="{self.property_list_url}"')
        # Managers should see Add button on property list page
        response_props = self.client.get(self.property_list_url)
        self.assertContains(response_props, "Add New Property")

    def test_nav_links_for_no_perms_user(self):
        """Verify nav links are hidden if user lacks view permissions."""
        self.client.login(username='noperms', password='password')
        response = self.client.get(self.dashboard_url) # Access dashboard (only needs login)
        self.assertEqual(response.status_code, 200)
        # Check that links requiring specific view perms are NOT shown
        self.assertNotContains(response, f'href="{self.llc_list_url}"')
        self.assertNotContains(response, f'href="{self.property_list_url}"')

class PropertyListViewPermissionTest(TestCase):
    """Tests permissions for the Property List View"""

    @classmethod
    def setUpTestData(cls):
        # Permissions
        cls.view_prop_perm = get_permission('rentals', 'property', 'view')
        # Groups
        viewer_group, _ = Group.objects.get_or_create(name='Viewers')
        viewer_group.permissions.add(cls.view_prop_perm)
        # Users
        cls.viewer_user = create_test_user(username='viewer', password='password', groups=['Viewers'])
        cls.no_perms_user = create_test_user(username='noperms', password='password')
        # URLs
        cls.properties_url = reverse('rentals:property_list')
        cls.login_url = reverse('login') # Assumes default Django login URL name

    def test_property_list_view_redirects_if_not_logged_in(self):
        """Verify accessing the property list page redirects if not logged in."""
        response = self.client.get(self.properties_url)
        # Expect a redirect (302) to the login page
        expected_redirect_url = f'{self.login_url}?next={self.properties_url}'
        self.assertRedirects(response, expected_redirect_url)

    def test_property_list_view_forbidden_if_logged_in_without_permission(self):
        """Verify logged-in users without 'view_property' permission get 403."""
        self.client.login(username='noperms', password='password')
        response = self.client.get(self.properties_url)
        # Because we used raise_exception=True in the decorator
        self.assertEqual(response.status_code, 403)

    def test_property_list_view_accessible_with_permission(self):
        """Verify logged-in users with 'view_property' permission can access."""
        self.client.login(username='viewer', password='password')
        response = self.client.get(self.properties_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rentals/property_list.html')
        self.assertContains(response, '<h1>Properties</h1>')


# --- Running the tests ---
# In your terminal, navigate to the project root (where manage.py is)
# Run: python manage.py test rentals
#
# EXPECTED OUTPUT: Lots of failures! (NoReverseMatch, AssertionError, TemplateDoesNotExist, etc.) This is the RED step.

# --- (Keep existing tests like NavigationTest and PropertyListViewTest,
#      but adapt them or add new ones focusing on permissions) ---

# Remove or adapt the old PropertyListViewTest that didn't check permissions
# class PropertyListViewTest(TestCase): ... (old version)

# --- Running the tests ---
# In your terminal, navigate to the project root (where manage.py is)
# Run: python manage.py test rentals
#
# EXPECTED OUTPUT: Tests should pass if views, templates, and permissions are set up correctly.
# You might need to create the templates first (base.html, rentals/property_list.html)
# and ensure the login/logout URLs are configured in your main project urls.py.