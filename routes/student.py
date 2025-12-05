from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt
from models import (
    db,
    User,
    StudentProfile,
    Application,
    Opportunity,
    Notification,
    StudentEducation,
    StudentInternship,
    StudentExperience,
    StudentProject,
    StudentTraining,
    StudentCertification,
    StudentPublication,
    StudentPosition,
    StudentAttachment,
    StudentOffer,
)
from werkzeug.utils import secure_filename
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
from resume_extraction_service import extract_resume_data
from apify_jobs_service import fetch_jobs_from_apify
import os
import json
from routes.helpers import get_user_id
from supabase_storage import is_supabase_configured, upload_file_to_supabase
from skills_matching import SkillsMatchingService
from models import Skill, StudentSkill, OpportunitySkill, ExternalJob, ExternalJobSkill

student_bp = Blueprint('student', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}

SECTION_CONFIG = {
    'education': {
        'model': StudentEducation,
        'fields': ['degree', 'institution', 'course', 'specialization', 'start_date', 'end_date', 'is_current', 'gpa', 'description', 'achievements'],
        'date_fields': ['start_date', 'end_date'],
        'bool_fields': ['is_current'],
        'order_by': StudentEducation.start_date.desc(),
    },
    'experiences': {
        'model': StudentExperience,
        'fields': ['company_name', 'designation', 'employment_type', 'start_date', 'end_date', 'is_current', 'location', 'description', 'technologies'],
        'date_fields': ['start_date', 'end_date'],
        'bool_fields': ['is_current'],
        'json_fields': ['technologies'],
        'order_by': StudentExperience.start_date.desc(),
    },
    'internships': {
        'model': StudentInternship,
        'fields': ['designation', 'organization', 'industry_sector', 'stipend', 'internship_type', 'start_date', 'end_date', 'is_current', 'country', 'state', 'city', 'mentor_name', 'mentor_contact', 'mentor_designation', 'description', 'technologies'],
        'date_fields': ['start_date', 'end_date'],
        'bool_fields': ['is_current'],
        'json_fields': ['technologies'],
        'order_by': StudentInternship.start_date.desc(),
    },
    'projects': {
        'model': StudentProject,
        'fields': ['title', 'organization', 'role', 'start_date', 'end_date', 'description', 'technologies', 'links'],
        'date_fields': ['start_date', 'end_date'],
        'json_fields': ['technologies', 'links'],
        'order_by': StudentProject.start_date.desc(),
    },
    'trainings': {
        'model': StudentTraining,
        'fields': ['title', 'provider', 'mode', 'start_date', 'end_date', 'description'],
        'date_fields': ['start_date', 'end_date'],
        'order_by': StudentTraining.start_date.desc(),
    },
    'certifications': {
        'model': StudentCertification,
        'fields': ['name', 'issuer', 'issue_date', 'expiry_date', 'credential_id', 'credential_url', 'description'],
        'date_fields': ['issue_date', 'expiry_date'],
        'order_by': StudentCertification.issue_date.desc(),
    },
    'publications': {
        'model': StudentPublication,
        'fields': ['title', 'publication_type', 'publisher', 'publication_date', 'url', 'description'],
        'date_fields': ['publication_date'],
        'order_by': StudentPublication.publication_date.desc(),
    },
    'positions': {
        'model': StudentPosition,
        'fields': ['title', 'organization', 'start_date', 'end_date', 'is_current', 'description'],
        'date_fields': ['start_date', 'end_date'],
        'bool_fields': ['is_current'],
        'order_by': StudentPosition.start_date.desc(),
    },
    'offers': {
        'model': StudentOffer,
        'fields': ['company_name', 'role', 'ctc', 'status', 'offer_date', 'joining_date', 'location', 'notes'],
        'date_fields': ['offer_date', 'joining_date'],
        'order_by': StudentOffer.offer_date.desc(),
    },
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None

def normalize_json_field(value):
    if value is None:
        return json.dumps([])
    if isinstance(value, list):
        return json.dumps(value)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return json.dumps(parsed)
        except json.JSONDecodeError:
            pass
        parts = [part.strip() for part in value.split(',') if part.strip()]
        return json.dumps(parts)
    return json.dumps(value)

def assign_section_fields(instance, data, config):
    fields = config.get('fields', [])
    date_fields = set(config.get('date_fields', []))
    bool_fields = set(config.get('bool_fields', []))
    json_fields = set(config.get('json_fields', []))

    for field in fields:
        if field not in data:
            continue
        value = data[field]
        if field in date_fields:
            value = parse_date(value)
        elif field in bool_fields:
            value = bool(value)
        elif field in json_fields:
            value = normalize_json_field(value)
        setattr(instance, field, value)

def serialize_all_sections(profile):
    sections = {}
    for key, config in SECTION_CONFIG.items():
        model = config['model']
        query = model.query.filter_by(student_id=profile.id)
        order_by = config.get('order_by')
        if order_by is not None:
            query = query.order_by(order_by)
        sections[key] = [entry.to_dict() for entry in query.all()]
    attachments = StudentAttachment.query.filter_by(student_id=profile.id).all()
    sections['attachments'] = [attachment.to_dict() for attachment in attachments]
    return sections

def friendly_application_status(status: str) -> str:
    mapping = {
        'pending': 'Next steps awaited',
        'shortlisted': 'Shortlisted',
        'rejected': 'Not selected',
        'interview': 'Interview scheduled',
        'accepted': 'Offer received',
        'withdrawn': 'Withdrawn',
    }
    return mapping.get(status, status.title() if status else 'In progress')

def get_student_profile():
    user_id = get_user_id()
    user = User.query.get(user_id)
    if not user or user.role != 'student':
        return None, jsonify({'error': 'Unauthorized'}), 403
    profile = user.student_profile
    if not profile:
        return None, jsonify({'error': 'Profile not found'}), 404
    return profile, None, None

@student_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status
    
    profile_dict = profile.to_dict()
    
    # Get skills from StudentSkill table (technical and non-technical)
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
                'proficiency_level': ss.proficiency_level,
                'years_of_experience': ss.years_of_experience
            }
            # Categorize as technical or non-technical based on category
            if skill.category in ['programming', 'framework', 'database', 'cloud', 'devops', 'mobile', 'data-science', 'web', 'library']:
                technical_skills.append(skill_data)
            else:
                non_technical_skills.append(skill_data)
    
    profile_dict['technical_skills'] = technical_skills
    profile_dict['non_technical_skills'] = non_technical_skills
    profile_dict['has_skills'] = len(student_skills) > 0  # Check if skills are set
    
    return jsonify(profile_dict), 200

