# CLAUDE.md - FortiDesk Development Documentation

This file provides guidance to Claude Code (claude.ai/code) and developers when working with code in this repository.

## Project Overview

**FortiDesk** is a comprehensive team management system for **Fortitudo 1901 Rugby ASD** youth teams. It streamlines administrative tasks, athlete and staff registry management, team organization, attendance tracking, equipment inventory, guardian communications, and documentation for youth rugby teams.

### Key Capabilities
- **Athlete Management**: Complete registry for youth athletes (ages 3-18) with guardian tracking and team assignments
- **Team Management**: Organize athletes by age group/level with head coach and staff assignments
- **Staff Management**: Personnel management for coaches, escorts, managers, and club officials
- **Attendance Tracking**: Bulk and individual attendance recording with reporting capabilities
- **Equipment Inventory**: Comprehensive equipment tracking with assignment and return workflows
- **Multi-language Support**: Full English/Italian internationalization
- **Role-based Access**: Admin, Coach, Parent, and Player roles with permission enforcement
- **Document Tracking**: Automated expiry alerts for documents, medical certificates, background checks

---

## Technology Stack

### Backend Framework
- **Flask 3.0.0**: Python web framework
- **SQLAlchemy 3.1.1**: Database ORM
- **Flask-Login 0.6.3**: User authentication and session management
- **Flask-WTF 1.2.1**: Form handling and CSRF protection
- **Flask-Babel 4.0.0**: Internationalization (i18n)
- **bcrypt 4.1.2**: Password hashing
- **PyMySQL 1.1.0**: MySQL database driver

### Frontend
- **Bootstrap 5.1.3**: Responsive CSS framework
- **Jinja2**: Template engine (Flask default)
- **Vanilla JavaScript**: Client-side interactions

### Database
- **MySQL 8.0**: Relational database
- **Schema**: 9 main tables (users, athletes, guardians, staff, teams, team_staff_assignments, attendance, equipment, equipment_assignments)

### Deployment
- **Docker + Docker Compose**: Containerization and orchestration
- **Nginx**: Reverse proxy
- **Gunicorn 21.2.0**: WSGI server
- **python-dotenv 1.0.0**: Environment configuration

---

## Project Structure

```
FortiDesk/
├── app/                              # Main Flask application package
│   ├── __init__.py                   # App factory, Babel configuration
│   ├── models/                       # SQLAlchemy database models
│   │   ├── __init__.py              # Model exports
│   │   ├── user.py                  # User authentication model
│   │   ├── athlete.py               # Athlete registry model (with team_id FK)
│   │   ├── guardian.py              # Guardian/parent model
│   │   ├── staff.py                 # Staff/personnel model
│   │   ├── team.py                  # Team and TeamStaffAssignment models
│   │   ├── attendance.py            # Attendance tracking model
│   │   └── equipment.py             # Equipment and EquipmentAssignment models
│   ├── views/                        # Flask blueprints (controllers)
│   │   ├── __init__.py
│   │   ├── auth.py                  # Authentication (login, register, logout)
│   │   ├── main.py                  # Dashboard and language switcher
│   │   ├── athletes.py              # Athlete CRUD operations
│   │   ├── staff.py                 # Staff CRUD operations
│   │   ├── teams.py                 # Team management and staff assignments
│   │   ├── attendance.py            # Attendance check-in, tracking, and reporting
│   │   └── equipment.py             # Equipment inventory and assignment workflows
│   ├── forms/                        # WTForms for validation
│   │   ├── __init__.py
│   │   ├── athletes_forms.py        # AthleteForm, GuardianForm
│   │   ├── staff_forms.py           # StaffForm with role-based validation
│   │   ├── team_forms.py            # TeamForm, TeamStaffAssignmentForm
│   │   ├── attendance_forms.py      # AttendanceForm, BulkAttendanceForm, AttendanceReportForm
│   │   └── equipment_forms.py       # EquipmentForm, EquipmentAssignmentForm, EquipmentReturnForm
│   ├── templates/                    # Jinja2 HTML templates
│   │   ├── base.html                # Base template with navbar, language switcher
│   │   ├── dashboard.html           # User dashboard
│   │   ├── auth/                    # Authentication pages (login, register)
│   │   ├── athletes/                # Athlete management templates (list, form, detail)
│   │   ├── staff/                   # Staff management templates
│   │   ├── teams/                   # Team management templates (list, new, edit, view, assign_staff)
│   │   ├── attendance/              # Attendance templates (list, check-in, bulk, report)
│   │   └── equipment/               # Equipment templates (list, new, edit, view, assign, return, assignments)
│   └── static/                       # Static files
│       ├── css/style.css            # Custom styles
│       └── js/app.js                # JavaScript utilities
├── docker/                           # Docker configurations
│   ├── nginx/                       # Nginx reverse proxy configuration
│   └── mysql/                       # Database initialization scripts
├── translations/                     # i18n translation files
│   └── it/LC_MESSAGES/              # Italian translations
│       ├── messages.po              # Translation source file
│       └── messages.mo              # Compiled binary catalog
├── babel.cfg                         # Babel extraction configuration
├── config.py                         # Flask configuration classes
├── docker-compose.yml               # Multi-container orchestration
├── docker-entrypoint.sh             # Container startup script with DB retries
├── Dockerfile                       # Flask app container definition
├── create_tables.py                 # Standalone database table creation utility
├── requirements.txt                 # Python dependencies (pip)
├── run.py                           # Application entry point with init_db()
├── .env.docker                      # Docker environment variables template
└── README.md                        # User documentation
```

