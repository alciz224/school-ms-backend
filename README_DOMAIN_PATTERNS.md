# Django DDD Domain Implementation Patterns

**📚 Complete pattern extraction and implementation guide for this Django DDD project**

---

## 🎯 Purpose

This documentation suite extracts and documents the **exact patterns** used across all existing domain implementations (`academic`, `geography`, `school_operations`) to ensure **100% consistency** for any new model implementation.

---

## 📂 Documentation Files

| File | Purpose | When to Use |
|------|---------|-------------|
| **[DOMAIN_IMPLEMENTATION_INDEX.md](DOMAIN_IMPLEMENTATION_INDEX.md)** | **Start here** - Navigation hub for all docs | First visit, finding specific patterns |
| **[DOMAIN_MODEL_IMPLEMENTATION_GUIDE.md](DOMAIN_MODEL_IMPLEMENTATION_GUIDE.md)** | Complete reference (15 sections, 68 KB) | In-depth learning, first implementation |
| **[DOMAIN_MODEL_QUICK_REFERENCE.md](DOMAIN_MODEL_QUICK_REFERENCE.md)** | One-page templates (11 KB) | Quick copy-paste, experienced developers |
| **[DOMAIN_MODEL_REAL_EXAMPLES.md](DOMAIN_MODEL_REAL_EXAMPLES.md)** | Real implementations (25 KB) | See patterns in practice, understand complexity levels |

---

## 🚀 Quick Start

### First Time?
1. Read **[DOMAIN_IMPLEMENTATION_INDEX.md](DOMAIN_IMPLEMENTATION_INDEX.md)**
2. Review **[DOMAIN_MODEL_REAL_EXAMPLES.md](DOMAIN_MODEL_REAL_EXAMPLES.md)** - find a similar model
3. Use **[DOMAIN_MODEL_QUICK_REFERENCE.md](DOMAIN_MODEL_QUICK_REFERENCE.md)** - copy templates
4. Follow checklist in **[DOMAIN_MODEL_IMPLEMENTATION_GUIDE.md](DOMAIN_MODEL_IMPLEMENTATION_GUIDE.md)** Section 15

### Experienced Developer?
1. Open **[DOMAIN_MODEL_QUICK_REFERENCE.md](DOMAIN_MODEL_QUICK_REFERENCE.md)**
2. Copy relevant templates
3. Verify with checklist

---

## 🏗️ What's Covered

### 1. File Structure Pattern
- Exact directory structure for any domain
- Required vs optional files
- Naming conventions

### 2. Code Organization Pattern
- Model file structure
- Service file structure
- Selector file structure
- API layer structure

### 3. Naming Conventions
- Python/Django conventions
- Database conventions
- API conventions
- Import conventions

### 4. Import Patterns
- Standard import order
- Relative vs absolute imports
- __init__.py export patterns

### 5. Model Implementation Pattern
- Base model selection (AuditModel)
- Field definition patterns
- Meta class configuration
- Custom managers
- Model methods
- Foreign key patterns

### 6. Service Implementation Pattern
- CRUD methods (create, update, delete, restore)
- Business action methods
- Transaction handling
- Dependency checking

### 7. Selector Implementation Pattern
- Query methods (get_all, get_by_id, get_by_code)
- Search methods
- Filter methods
- Annotated queries

### 8. API Serializer Pattern
- Simple serializers
- Serializers with computed fields
- Multiple serializers per model

### 9. API ViewSet Pattern
- ModelViewSet pattern (simple)
- ViewSet pattern (complex)
- Custom actions

### 10. Admin Interface Pattern
- Simple admin configuration
- Advanced admin with custom display
- Soft delete handling

### 11. Constants Pattern
- TextChoices for statuses
- Domain-wide constants

### 12. Validators Pattern
- Custom validator functions
- Field-level validation
- Model-level validation

### 13. URL Configuration Pattern
- Router setup
- URL naming
- Namespace configuration

### 14. Test Structure Pattern
- Model tests
- Service tests
- Selector tests
- API tests

### 15. Complete Implementation Checklist
- Step-by-step verification
- Nothing gets missed

---

## 📊 Pattern Examples

