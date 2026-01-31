# School Model - Planning Summary

**Status**: ✅ Planning Complete | 🚀 Ready for Implementation  
**Domain**: school_operations  
**Model**: School (First model in domain)  
**Date**: Planning completed  
**Estimated Implementation Time**: 5-7 working days (39-51 hours)

---

## 📋 Quick Navigation

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [README.md](./README.md) | Domain overview & getting started | Start here |
| [SCHOOL_MODEL_DESIGN.md](./SCHOOL_MODEL_DESIGN.md) | Complete technical specification | Reference during implementation |
| [SCHOOL_MODEL_OVERVIEW.md](./SCHOOL_MODEL_OVERVIEW.md) | Visual guide & quick reference | Quick lookups |
| [DOMAIN_INTEGRATION.md](./DOMAIN_INTEGRATION.md) | Cross-domain relationships | Integration questions |
| [KEY_DECISIONS.md](./KEY_DECISIONS.md) | Design rationale | Understanding "why" |
| [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) | Step-by-step guide | Implementation planning |
| [IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md) | Detailed task list | Daily progress tracking |
| This file | Executive summary | High-level overview |

---

## 🎯 What Is the School Model?

The **School model** is the foundational entity for the school_operations domain, representing a physical school institution with its operational metadata.

### Purpose
- Register and manage schools
- Track school classification (type, level, status)
- Link schools to geographic locations
- Assign school leadership (director, registrar)
- Manage capacity and enrollment tracking
- Store school-specific configuration

### Position in Architecture
```
Foundation Layer: School
    ↓
Operational Layer: SchoolYear, Enrollment, ClassSection
    ↓
Application Layer: Student assignments, Staff management, Reporting
```

---

## 🏗️ Architecture Overview

### Base Model
**AuditModel** - Full audit capabilities for business entities

**Provides**:
- Timestamps: created_at, updated_at
- Authors: created_by, updated_by, deleted_by
- Soft delete: is_deleted, deleted_at
- Activation: is_active
- Managers: objects, active, deleted, inactive, all_objects

### Core Components

```
School Model
├── Manager (SchoolManager)
│   ├── by_locality()
│   ├── by_region()
│   ├── active_operational()
│   └── at_capacity()
│
├── Fields (25 total)
│   ├── Identity: code, name, short_name
│   ├── Classification: type, level, status
│   ├── Relationships: locality, director, registrar
│   ├── Contact: email, phone, website, address
│   ├── Operations: founded_year, capacity, current_enrollment
│   └── Extensibility: settings (JSON), notes
│
├── Methods
│   ├── Business: activate(), suspend(), close()
│   ├── Queries: can_activate(), is_at_capacity()
│   ├── Utilities: get_full_address(), get_geographic_path()
│   └── Settings: get_setting(), set_setting()
│
└── Meta
    ├── 6 Indexes (optimized for common queries)
    ├── 3 Constraints (uniqueness + business rules)
    └── Ordering by geography + name
```

---

## 🔗 Domain Relationships

### Dependencies (What School Uses)

| Domain | Model | Relationship | Type |
|--------|-------|--------------|------|
| Geography | Locality | locality FK | Required (PROTECT) |
| Account | CustomUser | director FK | Optional (SET_NULL) |
| Account | CustomUser | registrar FK | Optional (SET_NULL) |
| Shared | AuditModel | Base class | Inheritance |

### Future Dependents (What Will Use School)

| Domain | Model | Relationship | Purpose |
|--------|-------|--------------|---------|
| school_operations | SchoolYear | school FK | Academic year per school |
| school_operations | Enrollment | school FK | Student enrollments |
| school_operations | ClassSection | school FK | Classes/sections |
| school_operations | Staff | school FK | Staff assignments |

---

## 📊 Key Design Decisions

### 1. Base Model: AuditModel ✓
**Why**: Business entity needing full audit capabilities  
**Pattern**: Same as AcademicYear, Subject, Cycle

### 2. Geographic Location: Required Locality FK
**Why**: Schools must have physical location  
**Benefit**: Automatic access to full geographic hierarchy

### 3. Uniqueness Rules
- **Code**: Global unique (like license plate)
- **Name**: Unique per locality (realistic - "École Primaire" in many villages)

### 4. Status Workflow: 4-State Model
```
DRAFT → ACTIVE ↔ SUSPENDED → CLOSED
```
- DRAFT: Incomplete profile
- ACTIVE: Fully operational
- SUSPENDED: Temporarily halted (reversible)
- CLOSED: Permanently closed (irreversible)

### 5. Settings Field: JSONField
**New Pattern** for extensibility without migrations
```json
{
  "academic": { "default_term_type": "TRIMESTER" },
  "operations": { "allow_online_enrollment": true },
  "localization": { "timezone": "Africa/Conakry" }
}
```

### 6. Capacity Management
- `capacity`: Optional max students
- `current_enrollment`: Auto-calculated
- Database constraint: enrollment ≤ capacity

---

## 📈 Implementation Phases

### Phase 1: Core Model (Day 1) - 5-6 hours
- [ ] Constants (SchoolType, SchoolLevel, SchoolStatus)
- [ ] Validators (founded_year, capacity, phone)
- [ ] School model with SchoolManager
- [ ] Migration

