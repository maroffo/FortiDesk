# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**FortiDesk** is a comprehensive team management system for **Fortitudo 1901 Rugby ASD** youth teams. It streamlines administrative tasks, athlete and staff registry management, guardian communications, and documentation for youth rugby teams.

### Key Capabilities
- **Athlete Management**: Complete registry for youth athletes (ages 3-18) with guardian tracking
- **Staff Management**: Personnel management for coaches, escorts, managers, and club officials
- **Attendance Tracking**: Track athlete attendance at training sessions, matches, and events
- **Equipment Management**: Inventory management and equipment assignment tracking
- **Multi-language Support**: Full English/Italian internationalization
- **Role-based Access**: Admin, Coach, Parent, and Player roles
- **Document Tracking**: Automated expiry alerts for documents, medical certificates, and background checks

---

## Quick Command Reference

### Docker Operations
```bash
# Start application
./docker-start.sh

# Start manually
docker-compose up -d

# View logs
docker-compose logs -f              # All services
docker-compose logs -f web          # Flask app only
docker-compose logs -f db           # MySQL only

# Stop services
docker-compose down                 # Stop containers
docker-compose down -v              # Stop and remove volumes (⚠️ deletes data!)

# Rebuild
docker-compose build --no-cache
docker-compose up -d --build

# Restart specific service
docker-compose restart web
docker-compose restart db

# Check service status
docker-compose ps
```

### Database Operations
```bash
# Access MySQL shell
docker-compose exec db mysql -u fortidesk -p fortidesk

# Access Python shell with Flask context
docker-compose exec web python
>>> from run import app, db, User, Athlete, Staff, Attendance, Equipment
>>> with app.app_context():
...     users = User.query.all()
...     athletes = Athlete.query.filter_by(is_active=True).all()
```

### Local Development (without Docker)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate              # Linux/Mac
# venv\Scripts\activate                # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with local MySQL connection

# Run development server
flask run
# Or: python run.py
```

### Code Quality
```bash
# Linting
uvx ruff check

# Type checking
uvx --from pyright pyright app/
```

### Internationalization (i18n)
```bash
# 1. Extract new translatable strings
uvx --with jinja2 --from babel pybabel extract -F babel.cfg -k _l -k _ -o messages.pot .

# 2. Update translation catalogs
uvx --with jinja2 --from babel pybabel update -i messages.pot -d translations

# 3. Edit translations manually
# Edit: translations/it/LC_MESSAGES/messages.po

# 4. Compile translations
uvx --with jinja2 --from babel pybabel compile -d translations

