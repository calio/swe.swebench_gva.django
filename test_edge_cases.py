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
test_cases = [
    ("Exists with empty queryset in annotation", 
     lambda: User.objects.annotate(has_exists=models.Exists(User.objects.none()))),
    ("Exists with empty queryset in Q object", 
     lambda: User.objects.filter(models.Q(~models.Exists(User.objects.none())) | models.Q(username='test'))),
    ("Exists with empty queryset in exclude", 
     lambda: User.objects.exclude(~models.Exists(User.objects.none()))),
]

print("Testing edge cases:")
print("=" * 60)

for test_name, test_func in test_cases:
    print(f"\nTest: {test_name}")
    try:
        qs = test_func()
        sql = str(qs.query)
        print(f"✓ SQL generated successfully")
        print(f"  SQL: {sql[:100]}...")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("All edge case tests completed!")
