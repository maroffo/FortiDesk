# ABOUTME: Shared pytest fixtures for FortiDesk test suite
# ABOUTME: Provides app, client, db_session, and sample data fixtures

import pytest
from datetime import date

from app import create_app, db
from app.models import User, Staff, Team, Season, Athlete, Guardian


@pytest.fixture(scope='session')
def app():
    """Create the Flask application configured for testing.

    Session-scoped: the app instance is reused across all tests.
    Database tables are created/dropped per test via the ``_setup_db`` fixture.
    """
    application = create_app('testing')
    yield application


@pytest.fixture(autouse=True)
def _setup_db(app):
    """Create all tables before each test and drop them after.

    This gives each test a completely clean database, avoiding leftover
    data from previous tests without needing complex SAVEPOINT tricks.
    """
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """A Flask test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Expose the database session for the current app context.

    The ``_setup_db`` autouse fixture handles table lifecycle, so this
    just returns the session for convenience.
    """
    return db.session


# ---- User fixtures -----------------------------------------------------------

@pytest.fixture(scope='function')
def admin_user(app):
    """An active admin user persisted in the database."""
    user = User(
        username='testadmin',
        email='admin@test.com',
        first_name='Admin',
        last_name='Test',
        role='admin',
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def coach_user(app):
    """An active coach user persisted in the database."""
    user = User(
        username='testcoach',
        email='coach@test.com',
        first_name='Coach',
        last_name='Test',
        role='coach',
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user


# ---- Domain-object fixtures --------------------------------------------------

@pytest.fixture(scope='function')
def sample_staff(admin_user):
    """A coach staff member with all required fields populated."""
    staff = Staff(
        first_name='Mario',
        last_name='Rossi',
        birth_date=date(1985, 1, 15),
        birth_place='Bologna',
        fiscal_code='RSSMRA85A15A944X',
        phone='+393331234567',
        email='mario.rossi@test.com',
        street_address='Via Roma',
        street_number='10',
        postal_code='40100',
        city='Bologna',
        province='BO',
        document_number='AA1234567',
        issuing_authority='Comune di Bologna',
        document_expiry=date(2030, 12, 31),
        role='coach',
        created_by=admin_user.id,
    )
    db.session.add(staff)
    db.session.commit()
    return staff


@pytest.fixture(scope='function')
def sample_season(admin_user):
    """The current sporting season (2025-2026)."""
    season = Season(
        name='2025-2026',
        start_date=date(2025, 9, 1),
        end_date=date(2026, 6, 30),
        is_current=True,
        created_by=admin_user.id,
    )
    db.session.add(season)
    db.session.commit()
    return season


@pytest.fixture(scope='function')
def sample_team(admin_user, sample_staff, sample_season):
    """An Under-10 team linked to the sample season and staff coach."""
    team = Team(
        name='Under 10',
        age_group='U10',
        season='2025-2026',
        head_coach_id=sample_staff.id,
        season_id=sample_season.id,
        created_by=admin_user.id,
    )
    db.session.add(team)
    db.session.commit()
    return team


@pytest.fixture(scope='function')
def sample_athlete(admin_user, sample_team):
    """A youth athlete with two guardians, assigned to the sample team."""
    athlete = Athlete(
        first_name='Marco',
        last_name='Bianchi',
        birth_date=date(2015, 3, 20),
        birth_place='Bologna',
        fiscal_code='BNCMRC15C20A944Y',
        street_address='Via Garibaldi',
        street_number='5',
        postal_code='40100',
        city='Bologna',
        province='BO',
        document_number='BB9876543',
        issuing_authority='Comune di Bologna',
        document_expiry=date(2030, 6, 30),
        team_id=sample_team.id,
        created_by=admin_user.id,
    )
    db.session.add(athlete)
    db.session.commit()

    father = Guardian(
        first_name='Paolo',
        last_name='Bianchi',
        phone='+393331111111',
        email='paolo@test.com',
        guardian_type='father',
        athlete_id=athlete.id,
    )
    mother = Guardian(
        first_name='Laura',
        last_name='Bianchi',
        phone='+393332222222',
        email='laura@test.com',
        guardian_type='mother',
        athlete_id=athlete.id,
    )
    db.session.add_all([father, mother])
    db.session.commit()

    return athlete


# ---- Authenticated client fixtures -------------------------------------------

@pytest.fixture(scope='function')
def logged_in_admin(client, admin_user):
    """A test client with an active admin session cookie.

    Does NOT follow redirects so the login fixture itself never renders
    pages that might fail due to unrelated template issues.
    """
    response = client.post('/auth/login', data={
        'username_or_email': 'testadmin',
        'password': 'password123',
    })
    # Login should redirect (302); we just need the session cookie set
    assert response.status_code == 302, (
        f'Login failed with status {response.status_code}'
    )
    return client


@pytest.fixture(scope='function')
def logged_in_coach(client, coach_user):
    """A test client with an active coach session cookie."""
    response = client.post('/auth/login', data={
        'username_or_email': 'testcoach',
        'password': 'password123',
    })
    assert response.status_code == 302, (
        f'Login failed with status {response.status_code}'
    )
    return client
