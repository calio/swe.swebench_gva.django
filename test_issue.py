import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
sys.path.insert(0, '/Users/calio/swebench_gva/django__django-15375')

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
            'tests.aggregation',
        ],
        USE_TZ=True,
    )

django.setup()

from django.db import connection
from django.db.models import F, Sum
from tests.aggregation.models import Book, Author, Publisher
from datetime import date

# Create tables
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(Author)
    schema_editor.create_model(Publisher)
    schema_editor.create_model(Book)

# Create test data
author = Author.objects.create(name='Test Author', age=30)
publisher = Publisher.objects.create(name='Test Publisher', num_awards=0)
book = Book.objects.create(
    isbn='123456789',
    name='Test Book',
    pages=100,
    rating=4.5,
    price=10.00,
    contact=author,
    publisher=publisher,
    pubdate=date.today()
)
book.authors.add(author)

# Test 1: annotate + aggregate without default (should work)
print('Test 1: annotate + aggregate without default')
try:
    result = Book.objects.annotate(idx=F('id')).aggregate(Sum('id'))
    print(f'  Result: {result}')
except Exception as e:
    print(f'  Error: {type(e).__name__}: {e}')

# Test 2: annotate + aggregate with default (should fail)
print('\nTest 2: annotate + aggregate with default')
try:
    result = Book.objects.annotate(idx=F('id')).aggregate(Sum('id', default=0))
    print(f'  Result: {result}')
except Exception as e:
    print(f'  Error: {type(e).__name__}: {e}')

# Test 3: aggregate with default without annotate (should work)
print('\nTest 3: aggregate with default without annotate')
try:
    result = Book.objects.aggregate(Sum('id', default=0))
    print(f'  Result: {result}')
except Exception as e:
    print(f'  Error: {type(e).__name__}: {e}')

# Test 4: Print the SQL for Test 2
print('\nTest 4: Print SQL for annotate + aggregate with default')
try:
    qs = Book.objects.annotate(idx=F('id')).aggregate(Sum('id', default=0))
except Exception as e:
    pass

# Let's check the query
from django.db.models.sql.compiler import SQLAggregateCompiler
qs = Book.objects.annotate(idx=F('id'))
print(f'Query after annotate: {qs.query}')
print(f'Query annotation_select: {qs.query.annotation_select}')

# Now let's see what happens when we aggregate
from django.db.models import Sum as SumAggregate
agg = SumAggregate('id', default=0)
print(f'Aggregate before resolve: {agg}')
print(f'Aggregate default: {agg.default}')

# Resolve the aggregate
resolved_agg = agg.resolve_expression(qs.query)
print(f'Aggregate after resolve: {resolved_agg}')
print(f'Aggregate type after resolve: {type(resolved_agg).__name__}')
