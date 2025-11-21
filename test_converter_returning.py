"""Test to reproduce the converter issue with returning fields."""
import datetime
from django.db import models
from django.test import TestCase, skipUnlessDBFeature
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

# Create test models
class AutoModel(models.Model):
    id = MyAutoField(primary_key=True)
    
    class Meta:
        app_label = 'queries'

class AutoModelWithOtherField(models.Model):
    id = MyAutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True, db_returning=True)
    
    class Meta:
        app_label = 'queries'

# Test cases
@skipUnlessDBFeature('can_return_columns_from_insert')
class ConverterReturningFieldsTests(TestCase):
    def test_create_applies_converter(self):
        """Test that create() applies from_db_value converter to returned fields."""
        am = AutoModel.objects.create()
        self.assertIsInstance(am.id, MyIntWrapper, 
            f"Expected MyIntWrapper but got {type(am.id)}")
    
    def test_bulk_create_applies_converter(self):
        """Test that bulk_create() applies from_db_value converter to returned fields."""
        ams = [AutoModel()]
        AutoModel.objects.bulk_create(ams)
        self.assertIsInstance(ams[0].id, MyIntWrapper,
            f"Expected MyIntWrapper but got {type(ams[0].id)}")
    
    def test_query_applies_converter(self):
        """Test that normal queries apply from_db_value converter."""
        am = AutoModel.objects.create()
        am2 = AutoModel.objects.first()
        self.assertIsInstance(am2.id, MyIntWrapper,
            f"Expected MyIntWrapper but got {type(am2.id)}")

if __name__ == '__main__':
    import sys
    from django.core.management import call_command
    
    # Run the tests
    call_command('test', 'test_converter_returning', verbosity=2)
