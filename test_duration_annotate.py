import os
import sys
import django

# Add the project to the path
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
django.setup()

from tests.expressions.models import Experiment
from django.db.models import F, Value
from django.db.models.fields import DurationField
import datetime

# Create test data
Experiment.objects.all().delete()
exp = Experiment.objects.create(
    name='test',
    assigned='2020-01-01',
    completed='2020-01-02',
    estimated_time=datetime.timedelta(hours=1),
    start='2020-01-01 10:00:00',
    end='2020-01-01 11:00:00'
)

# Try the problematic query - annotate with duration-only expression
delta = datetime.timedelta(days=1)
try:
    print("Testing: annotate(duration=F('estimated_time') + timedelta(days=1))")
    result = list(Experiment.objects.annotate(duration=F('estimated_time') + delta))
    print(f'SUCCESS: Query executed without error')
    print(f'Result duration: {result[0].duration}')
except Exception as e:
    print(f'ERROR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
