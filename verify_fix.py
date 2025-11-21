#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/calio/swebench_gva/django__django-16263')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')

# Import settings first
from tests import settings as test_settings

django.setup()

from django.db import connection
from django.db.models import Count
from tests.aggregation_regress.models import Book, Author, Publisher
from django.test.utils import CaptureQueriesContext

# Create tables
from django.core.management import call_command
call_command('migrate', '--run-syncdb', verbosity=0)

# Create test data
publisher = Publisher.objects.create(name='Test Publisher', num_awards=1)
author = Author.objects.create(name='Test Author', age=30)
book = Book.objects.create(title='Test Book', publisher=publisher, pages=100, price=10.0)
book.authors.add(author)

print("=" * 80)
print("Test 1: Book.objects.count() - baseline")
print("=" * 80)
with CaptureQueriesContext(connection) as ctx:
    result = Book.objects.count()
print(f'Result: {result}')
print(f'SQL: {ctx[0]["sql"]}')
print()

print("=" * 80)
print("Test 2: Book.objects.annotate(Count('store')).count() - with unused annotation")
print("=" * 80)
with CaptureQueriesContext(connection) as ctx:
    result = Book.objects.annotate(Count('store')).count()
print(f'Result: {result}')
print(f'SQL: {ctx[0]["sql"]}')
print()

print("=" * 80)
print("Test 3: Book.objects.annotate(Count('authors')).count() - with unused annotation")
print("=" * 80)
with CaptureQueriesContext(connection) as ctx:
    result = Book.objects.annotate(Count('authors')).count()
print(f'Result: {result}')
print(f'SQL: {ctx[0]["sql"]}')
print()

print("=" * 80)
print("Test 4: Book.objects.annotate(Count('authors')).filter(authors__isnull=False).count() - with used annotation in filter")
print("=" * 80)
with CaptureQueriesContext(connection) as ctx:
    result = Book.objects.annotate(Count('authors')).filter(authors__isnull=False).count()
print(f'Result: {result}')
print(f'SQL: {ctx[0]["sql"]}')
print()

print("=" * 80)
print("Test 5: Book.objects.annotate(Count('authors')).order_by('-authors__count').count() - with used annotation in ordering")
print("=" * 80)
with CaptureQueriesContext(connection) as ctx:
    result = Book.objects.annotate(Count('authors')).order_by('-authors__count').count()
print(f'Result: {result}')
print(f'SQL: {ctx[0]["sql"]}')
