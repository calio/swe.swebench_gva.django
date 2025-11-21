import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
django.setup()

from django.db.models.functions import ExtractIsoYear, ExtractYear
from django.db.models.lookups import YearExact
from django.db.models import DateField, Value
from datetime import datetime

# Create a YearExact lookup with ExtractIsoYear
extract_iso_year = ExtractIsoYear(Value(datetime(2014, 12, 31)))
year_exact = YearExact(extract_iso_year, 2015)

print("year_exact.lhs:", year_exact.lhs)
print("year_exact.lhs.lookup_name:", year_exact.lhs.lookup_name)
print("year_exact.lhs.lhs:", year_exact.lhs.lhs)
print("year_exact.rhs:", year_exact.rhs)

# Compare with ExtractYear
extract_year = ExtractYear(Value(datetime(2014, 12, 31)))
year_exact2 = YearExact(extract_year, 2015)

print("\nWith ExtractYear:")
print("year_exact2.lhs:", year_exact2.lhs)
print("year_exact2.lhs.lookup_name:", year_exact2.lhs.lookup_name)
print("year_exact2.lhs.lhs:", year_exact2.lhs.lhs)