@student_bp.route('/profile/full', methods=['GET'])
@jwt_required()
def get_full_profile_data():
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    sections = serialize_all_sections(profile)
    stats = {key: len(value) for key, value in sections.items()}

    return jsonify({
        'profile': profile.to_dict(),
        'sections': sections,
        'resume_path': profile.resume_path,
        'stats': stats
    }), 200

@student_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        profile, error_response, status = get_student_profile()
        if error_response:
            return error_response, status
        
        data = request.get_json()
        
        if 'first_name' in data:
            profile.first_name = data['first_name']
        if 'last_name' in data:
            profile.last_name = data['last_name']
        if 'middle_name' in data:
            profile.middle_name = data['middle_name']
        if 'phone' in data:
            profile.phone = data['phone']
        if 'date_of_birth' in data:
            dob = data.get('date_of_birth')
            profile.date_of_birth = parse_date(dob) if dob else None
        if 'address' in data:
            profile.address = data['address']
        if 'prn_number' in data:
            profile.prn_number = data['prn_number']
        if 'course' in data:
            profile.course = data['course']
        if 'specialization' in data:
            profile.specialization = data['specialization']
        if 'gender' in data:
            profile.gender = data['gender']
        if 'education' in data:
            profile.education = json.dumps(data['education'])
        if 'skills' in data:
            profile.skills = json.dumps(data['skills'])
        if 'technical_skills' in data or 'non_technical_skills' in data:
            # Update skills from the new skills section
            technical_skills = data.get('technical_skills', [])
            non_technical_skills = data.get('non_technical_skills', [])
            
            # Combine all skill names
            all_skill_names = []
            proficiency_levels = {}
            
            for skill_data in technical_skills + non_technical_skills:
                if isinstance(skill_data, dict):
                    skill_name = skill_data.get('name') or skill_data.get('skill')
                    if skill_name:
                        all_skill_names.append(skill_name)
                        if 'proficiency_level' in skill_data:
                            proficiency_levels[skill_name] = skill_data['proficiency_level']
                elif isinstance(skill_data, str):
                    all_skill_names.append(skill_data)
            
            # Update skills using SkillsMatchingService
            if all_skill_names:
                SkillsMatchingService.update_student_skills(
                    profile.id,
                    all_skill_names,
                    proficiency_levels
                )
        if 'interests' in data:
            profile.interests = json.dumps(data['interests'])
        if 'bio' in data:
            profile.bio = data['bio']
        if 'linkedin_url' in data:
            profile.linkedin_url = data['linkedin_url']
        if 'github_url' in data:
            profile.github_url = data['github_url']
        if 'portfolio_url' in data:
            profile.portfolio_url = data['portfolio_url']
        
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Profile updated successfully', 'profile': profile.to_dict()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
#
# ---------- Rich Profile Sections ----------
#

def _ensure_entry(query, entry_id, student_id):
    entry = query.filter_by(id=entry_id, student_id=student_id).first()
    if not entry:
        return None, jsonify({'error': 'Record not found'}), 404
    return entry, None, None

@student_bp.route('/education', methods=['GET', 'POST'])
@jwt_required()
def education_collection():
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    if request.method == 'GET':
        entries = StudentEducation.query.filter_by(student_id=profile.id).order_by(StudentEducation.start_date.desc().nullslast()).all()
        return jsonify([e.to_dict() for e in entries]), 200

    data = request.get_json()
    required = ['degree', 'institution']
    if any(not data.get(field) for field in required):
        return jsonify({'error': 'degree and institution are required'}), 400
    entry = StudentEducation(
        student_id=profile.id,
        degree=data.get('degree'),
        institution=data.get('institution'),
        course=data.get('course'),
        specialization=data.get('specialization'),
        start_date=parse_date(data.get('start_date')),
        end_date=parse_date(data.get('end_date')),
        is_current=data.get('is_current', False),
        gpa=data.get('gpa'),
        description=data.get('description'),
        achievements=data.get('achievements')
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'message': 'Education added', 'education': entry.to_dict()}), 201

@student_bp.route('/education/<int:entry_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def education_detail(entry_id):
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    entry, error_response, status = _ensure_entry(StudentEducation.query, entry_id, profile.id)
    if error_response:
        return error_response, status

    if request.method == 'DELETE':
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'Education removed'}), 200

    data = request.get_json()
    for field in ['degree', 'institution', 'course', 'specialization', 'gpa', 'description', 'achievements']:
        if field in data:
            setattr(entry, field, data[field])
    if 'is_current' in data:
        entry.is_current = data['is_current']
    if 'start_date' in data:
        entry.start_date = parse_date(data.get('start_date'))
    if 'end_date' in data:
        entry.end_date = parse_date(data.get('end_date'))
    db.session.commit()
    return jsonify({'message': 'Education updated', 'education': entry.to_dict()}), 200

def _create_internship(profile, data):
    required = ['designation', 'organization']
    if any(not data.get(field) for field in required):
        return None, jsonify({'error': 'designation and organization are required'}), 400
    entry = StudentInternship(
        student_id=profile.id,
        designation=data.get('designation'),
        organization=data.get('organization'),
        industry_sector=data.get('industry_sector'),
        stipend=data.get('stipend'),
        internship_type=data.get('internship_type'),
        start_date=parse_date(data.get('start_date')),
        end_date=parse_date(data.get('end_date')),
        is_current=data.get('is_current', False),
        country=data.get('country'),
        state=data.get('state'),
        city=data.get('city'),
        mentor_name=data.get('mentor_name'),
        mentor_contact=data.get('mentor_contact'),
        mentor_designation=data.get('mentor_designation'),
        description=data.get('description'),
        technologies=json.dumps(data.get('technologies', []))
    )
    return entry, None, None

