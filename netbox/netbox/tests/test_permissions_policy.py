from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from netbox.middleware import PermissionsPolicyMiddleware

HEADER = 'Permissions-Policy'

DEFAULT_HEADER = 'camera=(), microphone=(), geolocation=(), payment=(), usb=(), hid=(), serial=(), bluetooth=()'


class PermissionsPolicyHeaderTestCase(TestCase):
    """
    Check the header on real responses, through the whole middleware stack.
    """

    def test_default_denies_the_default_deny_list(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response[HEADER], DEFAULT_HEADER)

    @override_settings(PERMISSIONS_POLICY={'camera': ['self'], 'geolocation': []})
    def test_custom_policy_replaces_default(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response[HEADER], 'camera=(self), geolocation=()')

    @override_settings(PERMISSIONS_POLICY={'camera': ['self', 'https://scan.example.com']})
    def test_origins_are_quoted_and_self_is_a_token(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response[HEADER], 'camera=(self "https://scan.example.com")')

    @override_settings(PERMISSIONS_POLICY={})
    def test_empty_policy_sends_no_header(self):
        response = self.client.get(reverse('login'))
        self.assertNotIn(HEADER, response)


class PermissionsPolicyMiddlewareTestCase(SimpleTestCase):
    """
    Check the middleware in isolation, with a view that sets the header itself.
    """

    def test_header_set_by_view_is_untouched(self):
        def view(request):
            response = HttpResponse()
            response[HEADER] = 'fullscreen=(self)'
            return response

        response = PermissionsPolicyMiddleware(view)(RequestFactory().get('/'))
        self.assertEqual(response[HEADER], 'fullscreen=(self)')