---

## Database Models

### User Model (`app/models/user.py`)
**Purpose**: System authentication and authorization

**Fields**:
- `id`: Primary key
- `username`: Unique username (indexed)
- `email`: Unique email (indexed)
- `password_hash`: Bcrypt hashed password
- `first_name`, `last_name`: User's name
- `role`: User role (admin/coach/parent/player)
- `is_active`: Account status flag
- `created_at`, `last_login`: Timestamps

**Methods**:
- `set_password(password)`: Hash and store password
- `check_password(password)`: Verify password
- `get_full_name()`: Return formatted name
- `is_admin()`, `is_coach()`: Role checks

**Relationships**:
- `athletes_created`: One-to-many with Athlete (via created_by)
- `staff_created`: One-to-many with Staff (via created_by)
- `teams_created`: One-to-many with Team (via created_by)
- `attendance_created`: One-to-many with Attendance (via created_by)
- `equipment_created`: One-to-many with Equipment (via created_by)

---

### Athlete Model (`app/models/athlete.py`)
**Purpose**: Youth athlete registry (ages 3-18) with team assignment

**Fields**:
- Personal: `first_name`, `last_name`, `birth_date`, `birth_place`, `fiscal_code` (unique)
- Address: `street_address`, `street_number`, `postal_code`, `city`, `province`
- Document: `document_number`, `issuing_authority`, `document_expiry`
- Medical: `has_medical_certificate`, `certificate_type`, `certificate_expiry`
- Team: `team_id` (FK→teams, nullable, indexed)
- Meta: `created_at`, `updated_at`, `created_by` (FK→users), `is_active`

**Methods**:
- `get_full_name()`: Return formatted name
- `get_age()`: Calculate current age
- `get_full_address()`: Format complete address
- `is_certificate_expired()`: Check medical certificate status
- `is_document_expired()`: Check ID document status
- `days_until_certificate_expiry()`: Days remaining
- `days_until_document_expiry()`: Days remaining

**Relationships**:
- `guardians`: One-to-many with Guardian (cascade delete)
- `created_by_user`: Many-to-one with User
- `team`: Many-to-one with Team
- `attendance_records`: One-to-many with Attendance
- `equipment_assignments`: One-to-many with EquipmentAssignment

**Validation**:
- Age must be 3-18 years
- Fiscal code must match Italian format
- Document cannot be expired
- Requires 2 guardians of different types

---

### Guardian Model (`app/models/guardian.py`)
**Purpose**: Parent/legal guardian contact information

**Fields**:
- `first_name`, `last_name`: Guardian's name
- `phone`, `email`: Contact information
- `guardian_type`: Type (father/mother/guardian)
- `athlete_id`: Foreign key to Athlete (required)
- `created_at`, `updated_at`, `is_active`: Metadata

**Methods**:
- `get_full_name()`: Return formatted name
- `get_guardian_type_display()`: Localized type name

**Relationships**:
- `athlete`: Many-to-one with Athlete

**Business Rules**:
- Athlete must have exactly 2 guardians
- Cannot have two guardians of same type

---

### Staff Model (`app/models/staff.py`)
**Purpose**: Organizational personnel management (coaches, escorts, managers, officials)

**Fields**:
- Personal: `first_name`, `last_name`, `birth_date`, `birth_place`, `fiscal_code` (unique)
- Contact: `phone`, `email`
- Address: `street_address`, `street_number`, `postal_code`, `city`, `province`
- Document: `document_number`, `issuing_authority`, `document_expiry`
- Role: `role` (coach/assistant_coach/escort/manager/president/vice_president/secretary)
- `role_notes`: Optional text description
- Medical: `has_medical_certificate`, `certificate_type`, `certificate_expiry`
- Background: `has_background_check`, `background_check_date`, `background_check_expiry`
- Meta: `created_at`, `updated_at`, `created_by` (FK→users), `is_active`

