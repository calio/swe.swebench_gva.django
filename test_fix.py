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
from django.db.models import F, Sum, Avg, Min, Max
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
book1 = Book.objects.create(
    isbn='123456789',
    name='Test Book 1',
    pages=100,
    rating=4.5,
    price=10.00,
    contact=author,
    publisher=publisher,
    pubdate=date.today()
)
book1.authors.add(author)

book2 = Book.objects.create(
    isbn='987654321',
    name='Test Book 2',
    pages=200,
    rating=3.5,
    price=20.00,
    contact=author,
    publisher=publisher,
    pubdate=date.today()
)
book2.authors.add(author)

print("Testing aggregate() with 'default' after annotate():")
print("=" * 60)

# Test 1: Sum with default after annotate
print("\n1. Sum with default after annotate:")
try:
    result = Book.objects.annotate(idx=F('id')).aggregate(Sum('pages', default=0))
    print(f"   ✓ Result: {result}")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")

# Test 2: Avg with default after annotate
print("\n2. Avg with default after annotate:")
try:
    result = Book.objects.annotate(idx=F('id')).aggregate(Avg('rating', default=0))
    print(f"   ✓ Result: {result}")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")

# Test 3: Min with default after annotate
print("\n3. Min with default after annotate:")
try:
    result = Book.objects.annotate(idx=F('id')).aggregate(Min('pages', default=0))
    print(f"   ✓ Result: {result}")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")

# Test 4: Max with default after annotate
print("\n4. Max with default after annotate:")
try:
    result = Book.objects.annotate(idx=F('id')).aggregate(Max('pages', default=0))
    print(f"   ✓ Result: {result}")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")

# Test 5: Multiple aggregates with defaults after annotate
print("\n5. Multiple aggregates with defaults after annotate:")
try:
    result = Book.objects.annotate(idx=F('id')).aggregate(
        total_pages=Sum('pages', default=0),
        avg_rating=Avg('rating', default=0),
        min_pages=Min('pages', default=0),
    )
    print(f"   ✓ Result: {result}")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")

# Test 6: Empty queryset with default after annotate
print("\n6. Empty queryset with default after annotate:")
try:
    result = Book.objects.filter(pages__gt=1000).annotate(idx=F('id')).aggregate(Sum('pages', default=0))
    print(f"   ✓ Result: {result}")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")

# Test 7: Aggregate without default after annotate (should still work)
print("\n7. Aggregate without default after annotate:")
try:
    result = Book.objects.annotate(idx=F('id')).aggregate(Sum('pages'))
    print(f"   ✓ Result: {result}")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("All tests completed successfully!")