### Three Complexity Levels

#### 🟢 Simple: Country
- Basic fields
- Minimal logic
- No foreign keys
- **Use for:** Reference data, lookups

#### 🟡 Medium: AcademicYear
- Auto-generated fields
- Business rules (flags)
- Moderate logic
- **Use for:** Core entities with state

#### 🔴 Complex: School
- Multiple foreign keys
- Complex validation
- Many fields
- Hierarchical data
- **Use for:** Central business entities

**Full examples in:** [DOMAIN_MODEL_REAL_EXAMPLES.md](DOMAIN_MODEL_REAL_EXAMPLES.md)

---

## 🎯 Key Principles

### Architecture
```
API Layer (Views)
    ↓
Services (Write) ← → Selectors (Read)
    ↓
Models (Structure)
```

### Golden Rules
- ✅ **Always** inherit from `AuditModel`
- ✅ **Prefer DB constraints** for invariants that must never be violated
- ✅ **Use shared domain exceptions** (`domain/shared/exceptions.py`) for consistent API errors
- ✅ **Use `transaction.atomic`** for multi-step writes / workflow transitions
- ✅ **Always** use soft delete
- ✅ **Always** track users (created_by, updated_by, deleted_by)
- ✅ **Always** use keyword-only args in services/selectors
- ✅ **Always** use static methods in services/selectors
- ✅ **Always** validate before saving
- ✅ **Always** check dependencies before deleting
- ❌ **Never** put business logic in models
- ❌ **Never** query directly in views
- ❌ **Never** skip validation

---

## 📝 Templates

All code templates are in **[DOMAIN_MODEL_QUICK_REFERENCE.md](DOMAIN_MODEL_QUICK_REFERENCE.md)**:

- Model template
- Service template (with CRUD methods)
- Selector template (with query methods)
- Serializer template
- ViewSet template
- Admin template
- URL configuration template
- __init__.py export templates

---

## ✅ Implementation Checklist Summary

### Core Files (Always Required)
- [ ] `models/{model}.py` - Model class
- [ ] `services/{model}.py` - Business logic
- [ ] `selectors/{model}.py` - Query logic
- [ ] `api/serializers/{model}.py` - API serialization
- [ ] `api/views/{model}.py` - API endpoints
- [ ] `admin.py` - Register admin
- [ ] `api/urls.py` - URL routing
- [ ] All `__init__.py` exports

### Optional Files (As Needed)
- [ ] `constants.py` - Status/choice constants
- [ ] `validators.py` - Custom validators
- [ ] `signals.py` - Signal handlers

### Testing
- [ ] `tests/test_{model}.py` - Model, service, selector, API tests