**Methods**:
- `get_full_name()`: Return formatted name
- `get_age()`: Calculate current age (must be 18+)
- `get_full_address()`: Format complete address
- `get_role_display()`: Localized role name
- `is_certificate_expired()`: Check medical certificate
- `is_document_expired()`: Check ID document
- `is_background_check_expired()`: Check background check
- `days_until_*_expiry()`: Days remaining for each document
- `requires_medical_certificate()`: True for coach/assistant_coach/escort
- `requires_background_check()`: True for roles working with minors

**Relationships**:
- `created_by_user`: Many-to-one with User
- `teams_as_head_coach`: One-to-many with Team (as head_coach)
- `team_assignments`: One-to-many with TeamStaffAssignment

**Validation**:
- Age must be 18+ years
- Fiscal code must be unique and valid
- Medical certificate required for coach/assistant_coach/escort roles
- Background check required for roles working with minors

---

### Team Model (`app/models/team.py`)
**Purpose**: Team/squad organization by age group or level with staff and athlete assignments

**Fields**:
- `name`: Team name (unique, indexed)
- `description`: Optional description
- `age_group`: e.g. "U6", "U8", "U10"
- `season`: e.g. "2024-2025"
- `head_coach_id`: FK→staff (one head coach per team)
- `created_by`: FK→users
- `created_at`, `updated_at`, `is_active`: Metadata

**Methods**:
- `get_assistant_coaches()`: Get all active assistant coaches assigned to team
- `get_escorts()`: Get all active escorts assigned to team
- `get_all_staff()`: Get head coach + assistants + escorts
- `get_athlete_count()`: Count active athletes in team

**Relationships**:
- `head_coach`: Many-to-one with Staff
- `creator`: Many-to-one with User
- `athletes`: One-to-many with Athlete
- `staff_assignments`: One-to-many with TeamStaffAssignment (cascade delete)

---

### TeamStaffAssignment Model (`app/models/team.py`)
**Purpose**: Many-to-many relationship for assigning staff roles to teams (assistant coaches, escorts)

**Fields**:
- `team_id`, `staff_id`: Foreign keys
- `role`: Role type (assistant_coach, escort)
- `assigned_date`: Date of assignment
- `assigned_by`: FK→users (who made the assignment)
- `notes`: Optional notes
- `created_at`, `updated_at`, `is_active`: Metadata

**Constraints**:
- Unique constraint on (team_id, staff_id, role): same staff can't have same role twice in same team
- Index on (team_id, staff_id, role) for query performance

**Relationships**:
- `staff`: Many-to-one with Staff
- `team`: Many-to-one with Team
- `assigner`: Many-to-one with User

---

### Attendance Model (`app/models/attendance.py`)
**Purpose**: Track attendance for training sessions, matches, and events

**Fields**:
- `athlete_id`: FK→athletes (indexed)
- `created_by`: FK→users
- `date`: Date of session (indexed)
- `session_type`: Type (training/match/event)
- `status`: Attendance status (present/absent/excused/late)
- `notes`: Optional notes
- `created_at`, `updated_at`, `is_active`: Metadata

**Methods**:
- `get_status_display()`: Localized status display
- `get_session_type_display()`: Localized session type display

**Indexes**:
- (athlete_id, date): For athlete attendance history
- (date, session_type): For session-based queries

**Relationships**:
- `athlete`: Many-to-one with Athlete
- `creator`: Many-to-one with User

---

### Equipment Model (`app/models/equipment.py`)
**Purpose**: Inventory management for team equipment (balls, jerseys, protective gear, training aids)

**Fields**:
- `name`: Equipment name (indexed)
- `category`: Equipment category (ball/jersey/protective/training_aid/other, indexed)
- `size`: Size designation (XS-XL or numeric)
- `code`: Inventory code/barcode (unique, indexed)
- `condition`: Current condition (new/good/fair/poor/damaged)
- `status`: Availability status (available/assigned/maintenance/retired)
- Purchase: `purchase_date`, `purchase_price`, `supplier`
- Maintenance: `last_maintenance_date`, `next_maintenance_date`, `maintenance_notes`
- `description`: Additional notes
- `location`: Storage location
- `quantity`: For bulk items
- Meta: `created_by` (FK→users), `created_at`, `updated_at`, `is_active`

**Methods**:
- `get_category_display()`: Localized category name
- `get_condition_display()`: Localized condition name
- `get_status_display()`: Localized status name
- `needs_maintenance()`: Check if next_maintenance_date <= today
- `is_available()`: Check if status=='available' and is_active

