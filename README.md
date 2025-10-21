# FortiDesk 🏉

A comprehensive team management system for **Fortitudo 1901 Rugby ASD** youth teams. FortiDesk streamlines administrative tasks, athlete and staff registry management, guardian communications, and documentation for youth rugby teams.

## 🎯 Features Overview

FortiDesk provides complete management for:
- 👦 **Youth Athletes** (ages 3-18)
- 👔 **Staff & Officials** (coaches, escorts, managers, executives)
- 🔐 **Role-based Access Control**
- 🌐 **Multi-language Support** (English/Italian)

---

## ✨ Current Features

### 🔐 Authentication & User Management
- **Secure Login/Registration** with bcrypt password hashing
- **4 User Roles** with different permissions:
  - **Admin**: Full system access, can delete records
  - **Coach**: Can create/edit athletes and staff
  - **Parent**: View-only access (future: only own children)
  - **Player**: View-only access (future: only own data)
- **Persistent sessions** with "Remember me" functionality
- **CSRF protection** on all forms
- **Password security**: Bcrypt hashing with salt

### 🏃‍♂️ Athlete Registry Management

Complete digital registry for young athletes with comprehensive data tracking:

#### Athlete Data
- **Personal Information**: first name, last name, birth date/place, fiscal code
- **Residential Address**: street, number, postal code, city, province
- **Identity Document**: number, issuing authority, expiration date
- **Medical Certificate/Sports Booklet**: presence, type, expiration date
- **Automatic age calculation** and validation (3-18 years)
- **Audit trail**: creation date, last update, creator user

#### Guardian/Parent Data
- **Two guardians per athlete**: father, mother, or legal guardians
- **Complete contacts**: first name, last name, phone, email
- **Guardian type validation**: cannot have two fathers/mothers

#### Advanced Features
- 🔍 **Advanced search** by name, surname, or fiscal code
- ⚠️ **Automatic expiry alerts** for documents (≤30 days warning)
- 🏥 **Medical certificate status** with visual indicators
- 📊 **Registry statistics** with total counts
- 📝 **Complete data validation** (fiscal code format, age limits, etc.)
- 🗂️ **Pagination** for large lists (20 items per page)
- 🎨 **Visual status badges**: expired (red), expiring soon (yellow), valid (green)

### 👔 Staff & Personnel Management

Complete management system for organizational staff:

#### 7 Staff Roles
1. **Coach** (Allenatore) - Head coaches
2. **Assistant Coach** (Allenatore Assistente) - Assistant coaches
3. **Escort** (Accompagnatore) - Team escorts/chaperones
4. **Manager** (Dirigente) - Team managers
5. **President** (Presidente) - Club president
6. **Vice President** (Vice Presidente) - Vice president
7. **Secretary** (Segretario) - Administrative secretary

#### Staff Data
- **Personal Information**: first name, last name, birth date/place, fiscal code
- **Contact Information**: email, phone
- **Residential Address**: complete address details
- **Identity Document**: number, issuing authority, expiration
- **Role & Notes**: position with optional role description
- **Medical Certificate**: required for coaches and escorts
- **Background Check** (Certificato Penale): required for roles working with minors
- **Age validation**: staff must be 18+ years old

#### Advanced Features
- 🔍 **Search & Filter**: by name, email, fiscal code, or role
- 📋 **Role-based filtering**: view staff by specific role
- ⚠️ **Triple expiry tracking**: documents, medical certificates, background checks
- 💡 **Smart requirements**: automatic hints for role-specific documents
- 📊 **Status indicators**: visual badges for all expiry items
- 🗂️ **Pagination** with total staff count

### 🌐 Internationalization (i18n)

Full bilingual support with professional translations:

- **2 Languages Supported**:
  - 🇬🇧 **English** (default)
  - 🇮🇹 **Italiano**
- **Language Switcher**: Dropdown in navbar with flag icons
- **250+ Translated Strings**: Complete coverage of:
  - All UI elements and navigation
  - Form labels and placeholders
  - Validation messages
  - Success/error messages
  - Role names and statuses
- **Session Persistence**: Language preference saved across sessions
- **Browser Detection**: Automatic language from browser settings as fallback
- **Professional Tone**: Formal Italian ("Lei" form) for user messages

