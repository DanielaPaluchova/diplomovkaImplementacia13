"""
Migration: Add max_story_points column to team_members table
"""
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db

def upgrade():
    """Add max_story_points column to team_members table"""
    with app.app_context():
        # Check if column exists
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('team_members')]
        
        if 'max_story_points' not in columns:
            # Add the column using raw SQL
            with db.engine.connect() as conn:
                conn.execute(db.text(
                    'ALTER TABLE team_members ADD COLUMN max_story_points INTEGER NOT NULL DEFAULT 20'
                ))
                conn.commit()
            print("✓ Added max_story_points column to team_members table")
        else:
            print("✓ max_story_points column already exists")

def downgrade():
    """Remove max_story_points column from team_members table"""
    with app.app_context():
        # Check if column exists
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('team_members')]
        
        if 'max_story_points' in columns:
            # Remove the column using raw SQL
            with db.engine.connect() as conn:
                conn.execute(db.text(
                    'ALTER TABLE team_members DROP COLUMN max_story_points'
                ))
                conn.commit()
            print("✓ Removed max_story_points column from team_members table")
        else:
            print("✓ max_story_points column does not exist")

if __name__ == '__main__':
    print("Running migration: add_max_story_points")
    upgrade()
    print("Migration complete!")

