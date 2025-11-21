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
            'tests.ordering',
        ],
        USE_TZ=True,
    )
    django.setup()

from django.core.management import call_command
from tests.ordering.models import OrderedByFArticle, Article, Reference, OrderedByAuthorArticle
from datetime import datetime

# Create tables
call_command('migrate', verbosity=0, interactive=False)

# Create test data
Article.objects.all().delete()
a1 = Article.objects.create(headline='Article 1', pub_date=datetime(2005, 7, 26))

# Try to order by a relation field on the parent model
print("Test 1: Article.objects.order_by('author')")
try:
    result = list(Article.objects.order_by('author'))
    print('  SUCCESS')
except Exception as e:
    print(f'  ERROR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()

# Try with OrderedByFArticle which has F expressions in Meta.ordering
print("\nTest 2: OrderedByFArticle.objects.order_by('author')")
try:
    result = list(OrderedByFArticle.objects.order_by('author'))
    print('  SUCCESS')
except Exception as e:
    print(f'  ERROR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()

# Try with Reference which has a FK to OrderedByAuthorArticle
print("\nTest 3: Reference.objects.all()")
try:
    result = list(Reference.objects.all())
    print('  SUCCESS')
except Exception as e:
    print(f'  ERROR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()

# Try with OrderedByAuthorArticle
print("\nTest 4: OrderedByAuthorArticle.objects.all()")
try:
    result = list(OrderedByAuthorArticle.objects.all())
    print('  SUCCESS')
except Exception as e:
    print(f'  ERROR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