### 📱 User Interface & Experience

- **Responsive Design**: Bootstrap 5.1.3 framework
- **Clean Navigation**:
  - Top navbar with Dashboard, Athletes, Staff links
  - Language selector dropdown
  - User profile dropdown
- **Smart Forms**:
  - Conditional fields (show/hide based on selections)
  - Real-time validation feedback
  - Clear error messages
- **Visual Feedback**:
  - Color-coded status badges (red/yellow/green/gray)
  - Flash messages for user actions
  - Loading states and transitions
- **Card-based Layouts**: Clean, scannable lists
- **Pagination Controls**: Previous/Next with page indicators
- **Mobile-Friendly**: Responsive on all devices

### 🔒 Security & Data Protection

- **Authentication Security**:
  - Bcrypt password hashing
  - Secure session management
  - CSRF token protection
- **Authorization**:
  - Role-based access control (RBAC)
  - Permission checks on all sensitive operations
  - Route protection with decorators
- **Data Security**:
  - SQL injection prevention (SQLAlchemy ORM)
  - Input validation and sanitization
  - XSS protection via Jinja2 auto-escaping
- **Audit Trail**:
  - Creation and modification timestamps
  - Creator user tracking
  - Soft delete (no data loss)

### 🗄️ Database Architecture

- **4 Core Models**:
  1. **User**: System users with authentication
  2. **Athlete**: Youth athlete registry
  3. **Guardian**: Parent/guardian contacts
  4. **Staff**: Organizational personnel
- **Optimized Relations**:
  - User → Athletes (1:many, created_by)
  - User → Staff (1:many, created_by)
  - Athlete → Guardians (1:2, required)
- **Performance**:
  - Indexes on fiscal_code, email, role
  - Efficient queries with eager loading
  - Pagination for large datasets
- **Data Integrity**:
  - Foreign key constraints
  - Unique constraints (fiscal codes, emails)
  - NOT NULL constraints on required fields

---

## 🛠️ Technology Stack

### Backend
- **Flask 3.0.0** - Modern Python web framework
- **SQLAlchemy 3.1.1** - Powerful ORM for database
- **Flask-Login 0.6.3** - User session management
- **Flask-WTF 1.2.1** - Form handling and validation
- **Flask-Babel 4.0.0** - Internationalization support
- **bcrypt 4.1.2** - Secure password hashing
- **PyMySQL 1.1.0** - MySQL database driver
- **python-dotenv 1.0.0** - Environment configuration

### Frontend
- **Bootstrap 5.1.3** - Responsive CSS framework
- **Jinja2** - Powerful template engine
- **Vanilla JavaScript** - Lightweight client-side logic

### Database
- **MySQL 8.0** - Reliable relational database
- **Optimized schema** with proper indexes
- **Foreign key relations** for data integrity

### Deployment
- **Docker** - Application containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy and static file serving
- **Gunicorn 21.2.0** - Production WSGI server

---

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git for repository cloning
- 8GB RAM recommended
- Ports 80, 443, 3306 available

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd FortiDesk

# 2. Copy environment file
cp .env.example .env

# 3. (Optional) Edit .env with your settings
nano .env

# 4. Start with automatic script
./docker-start.sh

# Or manually with docker-compose
docker-compose up -d
```

### First Access
- **Application URL**: http://localhost
- **Default Admin**:
  - Username: `admin`
  - Password: `admin123`
  - ⚠️ **Change immediately in production!**
- **Default Coach**:
  - Username: `coach`
  - Password: `coach123`

### Useful Commands

```bash
# View real-time logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f web

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v

# Rebuild containers
docker-compose build --no-cache

# Restart a specific service
docker-compose restart web

# Access database shell
docker-compose exec db mysql -u fortidesk -p fortidesk