@student_bp.route('/internships', methods=['GET', 'POST'])
@jwt_required()
def internships_collection():
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    if request.method == 'GET':
        entries = StudentInternship.query.filter_by(student_id=profile.id).order_by(StudentInternship.start_date.desc().nullslast()).all()
        return jsonify([e.to_dict() for e in entries]), 200

    data = request.get_json()
    entry, error_response, status = _create_internship(profile, data)
    if error_response:
        return error_response, status
    db.session.add(entry)
    db.session.commit()
    return jsonify({'message': 'Internship added', 'internship': entry.to_dict()}), 201

@student_bp.route('/internships/<int:entry_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def internships_detail(entry_id):
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    entry, error_response, status = _ensure_entry(StudentInternship.query, entry_id, profile.id)
    if error_response:
        return error_response, status

    if request.method == 'DELETE':
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'Internship removed'}), 200

    data = request.get_json()
    for field in [
        'designation', 'organization', 'industry_sector', 'stipend', 'internship_type',
        'country', 'state', 'city', 'mentor_name', 'mentor_contact', 'mentor_designation',
        'description'
    ]:
        if field in data:
            setattr(entry, field, data[field])
    if 'technologies' in data:
        entry.technologies = json.dumps(data.get('technologies', []))
    if 'is_current' in data:
        entry.is_current = data['is_current']
    if 'start_date' in data:
        entry.start_date = parse_date(data.get('start_date'))
    if 'end_date' in data:
        entry.end_date = parse_date(data.get('end_date'))
    db.session.commit()
    return jsonify({'message': 'Internship updated', 'internship': entry.to_dict()}), 200

def _generic_collection(model, order_by=None):
    def decorator(func):
        return func
    return decorator

def _handle_generic_get(model, student_id, order_by=None):
    query = model.query.filter_by(student_id=student_id)
    if order_by is not None:
        query = query.order_by(order_by)
    return [entry.to_dict() for entry in query.all()]

def _update_entry(entry, data, field_names):
    for field in field_names:
        if field in data:
            setattr(entry, field, data[field])

@student_bp.route('/experiences', methods=['GET', 'POST'])
@jwt_required()
def experiences_collection():
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    if request.method == 'GET':
        return jsonify(_handle_generic_get(StudentExperience, profile.id, StudentExperience.start_date.desc().nullslast())), 200

    data = request.get_json()
    required = ['company_name', 'designation']
    if any(not data.get(field) for field in required):
        return jsonify({'error': 'company_name and designation are required'}), 400
    entry = StudentExperience(
        student_id=profile.id,
        company_name=data.get('company_name'),
        designation=data.get('designation'),
        employment_type=data.get('employment_type'),
        start_date=parse_date(data.get('start_date')),
        end_date=parse_date(data.get('end_date')),
        is_current=data.get('is_current', False),
        location=data.get('location'),
        description=data.get('description'),
        technologies=json.dumps(data.get('technologies', []))
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'message': 'Experience added', 'experience': entry.to_dict()}), 201

@student_bp.route('/experiences/<int:entry_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def experiences_detail(entry_id):
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    entry, error_response, status = _ensure_entry(StudentExperience.query, entry_id, profile.id)
    if error_response:
        return error_response, status

    if request.method == 'DELETE':
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'Experience removed'}), 200

    data = request.get_json()
    for field in ['company_name', 'designation', 'employment_type', 'location', 'description']:
        if field in data:
            setattr(entry, field, data[field])
    if 'technologies' in data:
        entry.technologies = json.dumps(data.get('technologies', []))
    if 'is_current' in data:
        entry.is_current = data['is_current']
    if 'start_date' in data:
        entry.start_date = parse_date(data.get('start_date'))
    if 'end_date' in data:
        entry.end_date = parse_date(data.get('end_date'))
    db.session.commit()
    return jsonify({'message': 'Experience updated', 'experience': entry.to_dict()}), 200

@student_bp.route('/projects', methods=['GET', 'POST'])
@jwt_required()
def projects_collection():
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    if request.method == 'GET':
        entries = StudentProject.query.filter_by(student_id=profile.id).order_by(StudentProject.start_date.desc().nullslast()).all()
        return jsonify([e.to_dict() for e in entries]), 200

    data = request.get_json()
    if not data.get('title'):
        return jsonify({'error': 'title is required'}), 400
    entry = StudentProject(
        student_id=profile.id,
        title=data.get('title'),
        organization=data.get('organization'),
        role=data.get('role'),
        start_date=parse_date(data.get('start_date')),
        end_date=parse_date(data.get('end_date')),
        description=data.get('description'),
        technologies=json.dumps(data.get('technologies', [])),
        links=json.dumps(data.get('links', []))
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'message': 'Project added', 'project': entry.to_dict()}), 201

@student_bp.route('/projects/<int:entry_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def projects_detail(entry_id):
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    entry, error_response, status = _ensure_entry(StudentProject.query, entry_id, profile.id)
    if error_response:
        return error_response, status

    if request.method == 'DELETE':
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'Project removed'}), 200

    data = request.get_json()
    for field in ['title', 'organization', 'role', 'description']:
        if field in data:
            setattr(entry, field, data[field])
    if 'technologies' in data:
        entry.technologies = json.dumps(data.get('technologies', []))
    if 'links' in data:
        entry.links = json.dumps(data.get('links', []))
    if 'start_date' in data:
        entry.start_date = parse_date(data.get('start_date'))
    if 'end_date' in data:
        entry.end_date = parse_date(data.get('end_date'))
    db.session.commit()
    return jsonify({'message': 'Project updated', 'project': entry.to_dict()}), 200

