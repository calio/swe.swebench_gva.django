from django.db import models


class Classification(models.Model):
    code = models.CharField(max_length=10)


class Employee(models.Model):
    name = models.CharField(max_length=40, blank=False, null=False)
    salary = models.PositiveIntegerField()
    department = models.CharField(max_length=40, blank=False, null=False)
    hire_date = models.DateField(blank=False, null=False)
    age = models.IntegerField(blank=False, null=False)
    classification = models.ForeignKey('Classification', on_delete=models.CASCADE, null=True)


class FilterableModel(models.Model):
    """Model with a 'filterable' field to test the check_filterable bug."""
    name = models.CharField(max_length=40)
    filterable = models.BooleanField(default=False)


class RelatedModel(models.Model):
    """Model that references FilterableModel."""
    value = models.CharField(max_length=100)
    filterable_ref = models.ForeignKey('FilterableModel', on_delete=models.CASCADE)
