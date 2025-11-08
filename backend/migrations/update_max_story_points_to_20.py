"""
Migration: Update max_story_points from 40 to 20 for all team members
"""
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def upgrade():
    """Update max_story_points to 20 for all team members"""
    app = create_app()
    with app.app_context():
        # Check if column exists
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('team_members')]
        
        if 'max_story_points' in columns:
            # Update all existing records to have max_story_points = 20
            with db.engine.connect() as conn:
                result = conn.execute(db.text(
                    'UPDATE team_members SET max_story_points = 20 WHERE max_story_points = 40'
                ))
                conn.commit()
                print(f"✓ Updated {result.rowcount} team members to have max_story_points = 20")
        else:
            print("✗ max_story_points column does not exist. Run add_max_story_points migration first.")

def downgrade():
    """Revert max_story_points back to 40 for all team members"""
    app = create_app()
    with app.app_context():
        # Check if column exists
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('team_members')]
        
        if 'max_story_points' in columns:
            # Update all existing records to have max_story_points = 40
            with db.engine.connect() as conn:
                result = conn.execute(db.text(
                    'UPDATE team_members SET max_story_points = 40 WHERE max_story_points = 20'
                ))
                conn.commit()
                print(f"✓ Reverted {result.rowcount} team members to have max_story_points = 40")
        else:
            print("✗ max_story_points column does not exist")

if __name__ == '__main__':
    print("Running migration: update_max_story_points_to_20")
    upgrade()
    print("Migration complete!")