**Relationships**:
- `creator`: Many-to-one with User
- `assignments`: One-to-many with EquipmentAssignment (cascade delete)

---

### EquipmentAssignment Model (`app/models/equipment.py`)
**Purpose**: Track equipment assignments to athletes with return tracking

**Fields**:
- `equipment_id`, `athlete_id`: Foreign keys
- `assigned_by`, `returned_by`: FK→users
- `assigned_date`: Date assigned (indexed)
- `expected_return_date`: Expected return date
- `actual_return_date`: Actual return date (indexed)
- `condition_at_assignment`: Condition when assigned
- `condition_at_return`: Condition when returned
- Assignment/return notes: `assignment_notes`, `return_notes`
- Status: `is_returned`, `is_active`
- Meta: `created_at`, `updated_at`

**Methods**:
- `is_overdue()`: Check if not returned and expected_return_date < today
- `days_overdue()`: Calculate days overdue

**Indexes**:
- (athlete_id, is_returned): For athlete's equipment history
- (equipment_id, is_returned): For equipment assignment history

**Relationships**:
- `athlete`: Many-to-one with Athlete
- `assigner`: Many-to-one with User (who assigned)
- `returner`: Many-to-one with User (who processed return)

---

## Views (Blueprints)

### Auth Blueprint (`app/views/auth.py`)
**Routes**:
- `GET/POST /auth/login`: User login
- `GET/POST /auth/register`: User registration
- `GET /auth/logout`: User logout

**Forms**:
- `LoginForm`: username_or_email, password, remember_me
- `RegistrationForm`: username, email, first_name, last_name, password, password2

**Permissions**: Public access (redirects authenticated users to dashboard)

---

### Main Blueprint (`app/views/main.py`)
**Routes**:
- `GET /`: Redirect to dashboard or login
- `GET /dashboard`: User dashboard (requires login)
- `GET /set_language/<language>`: Language switcher

**Functions**:
- Language preference stored in session
- Browser language detection as fallback
- Redirects to login if not authenticated

---

### Teams Blueprint (`app/views/teams.py`)
**Routes**:
- `GET /teams/`: List all active teams
- `GET/POST /teams/new`: Create team (admin/coach only)
- `GET /teams/<id>`: View team details with athletes and staff
- `GET/POST /teams/<id>/edit`: Edit team (admin/coach only)
- `POST /teams/<id>/delete`: Soft delete team (admin only)
- `GET/POST /teams/<id>/assign-staff`: Assign assistant coaches/escorts (admin/coach only)
- `POST /teams/staff-assignment/<id>/remove`: Remove staff assignment (admin/coach only)

**Features**:
- Soft delete (is_active=False)
- Head coach selection from staff members
- Dynamic staff assignment with role-based filtering
- Unique constraint prevents duplicate staff assignments

---

### Athletes Blueprint (`app/views/athletes.py`)
**Routes**:
- `GET /athletes/`: List athletes (paginated, searchable, filterable by team)
- `GET/POST /athletes/new`: Create athlete (admin/coach only)
- `GET /athletes/<id>`: View athlete details with guardians
- `GET/POST /athletes/<id>/edit`: Edit athlete (admin/coach only)
- `POST /athletes/<id>/delete`: Soft delete (admin only)

**Features**:
- Search by name, fiscal code
- Filter by team assignment
- Pagination (20 per page)
- Status badges for expiry alerts (document, certificate)
- Fiscal code uniqueness validation
- Guardian management (create/edit/remove)

---

### Staff Blueprint (`app/views/staff.py`)
**Routes**:
- `GET /staff/`: List staff (paginated, searchable, filterable by role)
- `GET/POST /staff/new`: Create staff member (admin/coach only)
- `GET /staff/<id>`: View staff details
- `GET/POST /staff/<id>/edit`: Edit staff member (admin/coach only)
- `POST /staff/<id>/delete`: Soft delete (admin only)

**Features**:
- Search by name, email, fiscal code
- Filter by role (7 types)
- Triple expiry tracking (document, medical cert, background check)
- Role-specific requirement hints
- Status badges for expiry alerts

---

### Attendance Blueprint (`app/views/attendance.py`)
**Routes**:
- `GET /attendance/`: List recent attendance records (paginated, filterable by date/session/team)
- `GET/POST /attendance/check-in`: Bulk check-in for multiple athletes (admin/coach only)
- `GET /attendance/<id>`: View attendance record details
- `GET/POST /attendance/<id>/edit`: Edit attendance record (admin/coach only)
- `POST /attendance/<id>/delete`: Soft delete (admin only)
- `GET/POST /attendance/report`: Generate attendance reports with filtering and statistics

