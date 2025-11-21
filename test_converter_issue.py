"""Test to reproduce the converter issue with returning fields."""
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
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'test_db',
                'USER': 'postgres',
                'PASSWORD': 'postgres',
                'HOST': 'localhost',
                'PORT': '5432',
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
from django.db.models import BigAutoField

# Create a wrapper class
class MyIntWrapper:
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return f'<MyIntWrapper: {self.value}>'
    
    def __eq__(self, other):
        if isinstance(other, MyIntWrapper):
            return self.value == other.value
        return self.value == other
    
    def __int__(self):
        return self.value

# Create a custom field with from_db_value converter
class MyAutoField(BigAutoField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        return MyIntWrapper(value)
    
    def get_prep_value(self, value):
        if value is None:
            return None
        if isinstance(value, MyIntWrapper):
            return int(value)
        return int(value)

# Create a test model
class AutoModel(models.Model):
    id = MyAutoField(primary_key=True)
    
    class Meta:
        app_label = 'test_app'

# Test the issue
if __name__ == '__main__':
    # Check if we can connect to the database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("Database connection successful")
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Skipping test - database not available")
        sys.exit(0)
    
    # Create the table
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor
    
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(AutoModel)
    
    print("\nTesting converter issue:")
    print("=" * 50)
    
    # Test 1: Create and check if converter is applied
    print("\nTest 1: Create with .create()")
    am = AutoModel.objects.create()
    print(f"am.id = {am.id}")
    print(f"type(am.id) = {type(am.id)}")
    print(f"Is MyIntWrapper? {isinstance(am.id, MyIntWrapper)}")
    
    # Test 2: Query and check if converter is applied
    print("\nTest 2: Query with .first()")
    am2 = AutoModel.objects.first()
    print(f"am2.id = {am2.id}")
    print(f"type(am2.id) = {type(am2.id)}")
    print(f"Is MyIntWrapper? {isinstance(am2.id, MyIntWrapper)}")
    
    # Test 3: bulk_create and check if converter is applied
    print("\nTest 3: bulk_create()")
    ams = [AutoModel()]
    AutoModel.objects.bulk_create(ams)
    print(f"ams[0].id = {ams[0].id}")
    print(f"type(ams[0].id) = {type(ams[0].id)}")
    print(f"Is MyIntWrapper? {isinstance(ams[0].id, MyIntWrapper)}")
    
    # Clean up
    with connection.schema_editor() as schema_editor:
        schema_editor.delete_model(AutoModel)
