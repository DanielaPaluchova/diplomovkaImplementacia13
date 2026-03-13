"""
Migration: Add Epic functionality
- Create 'epics' table for strategic planning
- Add 'epic_id' column to 'tasks' table (nullable, foreign key to epics.id)

Run this migration with: python backend/migrations/add_epic_functionality.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from sqlalchemy import text

# Create app instance
app = create_app()

def upgrade():
    """Add Epic functionality"""
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            # Create epics table
            if 'epics' not in existing_tables:
                print("Creating epics table...")
                db.session.execute(text("""
                    CREATE TABLE epics (
                        id SERIAL PRIMARY KEY,
                        project_id INTEGER NOT NULL,
                        name VARCHAR(200) NOT NULL,
                        description TEXT,
                        status VARCHAR(50) NOT NULL DEFAULT 'not_started',
                        pert_optimistic FLOAT,
                        pert_most_likely FLOAT,
                        pert_pessimistic FLOAT,
                        pert_expected FLOAT,
                        dependencies JSON,
                        business_value INTEGER NOT NULL DEFAULT 0,
                        target_release VARCHAR(100),
                        diagram_position_x FLOAT,
                        diagram_position_y FLOAT,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                    )
                """))
                print("✓ Created epics table")
            else:
                print("✓ epics table already exists")
            
            # Add epic_id column to tasks table
            columns = [col['name'] for col in inspector.get_columns('tasks')]
            
            if 'epic_id' not in columns:
                print("Adding epic_id column to tasks table...")
                db.session.execute(text("""
                    ALTER TABLE tasks 
                    ADD COLUMN epic_id INTEGER NULL
                """))
                
                # Add foreign key constraint with ON DELETE SET NULL
                db.session.execute(text("""
                    ALTER TABLE tasks 
                    ADD CONSTRAINT fk_task_epic 
                    FOREIGN KEY (epic_id) REFERENCES epics(id) ON DELETE SET NULL
                """))
                print("✓ Added epic_id column to tasks table")
            else:
                print("✓ epic_id column already exists in tasks table")
            
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            print("\nWhat was done:")
            print("  ✓ Created 'epics' table for strategic planning")
            print("  ✓ Added 'epic_id' column to 'tasks' table (nullable)")
            print("  ✓ Tasks can now optionally belong to an epic")
            print("  ✓ All existing tasks remain independent (epic_id = NULL)")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            raise

def downgrade():
    """Remove Epic functionality"""
    with app.app_context():
        try:
            print("Removing Epic functionality...")
            
            # Drop epic_id column from tasks
            db.session.execute(text("""
                ALTER TABLE tasks 
                DROP COLUMN IF EXISTS epic_id
            """))
            print("✓ Removed epic_id column from tasks")
            
            # Drop epics table
            db.session.execute(text("""
                DROP TABLE IF EXISTS epics CASCADE
            """))
            print("✓ Removed epics table")
            
            db.session.commit()
            print("\n✅ Downgrade completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Downgrade failed: {str(e)}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("EPIC FUNCTIONALITY MIGRATION")
    print("=" * 60)
    print("\nThis migration will:")
    print("  1. Create 'epics' table for strategic planning")
    print("  2. Add 'epic_id' column to 'tasks' table (nullable)")
    print("\nEpic fields:")
    print("  - id, project_id, name, description")
    print("  - status (not_started, in_progress, completed)")
    print("  - PERT estimates (optimistic, most_likely, pessimistic, expected)")
    print("  - dependencies (JSON array of epic IDs)")
    print("  - business_value, target_release")
    print("  - diagram_position_x, diagram_position_y")
    print("  - created_at, updated_at")
    print("\nTask changes:")
    print("  - New field: epic_id (nullable, foreign key to epics.id)")
    print("  - ON DELETE SET NULL (if epic is deleted, tasks remain)")
    print("  - All existing tasks will have epic_id = NULL")
    print()
    
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    
    if response == 'yes':
        upgrade()
    else:
        print("Migration cancelled.")
