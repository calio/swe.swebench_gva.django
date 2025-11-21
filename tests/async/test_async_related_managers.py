from asgiref.sync import async_to_sync

from django.test import TestCase

from .models import M2MModel, M2MRelatedModel, RelatedModel, SimpleModel


class AsyncRelatedManagerTest(TestCase):
    """Test async methods on related managers (reverse FK)."""

    async def test_acreate_on_reverse_fk(self):
        """Test acreate() on reverse FK relation."""
        simple = await SimpleModel.objects.acreate(field=1)
        # Create a related object using acreate
        related = await simple.relatedmodel_set.acreate()
        self.assertEqual(related.simple_id, simple.id)
        self.assertIsNotNone(related.id)

    async def test_aget_or_create_on_reverse_fk(self):
        """Test aget_or_create() on reverse FK relation."""
        simple = await SimpleModel.objects.acreate(field=2)
        # Get or create a related object
        related, created = await simple.relatedmodel_set.aget_or_create()
        self.assertTrue(created)
        self.assertEqual(related.simple_id, simple.id)
        # Try again, should not create
        related2, created = await simple.relatedmodel_set.aget_or_create()
        self.assertFalse(created)
        self.assertEqual(related, related2)

    async def test_aupdate_or_create_on_reverse_fk(self):
        """Test aupdate_or_create() on reverse FK relation."""
        simple = await SimpleModel.objects.acreate(field=3)
        # Update or create a related object
        related, created = await simple.relatedmodel_set.aupdate_or_create()
        self.assertTrue(created)
        self.assertEqual(related.simple_id, simple.id)
        # Try again, should not create
        related2, created = await simple.relatedmodel_set.aupdate_or_create()
        self.assertFalse(created)
        self.assertEqual(related, related2)


class AsyncM2MManagerTest(TestCase):
    """Test async methods on M2M managers."""

    async def test_acreate_on_m2m(self):
        """Test acreate() on M2M relation."""
        m2m_related = await M2MRelatedModel.objects.acreate(name="test")
        # Create a related object using acreate
        m2m = await m2m_related.m2m_models.acreate(name="m2m_obj")
        self.assertIsNotNone(m2m.id)
        # Check that the relationship was created
        self.assertTrue(await m2m_related.m2m_models.filter(id=m2m.id).aexists())

    async def test_aget_or_create_on_m2m(self):
        """Test aget_or_create() on M2M relation."""
        m2m_related = await M2MRelatedModel.objects.acreate(name="test2")
        # Get or create a related object
        m2m, created = await m2m_related.m2m_models.aget_or_create(name="m2m_obj2")
        self.assertTrue(created)
        self.assertIsNotNone(m2m.id)
        # Check that the relationship was created
        self.assertTrue(await m2m_related.m2m_models.filter(id=m2m.id).aexists())
        # Try again, should not create
        m2m2, created = await m2m_related.m2m_models.aget_or_create(name="m2m_obj2")
        self.assertFalse(created)
        self.assertEqual(m2m, m2m2)

    async def test_aupdate_or_create_on_m2m(self):
        """Test aupdate_or_create() on M2M relation."""
        m2m_related = await M2MRelatedModel.objects.acreate(name="test3")
        # Update or create a related object
        m2m, created = await m2m_related.m2m_models.aupdate_or_create(
            name="m2m_obj3", defaults={"name": "m2m_obj3"}
        )
        self.assertTrue(created)
        self.assertIsNotNone(m2m.id)
        # Check that the relationship was created
        self.assertTrue(await m2m_related.m2m_models.filter(id=m2m.id).aexists())
        # Try again, should not create
        m2m2, created = await m2m_related.m2m_models.aupdate_or_create(
            name="m2m_obj3", defaults={"name": "m2m_obj3_updated"}
        )
        self.assertFalse(created)
        self.assertEqual(m2m.id, m2m2.id)
