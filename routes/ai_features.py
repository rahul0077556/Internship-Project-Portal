from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, StudentProfile, Opportunity, Application, User
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import re
from routes.helpers import get_user_id

ai_bp = Blueprint('ai', __name__)

def calculate_skill_match(student_skills, required_skills):
    """Calculate skill match percentage"""
    if not required_skills or len(required_skills) == 0:
        return 100.0
    
    if not student_skills or len(student_skills) == 0:
        return 0.0
    
    student_skills_lower = [s.lower().strip() for s in student_skills]
    required_skills_lower = [s.lower().strip() for s in required_skills]
    
    matched = len(set(student_skills_lower) & set(required_skills_lower))
    return (matched / len(required_skills)) * 100

def calculate_resume_score(resume_text, required_skills, description):
    """Calculate resume score based on skills and description match"""
    if not resume_text:
        return 0.0
    
    # Combine required skills and description keywords
    keywords = required_skills + re.findall(r'\b\w+\b', description.lower())
    
    # Simple keyword matching
    resume_lower = resume_text.lower()
    matches = sum(1 for keyword in keywords if keyword.lower() in resume_lower)
    
    # Normalize score (0-100)
    total_keywords = len(keywords)
    if total_keywords == 0:
        return 50.0  # Default score if no keywords
    
    score = (matches / total_keywords) * 100
    return min(100.0, max(0.0, score))

@ai_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        
        if not user or user.role != 'student':
            return jsonify({'error': 'Only students can get recommendations'}), 403
        
        profile = user.student_profile
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        student_skills = json.loads(profile.skills) if profile.skills else []
        student_interests = json.loads(profile.interests) if profile.interests else []
        
        # Get all active opportunities
        opportunities = Opportunity.query.filter_by(is_active=True, is_approved=True).all()
        
        # Get already applied opportunity IDs
        applied_opp_ids = {app.opportunity_id for app in profile.applications}
        
        # Calculate scores for each opportunity
        scored_opportunities = []
        for opp in opportunities:
            if opp.id in applied_opp_ids:
                continue
            
            required_skills = json.loads(opp.required_skills) if opp.required_skills else []
            
            # Skill match
            skill_match = calculate_skill_match(student_skills, required_skills)
            
            # Interest match (if domain matches interest)
            interest_match = 0
            if opp.domain.lower() in [i.lower() for i in student_interests]:
                interest_match = 50
            
            # Combined score
            total_score = (skill_match * 0.7) + (interest_match * 0.3)
            
            scored_opportunities.append({
                'opportunity': opp.to_dict(),
                'score': round(total_score, 2),
                'skill_match': round(skill_match, 2),
                'matched_skills': list(set([s.lower() for s in student_skills]) & set([s.lower() for s in required_skills]))
            })
        
        # Sort by score
        scored_opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top 20
        return jsonify(scored_opportunities[:20]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/resume-score', methods=['POST'])
@jwt_required()
def get_resume_score():
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        
        if not user or user.role != 'student':
            return jsonify({'error': 'Only students can use this feature'}), 403
        
        profile = user.student_profile
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        data = request.get_json()
        opportunity_id = data.get('opportunity_id')
        
        if not opportunity_id:
            return jsonify({'error': 'opportunity_id is required'}), 400
        
        opportunity = Opportunity.query.get(opportunity_id)
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        required_skills = json.loads(opportunity.required_skills) if opportunity.required_skills else []
        student_skills = json.loads(profile.skills) if profile.skills else []
        
        # Calculate skill match
        skill_match = calculate_skill_match(student_skills, required_skills)
        
        # Calculate resume score (simplified - would need actual resume parsing)
        resume_score = 50.0  # Default
        if profile.resume_path:
            # In production, would parse PDF/DOCX here
            # For now, use skill match as proxy
            resume_score = skill_match
        
        # Overall score
        overall_score = (skill_match * 0.6) + (resume_score * 0.4)
        
        # Improvement suggestions
        suggestions = []
        missing_skills = set([s.lower() for s in required_skills]) - set([s.lower() for s in student_skills])
        if missing_skills:
            suggestions.append(f"Consider adding these skills: {', '.join(list(missing_skills)[:5])}")
        
        if skill_match < 50:
            suggestions.append("Your skills don't match well with the requirements. Consider upskilling.")
        
        if not profile.resume_path:
            suggestions.append("Upload a resume to improve your application.")
        
        return jsonify({
            'overall_score': round(overall_score, 2),
            'skill_match': round(skill_match, 2),
            'resume_score': round(resume_score, 2),
            'matched_skills': list(set([s.lower() for s in student_skills]) & set([s.lower() for s in required_skills])),
            'missing_skills': list(missing_skills),
            'suggestions': suggestions
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/screening/<int:opp_id>', methods=['GET'])
@jwt_required()
def screen_applicants(opp_id):
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        
        if user.role not in ['company', 'faculty']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        opportunity = Opportunity.query.get(opp_id)
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        if opportunity.company.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        applications = Application.query.filter_by(opportunity_id=opp_id).all()
        required_skills = json.loads(opportunity.required_skills) if opportunity.required_skills else []
        
        scored_applications = []
        for app in applications:
            student = app.student
            student_skills = json.loads(student.skills) if student.skills else []
            
            skill_match = calculate_skill_match(student_skills, required_skills)
            
            # Update application scores if not set
            if app.skill_match_percentage is None:
                app.skill_match_percentage = skill_match
                app.ai_score = skill_match
                db.session.commit()
            
            scored_applications.append({
                'application': app.to_dict(),
                'student_profile': student.to_dict(),
                'skill_match': round(skill_match, 2),
                'matched_skills': list(set([s.lower() for s in student_skills]) & set([s.lower() for s in required_skills])),
                'missing_skills': list(set([s.lower() for s in required_skills]) - set([s.lower() for s in student_skills]))
            })
        
        # Sort by score
        scored_applications.sort(key=lambda x: x['skill_match'], reverse=True)
        
        return jsonify(scored_applications), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

