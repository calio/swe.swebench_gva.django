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

# Test cases from the issue description
print("Testing the original issue:")
print("=" * 60)

# Original issue: filter on exists-subquery with empty queryset removes whole WHERE block
print("\nOriginal issue test:")
try:
    qs = User.objects.filter(~models.Exists(User.objects.none()), username='test')
    print(f"QuerySet: {qs}")
    sql = str(qs.query)
    print(f"SQL: {sql}")
    
    # Check that the WHERE clause is present
    if 'WHERE' not in sql:
        print("✗ FAILED: WHERE clause is missing!")
    elif 'username' not in sql:
        print("✗ FAILED: username filter is missing!")
    else:
        print("✓ PASSED: WHERE clause is present and contains the filter")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
