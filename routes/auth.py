from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, decode_token
from models import db, User, StudentProfile, CompanyProfile, Blacklist
from datetime import datetime
import re
from routes.helpers import get_user_id
from flask import current_app

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        role = data.get('role', '').lower()
        
        # Validation
        if not email or not password or not role:
            return jsonify({'error': 'Email, password, and role are required'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        if role not in ['student', 'company', 'faculty']:
            return jsonify({'error': 'Invalid role. Must be student, company, or faculty'}), 400
        
        # Check blacklist
        if Blacklist.query.filter_by(email=email).first():
            return jsonify({'error': 'This email is blacklisted'}), 403
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create user
        user = User(email=email, role=role)
        user.set_password(password)
        
        # Auto-approve all users for easier testing (change to False for production)
        # In production, companies/faculty should require admin approval
        user.is_approved = True  # Auto-approve everyone for development
        
        db.session.add(user)
        db.session.commit()
        
        # Create profile based on role
        if role == 'student':
            profile_data = data.get('profile', {})
            profile = StudentProfile(
                user_id=user.id,
                first_name=profile_data.get('first_name', ''),
                last_name=profile_data.get('last_name', ''),
                phone=profile_data.get('phone', ''),
                address=profile_data.get('address', '')
            )
            db.session.add(profile)
        else:
            profile_data = data.get('profile', {})
            profile = CompanyProfile(
                user_id=user.id,
                name=profile_data.get('name', ''),
                description=profile_data.get('description', ''),
                is_faculty=(role == 'faculty'),
                faculty_department=profile_data.get('faculty_department', '') if role == 'faculty' else None
            )
            db.session.add(profile)
        
        db.session.commit()
        
        token = user.generate_token()
        try:
            decoded = decode_token(token)
            current_app.logger.debug(f"Issued token for user {user.id}: sub={decoded.get('sub')} type={type(decoded.get('sub'))}")
        except Exception as decode_error:
            current_app.logger.error(f"Token decode error: {decode_error}")
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': user.to_dict(),
            'profile': profile.to_dict() if profile else None
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        if not user.is_approved:
            return jsonify({'error': 'Account pending approval'}), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        token = user.generate_token()
        try:
            decoded = decode_token(token)
            current_app.logger.debug(f"Login token for user {user.id}: sub={decoded.get('sub')} type={type(decoded.get('sub'))}")
        except Exception as decode_error:
            current_app.logger.error(f"Login token decode error: {decode_error}")
        
        # Get profile
        profile = None
        needs_skills_setup = False
        
        if user.role == 'student':
            profile = user.student_profile
            if profile:
                # Check if student has skills set up (first-time login check)
                from models import StudentSkill
                skill_count = StudentSkill.query.filter_by(student_id=profile.id).count()
                needs_skills_setup = skill_count == 0
        
        elif user.role in ['company', 'faculty']:
            profile = user.company_profile
        
        profile_dict = profile.to_dict() if profile else None
        
        # Add skills info for students
        if user.role == 'student' and profile:
            from models import StudentSkill, Skill
            student_skills = StudentSkill.query.filter_by(student_id=profile.id).all()
            technical_skills = []
            non_technical_skills = []
            
            for ss in student_skills:
                skill = Skill.query.get(ss.skill_id)
                if skill:
                    skill_data = {
                        'id': skill.id,
                        'name': skill.name,
                        'category': skill.category,
                        'proficiency_level': ss.proficiency_level
                    }
                    if skill.category in ['programming', 'framework', 'database', 'cloud', 'devops', 'mobile', 'data-science', 'web', 'library']:
                        technical_skills.append(skill_data)
                    else:
                        non_technical_skills.append(skill_data)
            
            if profile_dict:
                profile_dict['technical_skills'] = technical_skills
                profile_dict['non_technical_skills'] = non_technical_skills
                profile_dict['has_skills'] = len(student_skills) > 0
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict(),
            'profile': profile_dict,
            'needs_skills_setup': needs_skills_setup  # First-time login flag
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        profile = None
        if user.role == 'student':
            profile = user.student_profile
        elif user.role in ['company', 'faculty']:
            profile = user.company_profile
        
        return jsonify({
            'user': user.to_dict(),
            'profile': profile.to_dict() if profile else None
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    try:
        user_id = get_user_id()
        claims = get_jwt()
        return jsonify({
            'valid': True,
            'user_id': user_id,
            'role': claims.get('role')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 401

