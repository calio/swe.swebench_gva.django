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
        ],
        SECRET_KEY='test-secret-key',
    )
    django.setup()

from django.db import models

# Define test models
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

# Try to trigger the issue
try:
    print("Running model checks...")
    errors = Child.check()
    if errors:
        print(f"Errors found: {errors}")
    else:
        print("✓ Model checks passed!")
except TypeError as e:
    print(f"✗ TypeError occurred: {e}")
    import traceback
    traceback.print_exc()
