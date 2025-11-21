from django.forms.models import inlineformset_factory
from django.test import TestCase

from .models import (
    AutoPKChildOfUUIDPKParent,
    AutoPKParent,
    ChildRelatedViaAK,
    ChildWithEditablePK,
    ParentWithUUIDAlternateKey,
    UUIDPKChild,
    UUIDPKChildOfAutoPKParent,
    UUIDPKParent,
)


class InlineFormsetTests(TestCase):
    def test_inlineformset_factory_nulls_default_pks(self):
        """
        #24377 - If we're adding a new object, a parent's auto-generated pk
        from the model field default should be ignored as it's regenerated on
        the save request.

        Tests the case where both the parent and child have a UUID primary key.
        """
        FormSet = inlineformset_factory(UUIDPKParent, UUIDPKChild, fields="__all__")
        formset = FormSet()
        self.assertIsNone(formset.forms[0].fields["parent"].initial)
        # The parent instance should retain its UUID value
        self.assertIsNotNone(formset.instance.uuid)

    def test_inlineformset_factory_ignores_default_pks_on_submit(self):
        """
        #24377 - Inlines with a model field default should ignore that default
        value to avoid triggering validation on empty forms.
        """
        FormSet = inlineformset_factory(UUIDPKParent, UUIDPKChild, fields="__all__")
        formset = FormSet(
            {
                "uuidpkchild_set-TOTAL_FORMS": 3,
                "uuidpkchild_set-INITIAL_FORMS": 0,
                "uuidpkchild_set-MAX_NUM_FORMS": "",
                "uuidpkchild_set-0-name": "Foo",
                "uuidpkchild_set-1-name": "",
                "uuidpkchild_set-2-name": "",
            }
        )
        self.assertTrue(formset.is_valid())

    def test_inlineformset_factory_nulls_default_pks_uuid_parent_auto_child(self):
        """
        #24958 - Variant of test_inlineformset_factory_nulls_default_pks for
        the case of a parent object with a UUID primary key and a child object
        with an AutoField primary key.
        """
        FormSet = inlineformset_factory(
            UUIDPKParent, AutoPKChildOfUUIDPKParent, fields="__all__"
        )
        formset = FormSet()
        self.assertIsNone(formset.forms[0].fields["parent"].initial)
        # The parent instance should retain its UUID value
        self.assertIsNotNone(formset.instance.uuid)

    def test_inlineformset_factory_nulls_default_pks_auto_parent_uuid_child(self):
        """
        #24958 - Variant of test_inlineformset_factory_nulls_default_pks for
        the case of a parent object with an AutoField primary key and a child
        object with a UUID primary key.
        """
        FormSet = inlineformset_factory(
            AutoPKParent, UUIDPKChildOfAutoPKParent, fields="__all__"
        )
        formset = FormSet()
        self.assertIsNone(formset.forms[0].fields["parent"].initial)
        # The parent instance should retain its pk value (None for new objects)
        # since AutoField doesn't have a default value like UUID does
        self.assertIsNone(formset.instance.pk)

    def test_inlineformset_factory_nulls_default_pks_child_editable_pk(self):
        """
        #24958 - Variant of test_inlineformset_factory_nulls_default_pks for
        the case of a parent object with a UUID primary key and a child
        object with an editable natural key for a primary key.
        """
        FormSet = inlineformset_factory(
            UUIDPKParent, ChildWithEditablePK, fields="__all__"
        )
        formset = FormSet()
        self.assertIsNone(formset.forms[0].fields["parent"].initial)
        # The parent instance should retain its UUID value
        self.assertIsNotNone(formset.instance.uuid)

    def test_inlineformset_factory_nulls_default_pks_alternate_key_relation(self):
        """
        #24958 - Variant of test_inlineformset_factory_nulls_default_pks for
        the case of a parent object with a UUID alternate key and a child
        object that relates to that alternate key.
        """
        FormSet = inlineformset_factory(
            ParentWithUUIDAlternateKey, ChildRelatedViaAK, fields="__all__"
        )
        formset = FormSet()
        self.assertIsNone(formset.forms[0].fields["parent"].initial)
        # The parent instance should retain its UUID value
        self.assertIsNotNone(formset.instance.uuid)

    def test_inlineformset_factory_preserves_uuid_on_save(self):
        """
        Test that when saving an inline formset with a UUID parent and child,
        the parent's UUID is preserved and not set to NULL.
        """
        # Create a parent instance
        parent = UUIDPKParent(name="Parent")
        FormSet = inlineformset_factory(
            UUIDPKParent, AutoPKChildOfUUIDPKParent, fields="__all__"
        )
        formset = FormSet(
            {
                "autopkchildofuuidpkparent_set-TOTAL_FORMS": 1,
                "autopkchildofuuidpkparent_set-INITIAL_FORMS": 0,
                "autopkchildofuuidpkparent_set-MAX_NUM_FORMS": "",
                "autopkchildofuuidpkparent_set-0-name": "Child",
            },
            instance=parent,
        )
        self.assertTrue(formset.is_valid())
        # Verify the parent's UUID is not None before saving
        self.assertIsNotNone(parent.uuid)
        parent_uuid = parent.uuid
        # Save the parent first
        parent.save()
        # Save the formset (children)
        formset.save()
        # Verify the parent was saved with the same UUID (not NULL)
        saved_parent = UUIDPKParent.objects.get(uuid=parent_uuid)
        self.assertIsNotNone(saved_parent.uuid)
        self.assertEqual(saved_parent.uuid, parent_uuid)
        # Verify the child was created with the correct parent
        child = AutoPKChildOfUUIDPKParent.objects.get(name="Child")
        self.assertEqual(child.parent.uuid, parent_uuid)
