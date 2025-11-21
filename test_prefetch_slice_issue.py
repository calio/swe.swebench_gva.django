"""
Test to reproduce the Prefetch with slice issue
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
        ],
    )

django.setup()

from django.test import TestCase
from django.db.models import Prefetch
from tests.prefetch_related.models import Book, Author

class PrefetchSliceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.book1 = Book.objects.create(title='Book 1')
        cls.book2 = Book.objects.create(title='Book 2')
        
        cls.author1 = Author.objects.create(name='Author 1', first_book=cls.book1)
        cls.author2 = Author.objects.create(name='Author 2', first_book=cls.book1)
        cls.author3 = Author.objects.create(name='Author 3', first_book=cls.book1)
        cls.author4 = Author.objects.create(name='Author 4', first_book=cls.book1)
        
        cls.book1.authors.add(cls.author1, cls.author2, cls.author3, cls.author4)
        cls.book2.authors.add(cls.author1, cls.author2)
    
    def test_prefetch_with_slice(self):
        """Test that Prefetch works with sliced querysets"""
        result = list(Book.objects.prefetch_related(
            Prefetch('authors', queryset=Author.objects.all()[:2], to_attr='example_authors')
        ))
        
        # Should have 2 books
        self.assertEqual(len(result), 2)
        
        # First book should have 2 example authors (sliced to 2)
        self.assertEqual(len(result[0].example_authors), 2)
        
        # Second book should have 2 example authors (sliced to 2)
        self.assertEqual(len(result[1].example_authors), 2)

if __name__ == '__main__':
    import unittest
    unittest.main()
