import os
import time
from app import create_app, db
from app.models import (User, Athlete, Guardian, Staff, Team, TeamStaffAssignment,
                        Attendance, Equipment, EquipmentAssignment)

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
        'EquipmentAssignment': EquipmentAssignment
    }

def init_db():
    """Initialize database with retries for Docker environment"""
    max_retries = 10
    retry_count = 0

    while retry_count < max_retries:
        try:
            with app.app_context():
                db.create_all()
                print("Database tables created successfully!")

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
                    print("Created default admin user")

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
                    print("Created default coach user")

                db.session.commit()
                print("Database initialized successfully!")
                break
        except Exception as e:
            retry_count += 1
            print(f"Database connection failed (attempt {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                time.sleep(5)
            else:
                print("Failed to connect to database after maximum retries")
                raise

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')