# Access Python shell with Flask context
docker-compose exec web python
>>> from run import app, db, User, Athlete, Staff
>>> with app.app_context():
...     users = User.query.all()
```

---

## 📁 Project Structure

```
FortiDesk/
├── app/                              # Flask application
│   ├── __init__.py                   # App factory and config
│   ├── models/                       # SQLAlchemy models
│   │   ├── __init__.py              # Model exports
│   │   ├── user.py                  # User authentication model
│   │   ├── athlete.py               # Athlete registry model
│   │   ├── guardian.py              # Guardian/parent model
│   │   └── staff.py                 # Staff/personnel model
│   ├── views/                        # Flask blueprints (routes)
│   │   ├── __init__.py
│   │   ├── auth.py                  # Authentication routes
│   │   ├── main.py                  # Dashboard and main pages
│   │   ├── athletes.py              # Athlete CRUD operations
│   │   └── staff.py                 # Staff CRUD operations
│   ├── forms/                        # WTForms for validation
│   │   ├── __init__.py
│   │   ├── athletes_forms.py        # Athlete and guardian forms
│   │   └── staff_forms.py           # Staff forms
│   ├── templates/                    # Jinja2 templates
│   │   ├── base.html                # Base template with navbar
│   │   ├── dashboard.html           # Dashboard page
│   │   ├── auth/                    # Authentication pages
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── athletes/                # Athlete management
│   │   │   ├── index.html           # List view
│   │   │   ├── detail.html          # Detail view
│   │   │   └── form.html            # Create/edit form
│   │   └── staff/                   # Staff management
│   │       ├── index.html           # List view
│   │       ├── detail.html          # Detail view
│   │       └── form.html            # Create/edit form
│   └── static/                       # Static assets
│       ├── css/                     # Custom stylesheets
│       └── js/                      # JavaScript files
├── docker/                           # Docker configurations
│   ├── nginx/                       # Nginx configs
│   │   ├── nginx.conf
│   │   └── default.conf
│   └── mysql/                       # Database init scripts
│       └── init.sql
├── translations/                     # i18n translations
│   └── it/                          # Italian translations
│       └── LC_MESSAGES/
│           ├── messages.po          # Translation source
│           └── messages.mo          # Compiled translations
├── babel.cfg                         # Babel extraction config
├── config.py                         # Flask configuration
├── docker-compose.yml               # Service orchestration
├── Dockerfile                       # Flask app container
├── docker-start.sh                  # Quick start script
├── requirements.txt                 # Python dependencies
├── run.py                           # Application entry point
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
├── CLAUDE.md                        # Development documentation
└── README.md                        # This file
```

---

## 🗄️ Database Schema

### Tables Overview

#### **users** - System Users
- `id` (PK)
- `username` (unique, indexed)
- `email` (unique, indexed)
- `password_hash`
- `first_name`, `last_name`
- `role` (admin/coach/parent/player)
- `is_active`
- `created_at`, `last_login`

#### **athletes** - Youth Athletes
- `id` (PK)
- Personal: `first_name`, `last_name`, `birth_date`, `birth_place`, `fiscal_code` (unique)
- Address: `street_address`, `street_number`, `postal_code`, `city`, `province`
- Document: `document_number`, `issuing_authority`, `document_expiry`
- Medical: `has_medical_certificate`, `certificate_type`, `certificate_expiry`
- Meta: `created_at`, `updated_at`, `created_by` (FK→users), `is_active`

#### **guardians** - Parents/Legal Guardians
- `id` (PK)
- `first_name`, `last_name`
- `phone`, `email`
- `guardian_type` (father/mother/guardian)
- `athlete_id` (FK→athletes, required)
- `created_at`, `updated_at`, `is_active`

#### **staff** - Organizational Personnel
- `id` (PK)
- Personal: `first_name`, `last_name`, `birth_date`, `birth_place`, `fiscal_code` (unique)
- Contact: `phone`, `email`
- Address: `street_address`, `street_number`, `postal_code`, `city`, `province`
- Document: `document_number`, `issuing_authority`, `document_expiry`
- Role: `role` (coach/assistant_coach/escort/manager/president/vice_president/secretary)
- `role_notes` (optional text)
- Medical: `has_medical_certificate`, `certificate_type`, `certificate_expiry`
- Background: `has_background_check`, `background_check_date`, `background_check_expiry`
- Meta: `created_at`, `updated_at`, `created_by` (FK→users), `is_active`

### Relationships
- `User` 1→N `Athlete` (created_by)
- `User` 1→N `Staff` (created_by)
- `Athlete` 1→N `Guardian` (athlete_id, typically 2 per athlete)
- All deletions are "soft" (is_active=False)

---

## 🔑 Permission Matrix

| Action | Admin | Coach | Parent | Player |
|--------|-------|-------|--------|--------|
| View Athletes | ✅ | ✅ | ✅ | ✅ |
| Create Athletes | ✅ | ✅ | ❌ | ❌ |
| Edit Athletes | ✅ | ✅ | ❌ | ❌ |
| Delete Athletes | ✅ | ❌ | ❌ | ❌ |
| View Staff | ✅ | ✅ | ✅ | ✅ |
| Create Staff | ✅ | ✅ | ❌ | ❌ |
| Edit Staff | ✅ | ✅ | ❌ | ❌ |
| Delete Staff | ✅ | ❌ | ❌ | ❌ |
| User Management | ✅ | ❌ | ❌ | ❌ |

---

## 🌍 Internationalization

### Supported Languages
- **English (en)** - Default
- **Italian (it)** - Complete translation

### Adding New Translations

```bash
# 1. Mark new strings in code
# Python files: use _() or _l()
flash(_('Success message'))
label = _l('Form Label')

