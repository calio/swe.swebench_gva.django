"""
Test to reproduce the issue with through_fields not being hashable
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
sys.path.insert(0, os.path.dirname(__file__))

# Import after path setup
from django.conf import settings
if not settings.configured:
    from tests.test_sqlite import *

django.setup()

from django.db import models
from django.test import TestCase

# Create test models
class Parent(models.Model):
    name = models.CharField(max_length=256)
    class Meta:
        app_label = 'test_app'

class ProxyParent(Parent):
    class Meta:
        proxy = True
        app_label = 'test_app'

class Child(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    many_to_many_field = models.ManyToManyField(
        to=Parent,
        through="ManyToManyModel",
        through_fields=['child', 'parent'],
        related_name="something"
    )
    class Meta:
        app_label = 'test_app'

class ManyToManyModel(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='+')
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='+')
    second_child = models.ForeignKey(Child, on_delete=models.CASCADE, null=True, default=None)
    class Meta:
        app_label = 'test_app'

# Test hashing
print("Testing ManyToManyRel hashing with through_fields...")
field = Child._meta.get_field('many_to_many_field')
rel = field.remote_field

print(f"Field: {field}")
print(f"Remote field: {rel}")
print(f"Through fields: {rel.through_fields}")
print(f"Through fields type: {type(rel.through_fields)}")

try:
    h = hash(rel)
    print(f"✓ Hash successful: {h}")
except TypeError as e:
    print(f"✗ Hash failed with TypeError: {e}")
    import traceback
    traceback.print_exc()
