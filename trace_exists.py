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

# Monkey patch to trace the issue
original_exists_as_sql = models.Exists.as_sql

def traced_exists_as_sql(self, compiler, connection, template=None, **extra_context):
    print(f"Exists.as_sql called: negated={self.negated}")
    try:
        result = original_exists_as_sql(self, compiler, connection, template, **extra_context)
        print(f"Exists.as_sql returned: {result}")
        return result
    except Exception as e:
        print(f"Exists.as_sql raised: {type(e).__name__}: {e}")
        raise

models.Exists.as_sql = traced_exists_as_sql

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
