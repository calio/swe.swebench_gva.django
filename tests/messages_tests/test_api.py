from django.contrib import messages
from django.contrib.messages import constants
from django.contrib.messages.storage.base import Message
from django.test import RequestFactory, SimpleTestCase, override_settings


class DummyStorage:
    """
    dummy message-store to test the api methods
    """

    def __init__(self):
        self.store = []

    def add(self, level, message, extra_tags=''):
        self.store.append(message)


class ApiTests(SimpleTestCase):
    rf = RequestFactory()

    def setUp(self):
        self.request = self.rf.request()
        self.storage = DummyStorage()

    def test_ok(self):
        msg = 'some message'
        self.request._messages = self.storage
        messages.add_message(self.request, messages.DEBUG, msg)
        self.assertIn(msg, self.storage.store)

    def test_request_is_none(self):
        msg = "add_message() argument must be an HttpRequest object, not 'NoneType'."
        self.request._messages = self.storage
        with self.assertRaisesMessage(TypeError, msg):
            messages.add_message(None, messages.DEBUG, 'some message')
        self.assertEqual(self.storage.store, [])

    def test_middleware_missing(self):
        msg = 'You cannot add messages without installing django.contrib.messages.middleware.MessageMiddleware'
        with self.assertRaisesMessage(messages.MessageFailure, msg):
            messages.add_message(self.request, messages.DEBUG, 'some message')
        self.assertEqual(self.storage.store, [])

    def test_middleware_missing_silently(self):
        messages.add_message(self.request, messages.DEBUG, 'some message', fail_silently=True)
        self.assertEqual(self.storage.store, [])


class CustomRequest:
    def __init__(self, request):
        self._request = request

    def __getattribute__(self, attr):
        try:
            return super().__getattribute__(attr)
        except AttributeError:
            return getattr(self._request, attr)


class CustomRequestApiTests(ApiTests):
    """
    add_message() should use ducktyping to allow request wrappers such as the
    one in Django REST framework.
    """
    def setUp(self):
        super().setUp()
        self.request = CustomRequest(self.request)


class OverrideSettingsTagsTests(SimpleTestCase):
    """
    Test that MESSAGE_TAGS overrides work correctly with Message.level_tag
    """

    def test_level_tag_with_override_settings(self):
        """
        Test that level_tag property reflects MESSAGE_TAGS changes from @override_settings
        """
        # First, test default behavior
        msg = Message(constants.INFO, 'Test message')
        self.assertEqual(msg.level_tag, 'info')

        # Now test with override_settings
        with override_settings(MESSAGE_TAGS={constants.INFO: 'custom-info'}):
            msg = Message(constants.INFO, 'Test message')
            # This should be 'custom-info' but currently returns empty string (BUG)
            self.assertEqual(msg.level_tag, 'custom-info')

    def test_level_tag_with_multiple_overrides(self):
        """
        Test that level_tag works with multiple MESSAGE_TAGS overrides
        """
        with override_settings(MESSAGE_TAGS={
            constants.INFO: 'info-custom',
            constants.WARNING: 'warn-custom',
            constants.ERROR: 'err-custom',
        }):
            info_msg = Message(constants.INFO, 'Info')
            warning_msg = Message(constants.WARNING, 'Warning')
            error_msg = Message(constants.ERROR, 'Error')

            self.assertEqual(info_msg.level_tag, 'info-custom')
            self.assertEqual(warning_msg.level_tag, 'warn-custom')
            self.assertEqual(error_msg.level_tag, 'err-custom')
