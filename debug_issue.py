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

# Try to reproduce the issue
print("=" * 60)
print("Test 1: ~Exists(User.objects.none()) AND username='test'")
print("=" * 60)

qs = User.objects.filter(~models.Exists(User.objects.none()), username='test')
print('QuerySet:', qs)
print('Query where clause:', qs.query.where)
print('Query where children:', qs.query.where.children if qs.query.where else None)

try:
    print('SQL:', str(qs.query))
except Exception as e:
    print(f'Error getting SQL: {type(e).__name__}: {e}')

print("\n" + "=" * 60)
print("Test 2: Just ~Exists(User.objects.none())")
print("=" * 60)

qs2 = User.objects.filter(~models.Exists(User.objects.none()))
print('QuerySet:', qs2)
print('Query where clause:', qs2.query.where)
print('Query where children:', qs2.query.where.children if qs2.query.where else None)

try:
    print('SQL:', str(qs2.query))
except Exception as e:
    print(f'Error getting SQL: {type(e).__name__}: {e}')

print("\n" + "=" * 60)
print("Test 3: Just username='test'")
print("=" * 60)

qs3 = User.objects.filter(username='test')
print('QuerySet:', qs3)
print('Query where clause:', qs3.query.where)
print('Query where children:', qs3.query.where.children if qs3.query.where else None)

try:
    print('SQL:', str(qs3.query))
except Exception as e:
    print(f'Error getting SQL: {type(e).__name__}: {e}')

print("\n" + "=" * 60)
print("Test 4: Exists(User.objects.none()) AND username='test'")
print("=" * 60)

qs4 = User.objects.filter(models.Exists(User.objects.none()), username='test')
print('QuerySet:', qs4)
print('Query where clause:', qs4.query.where)
print('Query where children:', qs4.query.where.children if qs4.query.where else None)

try:
    print('SQL:', str(qs4.query))
except Exception as e:
    print(f'Error getting SQL: {type(e).__name__}: {e}')
