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

# Create Exists expression
exists_expr = models.Exists(User.objects.none())
print(f"Exists.empty_result_set_value: {getattr(exists_expr, 'empty_result_set_value', 'NOT FOUND')}")

# Create negated Exists expression
negated_exists_expr = ~models.Exists(User.objects.none())
print(f"~Exists.empty_result_set_value: {getattr(negated_exists_expr, 'empty_result_set_value', 'NOT FOUND')}")

# Check the parent class
from django.db.models.expressions import Subquery
print(f"Subquery.empty_result_set_value: {Subquery.empty_result_set_value}")
