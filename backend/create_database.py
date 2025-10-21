"""
Create PostgreSQL database
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database connection details
DB_USER = 'postgres'
DB_PASSWORD = 'daniela13'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'diplonovka_db'

def create_database():
    """Create database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (to postgres default database)
        print(f"Connecting to PostgreSQL server as user '{DB_USER}'...")
        conn = psycopg2.connect(
            dbname='postgres',
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if exists:
            print(f"✓ Database '{DB_NAME}' already exists")
        else:
            # Create database
            print(f"Creating database '{DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"✅ Database '{DB_NAME}' created successfully!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection error: {e}")
        print("\nPlease check:")
        print("1. PostgreSQL server is running")
        print("2. Username and password are correct")
        print(f"3. User '{DB_USER}' has permission to create databases")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == '__main__':
    print("\n🗄️ Database Setup\n")
    if create_database():
        print("\n✅ Database setup completed successfully!")
        print(f"\nYou can now run: python seed_database.py")
    else:
        print("\n❌ Database setup failed!")
        print("\nTroubleshooting:")
        print("- Make sure PostgreSQL is installed and running")
        print("- Check if pgAdmin shows the PostgreSQL server as running")
        print("- Verify your credentials in the script")

