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
from datetime import datetime

# Create test models with custom manager
class TestTagMaster(models.Model):
    name = models.CharField(max_length=120)
    
    class Meta:
        app_label = 'serializers'

class TestTagManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related("master")  # follow master when retrieving object by default
        return qs

class TestTag(models.Model):
    objects = TestTagManager()
    name = models.CharField(max_length=120)
    master = models.ForeignKey(TestTagMaster, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        app_label = 'serializers'

class Test(models.Model):
    name = models.CharField(max_length=120)
    tags = models.ManyToManyField(TestTag, blank=True)
    
    class Meta:
        app_label = 'serializers'

# Create tables
from django.db import connection
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(TestTagMaster)
    schema_editor.create_model(TestTag)
    schema_editor.create_model(Test)
    schema_editor.create_model(Test._meta.get_field('tags').remote_field.through)

# Create test data
print("Creating test data...")
tag_master = TestTagMaster.objects.create(name="master")
tag = TestTag.objects.create(name="tag", master=tag_master)
test = Test.objects.create(name="test")
test.tags.add(tag)
test.save()

print("Attempting to serialize test object with m2m field...")
try:
    result = serializers.serialize("json", [test])
    print("SUCCESS: Serialization worked!")
    print(result)
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
