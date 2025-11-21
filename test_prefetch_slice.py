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
            'tests.prefetch_related',
        ],
        USE_TZ=True,
    )

django.setup()

from django.core.management import call_command
from tests.prefetch_related.models import Book, Author
from django.db.models import Prefetch

# Create tables
call_command('migrate', '--run-syncdb', verbosity=0)

# Create test data
book1 = Book.objects.create(title='Book 1')
book2 = Book.objects.create(title='Book 2')
book3 = Book.objects.create(title='Book 3')
book4 = Book.objects.create(title='Book 4')

author1 = Author.objects.create(name='Author 1', first_book=book1)
author2 = Author.objects.create(name='Author 2', first_book=book1)
author3 = Author.objects.create(name='Author 3', first_book=book1)
author4 = Author.objects.create(name='Author 4', first_book=book1)

book1.authors.add(author1, author2, author3, author4)

# Try to use Prefetch with sliced queryset
print("Testing Prefetch with sliced queryset...")
try:
    result = list(Book.objects.prefetch_related(
        Prefetch('authors', queryset=Author.objects.all()[:2], to_attr='example_authors')
    ))
    print('✓ SUCCESS: Prefetch with slice worked!')
    print(f'  First book has {len(result[0].example_authors)} example authors')
except TypeError as e:
    print(f'✗ ERROR: {e}')
    sys.exit(1)
