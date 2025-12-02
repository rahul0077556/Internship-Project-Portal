from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Opportunity, Application, StudentProfile, User
from datetime import datetime
import json
from routes.helpers import get_user_id

opportunities_bp = Blueprint('opportunities', __name__)

def get_optional_user_id():
    """Helper function to get user ID from JWT token if present, returns None if not"""
    try:
        # Check if Authorization header exists
        auth_header = request.headers.get('Authorization', '')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        # Try to get user ID using jwt_required context
        # We'll use a try-except to handle invalid tokens gracefully
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        return get_user_id()
    except Exception:
        # If token is invalid or missing, return None (anonymous user)
        return None

@opportunities_bp.route('', methods=['GET'])
def get_opportunities():
    try:
        # Get user ID if authenticated (optional)
        user_id = get_optional_user_id()
        
        # Get query parameters
        domain = request.args.get('domain', None)
        work_type = request.args.get('work_type', None)
        search = request.args.get('search', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Base query - only approved and active opportunities
        query = Opportunity.query.filter_by(is_active=True, is_approved=True)
        
        # Apply filters
        if domain:
            query = query.filter_by(domain=domain)
        if work_type:
            query = query.filter_by(work_type=work_type)
        if search:
            query = query.filter(
                (Opportunity.title.contains(search)) |
                (Opportunity.description.contains(search))
            )
        
        # Pagination
        pagination = query.order_by(Opportunity.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        opportunities = pagination.items
        
        # Check if user has applied (if authenticated)
        applied_opp_ids = set()
        if user_id:
            user = User.query.get(user_id)
            if user and user.role == 'student' and user.student_profile:
                applications = Application.query.filter_by(student_id=user.student_profile.id).all()
                applied_opp_ids = {app.opportunity_id for app in applications}
        
        result = []
        for opp in opportunities:
            opp_dict = opp.to_dict()
            opp_dict['has_applied'] = opp.id in applied_opp_ids
            result.append(opp_dict)
        
        return jsonify({
            'opportunities': result,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@opportunities_bp.route('/<int:opp_id>', methods=['GET'])
def get_opportunity(opp_id):
    try:
        # Get user ID if authenticated (optional)
        user_id = get_optional_user_id()
        
        opportunity = Opportunity.query.get(opp_id)
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        if not opportunity.is_active or not opportunity.is_approved:
            return jsonify({'error': 'Opportunity not available'}), 404
        
        # Increment view count
        opportunity.views_count += 1
        db.session.commit()
        
        opp_dict = opportunity.to_dict()
        
        # Check if user has applied (if authenticated)
        if user_id:
            user = User.query.get(user_id)
            if user and user.role == 'student' and user.student_profile:
                application = Application.query.filter_by(
                    student_id=user.student_profile.id,
                    opportunity_id=opp_id
                ).first()
                if application:
                    opp_dict['application'] = application.to_dict()
                opp_dict['has_applied'] = application is not None
            else:
                opp_dict['has_applied'] = False
        else:
            opp_dict['has_applied'] = False
        
        return jsonify(opp_dict), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@opportunities_bp.route('/domains', methods=['GET'])
def get_domains():
    try:
        domains = db.session.query(Opportunity.domain).distinct().filter_by(is_approved=True).all()
        return jsonify([domain[0] for domain in domains]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

