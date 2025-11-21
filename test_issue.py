#!/usr/bin/env python
"""
Test script to reproduce the serialization issue with m2m relations
and custom managers using select_related.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.db import models
from django.core import serializers
from tests.serializers.models.base import Category, Article, Author
from datetime import datetime

# Create test data
print("Creating test data...")
author = Author.objects.create(name="Test Author")
category = Category.objects.create(name="Test Category")
article = Article.objects.create(
    author=author,
    headline="Test Article",
    pub_date=datetime.now()
)
article.categories.add(category)
article.save()

print("Attempting to serialize article with m2m field...")
try:
    result = serializers.serialize("json", [article])
    print("SUCCESS: Serialization worked!")
    print(result)
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
