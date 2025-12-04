"""
Migration script to create skills matching tables
Run this once to set up the skills matching system
"""
from app import app, db
from models import Skill, StudentSkill, OpportunitySkill, ExternalJob, ExternalJobSkill

def create_skills_tables():
    """Create all skills-related tables"""
    with app.app_context():
        print("Creating skills matching tables...")
        
        # Create tables
        db.create_all()
        
        print("✅ Tables created successfully!")
        
        # Seed common skills
        common_skills = [
            # Programming Languages
            ('Python', 'programming'),
            ('JavaScript', 'programming'),
            ('Java', 'programming'),
            ('C++', 'programming'),
            ('C#', 'programming'),
            ('PHP', 'programming'),
            ('Ruby', 'programming'),
            ('Go', 'programming'),
            ('Rust', 'programming'),
            ('Swift', 'programming'),
            ('Kotlin', 'programming'),
            ('TypeScript', 'programming'),
            ('Scala', 'programming'),
            ('R', 'programming'),
            
            # Web Technologies
            ('HTML', 'web'),
            ('CSS', 'web'),
            ('React', 'framework'),
            ('Angular', 'framework'),
            ('Vue.js', 'framework'),
            ('Node.js', 'framework'),
            ('Express', 'framework'),
            ('Django', 'framework'),
            ('Flask', 'framework'),
            ('Spring', 'framework'),
            ('Laravel', 'framework'),
            ('Rails', 'framework'),
            ('ASP.NET', 'framework'),
            ('jQuery', 'library'),
            ('Bootstrap', 'library'),
            
            # Databases
            ('SQL', 'database'),
            ('MySQL', 'database'),
            ('PostgreSQL', 'database'),
            ('MongoDB', 'database'),
            ('Redis', 'database'),
            ('Oracle', 'database'),
            ('SQLite', 'database'),
            ('Cassandra', 'database'),
            ('Elasticsearch', 'database'),
            
            # Cloud & DevOps
            ('AWS', 'cloud'),
            ('Azure', 'cloud'),
            ('GCP', 'cloud'),
            ('Docker', 'devops'),
            ('Kubernetes', 'devops'),
            ('Jenkins', 'devops'),
            ('Git', 'devops'),
            ('CI/CD', 'devops'),
            ('Terraform', 'devops'),
            ('Linux', 'devops'),
            
            # Mobile
            ('Android', 'mobile'),
            ('iOS', 'mobile'),
            ('React Native', 'mobile'),
            ('Flutter', 'mobile'),
            
            # Data Science
            ('Machine Learning', 'data-science'),
            ('Deep Learning', 'data-science'),
            ('TensorFlow', 'data-science'),
            ('PyTorch', 'data-science'),
            ('Pandas', 'data-science'),
            ('NumPy', 'data-science'),
            ('Data Analysis', 'data-science'),
            ('Tableau', 'data-science'),
            
            # Other
            ('Blockchain', 'other'),
            ('GraphQL', 'other'),
            ('REST API', 'other'),
            ('Microservices', 'other'),
            ('Agile', 'other'),
            ('Scrum', 'other'),
            ('UI/UX', 'design'),
            ('Figma', 'design'),
        ]
        
        print("\nSeeding common skills...")
        added = 0
        skipped = 0
        
        for skill_name, category in common_skills:
            existing = Skill.query.filter_by(name=skill_name).first()
            if not existing:
                skill = Skill(name=skill_name, category=category)
                db.session.add(skill)
                added += 1
            else:
                skipped += 1
        
        db.session.commit()
        
        print(f"✅ Seeded {added} new skills ({skipped} already existed)")
        print("\n🎉 Skills matching system is ready!")
        print("\nNext steps:")
        print("1. Students can add skills via POST /api/student/skills")
        print("2. Companies can add skills to opportunities via PUT /api/company/opportunities/<id>/skills")
        print("3. Fetch external jobs: python external_jobs_service.py")
        print("4. Students can view matched jobs: GET /api/student/matched-opportunities")

if __name__ == '__main__':
    create_skills_tables()

