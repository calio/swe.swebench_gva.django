from django.db import models

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