@student_bp.route('/trainings', methods=['GET', 'POST'])
@jwt_required()
def trainings_collection():
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    if request.method == 'GET':
        entries = StudentTraining.query.filter_by(student_id=profile.id).order_by(StudentTraining.start_date.desc().nullslast()).all()
        return jsonify([e.to_dict() for e in entries]), 200

    data = request.get_json()
    if not data.get('title'):
        return jsonify({'error': 'title is required'}), 400
    entry = StudentTraining(
        student_id=profile.id,
        title=data.get('title'),
        provider=data.get('provider'),
        mode=data.get('mode'),
        start_date=parse_date(data.get('start_date')),
        end_date=parse_date(data.get('end_date')),
        description=data.get('description')
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'message': 'Training added', 'training': entry.to_dict()}), 201

@student_bp.route('/trainings/<int:entry_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def trainings_detail(entry_id):
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    entry, error_response, status = _ensure_entry(StudentTraining.query, entry_id, profile.id)
    if error_response:
        return error_response, status

    if request.method == 'DELETE':
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'Training removed'}), 200

    data = request.get_json()
    for field in ['title', 'provider', 'mode', 'description']:
        if field in data:
            setattr(entry, field, data[field])
    if 'start_date' in data:
        entry.start_date = parse_date(data.get('start_date'))
    if 'end_date' in data:
        entry.end_date = parse_date(data.get('end_date'))
    db.session.commit()
    return jsonify({'message': 'Training updated', 'training': entry.to_dict()}), 200

@student_bp.route('/certifications', methods=['GET', 'POST'])
@jwt_required()
def certifications_collection():
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    if request.method == 'GET':
        entries = StudentCertification.query.filter_by(student_id=profile.id).order_by(StudentCertification.issue_date.desc().nullslast()).all()
        return jsonify([e.to_dict() for e in entries]), 200

    data = request.get_json()
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    entry = StudentCertification(
        student_id=profile.id,
        name=data.get('name'),
        issuer=data.get('issuer'),
        issue_date=parse_date(data.get('issue_date')),
        expiry_date=parse_date(data.get('expiry_date')),
        credential_id=data.get('credential_id'),
        credential_url=data.get('credential_url'),
        description=data.get('description')
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'message': 'Certification added', 'certification': entry.to_dict()}), 201

@student_bp.route('/certifications/<int:entry_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def certifications_detail(entry_id):
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    entry, error_response, status = _ensure_entry(StudentCertification.query, entry_id, profile.id)
    if error_response:
        return error_response, status

    if request.method == 'DELETE':
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'Certification removed'}), 200

    data = request.get_json()
    for field in ['name', 'issuer', 'credential_id', 'credential_url', 'description']:
        if field in data:
            setattr(entry, field, data[field])
    if 'issue_date' in data:
        entry.issue_date = parse_date(data.get('issue_date'))
    if 'expiry_date' in data:
        entry.expiry_date = parse_date(data.get('expiry_date'))
    db.session.commit()
    return jsonify({'message': 'Certification updated', 'certification': entry.to_dict()}), 200

@student_bp.route('/publications', methods=['GET', 'POST'])
@jwt_required()
def publications_collection():
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    if request.method == 'GET':
        entries = StudentPublication.query.filter_by(student_id=profile.id).order_by(StudentPublication.publication_date.desc().nullslast()).all()
        return jsonify([e.to_dict() for e in entries]), 200

    data = request.get_json()
    if not data.get('title'):
        return jsonify({'error': 'title is required'}), 400
    entry = StudentPublication(
        student_id=profile.id,
        title=data.get('title'),
        publication_type=data.get('publication_type'),
        publisher=data.get('publisher'),
        publication_date=parse_date(data.get('publication_date')),
        url=data.get('url'),
        description=data.get('description')
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'message': 'Publication added', 'publication': entry.to_dict()}), 201

@student_bp.route('/publications/<int:entry_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def publications_detail(entry_id):
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    entry, error_response, status = _ensure_entry(StudentPublication.query, entry_id, profile.id)
    if error_response:
        return error_response, status

    if request.method == 'DELETE':
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'Publication removed'}), 200

    data = request.get_json()
    for field in ['title', 'publication_type', 'publisher', 'url', 'description']:
        if field in data:
            setattr(entry, field, data[field])
    if 'publication_date' in data:
        entry.publication_date = parse_date(data.get('publication_date'))
    db.session.commit()
    return jsonify({'message': 'Publication updated', 'publication': entry.to_dict()}), 200

@student_bp.route('/positions', methods=['GET', 'POST'])
@jwt_required()
def positions_collection():
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    if request.method == 'GET':
        entries = StudentPosition.query.filter_by(student_id=profile.id).order_by(StudentPosition.start_date.desc().nullslast()).all()
        return jsonify([e.to_dict() for e in entries]), 200

    data = request.get_json()
    if not data.get('title'):
        return jsonify({'error': 'title is required'}), 400
    entry = StudentPosition(
        student_id=profile.id,
        title=data.get('title'),
        organization=data.get('organization'),
        start_date=parse_date(data.get('start_date')),
        end_date=parse_date(data.get('end_date')),
        is_current=data.get('is_current', False),
        description=data.get('description')
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'message': 'Position added', 'position': entry.to_dict()}), 201

@student_bp.route('/positions/<int:entry_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def positions_detail(entry_id):
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    entry, error_response, status = _ensure_entry(StudentPosition.query, entry_id, profile.id)
    if error_response:
        return error_response, status

    if request.method == 'DELETE':
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'Position removed'}), 200

    data = request.get_json()
    for field in ['title', 'organization', 'description']:
        if field in data:
            setattr(entry, field, data[field])
    if 'is_current' in data:
        entry.is_current = data['is_current']
    if 'start_date' in data:
        entry.start_date = parse_date(data.get('start_date'))
    if 'end_date' in data:
        entry.end_date = parse_date(data.get('end_date'))
    db.session.commit()
    return jsonify({'message': 'Position updated', 'position': entry.to_dict()}), 200

