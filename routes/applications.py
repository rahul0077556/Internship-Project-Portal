from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Application, Opportunity, StudentProfile, User, Notification
from datetime import datetime
import os
from routes.helpers import get_user_id

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('', methods=['POST'])
@jwt_required()
def create_application():
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        
        if not user or user.role != 'student':
            return jsonify({'error': 'Only students can apply'}), 403
        
        profile = user.student_profile
        if not profile:
            return jsonify({'error': 'Profile not found. Please complete your profile first'}), 404
        
        data = request.get_json()
        opportunity_id = data.get('opportunity_id')
        
        if not opportunity_id:
            return jsonify({'error': 'opportunity_id is required'}), 400
        
        opportunity = Opportunity.query.get(opportunity_id)
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        if not opportunity.is_active or not opportunity.is_approved:
            return jsonify({'error': 'Opportunity is not available'}), 400
        
        # Check if already applied
        existing = Application.query.filter_by(
            student_id=profile.id,
            opportunity_id=opportunity_id
        ).first()
        
        if existing:
            return jsonify({'error': 'You have already applied for this opportunity'}), 409
        
        # Check deadline
        if opportunity.application_deadline and opportunity.application_deadline < datetime.now().date():
            return jsonify({'error': 'Application deadline has passed'}), 400
        
        # Create application
        application = Application(
            student_id=profile.id,
            opportunity_id=opportunity_id,
            resume_path=profile.resume_path,
            cover_letter=data.get('cover_letter', ''),
            status='pending'
        )
        
        db.session.add(application)
        
        # Update opportunity application count
        opportunity.applications_count += 1
        
        # Create notification for company
        company_user = opportunity.company.user
        notification = Notification(
            user_id=company_user.id,
            title='New Application',
            message=f'{profile.first_name} {profile.last_name} applied for "{opportunity.title}"',
            notification_type='new_application',
            related_id=application.id
        )
        db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Application submitted successfully',
            'application': application.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/<int:app_id>', methods=['GET'])
@jwt_required()
def get_application(app_id):
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        
        application = Application.query.get(app_id)
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Check authorization
        if user.role == 'student':
            if application.student.user_id != user_id:
                return jsonify({'error': 'Unauthorized'}), 403
        elif user.role in ['company', 'faculty']:
            opportunity = Opportunity.query.get(application.opportunity_id)
            if not opportunity or opportunity.company.user_id != user_id:
                return jsonify({'error': 'Unauthorized'}), 403
        elif user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify(application.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/<int:app_id>', methods=['DELETE'])
@jwt_required()
def withdraw_application(app_id):
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        
        if user.role != 'student':
            return jsonify({'error': 'Only students can withdraw applications'}), 403
        
        application = Application.query.get(app_id)
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        if application.student.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if application.status in ['accepted', 'rejected']:
            return jsonify({'error': 'Cannot withdraw application in current status'}), 400
        
        application.status = 'withdrawn'
        application.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Application withdrawn successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

