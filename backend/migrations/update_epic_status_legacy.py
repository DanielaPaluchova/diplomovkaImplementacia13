"""
Update legacy epic status values from 'not_started' to 'to_do'
"""
from app import create_app, db
from sqlalchemy import text, inspect


def upgrade():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        if 'epics' not in inspector.get_table_names():
            print("❌ Epics table doesn't exist.")
            return
        
        print("✓ Epics table exists")
        
        try:
            # Update any epics with 'not_started' status to 'to_do'
            result = db.session.execute(
                text("UPDATE epics SET status = 'to_do' WHERE status = 'not_started'")
            )
            db.session.commit()
            print(f"✓ Updated {result.rowcount} epic(s) from 'not_started' to 'to_do'")
            
            if result.rowcount == 0:
                print("ℹ All epics already have correct status")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating epic statuses: {e}")
            raise


if __name__ == '__main__':
    print("Running Epic Status Update Migration...")
    upgrade()
    print("✓ Migration complete!")
