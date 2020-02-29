# Task 3 Bugs, Errors and Fixes
## Bugs:
Encountered a couple bugs below:
### Bug 1
ERROR: test_find_unique_number_between_dates_with_diameter (tests.test_neo_database.TestNEOSearchUseCases) AttributeError: 'NearEarthObject' object has no attribute 'diameter_min_km'

**Remedy**:
Rename an attribute for NearEarthObject in model to match diameter_min_km

### Bug 2:
ERROR: test_find_unique_number_between_dates_with_diameter_and_hazardous_and_distance (tests.test_neo_database.TestNEOSearchUseCases)
AttributeError: 'OrbitPath' object has no attribute 'neo_name'

**Remedy**:
Renamed one of my defined attribute in OrbitPath to neo_name