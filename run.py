import os
import time
from app import create_app, db
from app.models import User, Athlete, Guardian, Staff

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Athlete': Athlete, 'Guardian': Guardian, 'Staff': Staff}

def init_db():
    """Initialize database with retries for Docker environment"""
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            with app.app_context():
                db.create_all()
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