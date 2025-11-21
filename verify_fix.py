#!/usr/bin/env python
"""
Verify that the fix correctly handles GROUP BY queries with Meta.ordering.
"""
import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings
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
            'tests.queries',
        ],
    )
    django.setup()

from django.db.models import Count
from tests.queries.models import Tag

print("=" * 80)
print("Verifying the fix for QuerySet.ordered with GROUP BY queries")
print("=" * 80)
print()

# Test 1: Tag with default ordering (no annotate)
print("Test 1: Tag.objects.all()")
qs = Tag.objects.all()
print(f"  qs.ordered: {qs.ordered}")
print(f"  SQL: {str(qs.query)}")
print(f"  Has ORDER BY: {'ORDER BY' in str(qs.query)}")
print()

# Test 2: Tag with annotate and default ordering
print("Test 2: Tag.objects.annotate(Count('children'))")
qs2 = Tag.objects.annotate(num_children=Count('children'))
print(f"  qs2.ordered: {qs2.ordered}")
print(f"  SQL: {str(qs2.query)}")
print(f"  Has GROUP BY: {'GROUP BY' in str(qs2.query)}")
print(f"  Has ORDER BY: {'ORDER BY' in str(qs2.query)}")
print()

# Verify the fix
if 'GROUP BY' in str(qs2.query) and 'ORDER BY' not in str(qs2.query):
    if qs2.ordered == False:
        print("✓ PASS: qs2.ordered is False when GROUP BY is present and ORDER BY is absent")
    else:
        print("✗ FAIL: qs2.ordered should be False when GROUP BY is present and ORDER BY is absent")
else:
    print("✗ FAIL: Expected GROUP BY without ORDER BY in the SQL")

print()

# Test 3: Tag with annotate, default ordering, and explicit order_by
print("Test 3: Tag.objects.annotate(Count('children')).order_by('name')")
qs3 = Tag.objects.annotate(num_children=Count('children')).order_by('name')
print(f"  qs3.ordered: {qs3.ordered}")
print(f"  SQL: {str(qs3.query)}")
print(f"  Has GROUP BY: {'GROUP BY' in str(qs3.query)}")
print(f"  Has ORDER BY: {'ORDER BY' in str(qs3.query)}")
print()

# Verify the fix
if qs3.ordered == True:
    print("✓ PASS: qs3.ordered is True when explicit order_by is used")
else:
    print("✗ FAIL: qs3.ordered should be True when explicit order_by is used")

print()

# Test 4: Tag with annotate and cleared ordering
print("Test 4: Tag.objects.annotate(Count('children')).order_by()")
qs4 = Tag.objects.annotate(num_children=Count('children')).order_by()
print(f"  qs4.ordered: {qs4.ordered}")
print(f"  SQL: {str(qs4.query)}")
print(f"  Has GROUP BY: {'GROUP BY' in str(qs4.query)}")
print(f"  Has ORDER BY: {'ORDER BY' in str(qs4.query)}")
print()

# Verify the fix
if qs4.ordered == False:
    print("✓ PASS: qs4.ordered is False when ordering is cleared")
else:
    print("✗ FAIL: qs4.ordered should be False when ordering is cleared")