@student_bp.route('/attachments', methods=['GET', 'POST'])
@jwt_required()
def attachments_collection():
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    if request.method == 'GET':
        entries = StudentAttachment.query.filter_by(student_id=profile.id).all()
        return jsonify([e.to_dict() for e in entries]), 200

    # Handle file upload (form-data)
    if 'file' in request.files:
        upload = request.files['file']
        if upload.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        filename = secure_filename(upload.filename)

        # Prefer Supabase Storage if configured
        file_url = None
        if is_supabase_configured():
            folder = f"attachments/{profile.id}"
            file_url = upload_file_to_supabase(upload, filename, folder)

        # Fallback to local filesystem if Supabase not available
        if not file_url:
            attachments_dir = os.path.join('uploads', 'attachments')
            os.makedirs(attachments_dir, exist_ok=True)
            filepath = os.path.join(
                attachments_dir,
                f"{profile.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}",
            )
            upload.save(filepath)
            file_url = filepath

        entry = StudentAttachment(
            student_id=profile.id,
            title=request.form.get('title', filename),
            file_path=file_url,
            attachment_type=request.form.get('attachment_type', 'document'),
        )
        db.session.add(entry)
        db.session.commit()
        return jsonify({'message': 'Attachment uploaded', 'attachment': entry.to_dict()}), 201

    data = request.get_json() or {}
    if not data.get('title') or not data.get('file_path'):
        return jsonify({'error': 'title and file_path are required'}), 400
    entry = StudentAttachment(
        student_id=profile.id,
        title=data.get('title'),
        file_path=data.get('file_path'),
        attachment_type=data.get('attachment_type')
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'message': 'Attachment added', 'attachment': entry.to_dict()}), 201

@student_bp.route('/attachments/<int:entry_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def attachments_detail(entry_id):
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    entry, error_response, status = _ensure_entry(StudentAttachment.query, entry_id, profile.id)
    if error_response:
        return error_response, status

    if request.method == 'DELETE':
        # If stored locally, remove from filesystem; Supabase objects are kept
        if entry.file_path and not entry.file_path.startswith("http") and os.path.exists(entry.file_path):
            try:
                os.remove(entry.file_path)
            except OSError:
                pass
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'Attachment removed'}), 200

    data = request.get_json()
    for field in ['title', 'file_path', 'attachment_type']:
        if field in data:
            setattr(entry, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Attachment updated', 'attachment': entry.to_dict()}), 200

@student_bp.route('/offers', methods=['GET', 'POST'])
@jwt_required()
def offers_collection():
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    if request.method == 'GET':
        entries = StudentOffer.query.filter_by(student_id=profile.id).order_by(StudentOffer.offer_date.desc().nullslast()).all()
        return jsonify([e.to_dict() for e in entries]), 200

    data = request.get_json()
    if not data.get('company_name'):
        return jsonify({'error': 'company_name is required'}), 400
    entry = StudentOffer(
        student_id=profile.id,
        company_name=data.get('company_name'),
        role=data.get('role'),
        ctc=data.get('ctc'),
        status=data.get('status', 'pending'),
        offer_date=parse_date(data.get('offer_date')),
        joining_date=parse_date(data.get('joining_date')),
        location=data.get('location'),
        notes=data.get('notes')
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'message': 'Offer added', 'offer': entry.to_dict()}), 201

@student_bp.route('/offers/<int:entry_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def offers_detail(entry_id):
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    entry, error_response, status = _ensure_entry(StudentOffer.query, entry_id, profile.id)
    if error_response:
        return error_response, status

    if request.method == 'DELETE':
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'Offer removed'}), 200

    data = request.get_json()
    for field in ['company_name', 'role', 'ctc', 'status', 'location', 'notes']:
        if field in data:
            setattr(entry, field, data[field])
    if 'offer_date' in data:
        entry.offer_date = parse_date(data.get('offer_date'))
    if 'joining_date' in data:
        entry.joining_date = parse_date(data.get('joining_date'))
    db.session.commit()
    return jsonify({'message': 'Offer updated', 'offer': entry.to_dict()}), 200


