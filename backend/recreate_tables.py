"""
Recreate database tables with updated schema
"""
from app import create_app, db

def recreate_tables():
    """Drop and recreate all database tables"""
    app = create_app()
    
    with app.app_context():
        print("⚠️  Dropping all existing tables...")
        db.drop_all()
        print("✅ Tables dropped")
        
        print("\n📋 Creating tables with updated schema...")
        db.create_all()
        print("✅ Tables created successfully!")
        
        print("\n✨ Database schema updated!")
        print("\nNext step: Run 'python seed_database.py' to populate with data")

if __name__ == '__main__':
    print("\n🔄 Database Schema Update\n")
    print("This will DELETE all existing data and recreate tables.")
    
    confirm = input("Are you sure you want to continue? (yes/no): ")
    
    if confirm.lower() == 'yes':
        recreate_tables()
    else:
        print("\n❌ Operation cancelled")

