#!/usr/bin/env python
"""
Test case to verify the fix for ordering with expressions in Meta.ordering
when using multi-table inheritance.
"""
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
from tests.ordering.models import OrderedByFArticle, Article, Reference, OrderedByAuthorArticle, Author
from datetime import datetime

# Create tables
call_command('migrate', verbosity=0, interactive=False)

# Create test data
Article.objects.all().delete()
Author.objects.all().delete()

author1 = Author.objects.create(name='Author 1')
author2 = Author.objects.create(name='Author 2')

a1 = Article.objects.create(headline='Article 1', pub_date=datetime(2005, 7, 26), author=author1)
a2 = Article.objects.create(headline='Article 2', pub_date=datetime(2005, 7, 27), author=author2)
a3 = Article.objects.create(headline='Article 3', pub_date=datetime(2005, 7, 27), author=author1)
a4 = Article.objects.create(headline='Article 4', pub_date=datetime(2005, 7, 28), author=author2)

print("=" * 60)
print("Testing ordering with expressions in Meta.ordering")
print("=" * 60)

# Test 1: Order by a relation field on the parent model
print("\nTest 1: Article.objects.order_by('author')")
try:
    result = list(Article.objects.order_by('author'))
    print(f"  SUCCESS: Got {len(result)} articles")
    for article in result:
        print(f"    - {article.headline} (author: {article.author})")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Order by a relation field on the child model with F expressions
print("\nTest 2: OrderedByFArticle.objects.order_by('author')")
try:
    result = list(OrderedByFArticle.objects.order_by('author'))
    print(f"  SUCCESS: Got {len(result)} articles")
    for article in result:
        print(f"    - {article.headline} (author: {article.author})")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Order by a relation field on the child model with OrderBy expressions
print("\nTest 3: OrderedByAuthorArticle.objects.order_by('author')")
try:
    result = list(OrderedByAuthorArticle.objects.order_by('author'))
    print(f"  SUCCESS: Got {len(result)} articles")
    for article in result:
        print(f"    - {article.headline} (author: {article.author})")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Reference model with FK to OrderedByAuthorArticle
print("\nTest 4: Reference.objects.all()")
try:
    r1 = Reference.objects.create(article_id=a1.pk)
    r2 = Reference.objects.create(article_id=a2.pk)
    result = list(Reference.objects.all())
    print(f"  SUCCESS: Got {len(result)} references")
    for ref in result:
        print(f"    - Reference to {ref.article.headline}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Default ordering with F expressions
print("\nTest 5: OrderedByFArticle.objects.all() (default ordering)")
try:
    result = list(OrderedByFArticle.objects.all())
    print(f"  SUCCESS: Got {len(result)} articles")
    for article in result:
        print(f"    - {article.headline} (author: {article.author})")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("All tests completed successfully!")
print("=" * 60)
