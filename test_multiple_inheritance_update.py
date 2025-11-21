#!/usr/bin/env python
"""
Test script to reproduce the multiple inheritance update issue.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
sys.path.insert(0, os.path.dirname(__file__))

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
            'tests.model_inheritance',
        ],
        USE_TZ=True,
    )

django.setup()

from django.db import connection
from django.core.management import call_command
from tests.model_inheritance.models import Restaurant, Place

# Create tables
call_command('migrate', '--run-syncdb', verbosity=0)

# Clean up
Restaurant.objects.all().delete()
Place.objects.all().delete()

print("Testing multiple inheritance update issue...")
print("=" * 60)

# Create test data
place1 = Place.objects.create(name='Place 1', address='Address 1')
place2 = Place.objects.create(name='Place 2', address='Address 2')
print(f"Created Place 1: id={place1.id}")
print(f"Created Place 2: id={place2.id}")

restaurant1 = Restaurant.objects.create(
    name='Restaurant 1', 
    address='Address 1',
    serves_hot_dogs=True,
    serves_pizza=False
)
restaurant2 = Restaurant.objects.create(
    name='Restaurant 2', 
    address='Address 2',
    serves_hot_dogs=False,
    serves_pizza=True
)
print(f"Created Restaurant 1: id={restaurant1.id}, serves_hot_dogs={restaurant1.serves_hot_dogs}")
print(f"Created Restaurant 2: id={restaurant2.id}, serves_hot_dogs={restaurant2.serves_hot_dogs}")

print("\n" + "=" * 60)
print("Before update:")
print(f"Restaurant 1 serves_hot_dogs: {Restaurant.objects.get(id=restaurant1.id).serves_hot_dogs}")
print(f"Restaurant 2 serves_hot_dogs: {Restaurant.objects.get(id=restaurant2.id).serves_hot_dogs}")

# Enable query logging
from django.db import connection
from django.test.utils import CaptureQueriesContext

print("\n" + "=" * 60)
print("Executing: Restaurant.objects.update(serves_hot_dogs=False)")
print("=" * 60)

with CaptureQueriesContext(connection) as queries:
    result = Restaurant.objects.update(serves_hot_dogs=False)
    print(f"Update returned: {result}")
    
print("\nQueries executed:")
for i, query in enumerate(queries, 1):
    print(f"\n{i}. {query['sql']}")

print("\n" + "=" * 60)
print("After update:")
r1_after = Restaurant.objects.get(id=restaurant1.id)
r2_after = Restaurant.objects.get(id=restaurant2.id)
print(f"Restaurant 1 serves_hot_dogs: {r1_after.serves_hot_dogs}")
print(f"Restaurant 2 serves_hot_dogs: {r2_after.serves_hot_dogs}")

print("\n" + "=" * 60)
print("Checking Place table directly:")
p1_after = Place.objects.get(id=place1.id)
p2_after = Place.objects.get(id=place2.id)
print(f"Place 1 name: {p1_after.name}")
print(f"Place 2 name: {p2_after.name}")

print("\n" + "=" * 60)
if r1_after.serves_hot_dogs == False and r2_after.serves_hot_dogs == False:
    print("✓ TEST PASSED: Both restaurants updated correctly")
else:
    print("✗ TEST FAILED: Restaurants not updated correctly")
    print(f"  Expected: serves_hot_dogs=False for both")
    print(f"  Got: r1={r1_after.serves_hot_dogs}, r2={r2_after.serves_hot_dogs}")