# 5. Restart web container to see changes
docker-compose restart web
```

---

## Technology Stack

### Backend Framework
- **Flask 3.0.0**: Python web framework
- **SQLAlchemy 3.1.1**: Database ORM
- **Flask-Login 0.6.3**: User authentication
- **Flask-WTF 1.2.1**: Form handling and validation
- **Flask-Babel 4.0.0**: Internationalization (i18n)
- **bcrypt 4.1.2**: Password hashing
- **PyMySQL 1.1.0**: MySQL driver

### Frontend
- **Bootstrap 5.1.3**: Responsive CSS framework
- **Jinja2**: Template engine
- **Vanilla JavaScript**: Client-side interactions

### Database
- **MySQL 8.0**: Relational database
- **Schema**: 7 main tables (users, athletes, guardians, staff, attendance, equipment, equipment_assignments)

### Deployment
- **Docker + Docker Compose**: Containerization
- **Nginx**: Reverse proxy
- **Gunicorn 21.2.0**: WSGI server

---

## Project Structure

```
FortiDesk/
├── app/                              # Main Flask application
│   ├── __init__.py                   # App factory, Babel configuration
│   ├── models/                       # SQLAlchemy database models
│   │   ├── __init__.py              # Model exports
│   │   ├── user.py                  # User authentication model
│   │   ├── athlete.py               # Athlete registry model
│   │   ├── guardian.py              # Guardian/parent model
│   │   ├── staff.py                 # Staff/personnel model
│   │   ├── attendance.py            # Attendance tracking model
│   │   └── equipment.py             # Equipment & assignment models
│   ├── views/                        # Flask blueprints (controllers)
│   │   ├── __init__.py
│   │   ├── auth.py                  # Login/logout/register routes
│   │   ├── main.py                  # Dashboard, language switcher
│   │   ├── athletes.py              # Athlete CRUD operations
│   │   ├── staff.py                 # Staff CRUD operations
│   │   ├── attendance.py            # Attendance tracking routes
│   │   └── equipment.py             # Equipment management routes
│   ├── forms/                        # WTForms for validation
│   │   ├── __init__.py
│   │   ├── athletes_forms.py        # AthleteForm, GuardianForm fields
│   │   ├── staff_forms.py           # StaffForm with role-based validation
│   │   ├── attendance_forms.py      # Attendance forms
│   │   └── equipment_forms.py       # Equipment and assignment forms
│   ├── templates/                    # Jinja2 HTML templates
│   │   ├── base.html                # Base template with navbar, language switcher
│   │   ├── dashboard.html           # User dashboard
│   │   ├── auth/                    # Authentication pages
│   │   ├── athletes/                # Athlete management templates
│   │   ├── staff/                   # Staff management templates
│   │   ├── attendance/              # Attendance tracking templates
│   │   └── equipment/               # Equipment management templates
│   └── static/                       # Static files
│       ├── css/style.css            # Custom styles
│       └── js/app.js                # JavaScript utilities
├── docker/                           # Docker configurations
│   ├── nginx/                       # Nginx reverse proxy config
│   └── mysql/                       # Database initialization scripts
├── translations/                     # i18n translation files
│   └── it/LC_MESSAGES/              # Italian translations
│       ├── messages.po              # Translation source
│       └── messages.mo              # Compiled catalog
├── babel.cfg                         # Babel extraction configuration
├── config.py                         # Flask configuration classes
├── docker-compose.yml               # Multi-container orchestration
├── Dockerfile                       # Flask app container definition
├── docker-start.sh                  # Quick start script
├── docker-entrypoint.sh             # Container initialization script
├── requirements.txt                 # Python dependencies
├── run.py                           # Application entry point
└── README.md                        # User documentation
```

---

## Database Models

The system uses **7 core database models**:

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
- `attendance_created`: One-to-many with Attendance (via created_by)
- `equipment_created`: One-to-many with Equipment (via created_by)

---

### Athlete Model (`app/models/athlete.py`)
**Purpose**: Youth athlete registry (ages 3-18)

**Fields**:
- Personal: `first_name`, `last_name`, `birth_date`, `birth_place`, `fiscal_code` (unique)
- Address: `street_address`, `street_number`, `postal_code`, `city`, `province`
- Document: `document_number`, `issuing_authority`, `document_expiry`
- Medical: `has_medical_certificate`, `certificate_type`, `certificate_expiry`
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
- Cannot have two guardians of same type (e.g., two fathers)

---

### Staff Model (`app/models/staff.py`)
**Purpose**: Organizational personnel management

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

**Validation**:
- Age must be 18+ years
- Fiscal code must be unique and valid
- Medical certificate required for coach/assistant_coach/escort roles
- Background check required for roles working with minors

---

### Attendance Model (`app/models/attendance.py`)
**Purpose**: Track athlete attendance at training sessions, matches, and events

**Fields**:
- `athlete_id`: Foreign key to Athlete (required)
- `date`: Date of session (indexed)
- `session_type`: Type of session (training/match/event)
- `status`: Attendance status (present/absent/excused/late)
- `notes`: Optional notes about attendance
- `created_by`: Foreign key to User who recorded attendance
- `created_at`, `updated_at`: Timestamps
- `is_active`: Soft delete flag

**Methods**:
- `get_status_display()`: Return localized status name
- `get_session_type_display()`: Return localized session type

**Relationships**:
- `athlete`: Many-to-one with Athlete
- `creator`: Many-to-one with User (who recorded it)

**Indexes**:
- Composite index on (athlete_id, date) for athlete history queries
- Composite index on (date, session_type) for session reports

**Business Logic**:
- Tracks individual attendance records per athlete per session
- Supports different session types (training, match, event)
- Four status types: present, absent, excused, late

---

### Equipment Model (`app/models/equipment.py`)
**Purpose**: Inventory management for rugby equipment

**Fields**:
- `name`: Equipment name (indexed)
- `category`: Equipment category (ball/jersey/protective/training_aid/other) (indexed)
- `size`: Size designation (XS/S/M/L/XL or numeric)
- `code`: Unique inventory/barcode (unique, indexed)
- `condition`: Current condition (new/good/fair/poor/damaged)
- `status`: Availability status (available/assigned/maintenance/retired)
- Purchase: `purchase_date`, `purchase_price`, `supplier`
- Maintenance: `last_maintenance_date`, `next_maintenance_date`, `maintenance_notes`
- Additional: `description`, `location`, `quantity`
- Meta: `created_by`, `created_at`, `updated_at`, `is_active`

**Methods**:
- `get_category_display()`: Localized category name
- `get_condition_display()`: Localized condition name
- `get_status_display()`: Localized status name
- `needs_maintenance()`: Check if maintenance is due
- `is_available()`: Check if available for assignment

**Relationships**:
- `creator`: Many-to-one with User
- `assignments`: One-to-many with EquipmentAssignment (cascade delete)

**Business Logic**:
- Unique inventory codes for tracking
- Maintenance scheduling with alerts
- Status tracking (available/assigned/maintenance/retired)

---

### EquipmentAssignment Model (`app/models/equipment.py`)
**Purpose**: Track equipment loans to athletes

**Fields**:
- Foreign keys: `equipment_id`, `athlete_id`, `assigned_by`, `returned_by`
- Dates: `assigned_date`, `expected_return_date`, `actual_return_date`
- Condition: `condition_at_assignment`, `condition_at_return`
- Notes: `assignment_notes`, `return_notes`
- Status: `is_returned`, `is_active`
- Meta: `created_at`, `updated_at`

**Methods**:
- `is_overdue()`: Check if return is overdue
- `days_overdue()`: Calculate days overdue

**Relationships**:
- `equipment`: Many-to-one with Equipment
- `athlete`: Many-to-one with Athlete
- `assigner`: Many-to-one with User (who assigned)
- `returner`: Many-to-one with User (who processed return)

**Indexes**:
- Composite index on (athlete_id, is_returned) for athlete's current assignments
- Composite index on (equipment_id, is_returned) for equipment availability

**Business Logic**:
- Tracks condition at assignment and return
- Calculates overdue returns
- Links to both assigning and returning users for audit trail

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

**Permissions**: Public access (redirects if authenticated)

---

### Main Blueprint (`app/views/main.py`)
**Routes**:
- `GET /`: Redirect to dashboard or login
- `GET /dashboard`: User dashboard (requires login)
- `GET /set_language/<language>`: Language switcher

**Functions**:
- Language preference stored in session
- Browser language detection as fallback

---

### Athletes Blueprint (`app/views/athletes.py`)
**Routes**:
- `GET /athletes/`: List athletes (paginated, searchable)
- `GET/POST /athletes/new`: Create athlete (admin/coach only)
- `GET /athletes/<id>`: View athlete details
- `GET/POST /athletes/<id>/edit`: Edit athlete (admin/coach only)
- `POST /athletes/<id>/delete`: Soft delete (admin only)

**Features**:
- Search by name, fiscal code
- Pagination (20 per page)
- Status badges for expiry alerts
- Fiscal code uniqueness validation

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

---

### Attendance Blueprint (`app/views/attendance.py`)
**Routes**:
- `GET /attendance/`: List attendance records (paginated, filterable)
- `GET/POST /attendance/new`: Record new attendance (admin/coach only)
- `GET/POST /attendance/bulk`: Bulk attendance entry for sessions (admin/coach only)
- `GET /attendance/<id>`: View attendance details
- `GET/POST /attendance/<id>/edit`: Edit attendance record (admin/coach only)
- `POST /attendance/<id>/delete`: Soft delete (admin only)

**Features**:
- Filter by athlete, date range, session type, status
- Bulk entry for recording entire session attendance
- Attendance statistics and reports
- Visual status indicators

---

### Equipment Blueprint (`app/views/equipment.py`)
**Routes**:
- `GET /equipment/`: List equipment inventory (paginated, filterable)
- `GET/POST /equipment/new`: Add new equipment (admin/coach only)
- `GET /equipment/<id>`: View equipment details and assignment history
- `GET/POST /equipment/<id>/edit`: Edit equipment (admin/coach only)
- `POST /equipment/<id>/delete`: Soft delete (admin only)
- `GET/POST /equipment/<id>/assign`: Assign to athlete (admin/coach only)
- `POST /equipment/assignment/<id>/return`: Process equipment return (admin/coach only)

**Features**:
- Filter by category, status, condition
- Search by name or inventory code
- Assignment history tracking
- Overdue equipment alerts
- Maintenance scheduling

---

## Forms (`app/forms/`)

### AthleteForm (`athletes_forms.py`)
**Fields**:
- Personal data (name, birth info, fiscal code)
- Address (street, number, postal code, city, province)
- Document (number, authority, expiry)
- Medical certificate (optional)
- Guardian 1 (name, contact, type)
- Guardian 2 (name, contact, type)

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

### AttendanceForm (`attendance_forms.py`)
**Fields**:
- `athlete_id`: Athlete selection
- `date`: Session date
- `session_type`: Type (training/match/event)
- `status`: Attendance status (present/absent/excused/late)
- `notes`: Optional notes

**Features**:
- Bulk attendance form for recording multiple athletes at once
- Date validation (not in future)

---

### EquipmentForm & AssignmentForm (`equipment_forms.py`)
**EquipmentForm Fields**:
- Basic info (name, category, size, code)
- Condition and status
- Purchase info (date, price, supplier)
- Maintenance scheduling
- Location and description

**AssignmentForm Fields**:
- `equipment_id`: Equipment selection
- `athlete_id`: Athlete selection
- `assigned_date`: Assignment date
- `expected_return_date`: Expected return
- `condition_at_assignment`: Condition when assigned
- `assignment_notes`: Optional notes

**Custom Validation**:
- Unique equipment codes
- Equipment must be available for assignment
- Return date cannot be before assignment date

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
- `translations/it/LC_MESSAGES/messages.po`: Italian catalog
- `translations/it/LC_MESSAGES/messages.mo`: Compiled binary

### Usage in Code

**Python files**:
```python
from flask_babel import gettext as _, lazy_gettext as _l

