"""
Verification test for SECRET_KEY_FALLBACKS fix for sessions.

This test verifies that the issue described in the task has been fixed:
- Sessions should remain valid when SECRET_KEY is rotated
- Old sessions created with the old SECRET_KEY should still work when that key is in SECRET_KEY_FALLBACKS
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.test_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.http import HttpRequest
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import HASH_SESSION_KEY, SESSION_KEY, BACKEND_SESSION_KEY


class SecretKeyFallbackVerification(TestCase):
    """Verify that SECRET_KEY_FALLBACKS works correctly for sessions."""
    
    def setUp(self):
        """Create a test user."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_session_auth_hash_with_old_secret_key(self):
        """
        Verify that a session created with an old SECRET_KEY remains valid
        when that key is moved to SECRET_KEY_FALLBACKS.
        """
        # Step 1: Create a session with the old SECRET_KEY
        with override_settings(
            SECRET_KEY='old-secret-key-12345',
            SECRET_KEY_FALLBACKS=[]
        ):
            # Get the session auth hash with the old key
            old_session_hash = self.user.get_session_auth_hash()
            
            # Create a session
            session = SessionStore()
            session[SESSION_KEY] = self.user.pk
            session[BACKEND_SESSION_KEY] = 'django.contrib.auth.backends.ModelBackend'
            session[HASH_SESSION_KEY] = old_session_hash
            session.save()
            
            session_key = session.session_key
            session_data = dict(session)
        
        # Step 2: Rotate the SECRET_KEY and add old key to fallbacks
        with override_settings(
            SECRET_KEY='new-secret-key-67890',
            SECRET_KEY_FALLBACKS=['old-secret-key-12345']
        ):
            # Load the session
            request = HttpRequest()
            request.session = SessionStore(session_key=session_key)
            
            # Try to get the user - this should work with fallback key
            user = get_user(request)
            
            # Verify the user is authenticated (not anonymous)
            self.assertFalse(user.is_anonymous, 
                           "User should remain authenticated with fallback key")
            self.assertEqual(user.pk, self.user.pk,
                           "Should retrieve the correct user")
            self.assertEqual(user.username, 'testuser',
                           "User data should be intact")
    
    def test_session_invalid_without_fallback_key(self):
        """
        Verify that a session becomes invalid when SECRET_KEY is rotated
        without adding the old key to SECRET_KEY_FALLBACKS.
        """
        # Step 1: Create a session with the old SECRET_KEY
        with override_settings(
            SECRET_KEY='old-secret-key-12345',
            SECRET_KEY_FALLBACKS=[]
        ):
            old_session_hash = self.user.get_session_auth_hash()
            
            session = SessionStore()
            session[SESSION_KEY] = self.user.pk
            session[BACKEND_SESSION_KEY] = 'django.contrib.auth.backends.ModelBackend'
            session[HASH_SESSION_KEY] = old_session_hash
            session.save()
            
            session_key = session.session_key
        
        # Step 2: Rotate the SECRET_KEY WITHOUT adding to fallbacks
        with override_settings(
            SECRET_KEY='new-secret-key-67890',
            SECRET_KEY_FALLBACKS=[]  # Old key NOT in fallbacks
        ):
            request = HttpRequest()
            request.session = SessionStore(session_key=session_key)
            
            # Try to get the user - this should fail
            user = get_user(request)
            
            # Verify the user is anonymous (logged out)
            self.assertTrue(user.is_anonymous,
                          "User should be logged out without fallback key")
    
    def test_multiple_fallback_keys(self):
        """
        Verify that multiple fallback keys work correctly.
        """
        # Create sessions with different keys
        sessions_data = []
        
        for i, secret_key in enumerate(['key1', 'key2', 'key3']):
            with override_settings(
                SECRET_KEY=secret_key,
                SECRET_KEY_FALLBACKS=[]
            ):
                session_hash = self.user.get_session_auth_hash()
                
                session = SessionStore()
                session[SESSION_KEY] = self.user.pk
                session[BACKEND_SESSION_KEY] = 'django.contrib.auth.backends.ModelBackend'
                session[HASH_SESSION_KEY] = session_hash
                session.save()
                
                sessions_data.append({
                    'key': session.session_key,
                    'secret': secret_key
                })
        
        # Now use a new key with all old keys as fallbacks
        with override_settings(
            SECRET_KEY='new-key',
            SECRET_KEY_FALLBACKS=['key3', 'key2', 'key1']  # All old keys
        ):
            # All sessions should still be valid
            for session_info in sessions_data:
                request = HttpRequest()
                request.session = SessionStore(session_key=session_info['key'])
                
                user = get_user(request)
                
                self.assertFalse(user.is_anonymous,
                               f"Session created with {session_info['secret']} should be valid")
                self.assertEqual(user.pk, self.user.pk)


if __name__ == '__main__':
    import unittest
    
    # Run the tests
    suite = unittest.TestLoader().loadTestsFromTestCase(SecretKeyFallbackVerification)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
