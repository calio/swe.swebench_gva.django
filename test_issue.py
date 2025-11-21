#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
django.setup()

from django.db.models import Count
from tests.queries.models import Tag

# Test 1: Tag with default ordering (no annotate)
qs = Tag.objects.all()
print('Test 1: Tag.objects.all()')
print('  qs.ordered:', qs.ordered)
print('  SQL:', str(qs.query))
print()

# Test 2: Tag with annotate and default ordering
qs2 = Tag.objects.annotate(num_notes=Count('children'))
print('Test 2: Tag.objects.annotate(Count("children"))')
print('  qs2.ordered:', qs2.ordered)
print('  SQL:', str(qs2.query))
print()

# Check if there's a GROUP BY in the SQL
if 'GROUP BY' in str(qs2.query):
    print('  GROUP BY found in SQL')
    if 'ORDER BY' in str(qs2.query):
        print('  ORDER BY found in SQL')
    else:
        print('  ORDER BY NOT found in SQL - BUG!')
        print('  Expected qs2.ordered to be False, but got:', qs2.ordered)