**Features**:
- Bulk attendance recording with checkbox UI
- Filter by date, session type, team
- Attendance report with date range, athlete, team, and status filters
- Statistics: total, present count, absent, excused, late, presence percentage
- Dynamic athlete filtering by team

---

### Equipment Blueprint (`app/views/equipment.py`)
**Routes**:
- `GET /equipment/`: Equipment inventory list (paginated, searchable, filterable)
- `GET/POST /equipment/new`: Create equipment item (admin/coach only)
- `GET /equipment/<id>`: View equipment details with assignment history
- `GET/POST /equipment/<id>/edit`: Edit equipment (admin/coach only)
- `POST /equipment/<id>/delete`: Soft delete (admin only)
- `GET/POST /equipment/assign`: Assign equipment to athlete (admin/coach only)
- `GET /equipment/assignments`: List all equipment assignments (active by default, show all option)
- `GET/POST /equipment/assignments/<id>/return`: Process equipment return (admin/coach only)

**Features**:
- Full inventory tracking with category, condition, status, maintenance tracking
- Equipment assignment workflow with condition tracking
- Return processing with condition inspection
- Overdue tracking for unreturned items
- Search by name, code, description
- Filter by category, status, condition

---

## Forms (`app/forms/`)

### AthleteForm (`athletes_forms.py`)
**Fields**:
- Personal data (name, birth info, fiscal code)
- Address (street, number, postal code, city, province)
- Document (number, authority, expiry)
- Medical certificate (optional)
- Guardian 1 & 2 (name, contact, type)

**Custom Validation**:
- `validate_birth_date()`: Age 3-18 years
- `validate_document_expiry()`: Not expired
- `validate_certificate_expiry()`: Required if has_medical_certificate checked
- `validate_guardian*_type()`: Different types for two guardians

---

### StaffForm (`staff_forms.py`)
**Fields**:
- Personal data (name, birth info, fiscal code)
- Contact (phone, email)
- Address (complete residential address)
- Document (number, authority, expiry)
- Role (7 options) with optional notes
- Medical certificate (conditional)
- Background check (conditional)

**Custom Validation**:
- `validate_birth_date()`: Age 18+ years
- `validate_document_expiry()`: Not expired
- `validate_certificate_expiry()`: Required if checked
- `validate_background_check_expiry()`: Required if checked
- `validate_background_check_date()`: Not in future

---

### TeamForm (`team_forms.py`)
**Fields**:
- `name`: Team name (required, max 100)
- `description`: Optional description
- `age_group`: Optional age group (e.g. "U6")
- `season`: Optional season (e.g. "2024-2025")
- `head_coach_id`: SelectField for head coach assignment

---

### TeamStaffAssignmentForm (`team_forms.py`)
**Fields**:
- `staff_id`: SelectField for staff member selection (required)
- `role`: SelectField (assistant_coach/escort) (required)
- `assigned_date`: DateField (required)
- `notes`: Optional notes

---

### AttendanceForm (`attendance_forms.py`)
**Fields**:
- `athlete_id`: SelectField (required)
- `date`: DateField (required, default=today)
- `session_type`: SelectField (training/match/event) (required)
- `status`: SelectField (present/absent/excused/late) (required)
- `notes`: Optional notes

---

### BulkAttendanceForm (`attendance_forms.py`)
**Fields**:
- `date`: DateField (required, default=today)
- `session_type`: SelectField (training/match/event) (required)
- `notes`: Optional session notes

**Usage**: Athletes selected via request.form checkboxes (present/absent/excused/late lists)

---

### AttendanceReportForm (`attendance_forms.py`)
**Fields**:
- `team_id`: Optional team filter
- `athlete_id`: Optional athlete filter
- `start_date`, `end_date`: Optional date range
- `session_type`: Optional session type filter
- `status`: Optional status filter

**Output**: Attendance records and statistics (total, present %, breakdowns)

---

### EquipmentForm (`equipment_forms.py`)
**Fields**:
- Name, category, size, code, condition, status
- Purchase info (date, price, supplier)
- Location, quantity, description
- Maintenance (notes, last date, next date)

---

### EquipmentAssignmentForm (`equipment_forms.py`)
**Fields**:
- `equipment_id`: SelectField (available equipment only)
- `athlete_id`: SelectField
- `assigned_date`: DateField (required)
- `expected_return_date`: Optional
- `condition_at_assignment`: SelectField (required)
- `assignment_notes`: Optional

---

