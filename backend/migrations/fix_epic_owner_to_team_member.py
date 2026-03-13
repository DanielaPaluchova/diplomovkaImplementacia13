"""
Migration: Fix Epic owner_id to reference team_members instead of users
"""
from app import create_app, db
from sqlalchemy import text, inspect

app = create_app()


def upgrade():
    """Change epic owner_id foreign key from users to team_members"""
    with app.app_context():
        inspector = inspect(db.engine)
        
        print("\n=== Fixing Epic owner_id to reference team_members ===")
        
        # Check if owner_id column exists
        epic_columns = [col['name'] for col in inspector.get_columns('epics')]
        
        if 'owner_id' in epic_columns:
            try:
                # Drop existing foreign key constraint if it exists (PostgreSQL)
                # The constraint name might vary, so we'll try common names
                constraint_names = ['epics_owner_id_fkey', 'fk_epics_owner_id']
                
                for constraint_name in constraint_names:
                    try:
                        db.session.execute(text(f"ALTER TABLE epics DROP CONSTRAINT IF EXISTS {constraint_name}"))
                        print(f"✓ Dropped constraint: {constraint_name}")
                    except Exception as e:
                        print(f"  (Constraint {constraint_name} not found or already dropped)")
                
                # Now add the correct foreign key to team_members
                db.session.execute(text(
                    "ALTER TABLE epics ADD CONSTRAINT epics_owner_id_fkey "
                    "FOREIGN KEY (owner_id) REFERENCES team_members(id) ON DELETE SET NULL"
                ))
                print("✓ Added foreign key constraint to team_members")
                
                db.session.commit()
                print("✅ Migration completed successfully!")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error during migration: {e}")
                print("You may need to manually fix the foreign key constraint.")
        else:
            print("⚠ owner_id column does not exist in epics table")


def downgrade():
    """Revert epic owner_id foreign key back to users"""
    with app.app_context():
        try:
            # Drop the team_members foreign key
            db.session.execute(text("ALTER TABLE epics DROP CONSTRAINT IF EXISTS epics_owner_id_fkey"))
            
            # Add back the users foreign key
            db.session.execute(text(
                "ALTER TABLE epics ADD CONSTRAINT epics_owner_id_fkey "
                "FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL"
            ))
            
            db.session.commit()
            print("✅ Migration reverted successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during migration revert: {e}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        downgrade()
    else:
        upgrade()