### Phase 2: Admin Interface (Day 1-2) - 1 hour
- [ ] Admin configuration
- [ ] List/filter/search setup
- [ ] Custom actions

### Phase 3: Business Logic (Day 2) - 4-5 hours
- [ ] Selectors (query functions)
- [ ] Services (business operations)
- [ ] Unit tests

### Phase 4: API Layer (Day 3) - 6-7 hours
- [ ] Serializers (List, Detail, Create, Update)
- [ ] ViewSet with custom actions
- [ ] Permissions
- [ ] URL configuration

### Phase 5: Testing (Day 3-4) - 12-15 hours
- [ ] Model tests (constraints, methods, validation)
- [ ] Service tests (business logic)
- [ ] API tests (endpoints, permissions)
- [ ] Coverage > 90%

### Phase 6: Data Management (Day 4) - 2 hours
- [ ] Seed command (sample schools)

### Phase 7: Documentation (Day 5) - 4 hours
- [ ] API documentation
- [ ] Usage examples
- [ ] Update main docs

### Phase 8: Deployment (Day 5) - 5-7 hours
- [ ] Integration testing
- [ ] Code review
- [ ] Production deployment

---

## 🎨 Pattern Consistency

### Follows Existing Patterns ✅
- AuditModel for business entities
- PROTECT for critical relationships
- SET_NULL for optional relationships
- Soft delete with conditional constraints
- Strategic indexing
- clean() validation pattern
- Status enum pattern

### New Patterns Introduced ⭐
- JSONField for settings (extensible configuration)
- Capacity management (enrollment tracking)
- Multiple user role relationships
- Scoped name uniqueness (per locality)

### Modern Improvements 🔄
- TextChoices vs class constants (more Pythonic)
- Explicit indexes for performance
- CheckConstraint for business rules

---

## 🧪 Testing Strategy

### Model Tests (95%+ coverage)
- Field validation
- Constraint enforcement
- Business rule validation
- Method behavior
- Manager queries

### Service Tests (90%+ coverage)
- Create/Update/Delete operations
- Status transitions
- Audit trail verification
- Error handling

### API Tests (90%+ coverage)
- All endpoints (CRUD)
- Custom actions (activate, suspend, close)
- Filtering, ordering, pagination
- Permissions
- Error responses

---

## 📦 Deliverables

### Code Files (17 files)
```
domain/school_operations/
├── constants.py                    # Enums
├── validators.py                   # Validation functions
├── models/school.py                # School model + manager
├── models/__init__.py              # Exports
├── admin.py                        # Admin config
├── selectors/school.py             # Query functions
├── selectors/__init__.py           # Exports
├── services/school.py              # Business logic
├── services/__init__.py            # Exports
├── api/serializers/school.py       # API serializers
├── api/serializers/__init__.py     # Exports
├── api/views/school.py             # API views
├── api/views/__init__.py           # Exports
├── api/permissions.py              # API permissions
├── api/urls.py                     # API routes
├── management/commands/seed_schools.py  # Seed data
└── tests/
    ├── conftest.py                 # Test fixtures
    ├── test_models.py              # Model tests
    ├── test_services.py            # Service tests
    └── test_api.py                 # API tests
```

### Documentation Files (8 files)
```
domain/school_operations/
├── README.md                       # Domain overview
├── SCHOOL_MODEL_DESIGN.md          # Technical spec
├── SCHOOL_MODEL_OVERVIEW.md        # Quick reference
├── DOMAIN_INTEGRATION.md           # Cross-domain analysis
├── KEY_DECISIONS.md                # Design rationale
├── IMPLEMENTATION_ROADMAP.md       # Step-by-step guide
├── IMPLEMENTATION_CHECKLIST.md     # Task list
└── PLANNING_SUMMARY.md             # This file
```

---

## 🚀 Getting Started

### For Developers

**1. Read Documentation** (1-2 hours)
- Start: [README.md](./README.md)
- Design: [SCHOOL_MODEL_DESIGN.md](./SCHOOL_MODEL_DESIGN.md)
- Overview: [SCHOOL_MODEL_OVERVIEW.md](./SCHOOL_MODEL_OVERVIEW.md)

**2. Set Up Environment** (30 minutes)
```bash
# Create branch
git checkout -b feature/school-model

# Ensure dependencies
pip install -r requirements.txt

# Run existing tests
pytest
```

**3. Begin Implementation** (5-7 days)
- Follow: [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)
- Track: [IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md)
- Reference: [SCHOOL_MODEL_DESIGN.md](./SCHOOL_MODEL_DESIGN.md)

**4. Day-by-Day Plan**
- **Day 1**: Core model + admin
- **Day 2**: Business logic layer
- **Day 3**: API layer
- **Day 4**: Testing + data management
- **Day 5**: Documentation + deployment

---

## ✅ Success Criteria

### Code Quality
- [ ] All tests passing (100% pass rate)
- [ ] Test coverage > 90%
- [ ] No linting errors (Black, flake8)
- [ ] All docstrings complete
- [ ] Type hints present