### EquipmentReturnForm (`equipment_forms.py`)
**Fields**:
- `actual_return_date`: DateField (required)
- `condition_at_return`: SelectField (required)
- `return_notes`: Optional

---

### EquipmentSearchForm (`equipment_forms.py`)
**Fields**:
- `category`: Optional filter
- `status`: Optional filter
- `condition`: Optional filter

---

## Internationalization (i18n)

### Configuration (`app/__init__.py`)
```python
from flask_babel import Babel

babel = Babel()

def get_locale():
    # 1. Check session preference
    # 2. Fall back to browser accept-language
    # 3. Default to 'en'
```

### Supported Languages
- **en** (English): Default
- **it** (Italian): Complete translation

### Translation Files
- `babel.cfg`: Extraction configuration
- `messages.pot`: Translation template
- `translations/it/LC_MESSAGES/messages.po`: Italian catalog (source)
- `translations/it/LC_MESSAGES/messages.mo`: Compiled binary catalog

### Usage in Code

**Python files**:
```python
from flask_babel import gettext as _, lazy_gettext as _l

# Runtime strings (flash messages)
flash(_('Success message'))

# Form labels (evaluated at import time)
label = _l('Form Label')
```

**Templates**:
```jinja2
{# Simple string #}
<h1>{{ _('Page Title') }}</h1>

{# Parameterized string #}
<p>{{ _('Hello %(name)s', name=user.get_full_name()) }}</p>

{# HTML content #}
{% trans %}Text with <a href="#">link</a>{% endtrans %}
```

### Workflow for New Strings
```bash
# 1. Extract messages
uvx --with jinja2 --from babel pybabel extract -F babel.cfg -k _l -k _ -o messages.pot .

# 2. Update catalogs
uvx --with jinja2 --from babel pybabel update -i messages.pot -d translations

# 3. Edit translations/it/LC_MESSAGES/messages.po

# 4. Compile
uvx --with jinja2 --from babel pybabel compile -d translations
```

---

## Security Features

### Authentication
- **Password hashing**: bcrypt with salt
- **Session management**: Flask-Login with secure cookies
- **CSRF protection**: Flask-WTF on all forms
- **SQL injection prevention**: SQLAlchemy ORM (no raw SQL)

### Authorization (RBAC)
```python
# Route protection
@login_required
def protected_view():
    pass

# Permission checks in views
if not (current_user.is_admin() or current_user.is_coach()):
    flash(_('Permission denied'))
    return redirect(url_for('main.dashboard'))
```

### Data Protection
- **Soft delete**: Records marked inactive (is_active=False), never truly deleted
- **Audit trail**: created_at, updated_at, created_by on all records
- **Input validation**: WTForms validators on all user input
- **XSS protection**: Jinja2 auto-escaping enabled by default

---

## Common Development Tasks

### Adding a New Model

1. Create model in `app/models/new_model.py`
2. Import and export in `app/models/__init__.py`
3. Add to shell context in `run.py`
4. Restart containers to apply (tables auto-created via db.create_all())

### Adding a New Blueprint

1. Create view file in `app/views/new_feature.py` with Blueprint
2. Register blueprint in `app/__init__.py` create_app()
3. Create forms in `app/forms/new_feature_forms.py`
4. Create templates in `app/templates/new_feature/`
5. Add navigation links in `base.html`

### Adding a New Route

1. Add route function in appropriate blueprint with `@login_required` and permission checks
2. Create form in `app/forms/` (if needed)
3. Create template in `app/templates/`
4. Add navigation link in `base.html`
5. Mark all user-visible strings with `_()` or `_l()`
6. Extract and compile translations

### Adding Form Validation

```python
from wtforms.validators import ValidationError

class MyForm(FlaskForm):
    field_name = StringField(_l('Label'), validators=[DataRequired()])

    def validate_field_name(self, field):
        if not condition:
            raise ValidationError(_l('Error message'))
```

### Database Operations

```python
# Create
athlete = Athlete(first_name='John', last_name='Doe', ...)
db.session.add(athlete)
db.session.commit()

# Read
athlete = Athlete.query.get(id)
athletes = Athlete.query.filter_by(is_active=True).all()

# Update
athlete.first_name = 'Jane'
db.session.commit()

# Soft Delete
athlete.is_active = False
db.session.commit()
```

---

## Deployment

### Docker Environment Variables
Set in `.env.docker` or `.env` file:
```bash
DATABASE_URL=mysql+pymysql://fortidesk:password@db:3306/fortidesk
SECRET_KEY=your-production-secret-key-here
FLASK_ENV=production
FLASK_CONFIG=production
MYSQL_ROOT_PASSWORD=root-password
MYSQL_DATABASE=fortidesk
MYSQL_USER=fortidesk
MYSQL_PASSWORD=password
```

