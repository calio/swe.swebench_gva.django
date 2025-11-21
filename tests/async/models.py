from django.db import models
from django.utils import timezone


class RelatedModel(models.Model):
    simple = models.ForeignKey("SimpleModel", models.CASCADE, null=True)


class SimpleModel(models.Model):
    field = models.IntegerField()
    created = models.DateTimeField(default=timezone.now)


class M2MModel(models.Model):
    name = models.CharField(max_length=100)


class M2MRelatedModel(models.Model):
    name = models.CharField(max_length=100)
    m2m_models = models.ManyToManyField(M2MModel, related_name="m2m_related")
