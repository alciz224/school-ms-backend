# School Operations Domain

## Overview

The **school_operations** domain manages the foundational entities for school operations, starting with the School model as the anchor point for all school-specific activities.

## Domain Purpose

This domain represents the operational aspects of physical school institutions, including:
- School registration and management
- School classification and status tracking
- Geographic placement and organizational structure
- Staff assignment (directors, registrars)
- Capacity and enrollment tracking
- School-specific settings and configuration

## Core Concepts

### School (First Model)
The School model represents a physical school institution with its operational metadata. It serves as the foundation for:
- School years (academic year implementations per school)
- Student enrollments
- Class sections and groupings
- Staff assignments
- Operational reporting

### Design Philosophy

**Domain-Driven Design Principles**:
1. **Bounded Context**: School operations are separate from academic structure (academic domain) and user management (account domain)
2. **Aggregate Root**: School is the root entity for school-specific operations
3. **Rich Domain Model**: Business logic in the model, services orchestrate
4. **Ubiquitous Language**: Terms match real-world school administration

**Architectural Patterns**:
- **Clean Architecture**: Separation of concerns (models, services, selectors, API)
- **Repository Pattern**: Selectors for queries, Services for commands
- **Audit Trail**: Full traceability (who, when, what)
- **Soft Delete**: Preserve data integrity and history

## Domain Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                    SCHOOL OPERATIONS                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                     School                          │  │
│  │  - Foundational entity                              │  │
│  │  - Geographic placement                             │  │
│  │  - Staff assignments                                │  │
│  │  - Capacity tracking                                │  │
│  └────────┬────────────────────────────────┬───────────┘  │
│           │                                │               │
│           │ Uses                           │ Foundation    │
│           │                                │ For           │
│  ┌────────▼────────┐            ┌──────────▼──────────┐  │
│  │  Geography      │            │  SchoolYear         │  │
│  │  (Locality)     │            │  (Future)           │  │
│  └─────────────────┘            └─────────────────────┘  │
│  ┌─────────────────┐            ┌─────────────────────┐  │
│  │  Account        │            │  Enrollment         │  │
│  │  (Users)        │            │  (Future)           │  │
│  └─────────────────┘            └─────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Documentation

### Planning Documents
1. **[SCHOOL_MODEL_DESIGN.md](./SCHOOL_MODEL_DESIGN.md)** - Comprehensive design specification
   - Field definitions
   - Business rules
   - Validation logic
   - Methods and managers
   - Constants and validators
   - Future extensibility

2. **[SCHOOL_MODEL_OVERVIEW.md](./SCHOOL_MODEL_OVERVIEW.md)** - Quick reference guide
   - Model structure
   - Key design decisions
   - Status workflow
   - Comparison with other models
   - Index strategy

3. **[DOMAIN_INTEGRATION.md](./DOMAIN_INTEGRATION.md)** - Cross-domain analysis
   - Integration with geography domain
   - Integration with account domain
   - Integration with academic domain (future)
   - Pattern consistency analysis
   - Query patterns
   - Migration considerations

4. **[IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)** - Step-by-step implementation guide
   - 8 phases of implementation
   - Time estimates
   - Dependencies
   - Success criteria
   - Quick start guide

## Current Status

### ✅ Completed
- [x] Domain design and planning
- [x] Architecture analysis
- [x] Pattern review
- [x] Documentation

### 🚧 In Progress
- [ ] School model implementation

### 📋 Planned
- [ ] SchoolYear model
- [ ] Enrollment model
- [ ] ClassSection model
- [ ] Staff model

## Getting Started

### For New Developers

1. **Read the Overview** (this file)
2. **Review Design Document**: [SCHOOL_MODEL_DESIGN.md](./SCHOOL_MODEL_DESIGN.md)
3. **Check Integration Points**: [DOMAIN_INTEGRATION.md](./DOMAIN_INTEGRATION.md)
4. **Follow Implementation Guide**: [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)

### Quick Implementation Start

See the **Quick Start Guide** section in [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) for a day-by-day implementation plan.

## School Model - Key Features

