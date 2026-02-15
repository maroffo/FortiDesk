# FortiDesk

Team management system per Fortitudo 1901 Rugby ASD (settore giovanile). Atleti, staff, squadre, presenze, attrezzature, documenti, comunicazioni, compliance.

## Stack

Flask 3.0, SQLAlchemy, Flask-Login, Flask-WTF, Flask-Babel (EN/IT), Flask-Mail, Bootstrap 5, HTMX, MySQL 8.0 (prod), SQLite in-memory (test), Docker + Nginx + Gunicorn

## Commands

```bash
# Test (169 tests, SQLite in-memory)
.venv/bin/python -m pytest tests/ -v

# Lint + type check
uvx ruff check
uvx --from pyright pyright app/

# Translations (after changing user-visible strings)
uvx --with jinja2 --from babel pybabel extract -F babel.cfg -k _l -k _ -o messages.pot .
uvx --with jinja2 --from babel pybabel update -i messages.pot -d translations
# edit translations/it/LC_MESSAGES/messages.po
uvx --with jinja2 --from babel pybabel compile -d translations

# Docker
docker-compose up -d
# Default users: admin/admin123, coach/coach123
```

## Architecture

- `app/models/`: SQLAlchemy models (17 tables). Each has `is_active`, `created_at`, `created_by`.
- `app/views/` : Flask blueprints (15). Each route has `@login_required` + RBAC check.
- `app/forms/` : WTForms. Labels use `_l()`, flash messages use `_()`.
- `app/templates/` : Jinja2, extends `base.html`. Bootstrap 5. All text wrapped in `_()`.
- `app/utils/` : `email.py` (async via thread), `export.py` (CSV/PDF), `uploads.py`
- `tests/` : pytest + pytest-flask. `conftest.py` has 12 fixtures. Per-test DB isolation.
- `config.py` : `DevelopmentConfig`, `ProductionConfig`, `TestingConfig`

## Conventions

- **RBAC**: admin can CRUD + delete. coach can CRUD (no delete). Views check `current_user.is_admin() or current_user.is_coach()`.
- **Soft delete**: `is_active = False`, never hard delete. Query with `filter_by(is_active=True)`.
- **Audit**: all models have `created_at`, `updated_at`, `created_by` (FK to users).
- **i18n**: every user-visible string wrapped in `_()` (runtime) or `_l()` (form labels). Two languages: en, it.
- **Forms**: WTForms for all input. CSRF via Flask-WTF. Custom `validate_<field>()` for business rules.
- **Pagination**: 20 per page via `query.paginate()`.
- **2-line ABOUTME header**: every file starts with `# ABOUTME:` comments.
- **Email**: async via `threading.Thread` + app context copy (no Celery).
- **Blueprints**: new feature = new blueprint in `views/`, register in `app/__init__.py`, add nav in `base.html`.

## Gotchas

- `AthleteForm` requires 2 guardians of different types (father/mother/guardian)
- `StaffForm` has role-conditional fields (medical cert for coaches, background check for minors roles)
- `AttendanceReportForm.athlete_id` uses lambda coerce (not `int`) to handle empty string
- Document soft delete keeps file on disk (intentional, for restoration)
- No Flask-Migrate: tables created via `db.create_all()` in `run.py`

## Vault Context

Obsidian vault: `Projects/FortiDesk/`

- **FortiDesk - Overview**: stack, architecture, blueprints, decisions
- **FortiDesk - Log**: session log
- **FortiDesk - Solutions**: solved problems, reusable patterns
- **FortiDesk - Code Review Follow-ups**: backlog (8 INFO items from Gemini review)
- **Plans/2026-02-14 - FortiDesk Feature Roadmap**: 6-phase plan (complete)
