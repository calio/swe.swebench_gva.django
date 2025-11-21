#!/usr/bin/env python
"""
Test script to verify the fix for serialization with custom manager using select_related.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings manually
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
            'tests.serializers',
        ],
        SECRET_KEY='test-secret-key',
    )

django.setup()

from django.db import models, connection
from django.core import serializers
from tests.serializers.models.base import Category, Topic, ArticleWithTopics

# Create tables
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(Category)
    schema_editor.create_model(Topic)
    schema_editor.create_model(ArticleWithTopics)
    schema_editor.create_model(ArticleWithTopics._meta.get_field('topics').remote_field.through)

# Create test data
print("Creating test data...")
category = Category.objects.create(name="Test Category")
topic = Topic.objects.create(name="Test Topic", category=category)
article = ArticleWithTopics.objects.create(headline="Test Article")
article.topics.add(topic)

print("Attempting to serialize article with m2m field (custom manager with select_related)...")
try:
    result = serializers.serialize("json", [article])
    print("✓ SUCCESS: Serialization worked!")
    print("Serialized data:")
    print(result)
except Exception as e:
    print(f"✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
