"""
Migration: Add RACI and PERT configuration fields
Run this script to add:
- raci_weights, pert_weights, and max_story_points_per_person to projects table
"""
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

app = create_app()

def upgrade():
    """Add RACI and PERT configuration fields"""
    with app.app_context():
        inspector = db.inspect(db.engine)
        
        # Check projects table columns
        project_columns = [col['name'] for col in inspector.get_columns('projects')]
        
        with db.engine.connect() as conn:
            # Add RACI weights field
            if 'raci_weights' not in project_columns:
                conn.execute(db.text(
                    'ALTER TABLE projects ADD COLUMN raci_weights JSON NULL'
                ))
                print("✓ Added raci_weights column to projects table")
            else:
                print("✓ raci_weights column already exists")
            
            # Add PERT weights field
            if 'pert_weights' not in project_columns:
                conn.execute(db.text(
                    'ALTER TABLE projects ADD COLUMN pert_weights JSON NULL'
                ))
                print("✓ Added pert_weights column to projects table")
            else:
                print("✓ pert_weights column already exists")
            
            # Add max story points per person field
            if 'max_story_points_per_person' not in project_columns:
                conn.execute(db.text(
                    'ALTER TABLE projects ADD COLUMN max_story_points_per_person INTEGER NOT NULL DEFAULT 20'
                ))
                print("✓ Added max_story_points_per_person column to projects table")
            else:
                print("✓ max_story_points_per_person column already exists")
            
            conn.commit()

def downgrade():
    """Remove RACI and PERT configuration fields"""
    with app.app_context():
        inspector = db.inspect(db.engine)
        
        # Check projects table columns
        project_columns = [col['name'] for col in inspector.get_columns('projects')]
        
        with db.engine.connect() as conn:
            # Remove RACI weights field
            if 'raci_weights' in project_columns:
                conn.execute(db.text(
                    'ALTER TABLE projects DROP COLUMN raci_weights'
                ))
                print("✓ Removed raci_weights column from projects table")
            
            # Remove PERT weights field
            if 'pert_weights' in project_columns:
                conn.execute(db.text(
                    'ALTER TABLE projects DROP COLUMN pert_weights'
                ))
                print("✓ Removed pert_weights column from projects table")
            
            # Remove max story points per person field
            if 'max_story_points_per_person' in project_columns:
                conn.execute(db.text(
                    'ALTER TABLE projects DROP COLUMN max_story_points_per_person'
                ))
                print("✓ Removed max_story_points_per_person column from projects table")
            
            conn.commit()

if __name__ == '__main__':
    print("Running migration: add_raci_pert_configuration")
    upgrade()
    print("Migration complete!")

