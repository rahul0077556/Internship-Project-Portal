"""
Database Initialization Script for PostgreSQL
This script creates all necessary tables in the PostgreSQL database.
Run this script once to set up your database schema.

Usage:
    python init_postgres_db.py
    
Make sure to set up your .env file with database credentials first!
See DATABASE_SETUP.md for instructions.
"""

from dotenv import load_dotenv
load_dotenv()

from app import app, db
from models import (
    User,
    StudentProfile,
    StudentEducation,
    StudentExperience,
    StudentInternship,
    StudentProject,
    StudentTraining,
    StudentCertification,
    StudentPublication,
    StudentPosition,
    StudentAttachment,
    StudentOffer,
    CompanyProfile,
    Opportunity,
    Application,
    Message,
    Notification,
    Blacklist,
)

def init_database():
    """Initialize the database by creating all tables."""
    print("=" * 60)
    print("PostgreSQL Database Initialization")
    print("=" * 60)
    
    try:
        with app.app_context():
            # Test database connection
            print("\n[1/3] Testing database connection...")
            db.engine.connect()
            print("✓ Database connection successful!")
            
            # Create all tables
            print("\n[2/3] Creating database tables...")
            db.create_all()
            print("✓ All tables created successfully!")
            
            # List created tables
            print("\n[3/3] Verifying table creation...")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\n✓ Created {len(tables)} tables:")
            for i, table in enumerate(sorted(tables), 1):
                print(f"  {i}. {table}")
            
            print("\n" + "=" * 60)
            print("Database initialization completed successfully!")
            print("=" * 60)
            print("\nYou can now start the Flask application with:")
            print("  python app.py")
            print("\n")
            
    except Exception as e:
        print(f"\n✗ Error during database initialization:")
        print(f"  {str(e)}")
        print("\nPlease check:")
        print("  1. PostgreSQL server is running")
        print("  2. Database 'MyPortalDb' exists")
        print("  3. Username and password are correct")
        print("  4. Connection settings in app.py are correct")
        print("\n")
        raise

if __name__ == '__main__':
    init_database()

