"""
Database migration script to add missing columns to existing tables.
This script safely adds new columns without dropping existing data.
"""
from app import app, db
from sqlalchemy import text, inspect

def migrate_database():
    """Add missing columns to existing tables."""
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Check and add missing columns to student_profiles table
        if 'student_profiles' in inspector.get_table_names():
            existing_columns = [col['name'] for col in inspector.get_columns('student_profiles')]
            
            # Columns that should exist in StudentProfile model
            required_columns = {
                'middle_name': 'VARCHAR(100)',
                'prn_number': 'VARCHAR(50)',
                'course': 'VARCHAR(150)',
                'specialization': 'VARCHAR(150)',
                'gender': 'VARCHAR(20)'
            }
            
            print("Checking student_profiles table...")
            for column_name, column_type in required_columns.items():
                if column_name not in existing_columns:
                    try:
                        print(f"  Adding column: {column_name} ({column_type})")
                        db.session.execute(text(f"ALTER TABLE student_profiles ADD COLUMN {column_name} {column_type}"))
                        db.session.commit()
                        print(f"  ✓ Added {column_name}")
                    except Exception as e:
                        print(f"  ✗ Error adding {column_name}: {e}")
                        db.session.rollback()
                else:
                    print(f"  ✓ Column {column_name} already exists")
        
        # Check if all new student profile tables exist
        new_tables = [
            'student_education',
            'student_experiences',
            'student_internships',
            'student_projects',
            'student_trainings',
            'student_certifications',
            'student_publications',
            'student_positions',
            'student_attachments',
            'student_offers'
        ]
        
        print("\nChecking for new tables...")
        existing_tables = inspector.get_table_names()
        for table_name in new_tables:
            if table_name not in existing_tables:
                print(f"  Creating table: {table_name}")
                try:
                    db.create_all()  # This will create missing tables
                    print(f"  ✓ Created {table_name}")
                except Exception as e:
                    print(f"  ✗ Error creating {table_name}: {e}")
            else:
                print(f"  ✓ Table {table_name} already exists")
        
        print("\n✓ Migration complete!")

if __name__ == '__main__':
    migrate_database()

