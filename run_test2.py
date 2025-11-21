#!/usr/bin/env python
import os
import sys
import django

# Add the project to the path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')

# Setup Django
from django.conf import settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
    )

django.setup()

# Now test the issue
from django.db import models
from django.contrib.auth.models import User
from django.core.management import call_command

# Create the table
call_command('migrate', verbosity=0)

# Test cases
print("Testing the fix:")
print("=" * 60)

# Test 1: ~Exists(User.objects.none()) AND username='test'
print("\nTest 1: ~Exists(User.objects.none()) AND username='test'")
try:
    qs = User.objects.filter(~models.Exists(User.objects.none()), username='test')
    sql = str(qs.query)
    assert 'WHERE' in sql, "WHERE clause missing"
    assert 'username' in sql, "username filter missing"
    print("✓ PASSED")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")

# Test 2: ~Exists(User.objects.none())
print("\nTest 2: ~Exists(User.objects.none())")
try:
    qs = User.objects.filter(~models.Exists(User.objects.none()))
    sql = str(qs.query)
    assert 'WHERE' in sql, "WHERE clause missing"
    print("✓ PASSED")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")

# Test 3: Exists(User.objects.none()) AND username='test'
print("\nTest 3: Exists(User.objects.none()) AND username='test'")
try:
    qs = User.objects.filter(models.Exists(User.objects.none()), username='test')
    sql = str(qs.query)
    assert 'WHERE' in sql, "WHERE clause missing"
    assert 'username' in sql, "username filter missing"
    print("✓ PASSED")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("All tests completed!")
