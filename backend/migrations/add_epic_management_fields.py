"""
Migration: Add Epic Management Fields
Adds: owner_id, priority, labels, start_date, target_date
"""
from app import create_app, db
from sqlalchemy import text, inspect


def upgrade():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Check if epics table exists
        if 'epics' not in inspector.get_table_names():
            print("❌ Epics table doesn't exist. Run add_epic_functionality.py first.")
            return
        
        print("✓ Epics table exists")
        
        columns = [col['name'] for col in inspector.get_columns('epics')]
        
        try:
            # Add owner_id column
            if 'owner_id' not in columns:
                db.session.execute(text(
                    "ALTER TABLE epics ADD COLUMN owner_id INTEGER REFERENCES users(id) ON DELETE SET NULL"
                ))
                print("✓ Added owner_id column")
            else:
                print("  owner_id already exists")
            
            # Add priority column
            if 'priority' not in columns:
                db.session.execute(text(
                    "ALTER TABLE epics ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'medium'"
                ))
                print("✓ Added priority column")
            else:
                print("  priority already exists")
            
            # Add labels column (JSON)
            if 'labels' not in columns:
                db.session.execute(text(
                    "ALTER TABLE epics ADD COLUMN labels JSON"
                ))
                print("✓ Added labels column")
            else:
                print("  labels already exists")
            
            # Add start_date column
            if 'start_date' not in columns:
                db.session.execute(text(
                    "ALTER TABLE epics ADD COLUMN start_date DATE"
                ))
                print("✓ Added start_date column")
            else:
                print("  start_date already exists")
            
            # Add target_date column
            if 'target_date' not in columns:
                db.session.execute(text(
                    "ALTER TABLE epics ADD COLUMN target_date DATE"
                ))
                print("✓ Added target_date column")
            else:
                print("  target_date already exists")
            
            db.session.commit()
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during migration: {e}")
            raise


def downgrade():
    app = create_app()
    with app.app_context():
        try:
            db.session.execute(text("ALTER TABLE epics DROP COLUMN IF EXISTS owner_id"))
            db.session.execute(text("ALTER TABLE epics DROP COLUMN IF EXISTS priority"))
            db.session.execute(text("ALTER TABLE epics DROP COLUMN IF EXISTS labels"))
            db.session.execute(text("ALTER TABLE epics DROP COLUMN IF EXISTS start_date"))
            db.session.execute(text("ALTER TABLE epics DROP COLUMN IF EXISTS target_date"))
            db.session.commit()
            print("✓ Reverted epic management fields migration")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error reverting migration: {e}")
            raise


if __name__ == '__main__':
    print("Running Epic Management Fields Migration...")
    print("Adding: owner_id, priority, labels, start_date, target_date")
    upgrade()
    print("✓ Migration complete!")
