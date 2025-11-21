from django.db.models import Exists, OuterRef, Q
from django.test import TestCase
from .models import Number, Item

class OuterRefExcludeTest(TestCase):
    def test_exists_exclude(self):
        # filter()
        qs = Number.objects.annotate(
            foo=Exists(
                Item.objects.filter(tags__category_id=OuterRef('pk'))
            )
        ).filter(foo=True)
        print('Test 1 (filter): SUCCESS')
        
        # exclude()
        qs = Number.objects.annotate(
            foo=Exists(
                Item.objects.exclude(tags__category_id=OuterRef('pk'))
            )
        ).filter(foo=True)
        print('Test 2 (exclude): SUCCESS')
        
        # filter(~Q())
        qs = Number.objects.annotate(
            foo=Exists(
                Item.objects.filter(~Q(tags__category_id=OuterRef('pk')))
            )
        ).filter(foo=True)
        print('Test 3 (filter ~Q): SUCCESS')
