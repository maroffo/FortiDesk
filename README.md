# FortiDesk 🏉

A comprehensive team management system for **Fortitudo 1901 Rugby ASD** youth teams. FortiDesk streamlines administrative tasks, player registry management, parent communications, and documentation for youth rugby teams.

## 🎯 Current Features

### 🔐 Authentication System
- **Secure Login/Registration** with bcrypt password hashing
- **User role management**: Admin, Coach, Parent, Player
- **Persistent sessions** with Flask-Login
- **Role-based dashboard** personalization

### 👶 Player Registry
Complete management system for young players data:

#### Player Data
- **Complete registry**: name, surname, birth date/place, fiscal code
- **Residential address**: street, number, postal code, city, province
- **Identity document**: number, issuing authority, expiration date
- **Medical certificate/sports booklet**: presence, type, expiration date
- **Automatic age calculation**

#### Parents Data
- **Two parents per player**: father, mother, or guardians
- **Complete contacts**: name, surname, phone, email
- **Parent type** (father/mother/guardian)

#### Advanced Features
- 🔍 **Advanced search** by name, surname, or fiscal code
- ⚠️ **Automatic alerts** for expiring documents (30 days)
- 🏥 **Medical certificate control** with visual status
- 📊 **Registry statistics** with counters
- 📝 **Complete data validation**
- 🗂️ **Pagination** for large lists

### 🔑 Permission System
- **Admin**: complete access, registry deletion
- **Coach**: player insertion and modification
- **Other roles**: view only

## 🛠️ Technologies Used

### Backend
- **Flask 3.0.0** - Python web framework
- **SQLAlchemy** - Database ORM
- **Flask-Login** - Authentication management
- **Flask-WTF** - Forms and validation
- **bcrypt** - Secure password hashing
- **PyMySQL** - MySQL database driver

### Frontend
- **Bootstrap 5.1.3** - Responsive CSS framework
- **Jinja2** - Template engine
- **Vanilla JavaScript** - Client-side interactions

### Database
- **MySQL 8.0** - Relational database
- **Optimized relations** with performance indexes

### Deployment
- **Docker** - Complete containerization
- **Docker Compose** - Service orchestration
- **Nginx** - Reverse proxy and static file handling
- **Gunicorn** - WSGI server for production

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git to clone the repository

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd FortiDesk

# Automatic startup with script
./docker-start.sh

# Or manually
docker-compose up -d
```

### Access
- **Application**: http://localhost
- **Database**: localhost:3306
- **Default users**:
  - Admin: `admin` / `admin123`
  - Coach: `coach` / `coach123`

### Useful Commands
```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild images
docker-compose build --no-cache
```

## 📁 Project Structure

```
FortiDesk/
├── app/                          # Flask application
│   ├── models/                   # Database models
│   │   ├── user.py              # System users
│   │   ├── bambino.py           # Player registry
│   │   └── genitore.py          # Parent data
│   ├── views/                    # Controllers (Blueprints)
│   │   ├── auth.py              # Authentication
│   │   ├── main.py              # Main pages
│   │   └── anagrafica.py        # Registry management
│   ├── forms/                    # WTForms
│   │   └── anagrafica_forms.py  # Player forms
│   ├── templates/                # Jinja2 templates
│   │   ├── base.html            # Base template
│   │   ├── auth/                # Authentication templates
│   │   └── anagrafica/          # Registry templates
│   └── static/                   # Static files (CSS, JS)
├── docker/                       # Docker configurations
│   ├── nginx/                   # Nginx config
│   └── mysql/                   # Database init scripts
├── docker-compose.yml           # Service orchestration
├── Dockerfile                   # Flask app image
├── requirements.txt             # Python dependencies
└── run.py                      # Application entry point
```

## 🗄️ Database Schema

### Main Tables
- **users**: System users with roles
- **bambini**: Complete player registry
- **genitori**: Parent contact data

### Relationships
- One player has two parents (1:2)
- One user can insert many players (1:N)
- Soft delete to maintain history

## 🛣️ Future Features Roadmap

### 📅 Training Management
- Training session planning
- Event and match calendar
- Player attendance

### 💬 Communications
- Parent-coach messaging system
- Automatic notifications
- Team newsletter

### 📋 Team Management
- Age category divisions
- Player team assignments
- Player statistics

### 📄 Documents
- Player document uploads
- Automatic form generation
- Digital archive

### 📊 Reporting
- Training attendance reports
- Team statistics
- Data export

## 🤝 Contributing

FortiDesk is developed specifically for Fortitudo 1901 Rugby ASD. For suggestions or bug reports:

1. Create an issue on GitHub
2. Contact the development team
3. Propose improvements via email

## 📝 License

Project developed for internal use of Fortitudo 1901 Rugby ASD.

---

**FortiDesk** - *Simplifying management, improving youth rugby* 🏉
