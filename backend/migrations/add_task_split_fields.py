"""
Migration: Add task split/merge fields to tasks table
- parent_task_id: Foreign key to parent task (for subtasks)
- has_subtasks: Boolean flag indicating if task was split
- subtask_ids: JSON array of subtask IDs

Run this migration with: python backend/migrations/add_task_split_fields.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from sqlalchemy import text

def upgrade():
    """Add task split/merge fields"""
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('tasks')]
            
            # Add parent_task_id column
            if 'parent_task_id' not in columns:
                print("Adding parent_task_id column...")
                db.session.execute(text("""
                    ALTER TABLE tasks 
                    ADD COLUMN parent_task_id INTEGER NULL
                """))
                
                # Add foreign key constraint
                db.session.execute(text("""
                    ALTER TABLE tasks 
                    ADD CONSTRAINT fk_parent_task 
                    FOREIGN KEY (parent_task_id) REFERENCES tasks(id)
                """))
                print("✓ Added parent_task_id column")
            else:
                print("✓ parent_task_id column already exists")
            
            # Add has_subtasks column
            if 'has_subtasks' not in columns:
                print("Adding has_subtasks column...")
                db.session.execute(text("""
                    ALTER TABLE tasks 
                    ADD COLUMN has_subtasks BOOLEAN NOT NULL DEFAULT FALSE
                """))
                print("✓ Added has_subtasks column")
            else:
                print("✓ has_subtasks column already exists")
            
            # Add subtask_ids column
            if 'subtask_ids' not in columns:
                print("Adding subtask_ids column...")
                db.session.execute(text("""
                    ALTER TABLE tasks 
                    ADD COLUMN subtask_ids JSON NULL
                """))
                print("✓ Added subtask_ids column")
            else:
                print("✓ subtask_ids column already exists")
            
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            raise

def downgrade():
    """Remove task split/merge fields"""
    with app.app_context():
        try:
            print("Removing task split/merge fields...")
            
            # Drop columns
            db.session.execute(text("""
                ALTER TABLE tasks 
                DROP COLUMN IF EXISTS parent_task_id,
                DROP COLUMN IF EXISTS has_subtasks,
                DROP COLUMN IF EXISTS subtask_ids
            """))
            
            db.session.commit()
            print("✅ Downgrade completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Downgrade failed: {str(e)}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("TASK SPLIT FIELDS MIGRATION")
    print("=" * 60)
    print("\nThis will add the following columns to the 'tasks' table:")
    print("  - parent_task_id (INTEGER, nullable)")
    print("  - has_subtasks (BOOLEAN, default FALSE)")
    print("  - subtask_ids (JSON, nullable)")
    print()
    
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    
    if response == 'yes':
        upgrade()
    else:
        print("Migration cancelled.")

