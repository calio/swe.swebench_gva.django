from django.db.models import Count
from django.db.models.functions import Random
from django.test import TestCase

from ..models import FloatModel, IntegerModel


class RandomTests(TestCase):
    def test(self):
        FloatModel.objects.create()
        obj = FloatModel.objects.annotate(random=Random()).first()
        self.assertIsInstance(obj.random, float)
        self.assertGreaterEqual(obj.random, 0)
        self.assertLess(obj.random, 1)

    def test_order_by_random_with_aggregation(self):
        """Test that order_by('?') doesn't break aggregation."""
        # Create test data
        obj1 = IntegerModel.objects.create()
        obj2 = IntegerModel.objects.create()
        
        # Test that order_by('?') with aggregation works correctly
        # The aggregation should not be broken by the random ordering
        qs = IntegerModel.objects.annotate(count=Count('id')).order_by('?')
        results = list(qs.values('id', 'count'))
        
        # Should have 2 results, each with count=1
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertEqual(result['count'], 1)
