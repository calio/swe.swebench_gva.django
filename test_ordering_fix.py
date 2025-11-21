"""
Test to reproduce the issue where RelatedFieldListFilter doesn't fall back 
to Model._meta.ordering when no ModelAdmin is registered.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.test_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.admin import ModelAdmin, site, RelatedOnlyFieldListFilter
from django.contrib.auth.models import User
from django.test import RequestFactory
from tests.admin_filters.models import Book, Employee, Department

# Create test data
def setup_test_data():
    """Setup test data for the ordering test."""
    # Clear existing data
    Employee.objects.all().delete()
    Department.objects.all().delete()
    Book.objects.all().delete()
    User.objects.all().delete()
    
    # Create departments
    dev = Department.objects.create(code='DEV', description='Development')
    design = Department.objects.create(code='DSN', description='Design')
    
    # Create employees with names that will test ordering
    # Without ordering, they would be returned in creation order (John, Jack)
    # With Model._meta.ordering by name, they should be (Jack, John) alphabetically
    john = Employee.objects.create(name='John Blue', department=dev)
    jack = Employee.objects.create(name='Jack Red', department=design)
    
    # Create a user for the request
    alfred = User.objects.create_superuser('alfred', 'alfred@example.com', 'password')
    
    # Create books with employees
    Book.objects.create(title='Book 1', employee=john)
    Book.objects.create(title='Book 2', employee=jack)
    
    return alfred, john, jack


def test_relatedfieldlistfilter_without_modeladmin():
    """
    Test that RelatedFieldListFilter falls back to Model._meta.ordering
    when no ModelAdmin is registered for the related model.
    """
    print("\n" + "="*70)
    print("TEST 1: RelatedFieldListFilter without ModelAdmin registration")
    print("="*70)
    
    # First, add ordering to Employee model
    Employee._meta.ordering = ['name']
    
    # Setup test data
    alfred, john, jack = setup_test_data()
    
    # Make sure Employee is NOT registered in admin
    if Employee in site._registry:
        site.unregister(Employee)
    
    # Create BookAdmin with employee filter
    class BookAdmin(ModelAdmin):
        list_filter = ('employee',)
    
    modeladmin = BookAdmin(Book, site)
    
    # Create request
    request_factory = RequestFactory()
    request = request_factory.get('/')
    request.user = alfred
    
    # Get the filter
    changelist = modeladmin.get_changelist_instance(request)
    filterspec = changelist.get_filters(request)[0][0]
    
    # Check the ordering
    print(f"\nEmployee model ordering: {Employee._meta.ordering}")
    print(f"Filter choices: {filterspec.lookup_choices}")
    
    # Expected: Should be ordered by name (Jack Red, John Blue)
    expected = [(jack.pk, 'Jack Red'), (john.pk, 'John Blue')]
    
    if filterspec.lookup_choices == expected:
        print("✓ PASS: Choices are correctly ordered by Model._meta.ordering")
        return True
    else:
        print(f"✗ FAIL: Expected {expected}")
        print(f"        Got {filterspec.lookup_choices}")
        return False


def test_relatedonlyfieldlistfilter_without_ordering():
    """
    Test that RelatedOnlyFieldListFilter respects ordering.
    """
    print("\n" + "="*70)
    print("TEST 2: RelatedOnlyFieldListFilter with ModelAdmin ordering")
    print("="*70)
    
    # Setup test data
    alfred, john, jack = setup_test_data()
    
    # Register Employee with ordering
    class EmployeeAdmin(ModelAdmin):
        ordering = ['name']
    
    if Employee in site._registry:
        site.unregister(Employee)
    site.register(Employee, EmployeeAdmin)
    
    # Create BookAdmin with RelatedOnlyFieldListFilter
    class BookAdmin(ModelAdmin):
        list_filter = (('employee', RelatedOnlyFieldListFilter),)
    
    modeladmin = BookAdmin(Book, site)
    
    # Create request
    request_factory = RequestFactory()
    request = request_factory.get('/')
    request.user = alfred
    
    # Get the filter
    changelist = modeladmin.get_changelist_instance(request)
    filterspec = changelist.get_filters(request)[0][0]
    
    # Check the ordering
    print(f"\nEmployeeAdmin ordering: {['name']}")
    print(f"Filter choices: {filterspec.lookup_choices}")
    
    # Expected: Should be ordered by name (Jack Red, John Blue)
    expected = [(jack.pk, 'Jack Red'), (john.pk, 'John Blue')]
    
    # Cleanup
    site.unregister(Employee)
    
    if filterspec.lookup_choices == expected:
        print("✓ PASS: Choices are correctly ordered by ModelAdmin.ordering")
        return True
    else:
        print(f"✗ FAIL: Expected {expected}")
        print(f"        Got {filterspec.lookup_choices}")
        return False


def test_relatedonlyfieldlistfilter_with_meta_ordering():
    """
    Test that RelatedOnlyFieldListFilter falls back to Model._meta.ordering.
    """
    print("\n" + "="*70)
    print("TEST 3: RelatedOnlyFieldListFilter with Model._meta.ordering")
    print("="*70)
    
    # Add ordering to Employee model
    Employee._meta.ordering = ['name']
    
    # Setup test data
    alfred, john, jack = setup_test_data()
    
    # Make sure Employee is NOT registered
    if Employee in site._registry:
        site.unregister(Employee)
    
    # Create BookAdmin with RelatedOnlyFieldListFilter
    class BookAdmin(ModelAdmin):
        list_filter = (('employee', RelatedOnlyFieldListFilter),)
    
    modeladmin = BookAdmin(Book, site)
    
    # Create request
    request_factory = RequestFactory()
    request = request_factory.get('/')
    request.user = alfred
    
    # Get the filter
    changelist = modeladmin.get_changelist_instance(request)
    filterspec = changelist.get_filters(request)[0][0]
    
    # Check the ordering
    print(f"\nEmployee model ordering: {Employee._meta.ordering}")
    print(f"Filter choices: {filterspec.lookup_choices}")
    
    # Expected: Should be ordered by name (Jack Red, John Blue)
    expected = [(jack.pk, 'Jack Red'), (john.pk, 'John Blue')]
    
    if filterspec.lookup_choices == expected:
        print("✓ PASS: Choices are correctly ordered by Model._meta.ordering")
        return True
    else:
        print(f"✗ FAIL: Expected {expected}")
        print(f"        Got {filterspec.lookup_choices}")
        return False


if __name__ == '__main__':
    print("\nRunning tests to reproduce the ordering issue...")
    
    results = []
    results.append(test_relatedfieldlistfilter_without_modeladmin())
    results.append(test_relatedonlyfieldlistfilter_without_ordering())
    results.append(test_relatedonlyfieldlistfilter_with_meta_ordering())
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        sys.exit(1)
