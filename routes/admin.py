from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, User, StudentProfile, CompanyProfile, Opportunity, Application, Blacklist
from datetime import datetime
from sqlalchemy import func
from routes.helpers import get_user_id

admin_bp = Blueprint('admin', __name__)

def is_admin():
    user_id = get_user_id()
    user = User.query.get(user_id)
    return user and user.role == 'admin'

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    role_filter = request.args.get('role', None)
    approval_filter = request.args.get('approved', None)
    
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    if approval_filter is not None:
        query = query.filter_by(is_approved=approval_filter == 'true')
    
    users = query.order_by(User.created_at.desc()).all()
    
    result = []
    for user in users:
        user_dict = user.to_dict()
        if user.role == 'student' and user.student_profile:
            user_dict['profile'] = user.student_profile.to_dict()
        elif user.role in ['company', 'faculty'] and user.company_profile:
            user_dict['profile'] = user.company_profile.to_dict()
        result.append(user_dict)
    
    return jsonify(result), 200

@admin_bp.route('/users/<int:user_id>/approve', methods=['PUT'])
@jwt_required()
def approve_user(user_id):
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user.is_approved = True
    db.session.commit()
    
    return jsonify({'message': 'User approved successfully', 'user': user.to_dict()}), 200

@admin_bp.route('/users/<int:user_id>/deactivate', methods=['PUT'])
@jwt_required()
def deactivate_user(user_id):
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'User deactivated successfully'}), 200

@admin_bp.route('/opportunities', methods=['GET'])
@jwt_required()
def get_opportunities():
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    approval_filter = request.args.get('approved', None)
    
    query = Opportunity.query
    if approval_filter is not None:
        query = query.filter_by(is_approved=approval_filter == 'true')
    
    opportunities = query.order_by(Opportunity.created_at.desc()).all()
    
    return jsonify([opp.to_dict() for opp in opportunities]), 200

@admin_bp.route('/opportunities/<int:opp_id>/approve', methods=['PUT'])
@jwt_required()
def approve_opportunity(opp_id):
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    opportunity = Opportunity.query.get(opp_id)
    if not opportunity:
        return jsonify({'error': 'Opportunity not found'}), 404
    
    opportunity.is_approved = True
    db.session.commit()
    
    return jsonify({'message': 'Opportunity approved successfully', 'opportunity': opportunity.to_dict()}), 200

@admin_bp.route('/opportunities/<int:opp_id>/reject', methods=['PUT'])
@jwt_required()
def reject_opportunity(opp_id):
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    opportunity = Opportunity.query.get(opp_id)
    if not opportunity:
        return jsonify({'error': 'Opportunity not found'}), 404
    
    opportunity.is_approved = False
    opportunity.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Opportunity rejected'}), 200

@admin_bp.route('/blacklist', methods=['POST'])
@jwt_required()
def add_to_blacklist():
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    reason = data.get('reason', '')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    existing = Blacklist.query.filter_by(email=email).first()
    if existing:
        return jsonify({'error': 'Email already blacklisted'}), 409
    
    blacklist_entry = Blacklist(email=email, reason=reason)
    db.session.add(blacklist_entry)
    
    # Deactivate user if exists
    user = User.query.filter_by(email=email).first()
    if user:
        user.is_active = False
    
    db.session.commit()
    
    return jsonify({'message': 'Email added to blacklist', 'entry': blacklist_entry.to_dict()}), 201

@admin_bp.route('/blacklist', methods=['GET'])
@jwt_required()
def get_blacklist():
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    entries = Blacklist.query.order_by(Blacklist.created_at.desc()).all()
    return jsonify([entry.to_dict() for entry in entries]), 200

@admin_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    # User statistics
    total_users = User.query.count()
    students = User.query.filter_by(role='student').count()
    companies = User.query.filter_by(role='company').count()
    faculty = User.query.filter_by(role='faculty').count()
    pending_approvals = User.query.filter_by(is_approved=False).count()
    
    # Opportunity statistics
    total_opportunities = Opportunity.query.count()
    active_opportunities = Opportunity.query.filter_by(is_active=True, is_approved=True).count()
    pending_opportunities = Opportunity.query.filter_by(is_approved=False).count()
    
    # Application statistics
    total_applications = Application.query.count()
    pending_applications = Application.query.filter_by(status='pending').count()
    shortlisted = Application.query.filter_by(status='shortlisted').count()
    accepted = Application.query.filter_by(status='accepted').count()
    
    # Popular domains
    domain_counts = db.session.query(
        Opportunity.domain,
        func.count(Opportunity.id).label('count')
    ).filter_by(is_approved=True).group_by(Opportunity.domain).all()
    
    popular_domains = [{'domain': domain, 'count': count} for domain, count in domain_counts]
    
    # Popular skills (from opportunities)
    all_skills = {}
    opportunities = Opportunity.query.filter_by(is_approved=True).all()
    for opp in opportunities:
        if opp.required_skills:
            import json
            skills = json.loads(opp.required_skills)
            for skill in skills:
                all_skills[skill] = all_skills.get(skill, 0) + 1
    
    popular_skills = [{'skill': skill, 'count': count} for skill, count in sorted(all_skills.items(), key=lambda x: x[1], reverse=True)[:10]]
    
    return jsonify({
        'users': {
            'total': total_users,
            'students': students,
            'companies': companies,
            'faculty': faculty,
            'pending_approvals': pending_approvals
        },
        'opportunities': {
            'total': total_opportunities,
            'active': active_opportunities,
            'pending': pending_opportunities
        },
        'applications': {
            'total': total_applications,
            'pending': pending_applications,
            'shortlisted': shortlisted,
            'accepted': accepted
        },
        'popular_domains': popular_domains,
        'popular_skills': popular_skills
    }), 200