### Functionality
- [ ] School CRUD operations working
- [ ] Status workflow functional
- [ ] Admin interface operational
- [ ] API endpoints functional
- [ ] Seed command working

### Performance
- [ ] Query time < 100ms for common patterns
- [ ] Migrations complete successfully
- [ ] Indexes optimizing queries

### Documentation
- [ ] API documentation complete
- [ ] Code documentation complete
- [ ] README updated
- [ ] CHANGELOG updated

---

## 🔍 Key Features

### Identity & Classification
✓ Unique code (global identifier)  
✓ Name (unique per locality)  
✓ Type (PUBLIC, PRIVATE, COMMUNITY, ISLAMIC, CONFESSIONAL)  
✓ Level (PRESCHOOL, PRIMARY, SECONDARY, combinations)  
✓ Status workflow (DRAFT → ACTIVE → SUSPENDED → CLOSED)

### Location & Relationships
✓ Geographic placement (linked to Locality)  
✓ Leadership assignment (director, registrar)  
✓ Full address (street, postal code)  
✓ Contact information (email, phone, website)

### Operations
✓ Capacity management (max vs current)  
✓ Founded year tracking  
✓ Enrollment counting  
✓ Settings (extensible JSON configuration)

### Audit & Compliance
✓ Full audit trail (who, when, what)  
✓ Soft delete (never lose data)  
✓ Activation control (active/inactive)  
✓ Status workflow (controlled transitions)

---

## 📊 Statistics

### Planning Metrics
- **Documents Created**: 8
- **Total Pages**: ~50 (estimated)
- **Design Hours**: ~8 hours
- **Implementation Estimate**: 39-51 hours

### Code Metrics (Estimated)
- **Files**: 17
- **Models**: 1 (School)
- **Fields**: 25
- **Methods**: 15+
- **Tests**: 50+
- **Lines of Code**: ~2,000-2,500

### Database Objects
- **Tables**: 1 (school)
- **Indexes**: 6
- **Constraints**: 3 (2 unique, 1 check)
- **Foreign Keys**: 3

---

## 🎓 Learning Resources

### Understanding the Design
1. Read [KEY_DECISIONS.md](./KEY_DECISIONS.md) - Why decisions were made
2. Read [DOMAIN_INTEGRATION.md](./DOMAIN_INTEGRATION.md) - How it fits
3. Review existing models in domain/academic/models/

### Implementation Guide
1. Follow [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)
2. Use [IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md)
3. Reference [SCHOOL_MODEL_DESIGN.md](./SCHOOL_MODEL_DESIGN.md)

### Pattern Examples
- **AuditModel**: `domain/shared/models/base.py`
- **Similar model**: `domain/academic/models/academic_year.py`
- **Geography pattern**: `domain/geography/models/locality.py`

---

## 🐛 Common Pitfalls to Avoid

### 1. Forgetting Soft Delete Conditions
❌ `UniqueConstraint(fields=['code'])`  
✅ `UniqueConstraint(fields=['code'], condition=Q(is_deleted=False))`

### 2. Not Using select_related
❌ `School.objects.all()`  
✅ `School.objects.select_related('locality', 'director')`

### 3. Skipping full_clean()
❌ `school.save()`  
✅ `school.full_clean()` then `school.save()`

### 4. Hard Delete Instead of Soft
❌ `school.delete()`  
✅ `school.soft_delete(user=current_user)`

### 5. Missing User in Services
❌ `school.save()`  
✅ `school.save_by(user=current_user)`

---

## 🔮 Future Extensions

### Version 1.1 - School Years
Link schools to academic years with school-specific configuration

### Version 1.2 - Enrollments
Student enrollment management per school year

### Version 1.3 - Class Sections
Organizational units within schools (classes, grades)

### Version 2.0 - Advanced Features
Facilities, licenses, inspections, multi-year analytics

---

## 📞 Support

### Questions During Implementation?

**Design Questions**: Review [SCHOOL_MODEL_DESIGN.md](./SCHOOL_MODEL_DESIGN.md)  
**Integration Questions**: Review [DOMAIN_INTEGRATION.md](./DOMAIN_INTEGRATION.md)  
**Implementation Questions**: Review [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)  
**Pattern Questions**: Review [KEY_DECISIONS.md](./KEY_DECISIONS.md)

### Stuck on a Task?

1. Check the relevant documentation
2. Review similar implementations in academic/geography domains
3. Consult the implementation checklist for detailed steps
4. Ask team for clarification

---

## 🎉 Ready to Start?

### Pre-Implementation Checklist
- [ ] All planning documents reviewed
- [ ] Design understood
- [ ] Environment set up
- [ ] Git branch created
- [ ] Team notified of start

### First Steps
1. Create `domain/school_operations/constants.py`
2. Create `domain/school_operations/validators.py`
3. Create `domain/school_operations/models/school.py`
4. Create migration
5. Write tests

**Good luck with the implementation! 🚀**

---

**Planning Status**: ✅ Complete  
**Next Phase**: Implementation  
**Estimated Completion**: 5-7 working days from start  
**Success Probability**: High (thorough planning completed)
