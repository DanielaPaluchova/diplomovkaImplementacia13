"""
Migration: Add actual_hours column to tasks table if it doesn't exist.
The column stores how long a task actually took (time tracking).

Run: python backend/migrations/add_actual_hours_if_missing.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from sqlalchemy import text


def upgrade():
    """Add actual_hours column if missing"""
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('tasks')]

            if 'actual_hours' not in columns:
                print("Adding actual_hours column...")
                db.session.execute(text("""
                    ALTER TABLE tasks
                    ADD COLUMN actual_hours INTEGER NOT NULL DEFAULT 0
                """))
                db.session.commit()
                print("✓ Added actual_hours column")
            else:
                print("✓ actual_hours column already exists")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {str(e)}")
            raise


if __name__ == '__main__':
    print("=" * 50)
    print("ADD ACTUAL_HOURS COLUMN (if missing)")
    print("=" * 50)
    upgrade()
    print("\nDone.")
