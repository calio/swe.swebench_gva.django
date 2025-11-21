#!/usr/bin/env python
"""
Test script to reproduce the issue: Migration crashes deleting an index_together 
if there is a unique_together on the same fields.

This reproduces the exact scenario described in the issue:
1) Create models with 2 fields, add 2 same fields to unique_together and to index_together
2) Delete index_together -> Should not fail
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
        ],
        USE_TZ=True,
    )
    django.setup()

from django.db import models, connection
from django.db.migrations.executor import MigrationExecutor
from django.apps import AppConfig, apps
from django.apps.registry import Apps

# Create a test app
test_apps = Apps()

class TestAppConfig(AppConfig):
    name = 'test_app'
    label = 'test_app'

# Register the app
test_app_config = TestAppConfig('test_app', None)
test_apps.populate([test_app_config])

class TestModel(models.Model):
    """Model with both unique_together and index_together on same fields"""
    field1 = models.CharField(max_length=100)
    field2 = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'test_app'
        db_table = 'test_model'
        unique_together = [['field1', 'field2']]
        index_together = [['field1', 'field2']]

def test_delete_index_together_with_unique_together():
    """Test that we can delete index_together when unique_together exists on same fields"""
    print("Testing: Delete index_together when unique_together exists on same fields")
    print("=" * 70)
    
    # Create the table with both constraints
    with connection.schema_editor() as editor:
        editor.create_model(TestModel)
    
    print("✓ Created model with both unique_together and index_together")
    
    # Get initial constraints
    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(cursor, 'test_model')
    
    print(f"✓ Initial constraints: {list(constraints.keys())}")
    
    # Count constraints on field1, field2
    field_constraints = [
        (name, info) for name, info in constraints.items()
        if info['columns'] == ['field1', 'field2']
    ]
    print(f"✓ Constraints on (field1, field2): {len(field_constraints)}")
    for name, info in field_constraints:
        print(f"  - {name}: unique={info['unique']}, index={info['index']}")
    
    # Now try to delete index_together
    print("\nAttempting to delete index_together...")
    try:
        with connection.schema_editor() as editor:
            # Simulate removing index_together
            editor.alter_index_together(TestModel, [['field1', 'field2']], [])
        print("✓ Successfully deleted index_together!")
    except ValueError as e:
        print(f"✗ FAILED with ValueError: {e}")
        return False
    except Exception as e:
        print(f"✗ FAILED with {type(e).__name__}: {e}")
        return False
    
    # Verify the result
    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(cursor, 'test_model')
    
    print(f"\n✓ Final constraints: {list(constraints.keys())}")
    
    # Count constraints on field1, field2 after deletion
    field_constraints = [
        (name, info) for name, info in constraints.items()
        if info['columns'] == ['field1', 'field2']
    ]
    print(f"✓ Constraints on (field1, field2) after deletion: {len(field_constraints)}")
    for name, info in field_constraints:
        print(f"  - {name}: unique={info['unique']}, index={info['index']}")
    
    # Verify that unique constraint still exists but index is gone
    unique_constraints = [
        (name, info) for name, info in constraints.items()
        if info['columns'] == ['field1', 'field2'] and info['unique']
    ]
    index_constraints = [
        (name, info) for name, info in constraints.items()
        if info['columns'] == ['field1', 'field2'] and info['index'] and not info['unique']
    ]
    
    if len(unique_constraints) == 1 and len(index_constraints) == 0:
        print("\n✓ SUCCESS: unique_together preserved, index_together deleted!")
        return True
    else:
        print(f"\n✗ FAILED: Expected 1 unique constraint and 0 index constraints")
        print(f"  Got {len(unique_constraints)} unique and {len(index_constraints)} index")
        return False

if __name__ == '__main__':
    try:
        success = test_delete_index_together_with_unique_together()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
