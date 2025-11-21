import os
import sys
import django
from django.conf import settings

# Configure Django settings
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
            'tests.expressions',
        ],
        USE_TZ=False,
    )
    django.setup()

from django.db import connection
from django.core.management import call_command
from tests.expressions.models import Experiment
from django.db.models import F
import datetime

# Create tables
call_command('migrate', '--run-syncdb', verbosity=0)

# Create a test record
Experiment.objects.all().delete()
exp = Experiment.objects.create(
    name='test',
    assigned='2020-01-01',
    completed='2020-01-02',
    estimated_time=datetime.timedelta(hours=1),
    start='2020-01-01 10:00:00',
    end='2020-01-01 11:00:00'
)

# Try the problematic query
delta = datetime.timedelta(days=1)
try:
    print("Testing: F('estimated_time') + timedelta(days=1)")
    result = list(Experiment.objects.annotate(duration=F('estimated_time') + delta))
    print(f'SUCCESS: Query executed without error')
    print(f'Result duration: {result[0].duration}')
except Exception as e:
    print(f'ERROR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
