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
qs = User.objects.filter(~models.Exists(User.objects.none()), username='test')
print('QuerySet:', qs)
print('Query where clause:', qs.query.where)
print('Query where children:', qs.query.where.children if qs.query.where else None)

for i, child in enumerate(qs.query.where.children):
    print(f"Child {i}: {child}")
    print(f"  Type: {type(child)}")
    print(f"  Has empty_result_set_value: {hasattr(child, 'empty_result_set_value')}")
    if hasattr(child, 'empty_result_set_value'):
        print(f"  empty_result_set_value: {child.empty_result_set_value}")
    if hasattr(child, 'rhs'):
        print(f"  rhs: {child.rhs}")
        print(f"  rhs type: {type(child.rhs)}")
        if hasattr(child.rhs, 'empty_result_set_value'):
            print(f"  rhs.empty_result_set_value: {child.rhs.empty_result_set_value}")
