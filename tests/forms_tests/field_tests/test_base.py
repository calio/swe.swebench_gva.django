import copy

from django.forms import ChoiceField, Field, Form, Select
from django.test import SimpleTestCase


class BasicFieldsTests(SimpleTestCase):

    def test_field_sets_widget_is_required(self):
        self.assertTrue(Field(required=True).widget.is_required)
        self.assertFalse(Field(required=False).widget.is_required)

    def test_cooperative_multiple_inheritance(self):
        class A:
            def __init__(self):
                self.class_a_var = True
                super().__init__()

        class ComplexField(Field, A):
            def __init__(self):
                super().__init__()

        f = ComplexField()
        self.assertTrue(f.class_a_var)

    def test_field_deepcopies_widget_instance(self):
        class CustomChoiceField(ChoiceField):
            widget = Select(attrs={'class': 'my-custom-class'})

        class TestForm(Form):
            field1 = CustomChoiceField(choices=[])
            field2 = CustomChoiceField(choices=[])

        f = TestForm()
        f.fields['field1'].choices = [('1', '1')]
        f.fields['field2'].choices = [('2', '2')]
        self.assertEqual(f.fields['field1'].widget.choices, [('1', '1')])
        self.assertEqual(f.fields['field2'].widget.choices, [('2', '2')])

    def test_field_deepcopies_error_messages(self):
        """Test that deepcopy creates independent error_messages dictionaries."""
        field1 = Field(error_messages={'required': 'Custom required message'})
        field2 = copy.deepcopy(field1)
        
        # Modify error_messages in field2
        field2.error_messages['required'] = 'Modified message'
        
        # field1's error_messages should not be affected
        self.assertEqual(field1.error_messages['required'], 'Custom required message')
        self.assertEqual(field2.error_messages['required'], 'Modified message')
        
        # Verify they are different dictionaries
        self.assertIsNot(field1.error_messages, field2.error_messages)

    def test_form_field_instances_have_independent_error_messages(self):
        """
        Test that form instances have independent error_messages for their fields.
        This is the real-world scenario described in the issue.
        """
        class TestForm(Form):
            name = Field()

        # Create two form instances
        form1 = TestForm()
        form2 = TestForm()
        
        # Modify error_messages in form1
        form1.fields['name'].error_messages['required'] = 'Form1 required'
        
        # form2's error_messages should not be affected
        self.assertNotEqual(
            form2.fields['name'].error_messages['required'],
            'Form1 required'
        )
        self.assertEqual(
            form1.fields['name'].error_messages['required'],
            'Form1 required'
        )


class DisabledFieldTests(SimpleTestCase):
    def test_disabled_field_has_changed_always_false(self):
        disabled_field = Field(disabled=True)
        self.assertFalse(disabled_field.has_changed('x', 'y'))
