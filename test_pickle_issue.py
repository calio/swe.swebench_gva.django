#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

# Configure Django settings
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
        USE_TZ=True,
    )
    django.setup()

# Now create the test model
from django.db import models
from django.db.models import Sum
import pickle

# Create a test model
class Toy(models.Model):
    name = models.CharField(max_length=16)
    material = models.CharField(max_length=16)
    price = models.PositiveIntegerField()
    
    class Meta:
        app_label = 'test_app'

# Create the table
from django.db import connection
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(Toy)

# Now run the test
print("Creating test data...")
Toy.objects.create(name='foo', price=10, material='wood')
Toy.objects.create(name='bar', price=20, material='plastic')
Toy.objects.create(name='baz', price=100, material='wood')

print("\n1. Testing normal values() + annotate():")
prices = Toy.objects.values('material').annotate(total_price=Sum('price'))
print(f"Type of prices[0]: {type(prices[0])}")
print(f"prices[0]: {prices[0]}")

print("\n2. Testing pickled query:")
prices2 = Toy.objects.all()
prices2.query = pickle.loads(pickle.dumps(prices.query))
print(f"Type of prices2[0]: {type(prices2[0])}")
try:
    print(f"prices2[0]: {prices2[0]}")
    print(f"prices2: {prices2}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