# Runtime strings (flash messages, etc.)
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
See "Quick Command Reference" section above for i18n commands.

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
- **Soft delete**: Records marked inactive, never truly deleted
- **Audit trail**: created_at, updated_at, created_by on all records
- **Input validation**: WTForms validators on all user input
- **XSS protection**: Jinja2 auto-escaping

---

## Common Development Tasks

### Adding a New Model

1. Create model in `app/models/new_model.py`
2. Import in `app/models/__init__.py`
3. Add to shell context in `run.py`
4. Restart containers to create table

### Adding a New Route

1. Add route function in appropriate blueprint
2. Create form in `app/forms/` (if needed)
3. Create template in `app/templates/`
4. Add navigation link in `base.html`
5. Mark all strings with `_()` or `_l()`
6. Extract and translate messages

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
Set in `.env` file:
```bash
DATABASE_URL=mysql+pymysql://fortidesk:password@db:3306/fortidesk
SECRET_KEY=your-production-secret-key-here
FLASK_ENV=production
MYSQL_ROOT_PASSWORD=root-password
MYSQL_DATABASE=fortidesk
MYSQL_USER=fortidesk
MYSQL_PASSWORD=password
```

### Container Architecture
- **web**: Flask app (Gunicorn on port 5000)
- **db**: MySQL 8.0 (port 3306)
- **nginx**: Reverse proxy (ports 80/443)