# Templates: use {{ _('text') }}
<h1>{{ _('Page Title') }}</h1>

# 2. Extract messages
uvx --with jinja2 --from babel pybabel extract -F babel.cfg -k _l -k _ -o messages.pot .

# 3. Update catalogs
uvx --with jinja2 --from babel pybabel update -i messages.pot -d translations

# 4. Edit translations
# Edit translations/it/LC_MESSAGES/messages.po

# 5. Compile
uvx --with jinja2 --from babel pybabel compile -d translations
```

---

## 🛣️ Future Features Roadmap

### 📅 Phase 2: Team Management
- [ ] Team/squad creation (U12, U14, U16, etc.)
- [ ] Athlete team assignments
- [ ] Season management
- [ ] Roster management

### 📋 Phase 3: Training & Attendance
- [ ] Training session planning
- [ ] Athlete attendance tracking
- [ ] Absence notifications
- [ ] Attendance reports

### 🏟️ Phase 4: Match Management
- [ ] Match scheduling
- [ ] Player call-ups
- [ ] Match lineups
- [ ] Results tracking

### 💬 Phase 5: Communications
- [ ] Parent messaging system
- [ ] Team announcements
- [ ] Email notifications
- [ ] Newsletter generation

### 📄 Phase 6: Document Management
- [ ] Document upload (PDF, images)
- [ ] Digital document archive
- [ ] Automatic form generation
- [ ] Document expiry reminders

### 💰 Phase 7: Financial Management
- [ ] Membership fee tracking
- [ ] Payment status
- [ ] Invoice generation
- [ ] Financial reports

### 📊 Phase 8: Analytics & Reporting
- [ ] Attendance statistics
- [ ] Team performance metrics
- [ ] Custom report builder
- [ ] Data export (Excel, CSV, PDF)

---

## 🧪 Development

### Local Development (without Docker)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env with local MySQL connection

# 4. Initialize database
python run.py  # First run creates tables

# 5. Run development server
flask run
# Or: python run.py
```

### Running Tests

```bash
# Linting
uvx ruff check

# Type checking
uvx --from pyright pyright app/

# Manual testing
# Access http://localhost:5000
```

---

## 🤝 Contributing

FortiDesk is developed specifically for **Fortitudo 1901 Rugby ASD**.

### Reporting Issues
1. Create an issue on GitHub
2. Include steps to reproduce
3. Provide error messages/screenshots

### Suggesting Features
1. Open a GitHub issue with "[Feature Request]" prefix
2. Describe the use case
3. Explain expected behavior

### Code Contributions
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

This project is developed for internal use of **Fortitudo 1901 Rugby ASD**.

---

## 📞 Support

For questions or support:
- 📧 Email: [contact information]
- 🐛 GitHub Issues: [repository issues page]
- 📚 Documentation: See CLAUDE.md for development docs

---

## 🙏 Acknowledgments

- **Fortitudo 1901 Rugby ASD** - For the opportunity and requirements
- **Flask Community** - For excellent documentation and support
- **Bootstrap Team** - For the responsive framework

---

**FortiDesk** - *Simplifying management, improving youth rugby* 🏉

*Built with ❤️ for Fortitudo 1901 Rugby ASD*
