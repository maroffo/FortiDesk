import os
import time
from app import create_app, db
from app.models import (User, Athlete, Guardian, Staff, Team, TeamStaffAssignment,
                        Attendance, Equipment, EquipmentAssignment,
                        Season, TrainingSession, Match, MatchLineup,
                        Document, EmergencyContact)

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Athlete': Athlete,
        'Guardian': Guardian,
        'Staff': Staff,
        'Team': Team,
        'TeamStaffAssignment': TeamStaffAssignment,
        'Attendance': Attendance,
        'Equipment': Equipment,
        'EquipmentAssignment': EquipmentAssignment,
        'Season': Season,
        'TrainingSession': TrainingSession,
        'Match': Match,
        'MatchLineup': MatchLineup,
        'Document': Document,
        'EmergencyContact': EmergencyContact
    }

def init_db():
    """Initialize database with retries for Docker environment"""
    max_retries = 10
    retry_count = 0

    while retry_count < max_retries:
        try:
            with app.app_context():
                db.create_all()
                app.logger.info('Database tables created successfully')

                # Add columns that create_all() won't add to existing tables
                _apply_schema_updates()

                # Create default users if they don't exist
                admin_user = User.query.filter_by(username='admin').first()
                if not admin_user:
                    admin_user = User(
                        username='admin',
                        email='admin@fortitudo1901.it',
                        first_name='Admin',
                        last_name='FortiDesk',
                        role='admin',
                        is_active=True
                    )
                    admin_user.set_password('admin123')
                    db.session.add(admin_user)
                    app.logger.info('Created default admin user')

                coach_user = User.query.filter_by(username='coach').first()
                if not coach_user:
                    coach_user = User(
                        username='coach',
                        email='coach@fortitudo1901.it',
                        first_name='Coach',
                        last_name='Example',
                        role='coach',
                        is_active=True
                    )
                    coach_user.set_password('coach123')
                    db.session.add(coach_user)
                    app.logger.info('Created default coach user')

                db.session.commit()
                app.logger.info('Database initialized successfully')
                break
        except Exception as e:
            retry_count += 1
            app.logger.warning(f'Database connection failed (attempt {retry_count}/{max_retries}): {e}')
            if retry_count < max_retries:
                time.sleep(5)
            else:
                app.logger.error('Failed to connect to database after maximum retries')
                raise

def _apply_schema_updates():
    """Add columns to existing tables that db.create_all() won't modify.

    create_all() only creates new tables; it does not ALTER existing ones.
    This function checks for missing columns and adds them manually.
    """
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)

    # athletes.team_id
    if 'athletes' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('athletes')]
        if 'team_id' not in columns:
            db.session.execute(text(
                'ALTER TABLE athletes ADD COLUMN team_id INTEGER NULL, '
                'ADD INDEX idx_athletes_team_id (team_id), '
                'ADD CONSTRAINT fk_athletes_team_id FOREIGN KEY (team_id) REFERENCES teams(id)'
            ))
            db.session.commit()
            app.logger.info('Added team_id column to athletes table')

    # teams.season_id
    if 'teams' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('teams')]
        if 'season_id' not in columns:
            db.session.execute(text(
                'ALTER TABLE teams ADD COLUMN season_id INTEGER NULL'
            ))
            db.session.commit()
            app.logger.info('Added season_id column to teams table')

    # attendance.training_session_id
    if 'attendance' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('attendance')]
        if 'training_session_id' not in columns:
            db.session.execute(text(
                'ALTER TABLE attendance ADD COLUMN training_session_id INTEGER NULL'
            ))
            db.session.commit()
            app.logger.info('Added training_session_id column to attendance table')

    # athletes medical fields (allergies, medical_conditions, blood_type, special_notes)
    if 'athletes' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('athletes')]
        medical_columns = {
            'allergies': 'TEXT',
            'medical_conditions': 'TEXT',
            'blood_type': 'VARCHAR(5)',
            'special_notes': 'TEXT',
        }
        for col_name, col_type in medical_columns.items():
            if col_name not in columns:
                db.session.execute(text(
                    f'ALTER TABLE athletes ADD COLUMN {col_name} {col_type} NULL'
                ))
                db.session.commit()
                app.logger.info(f'Added {col_name} column to athletes table')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')
