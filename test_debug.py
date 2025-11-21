import os
import sys

# Add tests directory to path
sys.path.insert(0, os.path.join(os.getcwd(), 'tests'))
sys.path.insert(0, os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_sqlite')

import django
django.setup()

from basic.models import PrimaryKeyWithDefault
from django.db.models.fields import NOT_PROVIDED

print(f'pk.default={PrimaryKeyWithDefault._meta.pk.default}')
print(f'pk.default is not NOT_PROVIDED={PrimaryKeyWithDefault._meta.pk.default is not NOT_PROVIDED}')
print(f'bool(pk.default)={bool(PrimaryKeyWithDefault._meta.pk.default)}')

# Now test the save
s = PrimaryKeyWithDefault()
print(f'\nBefore save:')
print(f'  _state.adding={s._state.adding}')
print(f'  pk={s.pk}')

from django.test.utils import CaptureQueriesContext
from django.db import connection

with CaptureQueriesContext(connection) as ctx:
    s.save()

print(f'\nAfter save:')
print(f'  _state.adding={s._state.adding}')
print(f'  pk={s.pk}')
print(f'  Number of queries: {len(ctx)}')
for i, query in enumerate(ctx):
    print(f'  Query {i+1}: {query["sql"][:100]}...')