### Identity & Classification
- **Unique Code**: Auto-generated or manual (e.g., "EPK-001")
- **Name**: Official school name (unique per locality)
- **Type**: PUBLIC, PRIVATE, COMMUNITY, ISLAMIC, CONFESSIONAL
- **Level**: PRESCHOOL, PRIMARY, SECONDARY, or combinations
- **Status**: DRAFT → ACTIVE → SUSPENDED → CLOSED

### Location & Relationships
- **Geographic Placement**: Linked to Locality (provides full hierarchy)
- **Leadership**: Director and Registrar (optional CustomUser links)
- **Full Address**: Multi-line address with postal code

### Operations
- **Capacity Management**: Max capacity vs current enrollment
- **Founded Year**: Historical tracking
- **Contact Info**: Email, phone, website
- **Settings**: Extensible JSONField for school-specific config

### Audit & Compliance
- **Full Audit Trail**: Created/updated/deleted by (who, when)
- **Soft Delete**: Never lose historical data
- **Activation Control**: Active/inactive status
- **Status Workflow**: Controlled state transitions

## Example Usage

### Creating a School

```python
from domain.school_operations.services.school import create_school
from domain.school_operations.constants import SchoolType, SchoolLevel, SchoolStatus
from domain.geography.models import Locality

# Get locality
locality = Locality.objects.get(code='KASSAPO')

# Create school
school = create_school(
    user=current_user,
    code='EPK-001',
    name='École Primaire de Kassapo',
    short_name='EP Kassapo',
    type=SchoolType.PUBLIC,
    level=SchoolLevel.PRIMARY,
    status=SchoolStatus.DRAFT,
    locality=locality,
    email='ep.kassapo@education.gn',
    phone='+224621000001',
    capacity=300,
    settings={
        'academic': {
            'default_term_type': 'TRIMESTER',
            'pass_mark': 10
        },
        'operations': {
            'allow_online_enrollment': False
        }
    }
)
```

### Querying Schools

```python
from domain.school_operations.selectors.school import (
    list_schools,
    list_schools_by_locality,
    list_active_schools
)
from domain.school_operations.constants import SchoolType

# All active public primary schools
schools = list_schools(
    type=SchoolType.PUBLIC,
    level=SchoolLevel.PRIMARY,
    status=SchoolStatus.ACTIVE
)

# Schools in a specific locality
schools = list_schools_by_locality(locality)

# Active operational schools
schools = list_active_schools()
```

### Managing School Status

```python
from domain.school_operations.services.school import (
    activate_school,
    suspend_school,
    close_school
)

# Activate a school
school = activate_school(school, user=current_user)

# Suspend temporarily
school = suspend_school(
    school, 
    user=current_user, 
    reason='Infrastructure repairs'
)

# Close permanently
school = close_school(
    school, 
    user=current_user, 
    reason='Merged with neighboring school'
)
```

### Working with Settings

```python
# Get a setting
term_type = school.get_setting('academic.default_term_type', default='TRIMESTER')

# Set a setting
school.set_setting('operations.has_library', True)
school.save()

# Complex settings
school.settings = {
    'academic': {
        'default_term_type': 'TRIMESTER',
        'grading_scale': '0-20',
        'pass_mark': 10
    },
    'operations': {
        'allow_online_enrollment': True,
        'has_cafeteria': True,
        'has_library': True
    },
    'localization': {
        'timezone': 'Africa/Conakry',
        'primary_language': 'fr',
        'supported_languages': ['fr', 'pular', 'malinke']
    }
}
school.save()
```

## API Endpoints (Future)

```
GET    /api/schools/                    # List schools
POST   /api/schools/                    # Create school
GET    /api/schools/{id}/               # Get school details
PUT    /api/schools/{id}/               # Update school
PATCH  /api/schools/{id}/               # Partial update
DELETE /api/schools/{id}/               # Soft delete school

POST   /api/schools/{id}/activate/     # Activate school
POST   /api/schools/{id}/suspend/      # Suspend school
POST   /api/schools/{id}/close/        # Close school
POST   /api/schools/{id}/restore/      # Restore deleted school
GET    /api/schools/statistics/        # Get statistics
```

