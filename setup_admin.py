"""
Script to create an admin user for the internship portal.
Run this after setting up the database.
"""
from app import app, db
from models import User

def create_admin():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        email = input("Enter admin email: ").strip().lower()
        password = input("Enter admin password: ").strip()
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists.")
            make_admin = input("Make this user an admin? (y/n): ").strip().lower()
            if make_admin == 'y':
                existing_user.role = 'admin'
                existing_user.is_approved = True
                existing_user.is_active = True
                db.session.commit()
                print(f"User {email} is now an admin.")
            return
        
        # Create new admin user
        admin = User(email=email, role='admin')
        admin.set_password(password)
        admin.is_approved = True
        admin.is_active = True
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Admin user {email} created successfully!")

if __name__ == '__main__':
    create_admin()

