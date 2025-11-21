from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=32, null=True)
    price = models.IntegerField(null=True)
    discounted_price = models.IntegerField(null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gt=models.F('discounted_price')),
                name='price_gt_discounted_price',
            ),
            models.UniqueConstraint(fields=['name', 'color'], name='name_color_uniq'),
            models.UniqueConstraint(
                fields=['name'],
                name='name_without_color_uniq',
                condition=models.Q(color__isnull=True),
            ),
        ]


class TestConstraint(models.Model):
    field_1 = models.IntegerField(blank=True, null=True)
    flag = models.BooleanField(blank=False, null=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(flag__exact=True, field_1__isnull=False) |
                      models.Q(flag__exact=False),
                name='field_1_has_value_if_flag_set',
            ),
        ]
