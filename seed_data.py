"""
Script to seed the database with dummy data for testing
Run this after setting up the database: python seed_data.py
"""
from app import app, db
from models import User, StudentProfile, CompanyProfile, Opportunity, Application, Notification
from datetime import datetime, timedelta
import json
import random

def create_dummy_data():
    with app.app_context():
        # Clear existing data (optional - comment out if you want to keep existing data)
        # db.drop_all()
        # db.create_all()

        print("Creating dummy data...")

        # Create Admin User
        admin = User.query.filter_by(email='admin@pict.edu').first()
        if not admin:
            admin = User(email='admin@pict.edu', role='admin')
            admin.set_password('admin123')
            admin.is_approved = True
            db.session.add(admin)
            print("✓ Created admin user: admin@pict.edu / admin123")

        # Create Company Users
        companies_data = [
            {
                'email': 'techcorp@example.com',
                'name': 'TechCorp Solutions',
                'description': 'Leading technology solutions provider',
                'industry': 'Technology',
                'company_size': '500-1000',
            },
            {
                'email': 'datascience@example.com',
                'name': 'DataScience Inc',
                'description': 'AI and Machine Learning solutions',
                'industry': 'Technology',
                'company_size': '100-500',
            },
            {
                'email': 'webdev@example.com',
                'name': 'WebDev Studios',
                'description': 'Web development and design agency',
                'industry': 'Technology',
                'company_size': '50-100',
            },
        ]

        company_users = []
        for i, comp_data in enumerate(companies_data):
            user = User.query.filter_by(email=comp_data['email']).first()
            if not user:
                user = User(email=comp_data['email'], role='company')
                user.set_password('company123')
                user.is_approved = True
                db.session.add(user)
                db.session.flush()

                profile = CompanyProfile(
                    user_id=user.id,
                    name=comp_data['name'],
                    description=comp_data['description'],
                    industry=comp_data['industry'],
                    company_size=comp_data['company_size'],
                    website=f"https://{comp_data['email'].split('@')[0]}.com"
                )
                db.session.add(profile)
                company_users.append((user, profile))
                print(f"✓ Created company: {comp_data['name']} / company123")

        # Create Faculty User
        faculty_user = User.query.filter_by(email='faculty@pict.edu').first()
        if not faculty_user:
            faculty_user = User(email='faculty@pict.edu', role='faculty')
            faculty_user.set_password('faculty123')
            faculty_user.is_approved = True
            db.session.add(faculty_user)
            db.session.flush()

            faculty_profile = CompanyProfile(
                user_id=faculty_user.id,
                name='PICT Computer Engineering Department',
                description='Computer Engineering Department',
                is_faculty=True,
                faculty_department='Computer Engineering'
            )
            db.session.add(faculty_profile)
            print("✓ Created faculty: faculty@pict.edu / faculty123")

        # Create Student Users
        students_data = [
            {'first_name': 'John', 'last_name': 'Doe', 'email': 'john@student.pict.edu'},
            {'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@student.pict.edu'},
            {'first_name': 'Alice', 'last_name': 'Johnson', 'email': 'alice@student.pict.edu'},
            {'first_name': 'Bob', 'last_name': 'Williams', 'email': 'bob@student.pict.edu'},
            {'first_name': 'Charlie', 'last_name': 'Brown', 'email': 'charlie@student.pict.edu'},
        ]

        student_users = []
        skills_list = ['Python', 'JavaScript', 'React', 'Node.js', 'Java', 'C++', 'SQL', 'Machine Learning', 'Data Science', 'Web Development', 'Mobile Development', 'Cloud Computing']
        
        for i, student_data in enumerate(students_data):
            user = User.query.filter_by(email=student_data['email']).first()
            if not user:
                user = User(email=student_data['email'], role='student')
                user.set_password('student123')
                user.is_approved = True
                db.session.add(user)
                db.session.flush()

                # Random skills for each student
                num_skills = random.randint(3, 6)
                student_skills = random.sample(skills_list, num_skills)
                
                profile = StudentProfile(
                    user_id=user.id,
                    first_name=student_data['first_name'],
                    last_name=student_data['last_name'],
                    phone=f'98765432{i:02d}',
                    skills=json.dumps(student_skills),
                    interests=json.dumps(['Technology', 'Software Development']),
                    education=json.dumps([{
                        'degree': 'B.E. Computer Engineering',
                        'institution': 'PICT',
                        'field': 'Computer Engineering',
                        'start_date': '2020-08-01',
                        'end_date': '2024-05-31',
                        'gpa': f'{random.uniform(7.5, 9.5):.2f}'
                    }]),
                    bio=f"Computer Engineering student at PICT with interest in {', '.join(student_skills[:3])}"
                )
                db.session.add(profile)
                student_users.append((user, profile))
                print(f"✓ Created student: {student_data['first_name']} {student_data['last_name']} / student123")

        db.session.commit()

        # Create Opportunities
        domains = ['Web Development', 'Machine Learning', 'Data Science', 'Mobile Development', 'Cloud Computing', 'Cybersecurity']
        work_types = ['remote', 'onsite', 'hybrid']
        durations = ['3 months', '6 months', '1 year', '2 months']
        stipends = ['5000-10000', '10000-20000', '20000-30000', 'Unpaid', 'Negotiable']

        opportunities_data = [
            {
                'title': 'Full Stack Web Developer Intern',
                'description': 'Join our team to build modern web applications using React and Node.js. Work on real projects and gain hands-on experience.',
                'domain': 'Web Development',
                'required_skills': ['JavaScript', 'React', 'Node.js', 'SQL'],
                'duration': '6 months',
                'stipend': '15000-20000',
                'location': 'Pune, Maharashtra',
                'work_type': 'hybrid',
            },
            {
                'title': 'Machine Learning Research Intern',
                'description': 'Work on cutting-edge ML projects. Research and implement machine learning models for real-world applications.',
                'domain': 'Machine Learning',
                'required_skills': ['Python', 'Machine Learning', 'Data Science'],
                'duration': '3 months',
                'stipend': '20000-30000',
                'location': 'Remote',
                'work_type': 'remote',
            },
            {
                'title': 'Mobile App Developer',
                'description': 'Develop mobile applications for iOS and Android platforms. Work with React Native or Flutter.',
                'domain': 'Mobile Development',
                'required_skills': ['React Native', 'JavaScript', 'Mobile Development'],
                'duration': '6 months',
                'stipend': '10000-20000',
                'location': 'Pune, Maharashtra',
                'work_type': 'onsite',
            },
            {
                'title': 'Data Science Intern',
                'description': 'Analyze large datasets, build predictive models, and create data visualizations. Work with Python, pandas, and scikit-learn.',
                'domain': 'Data Science',
                'required_skills': ['Python', 'Data Science', 'SQL', 'Machine Learning'],
                'duration': '3 months',
                'stipend': '15000-25000',
                'location': 'Remote',
                'work_type': 'remote',
            },
            {
                'title': 'Cloud Computing Intern',
                'description': 'Learn and work with AWS, Azure, and GCP. Deploy and manage cloud infrastructure.',
                'domain': 'Cloud Computing',
                'required_skills': ['Cloud Computing', 'Python', 'Linux'],
                'duration': '6 months',
                'stipend': '12000-18000',
                'location': 'Pune, Maharashtra',
                'work_type': 'hybrid',
            },
            {
                'title': 'Cybersecurity Intern',
                'description': 'Work on security assessments, penetration testing, and security tool development.',
                'domain': 'Cybersecurity',
                'required_skills': ['Cybersecurity', 'Python', 'Linux', 'Networking'],
                'duration': '3 months',
                'stipend': '18000-25000',
                'location': 'Pune, Maharashtra',
                'work_type': 'onsite',
            },
        ]

        opportunities = []
        for opp_data in opportunities_data:
            # Assign to random company or faculty
            if company_users:
                company_user, company_profile = random.choice(company_users)
            else:
                company_user, company_profile = faculty_user, faculty_profile

            opportunity = Opportunity(
                company_id=company_profile.id,
                title=opp_data['title'],
                description=opp_data['description'],
                domain=opp_data['domain'],
                required_skills=json.dumps(opp_data['required_skills']),
                duration=opp_data['duration'],
                stipend=opp_data['stipend'],
                location=opp_data['location'],
                work_type=opp_data['work_type'],
                application_deadline=(datetime.now() + timedelta(days=30)).date(),
                start_date=(datetime.now() + timedelta(days=45)).date(),
                is_active=True,
                is_approved=True
            )
            db.session.add(opportunity)
            opportunities.append(opportunity)
            print(f"✓ Created opportunity: {opp_data['title']}")

        db.session.commit()

        # Create some applications
        if student_users and opportunities:
            for student_user, student_profile in student_users[:3]:  # First 3 students
                # Each student applies to 2-3 random opportunities
                num_applications = random.randint(2, 3)
                selected_opps = random.sample(opportunities, min(num_applications, len(opportunities)))
                
                for opp in selected_opps:
                    application = Application(
                        student_id=student_profile.id,
                        opportunity_id=opp.id,
                        cover_letter=f"I am interested in this position and believe my skills align well with the requirements.",
                        status=random.choice(['pending', 'shortlisted', 'pending']),
                        skill_match_percentage=random.uniform(60, 95),
                        ai_score=random.uniform(70, 95)
                    )
                    db.session.add(application)
                    opp.applications_count += 1
                    print(f"✓ Created application: {student_profile.first_name} applied to {opp.title}")

        db.session.commit()
        print("\n✅ Dummy data created successfully!")
        print("\nTest Accounts:")
        print("  Admin: admin@pict.edu / admin123")
        print("  Faculty: faculty@pict.edu / faculty123")
        print("  Company: techcorp@example.com / company123")
        print("  Student: john@student.pict.edu / student123")

if __name__ == '__main__':
    create_dummy_data()