**Filtering**:
- `?type=PUBLIC` - Filter by type
- `?level=PRIMARY` - Filter by level
- `?status=ACTIVE` - Filter by status
- `?locality={id}` - Filter by locality
- `?region={id}` - Filter by region
- `?search=Kassapo` - Search by name/code

**Ordering**:
- `?ordering=name` - Order by name
- `?ordering=-created_at` - Most recent first
- `?ordering=locality__name` - By locality name

## Testing

### Running Tests

```bash
# All school_operations tests
pytest domain/school_operations/tests/

# Model tests only
pytest domain/school_operations/tests/test_models.py

# Service tests only
pytest domain/school_operations/tests/test_services.py

# API tests only
pytest domain/school_operations/tests/test_api.py

# With coverage
pytest domain/school_operations/tests/ --cov=domain/school_operations --cov-report=html
```

### Test Coverage Goals
- **Model Tests**: 100% (all fields, methods, constraints)
- **Service Tests**: 95%+ (all business logic paths)
- **API Tests**: 90%+ (all endpoints, major error cases)
- **Overall**: 90%+ coverage

## Database Schema

### Tables
- `school` - Main school entity table

### Key Indexes
- `school_code_idx` - Fast code lookups
- `school_type_status_idx` - Common filtering
- `school_locality_name_idx` - Geographic searches
- `school_enrollment_idx` - Reporting queries

### Constraints
- Unique code (when not deleted)
- Unique name per locality (when not deleted)
- Enrollment ≤ capacity (when capacity set)

## Future Roadmap

### Version 1.0 - Foundation
- [x] School model design
- [ ] School model implementation
- [ ] Admin interface
- [ ] API endpoints
- [ ] Tests (90%+ coverage)

### Version 1.1 - School Years
- [ ] SchoolYear model (School + AcademicYear bridge)
- [ ] Term dates per school
- [ ] Enrollment periods
- [ ] School year activation/closure

### Version 1.2 - Enrollments
- [ ] Enrollment model (Student + SchoolYear)
- [ ] Enrollment workflow
- [ ] Status tracking (enrolled, transferred, graduated, dropped)
- [ ] Enrollment history

### Version 1.3 - Class Sections
- [ ] ClassSection model (organizational units)
- [ ] Teacher assignments
- [ ] Student assignments per section
- [ ] Section capacity management

### Version 2.0 - Advanced Features
- [ ] School facilities management
- [ ] School licenses and accreditation
- [ ] Inspection tracking
- [ ] Multi-year statistics and analytics
- [ ] Advanced reporting

## Contributing

### Code Style
- Follow PEP 8
- Use Black for formatting
- Type hints for function signatures
- Comprehensive docstrings

### Commit Messages
```
feat(school): Add School model with full audit capabilities
fix(school): Correct enrollment capacity validation
test(school): Add tests for status transitions
docs(school): Update API documentation
```

### Pull Request Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Ensure all tests pass
4. Update documentation
5. Submit PR with clear description
6. Address review feedback

## Related Domains

### Dependencies (School uses)
- **geography**: Locality for geographic placement
- **account**: CustomUser for director/registrar
- **shared**: AuditModel, validators, utilities

### Dependents (Use School)
- **school_operations** (future): SchoolYear, Enrollment
- **academic** (future): School-specific academic configurations
- **reporting** (future): School-level reports and analytics

## Support & Questions

### Documentation
- **Design**: [SCHOOL_MODEL_DESIGN.md](./SCHOOL_MODEL_DESIGN.md)
- **Overview**: [SCHOOL_MODEL_OVERVIEW.md](./SCHOOL_MODEL_OVERVIEW.md)
- **Integration**: [DOMAIN_INTEGRATION.md](./DOMAIN_INTEGRATION.md)
- **Implementation**: [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)

### Contact
- Technical questions: Review design documents
- Architecture questions: Review domain integration document
- Implementation questions: Follow implementation roadmap

## License

This is part of the larger Django DDD School Management System project.

---

**Status**: Planning Complete ✅ | Implementation Ready 🚀

**Last Updated**: {{ current_date }}

**Next Steps**: Begin Phase 1 implementation (Core Model) following [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)
