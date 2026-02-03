# Geography Domain: Property Setter Fix

## Issue
Django was throwing errors when trying to set count properties on geography models:
- `property regions_count of Country object has no setter`
- `property administrative_units_count of RegionAdministrative object has no setter`
- `property localities_count of AdministrativeUnit object has no setter`
- `property children_count of AdministrativeUnit object has no setter`

## Root Cause
The count properties were defined as read-only `@property` decorators. When Django's ORM uses `annotate()` to add computed count fields, it tries to set these values on model instances, but there was no setter method defined.

## Solution
Added setter methods to all count properties that:
1. Store the annotated value in a private attribute (e.g., `_regions_count`)
2. The getter checks if the private attribute exists (from annotation) and uses it
3. Falls back to database query if no annotated value exists

This approach provides:
- ✅ Compatibility with Django ORM annotations
- ✅ Django Admin list_display support
- ✅ API serialization with annotated counts
- ✅ Fallback to database queries when not annotated
- ✅ No breaking changes to existing code

## Files Modified

### 1. `domain/geography/models/country.py`
**Before:**
```python
@property
def regions_count(self) -> int:
    """Return the count of non-deleted regions."""
    return self.regions.filter(is_deleted=False).count()
```

**After:**
```python
@property
def regions_count(self) -> int:
    """
    Return the count of non-deleted regions.
    
    If the queryset was annotated with regions_count, use that value.
    Otherwise, perform a database query.
    """
    if hasattr(self, '_regions_count'):
        return self._regions_count
    return self.regions.filter(is_deleted=False).count()

@regions_count.setter
def regions_count(self, value: int) -> None:
    """Allow Django ORM to set annotated value."""
    self._regions_count = value
```

### 2. `domain/geography/models/region.py`
Added setter for `administrative_units_count` property (same pattern as above).

### 3. `domain/geography/models/administrative_unit.py`
Added setters for both `localities_count` and `children_count` properties (same pattern as above).

## Testing Results

All tests passed successfully:

### ✅ Model Property Tests
- Country.regions_count with annotation: **PASS**
- Country.regions_count without annotation (fallback): **PASS**
- RegionAdministrative.administrative_units_count: **PASS**
- AdministrativeUnit.localities_count: **PASS**
- AdministrativeUnit.children_count: **PASS**
- Direct setter assignment: **PASS**

### ✅ Django Admin Tests
- All models registered in admin: **PASS**
- list_display with count properties: **PASS**
- Admin queryset methods: **PASS**
- Can access count properties in admin: **PASS**

### ✅ API Tests
- Country retrieve with regions_count: **PASS**
- Serializers include count fields: **PASS**

## Usage Examples

### In Views (with annotation)
```python
# Efficient: Uses annotation (single query)
countries = Country.objects.annotate(
    regions_count=Count('regions', filter=Q(regions__is_deleted=False))
)
for country in countries:
    print(country.regions_count)  # Uses annotated value
```

### Without Annotation
```python
# Less efficient: Queries database for each access
country = Country.objects.get(id=1)
print(country.regions_count)  # Executes database query
```

### In Django Admin
```python
class CountryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'regions_count', 'created_at']
    # Works automatically - Django will annotate the queryset
```

### In Serializers
```python
class CountrySerializer(serializers.ModelSerializer):
    regions_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Country
        fields = ['id', 'name', 'regions_count']
```

## Benefits

1. **Performance**: Annotations avoid N+1 query problems
2. **Compatibility**: Works with Django Admin, DRF serializers, and custom views
3. **Flexibility**: Falls back to queries when annotations aren't used
4. **Clean API**: No breaking changes to existing code
5. **Type Safety**: Maintains proper type hints

## Notes

- The private attribute naming convention (`_<property_name>`) ensures no conflicts
- The `hasattr()` check is efficient and doesn't trigger database queries
- This pattern can be reused for other computed properties that might be annotated
- No changes needed to views, serializers, or admin configurations

## Date
Fixed: February 2, 2026