**Full checklist in:** [DOMAIN_MODEL_IMPLEMENTATION_GUIDE.md](DOMAIN_MODEL_IMPLEMENTATION_GUIDE.md#15-complete-implementation-checklist)

---

## 🔍 How to Find What You Need

| I need to... | Go to... |
|--------------|----------|
| Get started | [DOMAIN_IMPLEMENTATION_INDEX.md](DOMAIN_IMPLEMENTATION_INDEX.md) |
| Understand patterns | [DOMAIN_MODEL_IMPLEMENTATION_GUIDE.md](DOMAIN_MODEL_IMPLEMENTATION_GUIDE.md) |
| Copy templates | [DOMAIN_MODEL_QUICK_REFERENCE.md](DOMAIN_MODEL_QUICK_REFERENCE.md) |
| See examples | [DOMAIN_MODEL_REAL_EXAMPLES.md](DOMAIN_MODEL_REAL_EXAMPLES.md) |
| Name something | Quick Reference → Naming Conventions |
| Structure files | Quick Reference → File Structure |
| Write a service | Quick Reference → Service Template |
| Write a selector | Quick Reference → Selector Template |
| Configure API | Quick Reference → Serializer & ViewSet Templates |
| Set up admin | Quick Reference → Admin Template |
| Add constants | Implementation Guide → Section 11 |
| Add validators | Implementation Guide → Section 12 |
| Write tests | Implementation Guide → Section 14 |
| Check completeness | Implementation Guide → Section 15 (Checklist) |

---

## 📈 What Was Analyzed

This documentation is based on complete analysis of:

### Domains Analyzed
1. **domain/academic/** - 8 models (AcademicYear, Term, TermType, Cycle, Level, Track, Subject, AssessmentType)
2. **domain/geography/** - 4 models (Country, Region, AdministrativeUnit, Locality)
3. **domain/school_operations/** - 2 models (School, SchoolYear)

### Patterns Extracted
- File structure (directory organization)
- Code organization (how code is structured within files)
- Naming conventions (all levels: Python, DB, API)
- Import patterns (order, style, exports)
- Model patterns (fields, meta, methods)
- Service patterns (CRUD, business logic)
- Selector patterns (queries, filters)
- API patterns (serializers, viewsets)
- Admin patterns (configuration, customization)
- Constants patterns (choices, enums)
- Validators patterns (custom validation)
- URL patterns (routing, naming)
- Test patterns (structure, coverage)

---

## 💡 Benefits of Following These Patterns

1. **Consistency** - All code looks and works the same way
2. **Maintainability** - Easy to understand and modify
3. **Predictability** - Developers know where to find things
4. **Quality** - Best practices baked in
5. **Onboarding** - New developers learn patterns once
6. **Scalability** - Architecture supports growth
7. **Testability** - Clean separation makes testing easier
8. **Team Alignment** - Everyone follows same standards

---

## 🎓 Learning Path

### Day 1: Understand
- Read Index (this file)
- Read Real Examples
- Understand architecture

### Day 2: Models & Services
- Read Implementation Guide Sections 5-6
- Study examples
- Implement simple model

### Day 3: Selectors & API
- Read Implementation Guide Sections 7-9
- Study API patterns
- Add API to your model

### Day 4: Testing & Admin
- Read Implementation Guide Sections 10, 14
- Add admin and tests
- Verify everything works

### Day 5: Master
- Review all patterns
- Implement complex model
- You're now a pattern expert!

---

## 📞 Questions?

### Common Questions Answered
- Do I need all these files? **Yes, for consistency**
- Can I deviate? **Only with good reason and team consensus**
- Which ViewSet type? **Simple → ModelViewSet, Complex → ViewSet**
- When custom validators? **When Django's built-ins don't suffice**

**More Q&A in:** [DOMAIN_IMPLEMENTATION_INDEX.md](DOMAIN_IMPLEMENTATION_INDEX.md#-common-questions)

---

## 🎯 Next Steps

1. **New to this project?**
   - Start with [DOMAIN_IMPLEMENTATION_INDEX.md](DOMAIN_IMPLEMENTATION_INDEX.md)
   - Read through the learning path

2. **Ready to implement?**
   - Open [DOMAIN_MODEL_QUICK_REFERENCE.md](DOMAIN_MODEL_QUICK_REFERENCE.md)
   - Follow the templates
   - Use the checklist

3. **Need deep understanding?**
   - Read [DOMAIN_MODEL_IMPLEMENTATION_GUIDE.md](DOMAIN_MODEL_IMPLEMENTATION_GUIDE.md)
   - Study [DOMAIN_MODEL_REAL_EXAMPLES.md](DOMAIN_MODEL_REAL_EXAMPLES.md)

---

## 📊 Documentation Stats

- **Total Files:** 4 comprehensive documents
- **Total Size:** ~118 KB of documentation
- **Total Lines:** ~4,047 lines
- **Sections:** 15 major patterns documented
- **Examples:** 3 complete real-world implementations
- **Templates:** Complete code templates for all layers
- **Checklists:** Step-by-step verification lists

---

## ✨ Final Note

These patterns represent the collective wisdom and best practices developed across multiple domain implementations. By following them, you ensure your code is:

- **Consistent** with the rest of the codebase
- **Maintainable** for future developers
- **Scalable** as the project grows
- **Professional** in structure and quality

**Remember:** Consistency is the foundation of maintainable code.

---

**Ready? Start here:** [DOMAIN_IMPLEMENTATION_INDEX.md](DOMAIN_IMPLEMENTATION_INDEX.md)

**Happy coding! 🚀**