### Startup Sequence
1. MySQL starts, initializes database
2. Web app waits for DB health check (via `docker-entrypoint.sh`)
3. `run.py:init_db()` creates tables and default users
4. Gunicorn starts with 4 workers
5. Nginx starts, proxies to Flask

### Startup Scripts

**docker-start.sh**: Quick start script
- Checks for `.env` file, creates from `.env.example` if missing
- Builds Docker images
- Starts services in detached mode
- Shows service status and connection info

**docker-entrypoint.sh**: Container initialization for web service
- Waits for database (30 retries, 2s intervals)
- Calls `init_db()` from `run.py` to create tables and default users
- Starts Gunicorn with 4 workers on port 5000

---

## Code Style & Best Practices

### Python
- Use **ruff** for linting: `uvx ruff check`
- Use **pyright** for type checking: `uvx --from pyright pyright app/`
- Follow PEP 8 conventions
- Docstrings for all models and complex functions

### Templates
- Use Bootstrap classes for styling
- Keep templates DRY (extend base.html)
- Mark all user-visible text with `_()` for i18n
- Use semantic HTML

### Forms
- All user input must use WTForms
- Include CSRF tokens
- Provide clear validation messages
- Use appropriate field types

### Database
- Always use SQLAlchemy ORM (no raw SQL)
- Add indexes for frequently queried fields
- Use foreign keys for relationships
- Implement soft delete (is_active=False)