### Container Architecture
- **web**: Flask app (Gunicorn on port 5000, 4 workers, 120s timeout)
- **db**: MySQL 8.0 (port 3306, data persists in named volume)
- **nginx**: Reverse proxy (ports 80/443, proxies to web service)

### Startup Sequence
1. MySQL starts, initializes database
2. Web container runs `docker-entrypoint.sh`:
   - Waits for DB with retries (30 attempts, 2s between each)
   - Calls `init_db()` to create tables and default users
   - Starts Gunicorn server
3. Nginx starts, proxies requests to Flask

### Default Users (created by init_db())
- **admin**: username='admin', password='admin123'
- **coach**: username='coach', password='coach123'

---

## Code Style & Best Practices

### Python
- Use **ruff** for linting: `uvx ruff check`
- Use **pyright** for type checking: `uvx --from pyright pyright app/`
- Follow PEP 8 conventions
- Docstrings for all models and complex functions
- Type hints encouraged for new code

### Templates
- Use Bootstrap 5 classes for styling
- Keep templates DRY (extend base.html)
- Mark all user-visible text with `_()` for i18n
- Use semantic HTML
- Pagination for lists > 20 items

### Forms
- All user input must use WTForms
- Include CSRF tokens automatically (FlaskForm does this)
- Provide clear validation messages (localized)
- Use appropriate field types (DateField, SelectField, etc.)
- Custom validators for complex logic

### Database
- Always use SQLAlchemy ORM (no raw SQL)
- Add indexes for frequently queried fields (see models)
- Use foreign keys for relationships with on_delete/cascade rules
- Implement soft delete (is_active=False) for auditing
- Add indexes to __table_args__ for composite keys

### API/Response Patterns
- Use meaningful HTTP status codes
- Always check `current_user.is_admin()` or `current_user.is_coach()` before write operations
- Flash messages for user feedback (success/error/warning)
- Redirect after POST (PRG pattern)
- Paginate lists with `query.paginate(page=page, per_page=per_page)`

---

## Testing Guidelines

### Manual Testing Checklist
- [ ] Login/logout functionality
- [ ] Create athlete with 2 guardians, assign to team
- [ ] Edit athlete, update guardian and team info
- [ ] Search athletes by name/fiscal code
- [ ] Create team, assign head coach and staff
- [ ] Create staff member (each role type)
- [ ] Filter staff by role
- [ ] Check-in: bulk attendance for team
- [ ] Create equipment, assign to athlete, process return
- [ ] Equipment search/filter by category/status/condition
- [ ] Attendance report with filters and statistics
- [ ] Check expiry alerts (red/yellow/green badges)
- [ ] Switch language (EN ↔ IT)
- [ ] Verify permission checks (admin vs coach vs parent)
- [ ] Test soft delete (record disappears from list)
- [ ] Equipment overdue tracking

### Browser Testing
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (if on Mac)
- Mobile responsive (Bootstrap 5 handles this)

### Database Testing
```bash
# Check tables created
docker-compose exec db mysql -u fortidesk -p fortidesk -e "SHOW TABLES;"

# Verify relationships
docker-compose exec db mysql -u fortidesk -p fortidesk -e "SELECT * FROM teams LIMIT 5;"

# Check default users
docker-compose exec db mysql -u fortidesk -p fortidesk -e "SELECT id, username, role FROM users;"
```

---

## Troubleshooting

### Database Connection Issues
```bash
# Check DB container is running
docker-compose ps

# View DB logs
docker-compose logs db

# Verify connection from web container
docker-compose exec web python
>>> from run import app, db
>>> with app.app_context():
...     db.session.execute('SELECT 1')
```

### Database Not Initializing
```bash
# Check docker-entrypoint.sh logs
docker-compose logs web

# Manual initialization
docker-compose exec web python create_tables.py

# Verify tables
docker-compose exec db mysql -u fortidesk -p fortidesk -e "SHOW TABLES;"
```

### Translation Not Showing
```bash
# Recompile translations
uvx --with jinja2 --from babel pybabel compile -d translations

# Restart web container
docker-compose restart web

# Clear browser cache
```

### Form Validation Not Working
- Check CSRF token in template: `{{ form.hidden_tag() }}`
- Verify validators in form class
- Check flash messages for errors
- Ensure form.validate_on_submit() returns True

### Permission Denied on Edit/Delete
- Verify user role (admin/coach)
- Check `@login_required` decorator
- Verify permission check in view:
  ```python
  if not (current_user.is_admin() or current_user.is_coach()):
      flash(_('Permission denied'))
      return redirect(...)
  ```