@student_bp.route('/resume/upload', methods=['POST'])
@jwt_required()
def upload_resume():
    try:
        profile, error_response, status = get_student_profile()
        if error_response:
            return error_response, status
        
        if 'resume' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: PDF, DOC, DOCX'}), 400
        
        filename = secure_filename(f"{profile.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")

        # Read bytes once for parsing, then reset pointer
        file_bytes = file.read()
        file.stream.seek(0)

        # Prefer Supabase Storage if configured
        resume_url = None
        if is_supabase_configured():
            folder = f"resumes/{profile.id}"
            resume_url = upload_file_to_supabase(file, filename, folder)

        # Fallback to local filesystem if Supabase not available
        if not resume_url:
            resumes_dir = os.path.join('uploads', 'resumes')
            os.makedirs(resumes_dir, exist_ok=True)
            filepath = os.path.join(resumes_dir, filename)
            file.save(filepath)
            resume_url = filepath
        
        # Delete old resume if exists and it was stored locally
        if profile.resume_path and not str(profile.resume_path).startswith("http") and os.path.exists(profile.resume_path):
            try:
                os.remove(profile.resume_path)
            except OSError:
                pass
        
        profile.resume_path = resume_url
        db.session.commit()

        # --------- Resume parsing + skills + external jobs ----------
        parsed = {}
        keywords = []
        external_jobs = []
        try:
            parsed = extract_resume_data(file_bytes, file.filename)
            keywords = parsed.get('keywords', []) or parsed.get('skills', [])

            # Update skills from resume keywords (merge)
            if keywords:
                SkillsMatchingService.update_student_skills(profile.id, keywords)

            # Fetch external jobs via Apify using keywords
            try:
                external_jobs = fetch_jobs_from_apify(keywords, location="India")
            except Exception as apify_err:
                # Don't fail upload; just log
                print(f"[Apify] fetch failed: {apify_err}")
        except Exception as parse_err:
            # Parsing shouldn't block resume upload
            print(f"[Resume Parse] failed: {parse_err}")
        
        return jsonify({
            'message': 'Resume uploaded successfully',
            'resume_path': resume_url,
            'parsed_resume': parsed,
            'keywords': keywords,
            'external_jobs': external_jobs
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/resume/download', methods=['GET'])
@jwt_required()
def download_resume():
    try:
        profile, error_response, status = get_student_profile()
        if error_response:
            return error_response, status
        
        if not profile.resume_path:
            return jsonify({'error': 'Resume not found'}), 404

        # If stored in Supabase (URL), let the client download from the URL directly
        if str(profile.resume_path).startswith("http"):
            return jsonify({'resume_url': profile.resume_path}), 200
        
        if not os.path.exists(profile.resume_path):
            return jsonify({'error': 'Resume not found'}), 404
        
        return send_file(profile.resume_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/resume/generate', methods=['GET'])
@jwt_required()
def generate_resume():
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status

    sections = serialize_all_sections(profile)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", 'B', 16)
    full_name = f"{profile.first_name} {profile.last_name}".strip()
    pdf.cell(0, 10, full_name or "Student Resume", ln=True)

    pdf.set_font("Helvetica", '', 11)
    contact_line = []
    if profile.phone:
        contact_line.append(f"Phone: {profile.phone}")
    if profile.linkedin_url:
        contact_line.append(f"LinkedIn: {profile.linkedin_url}")
    if profile.github_url:
        contact_line.append(f"GitHub: {profile.github_url}")
    if contact_line:
        pdf.multi_cell(0, 6, " | ".join(contact_line))
        pdf.ln(2)

    def add_section(title, items, formatter):
        if not items:
            return
        pdf.set_font("Helvetica", 'B', 13)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_font("Helvetica", '', 11)
        for item in items:
            formatter(item)
            pdf.ln(2)
        pdf.ln(3)

    add_section("Education", sections.get('education', []), lambda item: pdf.multi_cell(
        0, 6, f"{item.get('degree', '')} - {item.get('institution', '')} ({item.get('start_date', '')} - {item.get('end_date', '') or 'Present'})\nGPA: {item.get('gpa', 'N/A')}"
    ))

    add_section("Professional Experience", sections.get('experiences', []), lambda item: pdf.multi_cell(
        0, 6, f"{item.get('designation', '')} @ {item.get('company_name', '')} ({item.get('start_date', '')} - {item.get('end_date', '') or 'Present'})\n{item.get('description', '')}"
    ))

    add_section("Internships", sections.get('internships', []), lambda item: pdf.multi_cell(
        0, 6, f"{item.get('designation', '')} @ {item.get('organization', '')} ({item.get('start_date', '')} - {item.get('end_date', '') or 'Present'})\nMentor: {item.get('mentor_name', '-')}\n{item.get('description', '')}"
    ))

    add_section("Projects", sections.get('projects', []), lambda item: pdf.multi_cell(
        0, 6, f"{item.get('title', '')} ({item.get('start_date', '')} - {item.get('end_date', '') or 'Present'})\n{item.get('description', '')}"
    ))

    add_section("Certifications", sections.get('certifications', []), lambda item: pdf.multi_cell(
        0, 6, f"{item.get('name', '')} - {item.get('issuer', '')} ({item.get('issue_date', '')})"
    ))

    pdf_output = pdf.output(dest='S').encode('latin-1')
    buffer = BytesIO(pdf_output)
    buffer.seek(0)
    filename = f"{full_name.replace(' ', '_') or 'resume'}.pdf"
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)

@student_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    try:
        profile, error_response, status = get_student_profile()
        if error_response:
            return error_response, status
        
        # Get applications
        applications = Application.query.filter_by(student_id=profile.id).order_by(Application.applied_at.desc()).all()
        
        # Get recommended opportunities (basic - can be enhanced with AI)
        all_opportunities = Opportunity.query.filter_by(is_active=True, is_approved=True).all()
        
        # Simple recommendation based on skills
        student_skills = json.loads(profile.skills) if profile.skills else []
        recommended = []
        for opp in all_opportunities:
            if opp.id not in [app.opportunity_id for app in applications]:
                required_skills = json.loads(opp.required_skills) if opp.required_skills else []
                match_count = len(set(student_skills) & set(required_skills))
                if match_count > 0 or len(required_skills) == 0:
                    recommended.append(opp)
                    if len(recommended) >= 10:
                        break
        
        # Get notifications
        notifications = Notification.query.filter_by(user_id=profile.user_id, is_read=False).order_by(Notification.created_at.desc()).limit(10).all()
        
        return jsonify({
            'profile': profile.to_dict(),
            'applications': [app.to_dict() for app in applications],
            'recommended_opportunities': [opp.to_dict() for opp in recommended],
            'notifications': [notif.to_dict() for notif in notifications],
            'stats': {
                'total_applications': len(applications),
                'pending': len([a for a in applications if a.status == 'pending']),
                'shortlisted': len([a for a in applications if a.status == 'shortlisted']),
                'rejected': len([a for a in applications if a.status == 'rejected']),
                'interview': len([a for a in applications if a.status == 'interview'])
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/jobs/summary', methods=['GET'])
@jwt_required()
def get_jobs_summary():
    try:
        profile, error_response, status = get_student_profile()
        if error_response:
            return error_response, status

        student_skills = set(json.loads(profile.skills) if profile.skills else [])
        applications = Application.query.filter_by(student_id=profile.id).order_by(Application.applied_at.desc()).all()
        applications_by_opp = {app.opportunity_id: app for app in applications}
        offers = StudentOffer.query.filter_by(student_id=profile.id).order_by(StudentOffer.offer_date.desc().nullslast()).all()

        opportunities_query = Opportunity.query.filter_by(is_active=True, is_approved=True).order_by(Opportunity.created_at.desc())
        opportunities = opportunities_query.limit(60).all()

        tag_counts = {}
        opportunity_cards = []
        eligible_count = 0

        for opp in opportunities:
            required = json.loads(opp.required_skills) if opp.required_skills else []
            match = len(student_skills & set(required))
            match_pct = int((match / len(required)) * 100) if required else 100
            eligible = match_pct >= 40
            if eligible:
                eligible_count += 1

            application = applications_by_opp.get(opp.id)
            status_label = friendly_application_status(application.status) if application else ('Eligible' if eligible else 'Upskill suggested')

            for tag in required[:10]:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

            opportunity_cards.append({
                'id': opp.id,
                'title': opp.title,
                'company': opp.company.name if opp.company else None,
                'job_type': opp.work_type.title() if opp.work_type else 'Full Time',
                'ctc': opp.stipend or 'Not disclosed',
                'location': opp.location or 'Remote',
                'tags': required[:6],
                'eligible': eligible,
                'match': match_pct,
                'status': status_label,
                'applied': bool(application),
                'application_status': application.status if application else None,
                'application_id': application.id if application else None,
                'posted_on': opp.created_at.isoformat() if opp.created_at else None,
            })

        applications_cards = []
        for app in applications:
            opportunity = app.opportunity
            applications_cards.append({
                'id': app.id,
                'title': opportunity.title if opportunity else 'Opportunity',
                'company': opportunity.company.name if opportunity and opportunity.company else None,
                'location': opportunity.location if opportunity else None,
                'status': friendly_application_status(app.status),
                'job_type': opportunity.work_type.title() if opportunity and opportunity.work_type else 'Full Time',
                'ctc': opportunity.stipend if opportunity else None,
                'submitted_on': app.applied_at.isoformat() if app.applied_at else None,
                'tags': json.loads(opportunity.required_skills)[:6] if opportunity and opportunity.required_skills else [],
            })

        offers_cards = [{
            'id': offer.id,
            'company_name': offer.company_name,
            'role': offer.role,
            'ctc': offer.ctc,
            'status': friendly_application_status(offer.status),
            'offer_date': offer.offer_date.isoformat() if offer.offer_date else None,
            'joining_date': offer.joining_date.isoformat() if offer.joining_date else None,
            'location': offer.location,
            'notes': offer.notes,
        } for offer in offers]

        stats = {
            'eligible': eligible_count,
            'applications': len(applications_cards),
            'offers': len(offers_cards),
            'opportunities': len(opportunity_cards),
        }

        popular_tags = [
            {'tag': tag, 'count': count}
            for tag, count in sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)[:12]
        ]

        return jsonify({
            'opportunities': opportunity_cards,
            'applications': applications_cards,
            'offers': offers_cards,
            'stats': stats,
            'popular_tags': popular_tags,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    try:
        profile, error_response, status = get_student_profile()
        if error_response:
            return error_response, status
        
        applications = Application.query.filter_by(student_id=profile.id).order_by(Application.applied_at.desc()).all()
        
        return jsonify([app.to_dict() for app in applications]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/files/check', methods=['GET'])
@jwt_required()
def check_files_status():
    """
    Check the status of uploaded files - verify if they exist in Supabase.
    Returns information about resume and attachments for the current student.
    """
    try:
        profile, error_response, status = get_student_profile()
        if error_response:
            return error_response, status
        
        from supabase_storage import (
            is_supabase_configured,
            get_file_info_from_url,
            get_all_student_files
        )
        
        result = {
            'supabase_configured': is_supabase_configured(),
            'resume': None,
            'attachments': [],
            'storage_files': {
                'resumes': 0,
                'attachments': 0
            }
        }
        
        # Check resume
        if profile.resume_path:
            if str(profile.resume_path).startswith('http'):
                # Supabase URL
                file_info = get_file_info_from_url(profile.resume_path)
                result['resume'] = {
                    'url': profile.resume_path,
                    'exists': file_info['exists'] if file_info else False,
                    'storage_path': file_info.get('storage_path') if file_info else None,
                    'location': 'supabase'
                }
            else:
                # Local file
                result['resume'] = {
                    'path': profile.resume_path,
                    'exists': os.path.exists(profile.resume_path) if profile.resume_path else False,
                    'location': 'local'
                }
        
        # Check attachments
        attachments = StudentAttachment.query.filter_by(student_id=profile.id).all()
        for attachment in attachments:
            if str(attachment.file_path).startswith('http'):
                # Supabase URL
                file_info = get_file_info_from_url(attachment.file_path)
                result['attachments'].append({
                    'id': attachment.id,
                    'title': attachment.title,
                    'url': attachment.file_path,
                    'exists': file_info['exists'] if file_info else False,
                    'storage_path': file_info.get('storage_path') if file_info else None,
                    'location': 'supabase'
                })
            else:
                # Local file
                result['attachments'].append({
                    'id': attachment.id,
                    'title': attachment.title,
                    'path': attachment.file_path,
                    'exists': os.path.exists(attachment.file_path) if attachment.file_path else False,
                    'location': 'local'
                })
        
        # Get files directly from Supabase storage (if configured)
        if is_supabase_configured():
            storage_files = get_all_student_files(profile.id)
            result['storage_files'] = {
                'resumes': len(storage_files['resumes']),
                'attachments': len(storage_files['attachments'])
            }
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== SKILLS MATCHING ENDPOINTS ====================

@student_bp.route('/skills', methods=['GET', 'POST', 'PUT'])
@jwt_required()
def manage_skills():
    """Get, add, or update student skills (Technical and Non-Technical)"""
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status
    
    if request.method == 'GET':
        # Get all skills with student's skills marked
        all_skills = Skill.query.order_by(Skill.name).all()
        student_skill_ids = {ss.skill_id for ss in StudentSkill.query.filter_by(student_id=profile.id).all()}
        
        skills_list = []
        for skill in all_skills:
            skill_dict = skill.to_dict()
            skill_dict['has_skill'] = skill.id in student_skill_ids
            if skill.id in student_skill_ids:
                student_skill = StudentSkill.query.filter_by(
                    student_id=profile.id, 
                    skill_id=skill.id
                ).first()
                skill_dict['proficiency_level'] = student_skill.proficiency_level if student_skill else None
            skills_list.append(skill_dict)
        
        # Get student's current skills (separated by technical/non-technical)
        student_skills = StudentSkill.query.filter_by(student_id=profile.id).all()
        technical_skills = []
        non_technical_skills = []
        
        for ss in student_skills:
            skill = Skill.query.get(ss.skill_id)
            if skill:
                skill_data = ss.to_dict()
                skill_data['category'] = skill.category
                if skill.category in ['programming', 'framework', 'database', 'cloud', 'devops', 'mobile', 'data-science', 'web', 'library']:
                    technical_skills.append(skill_data)
                else:
                    non_technical_skills.append(skill_data)
        
        return jsonify({
            'all_skills': skills_list,
            'technical_skills': technical_skills,
            'non_technical_skills': non_technical_skills
        }), 200
    
    elif request.method == 'POST' or request.method == 'PUT':
        # Update student skills
        data = request.get_json() or {}
        technical_skills = data.get('technical_skills', [])
        non_technical_skills = data.get('non_technical_skills', [])
        proficiency_levels = data.get('proficiency_levels', {})
        
        # Combine all skills
        all_skill_names = []
        for skill_data in technical_skills + non_technical_skills:
            if isinstance(skill_data, dict):
                skill_name = skill_data.get('name') or skill_data.get('skill')
                if skill_name:
                    all_skill_names.append(skill_name)
                    if 'proficiency_level' in skill_data:
                        proficiency_levels[skill_name] = skill_data['proficiency_level']
            elif isinstance(skill_data, str):
                all_skill_names.append(skill_data)
        
        if not all_skill_names:
            return jsonify({'error': 'Skills list is required'}), 400
        
        try:
            SkillsMatchingService.update_student_skills(
                profile.id, 
                all_skill_names,
                proficiency_levels
            )
            
            # Return updated skills
            student_skills = StudentSkill.query.filter_by(student_id=profile.id).all()
            technical = []
            non_technical = []
            
            for ss in student_skills:
                skill = Skill.query.get(ss.skill_id)
                if skill:
                    skill_data = ss.to_dict()
                    skill_data['category'] = skill.category
                    if skill.category in ['programming', 'framework', 'database', 'cloud', 'devops', 'mobile', 'data-science', 'web', 'library']:
                        technical.append(skill_data)
                    else:
                        non_technical.append(skill_data)
            
            return jsonify({
                'message': 'Skills updated successfully',
                'technical_skills': technical,
                'non_technical_skills': non_technical
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500


@student_bp.route('/matched-opportunities', methods=['GET'])
@jwt_required()
def get_matched_opportunities():
    """Get opportunities matched with student's skills (70%+ match only - eligible to apply)"""
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status
    
    try:
        # Default to 70% minimum match as per requirement
        min_match = float(request.args.get('min_match', 70.0))
        limit = int(request.args.get('limit', 50))
        
        matched_opps = SkillsMatchingService.get_matched_opportunities(
            profile.id,
            limit=limit,
            min_match=min_match
        )
        
        # Filter to only show jobs with 70%+ match (can apply)
        applicable_jobs = [
            opp for opp in matched_opps 
            if opp['match_data']['match_percentage'] >= 70.0
        ]
        
        return jsonify({
            'matched_opportunities': applicable_jobs,
            'total': len(applicable_jobs),
            'min_match_threshold': 70.0,
            'message': 'Showing only jobs with 70%+ match (eligible to apply)'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@student_bp.route('/external-jobs', methods=['GET'])
@jwt_required()
def get_external_jobs():
    """Get external jobs matched with student's skills (70%+ match only) - New Tab for External Jobs"""
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status
    
    try:
        # Default to 70% minimum match
        min_match = float(request.args.get('min_match', 70.0))
        limit = int(request.args.get('limit', 50))
        
        matched_jobs = SkillsMatchingService.get_matched_external_jobs(
            profile.id,
            limit=limit,
            min_match=min_match
        )
        
        # Filter to only show jobs with 70%+ match
        applicable_jobs = [
            job for job in matched_jobs 
            if job['match_data']['match_percentage'] >= 70.0
        ]
        
        return jsonify({
            'external_jobs': applicable_jobs,
            'total': len(applicable_jobs),
            'min_match_threshold': 70.0,
            'message': 'Showing only external jobs with 70%+ match'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@student_bp.route('/opportunities/<int:opportunity_id>/match', methods=['GET'])
@jwt_required()
def get_opportunity_match(opportunity_id):
    """Get match details for a specific opportunity"""
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status
    
    try:
        opportunity = Opportunity.query.get_or_404(opportunity_id)
        match_data = SkillsMatchingService.calculate_match_score(profile.id, opportunity_id)
        
        return jsonify({
            'opportunity': opportunity.to_dict(),
            'match_data': match_data,
            'can_apply': match_data['match_percentage'] >= 70.0
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@student_bp.route('/external-jobs/<int:job_id>/match', methods=['GET'])
@jwt_required()
def get_external_job_match(job_id):
    """Get match details for a specific external job"""
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status
    
    try:
        job = ExternalJob.query.get_or_404(job_id)
        match_data = SkillsMatchingService.calculate_external_job_match(profile.id, job_id)
        
        return jsonify({
            'job': job.to_dict(),
            'match_data': match_data,
            'can_apply': match_data['match_percentage'] >= 70.0
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@student_bp.route('/check-skills-setup', methods=['GET'])
@jwt_required()
def check_skills_setup():
    """Check if student needs to set up skills (first-time login)"""
    profile, error_response, status = get_student_profile()
    if error_response:
        return error_response, status
    
    skill_count = StudentSkill.query.filter_by(student_id=profile.id).count()
    
    return jsonify({
        'has_skills': skill_count > 0,
        'skill_count': skill_count,
        'needs_setup': skill_count == 0,
        'message': 'Please add your skills to get matched with opportunities' if skill_count == 0 else 'Skills are set up'
    }), 200

