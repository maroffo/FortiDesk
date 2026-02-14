#!/usr/bin/env python3
from run import app, db

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables created successfully!")

    # Show all tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\nTables in database: {tables}")
