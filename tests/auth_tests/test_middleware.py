from django.contrib.auth import get_user
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from django.test import TestCase, override_settings


class TestAuthenticationMiddleware(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "test_user", "test@example.com", "test_password"
        )

    def setUp(self):
        self.middleware = AuthenticationMiddleware(lambda req: HttpResponse())
        self.client.force_login(self.user)
        self.request = HttpRequest()
        self.request.session = self.client.session

    def test_no_password_change_doesnt_invalidate_session(self):
        self.request.session = self.client.session
        self.middleware(self.request)
        self.assertIsNotNone(self.request.user)
        self.assertFalse(self.request.user.is_anonymous)

    def test_changed_password_invalidates_session(self):
        # After password change, user should be anonymous
        self.user.set_password("new_password")
        self.user.save()
        self.middleware(self.request)
        self.assertIsNotNone(self.request.user)
        self.assertTrue(self.request.user.is_anonymous)
        # session should be flushed
        self.assertIsNone(self.request.session.session_key)

    def test_no_session(self):
        msg = (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )
        with self.assertRaisesMessage(ImproperlyConfigured, msg):
            self.middleware(HttpRequest())

    async def test_auser(self):
        self.middleware(self.request)
        auser = await self.request.auser()
        self.assertEqual(auser, self.user)
        auser_second = await self.request.auser()
        self.assertIs(auser, auser_second)

    @override_settings(
        SECRET_KEY="new-secret-key",
        SECRET_KEY_FALLBACKS=["old-secret-key"],
    )
    def test_session_valid_with_fallback_key(self):
        """
        Test that sessions remain valid after SECRET_KEY rotation when the old
        key is in SECRET_KEY_FALLBACKS.
        """
        # First, create a session with the old key
        with override_settings(
            SECRET_KEY="old-secret-key",
            SECRET_KEY_FALLBACKS=[],
        ):
            self.client.force_login(self.user)
            # Get the session data
            old_session_key = self.client.session.session_key
            old_session_data = dict(self.client.session)

        # Now simulate a SECRET_KEY rotation
        # The session should still be valid with the fallback key
        self.request.session = old_session_data
        user = get_user(self.request)
        self.assertEqual(user, self.user)
        self.assertFalse(user.is_anonymous)
