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

# Create the table
from django.core.management import call_command
call_command('migrate', verbosity=0)

# Try to reproduce the issue
qs = User.objects.filter(~models.Exists(User.objects.none()), username='test')
print('QuerySet:', qs)
print('Query:', qs.query)
print('SQL:', str(qs.query))
