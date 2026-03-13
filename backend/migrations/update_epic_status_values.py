"""
Migration to update epic status values from 'not_started' to 'to_do'
"""
from app import create_app, db
from sqlalchemy import text, inspect

def upgrade():
    """Update epic status from 'not_started' to 'to_do'"""
    app = create_app()
    
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Check if epics table exists
        if 'epics' not in inspector.get_table_names():
            print("❌ Epics table doesn't exist. Run add_epic_functionality.py first.")
            return
        
        print("✓ Epics table exists")
        
        # Update status values
        try:
            result = db.session.execute(
                text("UPDATE epics SET status = 'to_do' WHERE status = 'not_started'")
            )
            db.session.commit()
            print(f"✓ Updated {result.rowcount} epic(s) from 'not_started' to 'to_do'")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating epic statuses: {e}")
            raise

def downgrade():
    """Revert epic status from 'to_do' back to 'not_started'"""
    app = create_app()
    
    with app.app_context():
        try:
            result = db.session.execute(
                text("UPDATE epics SET status = 'not_started' WHERE status = 'to_do'")
            )
            db.session.commit()
            print(f"✓ Reverted {result.rowcount} epic(s) from 'to_do' to 'not_started'")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error reverting epic statuses: {e}")
            raise

if __name__ == '__main__':
    print("Running epic status migration...")
    print("Updating 'not_started' → 'to_do'")
    upgrade()
    print("✓ Migration complete!")
