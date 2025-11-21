#!/usr/bin/env python
import os
import sys
import django
import traceback

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

# Try to reproduce the issue
print("=" * 60)
print("Test: ~Exists(User.objects.none()) AND username='test'")
print("=" * 60)

qs = User.objects.filter(~models.Exists(User.objects.none()), username='test')
print('QuerySet:', qs)

try:
    print('SQL:', str(qs.query))
except Exception as e:
    print(f'Error getting SQL: {type(e).__name__}: {e}')
    traceback.print_exc()
