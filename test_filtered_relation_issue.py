#!/usr/bin/env python
"""
Test script to reproduce the FilteredRelation issue where multiple
FilteredRelations with the same relation but different filters are ignored.
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
            'tests.filtered_relation',
        ],
        USE_TZ=True,
    )

django.setup()

from django.db.models import FilteredRelation, Q, F, Case, When
from tests.filtered_relation.models import Author, Book, Editor

# Create tables
from django.core.management import call_command
call_command('migrate', '--run-syncdb', verbosity=0)

# Create test data
Author.objects.all().delete()
Book.objects.all().delete()
Editor.objects.all().delete()

editor = Editor.objects.create(name='Editor A')
author1 = Author.objects.create(name='Alice')
book1 = Book.objects.create(title='Book Alice', author=author1, editor=editor)
book2 = Book.objects.create(title='Book Jane', author=author1, editor=editor)

print("=" * 80)
print("Test 1: Multiple FilteredRelations on same relation with different conditions")
print("=" * 80)

# Try the query with multiple FilteredRelations on the same relation
qs = Author.objects.annotate(
    book_alice=FilteredRelation('book', condition=Q(book__title__icontains='Alice')),
    book_jane=FilteredRelation('book', condition=Q(book__title__icontains='Jane')),
)

print("\nQuery SQL:")
sql = str(qs.query)
print(sql)
print()

# Count JOINs
join_count = sql.count('JOIN')
print(f"Number of JOINs: {join_count}")
print(f"Expected: 2, Got: {join_count}")

if join_count == 2:
    print("✓ PASS: Both FilteredRelations created separate JOINs")
else:
    print("✗ FAIL: Only one JOIN was created, the second FilteredRelation was ignored")

print("\n" + "=" * 80)
print("Test 2: Check alias_map to see if both joins are registered")
print("=" * 80)

print(f"\nAlias map keys: {list(qs.query.alias_map.keys())}")
print(f"Expected: ['T0', 'book_alice', 'book_jane'] or similar")

if 'book_alice' in qs.query.alias_map and 'book_jane' in qs.query.alias_map:
    print("✓ PASS: Both aliases are in the alias_map")
else:
    print("✗ FAIL: One or both aliases are missing from alias_map")
    print(f"  book_alice present: {'book_alice' in qs.query.alias_map}")
    print(f"  book_jane present: {'book_jane' in qs.query.alias_map}")

print("\n" + "=" * 80)
print("Test 3: Verify the Join.equals() method behavior")
print("=" * 80)

from django.db.models.sql.datastructures import Join
from django.db.models.fields.related import ForeignKey

# Create two joins with same relation but different filtered_relation
join1 = Join(
    table_name='filtered_relation_book',
    parent_alias='T0',
    table_alias='book_alice',
    join_type='LEFT OUTER',
    join_field=Book._meta.get_field('author'),
    nullable=True,
    filtered_relation=Q(book__title__icontains='Alice'),
)

join2 = Join(
    table_name='filtered_relation_book',
    parent_alias='T0',
    table_alias='book_jane',
    join_type='LEFT OUTER',
    join_field=Book._meta.get_field('author'),
    nullable=True,
    filtered_relation=Q(book__title__icontains='Jane'),
)

print(f"\njoin1.equals(join2): {join1.equals(join2)}")
print(f"join1 == join2: {join1 == join2}")
print(f"Expected equals(): False (they have different filtered_relation)")
print(f"Expected ==: False (they have different filtered_relation)")

if not join1.equals(join2):
    print("✓ PASS: equals() correctly returns False for different filtered_relations")
else:
    print("✗ FAIL: equals() incorrectly returns True for different filtered_relations")
