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

# Create some test data
User.objects.create(username='test1')
User.objects.create(username='test2')

# Test cases
test_cases = [
    # Original issue
    ("~Exists(empty) AND username='test1'", 
     lambda: User.objects.filter(~models.Exists(User.objects.none()), username='test1'),
     lambda qs: len(qs) == 1 and qs[0].username == 'test1'),
    
    # Negated Exists with empty queryset
    ("~Exists(empty)", 
     lambda: User.objects.filter(~models.Exists(User.objects.none())),
     lambda qs: len(qs) == 2),
    
    # Exists with empty queryset
    ("Exists(empty)", 
     lambda: User.objects.filter(models.Exists(User.objects.none())),
     lambda qs: len(qs) == 0),
    
    # Exists with empty queryset AND filter
    ("Exists(empty) AND username='test1'", 
     lambda: User.objects.filter(models.Exists(User.objects.none()), username='test1'),
     lambda qs: len(qs) == 0),
    
    # Negated Exists with non-empty queryset
    ("~Exists(non-empty)", 
     lambda: User.objects.filter(~models.Exists(User.objects.all())),
     lambda qs: len(qs) == 0),
    
    # Exists with non-empty queryset
    ("Exists(non-empty)", 
     lambda: User.objects.filter(models.Exists(User.objects.all())),
     lambda qs: len(qs) == 2),
]

print("Comprehensive test suite:")
print("=" * 60)

passed = 0
failed = 0

for test_name, test_func, assertion_func in test_cases:
    print(f"\nTest: {test_name}")
    try:
        qs = test_func()
        # First, check that SQL can be generated
        sql = str(qs.query)
        print(f"  SQL generated: ✓")
        
        # Then, check the assertion
        if assertion_func(qs):
            print(f"  Assertion passed: ✓")
            passed += 1
        else:
            print(f"  Assertion failed: ✗")
            failed += 1
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")
        failed += 1

print("\n" + "=" * 60)
print(f"Results: {passed} passed, {failed} failed")
if failed == 0:
    print("All tests PASSED!")
else:
    print(f"Some tests FAILED!")
    sys.exit(1)
