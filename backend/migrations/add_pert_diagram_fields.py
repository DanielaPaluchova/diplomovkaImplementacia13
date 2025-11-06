"""
Migration: Add PERT diagram fields
Run this script to add:
- diagram_position_x and diagram_position_y to tasks table
- pert_manual_edges and pert_layout_settings to projects table
"""
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

app = create_app()

def upgrade():
    """Add PERT diagram fields"""
    with app.app_context():
        inspector = db.inspect(db.engine)
        
        # Check tasks table columns
        task_columns = [col['name'] for col in inspector.get_columns('tasks')]
        
        with db.engine.connect() as conn:
            # Add diagram position fields to tasks table
            if 'diagram_position_x' not in task_columns:
                conn.execute(db.text(
                    'ALTER TABLE tasks ADD COLUMN diagram_position_x FLOAT NULL'
                ))
                print("✓ Added diagram_position_x column to tasks table")
            else:
                print("✓ diagram_position_x column already exists")
            
            if 'diagram_position_y' not in task_columns:
                conn.execute(db.text(
                    'ALTER TABLE tasks ADD COLUMN diagram_position_y FLOAT NULL'
                ))
                print("✓ Added diagram_position_y column to tasks table")
            else:
                print("✓ diagram_position_y column already exists")
            
            # Check projects table columns
            project_columns = [col['name'] for col in inspector.get_columns('projects')]
            
            # Add PERT settings fields to projects table
            if 'pert_manual_edges' not in project_columns:
                conn.execute(db.text(
                    'ALTER TABLE projects ADD COLUMN pert_manual_edges JSON NULL'
                ))
                print("✓ Added pert_manual_edges column to projects table")
            else:
                print("✓ pert_manual_edges column already exists")
            
            if 'pert_layout_settings' not in project_columns:
                conn.execute(db.text(
                    'ALTER TABLE projects ADD COLUMN pert_layout_settings JSON NULL'
                ))
                print("✓ Added pert_layout_settings column to projects table")
            else:
                print("✓ pert_layout_settings column already exists")
            
            conn.commit()

def downgrade():
    """Remove PERT diagram fields"""
    with app.app_context():
        inspector = db.inspect(db.engine)
        
        # Check tasks table columns
        task_columns = [col['name'] for col in inspector.get_columns('tasks')]
        
        with db.engine.connect() as conn:
            # Remove diagram position fields from tasks table
            if 'diagram_position_x' in task_columns:
                conn.execute(db.text(
                    'ALTER TABLE tasks DROP COLUMN diagram_position_x'
                ))
                print("✓ Removed diagram_position_x column from tasks table")
            
            if 'diagram_position_y' in task_columns:
                conn.execute(db.text(
                    'ALTER TABLE tasks DROP COLUMN diagram_position_y'
                ))
                print("✓ Removed diagram_position_y column from tasks table")
            
            # Check projects table columns
            project_columns = [col['name'] for col in inspector.get_columns('projects')]
            
            # Remove PERT settings fields from projects table
            if 'pert_manual_edges' in project_columns:
                conn.execute(db.text(
                    'ALTER TABLE projects DROP COLUMN pert_manual_edges'
                ))
                print("✓ Removed pert_manual_edges column from projects table")
            
            if 'pert_layout_settings' in project_columns:
                conn.execute(db.text(
                    'ALTER TABLE projects DROP COLUMN pert_layout_settings'
                ))
                print("✓ Removed pert_layout_settings column from projects table")
            
            conn.commit()

if __name__ == '__main__':
    print("Running migration: add_pert_diagram_fields")
    upgrade()
    print("Migration complete!")

