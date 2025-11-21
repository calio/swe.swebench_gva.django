#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
sys.path.insert(0, os.path.dirname(__file__))

from django.conf import settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'tests.expressions_window',
        ],
        USE_TZ=True,
    )

django.setup()

from django.db import connection
from django.db.models import Sum, Window, F, Coalesce
from tests.expressions_window.models import Employee

# Create tables
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(Employee)

# Insert test data
Employee.objects.create(name='Alice', salary=1000, department='Sales', hire_date='2020-01-01', age=30)
Employee.objects.create(name='Bob', salary=2000, department='Sales', hire_date='2020-02-01', age=35)
Employee.objects.create(name='Charlie', salary=3000, department='IT', hire_date='2020-03-01', age=40)

# Try to reproduce the issue
print("Testing aggregate over window functions...")
try:
    queryset = Employee.objects.all()
    queryset = queryset.annotate(
        cumul_salary=Coalesce(Window(Sum('salary'), order_by=F('hire_date').asc()), 0.0)
    )
    print("Query with annotation:", queryset.query)
    
    aggregate = queryset.aggregate(
        salary_total=Sum('salary'),
        cumul_salary_total=Sum('cumul_salary')
    )
    print('Success:', aggregate)
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