---

## Testing Guidelines

### Manual Testing Checklist
- [ ] Login/logout functionality
- [ ] Create athlete with 2 guardians
- [ ] Edit athlete, update guardian info
- [ ] Search athletes by name/fiscal code
- [ ] Create staff member (each role type)
- [ ] Filter staff by role
- [ ] Record attendance for training session
- [ ] Add equipment to inventory
- [ ] Assign equipment to athlete
- [ ] Process equipment return
- [ ] Check expiry alerts (red/yellow/green badges)
- [ ] Switch language (EN ↔ IT)
- [ ] Verify permission checks (admin vs coach vs parent)
- [ ] Test soft delete (record disappears from list)

### Browser Testing
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (if on Mac)
- Mobile responsive (Bootstrap handles this)

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

---

## Important Reminders

### When Adding New Features
1. ✅ **Always** mark user-facing strings with `_()` or `_l()`
2. ✅ **Always** add permission checks in views
3. ✅ **Always** validate user input with WTForms
4. ✅ **Always** use soft delete (is_active=False)
5. ✅ **Always** add audit trail fields (created_at, updated_at, created_by)

### When Modifying Existing Code
1. ✅ Maintain consistency with existing patterns
2. ✅ Update translations after changing strings
3. ✅ Test both English and Italian interfaces
4. ✅ Verify permission matrix still works
5. ✅ Update documentation (README.md, this file)

### Security Reminders
- 🔒 **Never** store plain text passwords
- 🔒 **Never** trust user input (always validate)
- 🔒 **Never** use raw SQL queries
- 🔒 **Never** expose sensitive data in templates
- 🔒 **Always** check user permissions before operations

---

## Contact & Support

For development questions:
- Check README.md for user documentation
- Review this file for technical details
- Examine existing code for patterns
- Test changes in Docker environment before committing

---

**FortiDesk** - Built with care for Fortitudo 1901 Rugby ASD 🏉
