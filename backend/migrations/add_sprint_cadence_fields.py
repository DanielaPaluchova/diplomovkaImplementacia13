"""
Migration: Add Sprint Cadence Fields to Projects
Adds: sprint_duration_days, sprint_start_date, last_planned_sprint_start_date
"""
from app import create_app, db
from sqlalchemy import text, inspect


def upgrade():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)

        if 'projects' not in inspector.get_table_names():
            print("❌ Projects table doesn't exist.")
            return

        print("✓ Projects table exists")

        columns = [col['name'] for col in inspector.get_columns('projects')]

        try:
            if 'sprint_duration_days' not in columns:
                db.session.execute(text(
                    "ALTER TABLE projects ADD COLUMN sprint_duration_days INTEGER NOT NULL DEFAULT 14"
                ))
                print("✓ Added sprint_duration_days column")
            else:
                print("  sprint_duration_days already exists")

            if 'sprint_start_date' not in columns:
                db.session.execute(text(
                    "ALTER TABLE projects ADD COLUMN sprint_start_date DATETIME"
                ))
                print("✓ Added sprint_start_date column")
            else:
                print("  sprint_start_date already exists")

            if 'last_planned_sprint_start_date' not in columns:
                db.session.execute(text(
                    "ALTER TABLE projects ADD COLUMN last_planned_sprint_start_date DATETIME"
                ))
                print("✓ Added last_planned_sprint_start_date column")
            else:
                print("  last_planned_sprint_start_date already exists")

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
            db.session.execute(text("ALTER TABLE projects DROP COLUMN IF EXISTS sprint_duration_days"))
            db.session.execute(text("ALTER TABLE projects DROP COLUMN IF EXISTS sprint_start_date"))
            db.session.execute(text("ALTER TABLE projects DROP COLUMN IF EXISTS last_planned_sprint_start_date"))
            db.session.commit()
            print("✓ Reverted sprint cadence fields migration")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error reverting migration: {e}")
            raise


if __name__ == '__main__':
    print("Running Sprint Cadence Fields Migration...")
    upgrade()
    print("✓ Migration complete!")