---

## Important Reminders

### When Adding New Features
1. **Always** mark user-facing strings with `_()` or `_l()`
2. **Always** add permission checks in views
3. **Always** validate user input with WTForms
4. **Always** use soft delete (is_active=False)
5. **Always** add audit trail fields (created_at, updated_at, created_by)
6. **Always** create templates extending base.html
7. **Always** add navigation links if new section

### When Modifying Existing Code
1. Maintain consistency with existing patterns
2. Update translations after changing strings
3. Test both English and Italian interfaces
4. Verify permission matrix still works
5. Update documentation (README.md, this file)
6. Maintain soft delete approach (don't remove old records)

### Security Reminders
- Never store plain text passwords
- Never trust user input (always validate via WTForms)
- Never use raw SQL queries
- Never expose sensitive data in templates
- Always check user permissions before operations
- Always use CSRF tokens (FlaskForm includes automatically)
- Always use parameterized queries (ORM does this)

### Performance Considerations
- Use pagination (20 per page) for lists
- Add database indexes for frequently filtered fields
- Avoid N+1 queries: use relationships with lazy='dynamic' or eager loading
- Cache frequently accessed data (language selection, user role)

---

## Key Implementation Patterns

### Permission Pattern
```python
@some_bp.route('/path')
@login_required
def some_view():
    if not (current_user.is_admin() or current_user.is_coach()):
        flash(_('Permission denied'), 'error')
        return redirect(url_for('main.dashboard'))
    # ... implementation
```

### Soft Delete Pattern
```python
# Delete
item.is_active = False
db.session.commit()

# Query active records
items = Item.query.filter_by(is_active=True).all()
```

### Form Handling Pattern
```python
form = MyForm()
if form.validate_on_submit():
    item = Item(field=form.field.data, ...)
    db.session.add(item)
    db.session.commit()
    flash(_('Created successfully'), 'success')
    return redirect(url_for('view_route', id=item.id))
return render_template('template.html', form=form)
```

### Pagination Pattern
```python
page = request.args.get('page', 1, type=int)
per_page = 20
pagination = Item.query.filter_by(is_active=True).paginate(
    page=page, per_page=per_page, error_out=False
)
items = pagination.items
# In template: pagination.iter_pages(), pagination.has_prev/next, etc.
```

---

## Contact & Support

For development questions:
- Check README.md for user/deployment documentation
- Review this file for technical architecture
- Examine existing code patterns in similar features
- Test changes in Docker environment before committing
- Run linting and type checking before PRs

---

## Vault Context

Obsidian vault: `Projects/FortiDesk/`

- **FortiDesk - Overview**: Project hub (stack, architecture, blueprints, decisions)
- **FortiDesk - Log**: Session log with goals, accomplishments, decisions per session
- **FortiDesk - Solutions**: Solved problems and reusable patterns
- **FortiDesk - Code Review Follow-ups**: Backlog of review findings (INFO items from Gemini)
- **Plans/2026-02-14 - FortiDesk Feature Roadmap**: 6-phase implementation plan (Phases 0-5, complete)

---

## Automated Testing

### Setup
```bash
# Create venv and install deps (includes pytest, pytest-flask)
uv venv && uv pip install -r requirements.txt
```

### Running Tests
```bash
# Full suite (169 tests)
.venv/bin/python -m pytest tests/ -v

# Smoke tests only (fast, covers all routes)
.venv/bin/python -m pytest tests/test_routes_smoke.py -v

# Model unit tests
.venv/bin/python -m pytest tests/test_models.py -v

# Form validation tests
.venv/bin/python -m pytest tests/test_forms.py -v

# Permission/RBAC tests
.venv/bin/python -m pytest tests/test_permissions.py -v
```

### Test Architecture
- **Config**: `TestingConfig` in `config.py` (SQLite in-memory, CSRF disabled)
- **Fixtures**: `tests/conftest.py` (12 fixtures: app, client, users, sample data, logged-in clients)
- **Isolation**: `create_all`/`drop_all` per test via autouse `_setup_db` fixture

### Test Coverage
| File | Tests | What |
|------|-------|------|
| `test_routes_smoke.py` | 86 | All GET routes return 200/302, no 500s |
| `test_models.py` | 40 | Model methods across 9 models |
| `test_forms.py` | 15 | Age limits, fiscal code, guardian types, background checks |
| `test_permissions.py` | 28 | Unauthenticated redirect, coach restrictions, admin-only, soft delete |

---

**FortiDesk** - Built with care for Fortitudo 1901 Rugby ASD Rugby Club
