from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, User, CompanyProfile, Opportunity, Application, StudentProfile, Notification
from models import Skill, OpportunitySkill
from datetime import datetime
import json
from routes.helpers import get_user_id
from skills_matching import SkillsMatchingService

company_bp = Blueprint('company', __name__)

def get_company_profile():
    user_id = get_user_id()
    user = User.query.get(user_id)
    if not user or user.role not in ['company', 'faculty']:
        return None, jsonify({'error': 'Unauthorized'}), 403
    profile = user.company_profile
    if not profile:
        return None, jsonify({'error': 'Profile not found'}), 404
    return profile, None, None

@company_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    profile, error_response, status = get_company_profile()
    if error_response:
        return error_response, status
    return jsonify(profile.to_dict()), 200

@company_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        profile, error_response, status = get_company_profile()
        if error_response:
            return error_response, status
        
        data = request.get_json()
        
        if 'name' in data:
            profile.name = data['name']
        if 'description' in data:
            profile.description = data['description']
        if 'website' in data:
            profile.website = data['website']
        if 'phone' in data:
            profile.phone = data['phone']
        if 'address' in data:
            profile.address = data['address']
        if 'industry' in data:
            profile.industry = data['industry']
        if 'company_size' in data:
            profile.company_size = data['company_size']
        if 'faculty_department' in data:
            profile.faculty_department = data['faculty_department']
        
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Profile updated successfully', 'profile': profile.to_dict()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@company_bp.route('/opportunities', methods=['POST'])
@jwt_required()
def create_opportunity():
    try:
        profile, error_response, status = get_company_profile()
        if error_response:
            return error_response, status
        
        data = request.get_json()
        
        required_fields = ['title', 'description', 'domain']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Auto-approve if published (is_active=True)
        is_active = data.get('is_active', False)
        is_approved = is_active  # Auto-approve when published
        
        # Parse dates safely
        application_deadline = None
        if data.get('application_deadline'):
            try:
                if isinstance(data['application_deadline'], str):
                    application_deadline = datetime.strptime(data['application_deadline'], '%Y-%m-%d').date()
                else:
                    application_deadline = data['application_deadline']
            except (ValueError, TypeError):
                application_deadline = None
        
        start_date = None
        if data.get('start_date'):
            try:
                if isinstance(data['start_date'], str):
                    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                else:
                    start_date = data['start_date']
            except (ValueError, TypeError):
                start_date = None
        
        opportunity = Opportunity(
            company_id=profile.id,
            title=data['title'],
            description=data['description'],
            domain=data['domain'],
            required_skills=json.dumps(data.get('required_skills', [])),
            duration=data.get('duration', ''),
            stipend=data.get('stipend', ''),
            location=data.get('location', ''),
            work_type=data.get('work_type', 'remote'),
            prerequisites=data.get('prerequisites', ''),
            application_deadline=application_deadline,
            start_date=start_date,
            is_active=is_active,
            is_approved=is_approved  # Auto-approve when published
        )
        
        db.session.add(opportunity)
        db.session.flush()  # Get the ID without committing
        
        # Auto-sync skills if provided
        if 'required_skills' in data and data['required_skills']:
            skill_names = data['required_skills']
            if isinstance(skill_names, list):
                try:
                    SkillsMatchingService.update_opportunity_skills(
                        opportunity.id,
                        skill_names,
                        skill_names  # All are required by default
                    )
                except Exception as e:
                    print(f"Warning: Could not sync skills: {e}")
        
        db.session.commit()
        
        return jsonify({'message': 'Opportunity created successfully', 'opportunity': opportunity.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@company_bp.route('/opportunities', methods=['GET'])
@jwt_required()
def get_opportunities():
    try:
        profile, error_response, status = get_company_profile()
        if error_response:
            return error_response, status
        
        opportunities = Opportunity.query.filter_by(company_id=profile.id).order_by(Opportunity.created_at.desc()).all()
        
        return jsonify([opp.to_dict() for opp in opportunities]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/opportunities/<int:opp_id>', methods=['PUT'])
@jwt_required()
def update_opportunity(opp_id):
    try:
        profile, error_response, status = get_company_profile()
        if error_response:
            return error_response, status
        
        opportunity = Opportunity.query.filter_by(id=opp_id, company_id=profile.id).first()
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        data = request.get_json()
        
        if 'title' in data:
            opportunity.title = data['title']
        if 'description' in data:
            opportunity.description = data['description']
        if 'domain' in data:
            opportunity.domain = data['domain']
        if 'required_skills' in data:
            opportunity.required_skills = json.dumps(data['required_skills'])
            # Also update normalized skills table
            skill_names = data['required_skills']
            if isinstance(skill_names, list):
                SkillsMatchingService.update_opportunity_skills(
                    opportunity.id,
                    skill_names,
                    skill_names  # All are required by default
                )
        if 'duration' in data:
            opportunity.duration = data['duration']
        if 'stipend' in data:
            opportunity.stipend = data['stipend']
        if 'location' in data:
            opportunity.location = data['location']
        if 'work_type' in data:
            opportunity.work_type = data['work_type']
        if 'prerequisites' in data:
            opportunity.prerequisites = data['prerequisites']
        if 'application_deadline' in data and data['application_deadline']:
            try:
                if isinstance(data['application_deadline'], str):
                    opportunity.application_deadline = datetime.strptime(data['application_deadline'], '%Y-%m-%d').date()
                else:
                    opportunity.application_deadline = data['application_deadline']
            except (ValueError, TypeError):
                pass  # Keep existing value if parsing fails
        if 'start_date' in data and data['start_date']:
            try:
                if isinstance(data['start_date'], str):
                    opportunity.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                else:
                    opportunity.start_date = data['start_date']
            except (ValueError, TypeError):
                pass  # Keep existing value if parsing fails
        if 'is_active' in data:
            opportunity.is_active = data['is_active']
            # Auto-approve when published
            if data['is_active']:
                opportunity.is_approved = True
        
        opportunity.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Opportunity updated successfully', 'opportunity': opportunity.to_dict()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@company_bp.route('/opportunities/<int:opp_id>/applicants', methods=['GET'])
@jwt_required()
def get_applicants(opp_id):
    try:
        profile, error_response, status = get_company_profile()
        if error_response:
            return error_response, status
        
        opportunity = Opportunity.query.filter_by(id=opp_id, company_id=profile.id).first()
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        status_filter = request.args.get('status', None)
        query = Application.query.filter_by(opportunity_id=opp_id)
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        applications = query.order_by(Application.applied_at.desc()).all()
        
        # Get full student details
        applicants = []
        for app in applications:
            student = StudentProfile.query.get(app.student_id)
            if student:
                app_dict = app.to_dict()
                app_dict['student_profile'] = student.to_dict()
                applicants.append(app_dict)
        
        return jsonify(applicants), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
@jwt_required()
def update_application_status(app_id):
    try:
        profile, error_response, status = get_company_profile()
        if error_response:
            return error_response, status
        
        application = Application.query.get(app_id)
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Verify the application belongs to an opportunity posted by this company
        opportunity = Opportunity.query.get(application.opportunity_id)
        if not opportunity or opportunity.company_id != profile.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['pending', 'shortlisted', 'rejected', 'interview', 'accepted', 'withdrawn']:
            return jsonify({'error': 'Invalid status'}), 400
        
        old_status = application.status
        application.status = new_status
        if 'notes' in data:
            application.notes = data['notes']
        
        application.updated_at = datetime.utcnow()
        
        # Create notification for student
        student = StudentProfile.query.get(application.student_id)
        if student:
            notification = Notification(
                user_id=student.user_id,
                title='Application Status Updated',
                message=f'Your application for "{opportunity.title}" has been {new_status}',
                notification_type='application_status',
                related_id=application.id
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({'message': 'Application status updated', 'application': application.to_dict()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@company_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    try:
        profile, error_response, status = get_company_profile()
        if error_response:
            return error_response, status
        
        opportunities = Opportunity.query.filter_by(company_id=profile.id).all()
        
        total_applications = 0
        pending_applications = 0
        for opp in opportunities:
            apps = Application.query.filter_by(opportunity_id=opp.id).all()
            total_applications += len(apps)
            pending_applications += len([a for a in apps if a.status == 'pending'])
        
        return jsonify({
            'profile': profile.to_dict(),
            'opportunities': [opp.to_dict() for opp in opportunities],
            'stats': {
                'total_opportunities': len(opportunities),
                'active_opportunities': len([o for o in opportunities if o.is_active]),
                'total_applications': total_applications,
                'pending_applications': pending_applications
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== SKILLS MATCHING ENDPOINTS FOR COMPANIES ====================

@company_bp.route('/opportunities/<int:opp_id>/skills', methods=['GET', 'PUT'])
@jwt_required()
def manage_opportunity_skills(opp_id):
    """Get or update required skills for an opportunity"""
    profile, error_response, status = get_company_profile()
    if error_response:
        return error_response, status
    
    opportunity = Opportunity.query.get_or_404(opp_id)
    if opportunity.company_id != profile.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'GET':
        # Get all skills with opportunity's skills marked
        all_skills = Skill.query.order_by(Skill.name).all()
        opp_skill_ids = {os.skill_id for os in OpportunitySkill.query.filter_by(opportunity_id=opp_id).all()}
        
        skills_list = []
        for skill in all_skills:
            skill_dict = skill.to_dict()
            skill_dict['is_required'] = skill.id in opp_skill_ids
            if skill.id in opp_skill_ids:
                opp_skill = OpportunitySkill.query.filter_by(
                    opportunity_id=opp_id,
                    skill_id=skill.id
                ).first()
                skill_dict['priority'] = opp_skill.priority if opp_skill else 1
            skills_list.append(skill_dict)
        
        # Get opportunity's current skills
        opp_skills = OpportunitySkill.query.filter_by(opportunity_id=opp_id).all()
        current_skills = [os.to_dict() for os in opp_skills]
        
        return jsonify({
            'all_skills': skills_list,
            'current_skills': current_skills
        }), 200
    
    elif request.method == 'PUT':
        # Update opportunity skills
        data = request.get_json() or {}
        skill_names = data.get('skills', [])
        required_skills = data.get('required_skills', skill_names)
        
        if not skill_names:
            return jsonify({'error': 'Skills list is required'}), 400
        
        try:
            SkillsMatchingService.update_opportunity_skills(
                opp_id,
                skill_names,
                required_skills
            )
            
            # Return updated skills
            opp_skills = OpportunitySkill.query.filter_by(opportunity_id=opp_id).all()
            return jsonify({
                'message': 'Skills updated successfully',
                'skills': [os.to_dict() for os in opp_skills]
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500


@company_bp.route('/opportunities/<int:opp_id>/matching-students', methods=['GET'])
@jwt_required()
def get_matching_students(opp_id):
    """Get students matched with an opportunity"""
    profile, error_response, status = get_company_profile()
    if error_response:
        return error_response, status
    
    opportunity = Opportunity.query.get_or_404(opp_id)
    if opportunity.company_id != profile.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        min_match = float(request.args.get('min_match', 0.0))
        limit = int(request.args.get('limit', 50))
        
        matched_students = SkillsMatchingService.get_matching_students(
            opp_id,
            limit=limit,
            min_match=min_match
        )
        
        return jsonify({
            'opportunity': opportunity.to_dict(),
            'matched_students': matched_students,
            'total': len(matched_students)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@company_bp.route('/skills', methods=['GET'])
@jwt_required()
def get_all_skills():
    """Get all available skills"""
    try:
        skills = Skill.query.order_by(Skill.name).all()
        return jsonify({
            'skills': [skill.to_dict() for skill in skills]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

