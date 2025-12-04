"""
Skills Matching Service - Real-time accurate skills matching algorithm
"""
from models import (
    db, StudentProfile, Opportunity, ExternalJob,
    Skill, StudentSkill, OpportunitySkill, ExternalJobSkill
)
from typing import List, Dict, Tuple, Optional
from sqlalchemy import func, and_, or_


class SkillsMatchingService:
    """Service for matching student skills with jobs"""
    
    @staticmethod
    def normalize_skill_name(skill_name: str) -> str:
        """Normalize skill name for matching"""
        if not skill_name:
            return ""
        # Convert to lowercase, strip spaces, handle common variations
        normalized = skill_name.lower().strip()
        # Handle common variations
        variations = {
            'js': 'javascript',
            'reactjs': 'react',
            'react.js': 'react',
            'nodejs': 'node.js',
            'node.js': 'node.js',
            'html5': 'html',
            'css3': 'css',
            'mongodb': 'mongo',
            'postgresql': 'postgres',
            'postgres': 'postgres',
            'aws': 'amazon web services',
        }
        return variations.get(normalized, normalized)
    
    @staticmethod
    def get_or_create_skill(skill_name: str, category: str = None) -> Skill:
        """Get existing skill or create new one"""
        normalized = SkillsMatchingService.normalize_skill_name(skill_name)
        
        # Try to find by normalized name first
        skill = Skill.query.filter_by(normalized_name=normalized).first()
        
        if not skill:
            # Try to find by exact name
            skill = Skill.query.filter(func.lower(Skill.name) == normalized).first()
        
        if not skill:
            # Create new skill
            skill = Skill(name=skill_name, category=category)
            db.session.add(skill)
            db.session.flush()  # Get the ID without committing
        
        return skill
    
    @staticmethod
    def update_student_skills(student_id: int, skill_names: List[str], 
                             proficiency_levels: Dict[str, str] = None) -> List[StudentSkill]:
        """Update student skills from list of skill names"""
        # Clear existing skills
        StudentSkill.query.filter_by(student_id=student_id).delete()
        
        student_skills = []
        proficiency_levels = proficiency_levels or {}
        
        for skill_name in skill_names:
            if not skill_name or not skill_name.strip():
                continue
            
            skill = SkillsMatchingService.get_or_create_skill(skill_name.strip())
            proficiency = proficiency_levels.get(skill_name, 'intermediate')
            
            student_skill = StudentSkill(
                student_id=student_id,
                skill_id=skill.id,
                proficiency_level=proficiency
            )
            db.session.add(student_skill)
            student_skills.append(student_skill)
        
        db.session.commit()
        return student_skills
    
    @staticmethod
    def update_opportunity_skills(opportunity_id: int, skill_names: List[str],
                                 required_skills: List[str] = None) -> List[OpportunitySkill]:
        """Update opportunity required skills"""
        # Clear existing skills
        OpportunitySkill.query.filter_by(opportunity_id=opportunity_id).delete()
        
        opportunity_skills = []
        required_set = set(required_skills or skill_names)
        
        for skill_name in skill_names:
            if not skill_name or not skill_name.strip():
                continue
            
            skill = SkillsMatchingService.get_or_create_skill(skill_name.strip())
            is_required = skill_name in required_set
            
            opp_skill = OpportunitySkill(
                opportunity_id=opportunity_id,
                skill_id=skill.id,
                is_required=is_required,
                priority=1 if is_required else 0
            )
            db.session.add(opp_skill)
            opportunity_skills.append(opp_skill)
        
        db.session.commit()
        return opportunity_skills
    
    @staticmethod
    def calculate_match_score(student_id: int, opportunity_id: int) -> Dict:
        """
        Calculate real-time match score between student and opportunity
        
        Returns:
            {
                'match_percentage': float,
                'matched_skills': List[str],
                'missing_skills': List[str],
                'total_required': int,
                'matched_count': int,
                'preferred_skills_matched': int,
                'total_preferred': int
            }
        """
        # Get student skills
        student_skills_query = db.session.query(StudentSkill.skill_id).filter_by(student_id=student_id)
        student_skill_ids = [row[0] for row in student_skills_query.all()]
        
        if not student_skill_ids:
            return {
                'match_percentage': 0.0,
                'matched_skills': [],
                'missing_skills': [],
                'total_required': 0,
                'matched_count': 0,
                'preferred_skills_matched': 0,
                'total_preferred': 0
            }
        
        # Get opportunity skills (required and preferred separately)
        opp_skills = OpportunitySkill.query.filter_by(opportunity_id=opportunity_id).all()
        
        required_skills = [os for os in opp_skills if os.is_required]
        preferred_skills = [os for os in opp_skills if not os.is_required]
        
        # Count matches
        matched_required = [os for os in required_skills if os.skill_id in student_skill_ids]
        matched_preferred = [os for os in preferred_skills if os.skill_id in student_skill_ids]
        
        total_required = len(required_skills)
        matched_count = len(matched_required)
        preferred_matched = len(matched_preferred)
        total_preferred = len(preferred_skills)
        
        # Calculate match percentage
        # Weight: Required skills = 80%, Preferred skills = 20%
        if total_required > 0:
            required_score = (matched_count / total_required) * 0.8
            preferred_score = (preferred_matched / total_preferred * 0.2) if total_preferred > 0 else 0
            match_percentage = (required_score + preferred_score) * 100
        else:
            # If no required skills, base on preferred only
            match_percentage = (preferred_matched / total_preferred * 100) if total_preferred > 0 else 0
        
        # Get skill names
        matched_skill_names = [
            os.skill.name for os in matched_required + matched_preferred
        ]
        
        missing_skill_names = [
            os.skill.name for os in required_skills if os.skill_id not in student_skill_ids
        ]
        
        return {
            'match_percentage': round(match_percentage, 2),
            'matched_skills': matched_skill_names,
            'missing_skills': missing_skill_names,
            'total_required': total_required,
            'matched_count': matched_count,
            'preferred_skills_matched': preferred_matched,
            'total_preferred': total_preferred
        }
    
    @staticmethod
    def calculate_external_job_match(student_id: int, external_job_id: int) -> Dict:
        """Calculate match score for external job"""
        # Get student skills
        student_skills_query = db.session.query(StudentSkill.skill_id).filter_by(student_id=student_id)
        student_skill_ids = [row[0] for row in student_skills_query.all()]
        
        if not student_skill_ids:
            return {
                'match_percentage': 0.0,
                'matched_skills': [],
                'missing_skills': [],
                'total_required': 0,
                'matched_count': 0
            }
        
        # Get external job skills
        job_skills = ExternalJobSkill.query.filter_by(external_job_id=external_job_id).all()
        
        if not job_skills:
            return {
                'match_percentage': 0.0,
                'matched_skills': [],
                'missing_skills': [],
                'total_required': 0,
                'matched_count': 0
            }
        
        # Count matches
        matched = [js for js in job_skills if js.skill_id in student_skill_ids]
        total_required = len(job_skills)
        matched_count = len(matched)
        
        # Calculate match percentage
        match_percentage = (matched_count / total_required * 100) if total_required > 0 else 0
        
        # Get skill names
        matched_skill_names = [js.skill.name for js in matched]
        missing_skill_names = [
            js.skill.name for js in job_skills if js.skill_id not in student_skill_ids
        ]
        
        return {
            'match_percentage': round(match_percentage, 2),
            'matched_skills': matched_skill_names,
            'missing_skills': missing_skill_names,
            'total_required': total_required,
            'matched_count': matched_count
        }
    
    @staticmethod
    def get_matched_opportunities(student_id: int, limit: int = 50, min_match: float = 0.0) -> List[Dict]:
        """
        Get all opportunities matched with student, sorted by match score
        
        Returns list of opportunities with match details
        """
        # Get all active, approved opportunities
        opportunities = Opportunity.query.filter_by(
            is_active=True,
            is_approved=True
        ).all()
        
        matched_opportunities = []
        
        for opp in opportunities:
            match_data = SkillsMatchingService.calculate_match_score(student_id, opp.id)
            
            if match_data['match_percentage'] >= min_match:
                opp_dict = opp.to_dict()
                opp_dict['match_data'] = match_data
                matched_opportunities.append(opp_dict)
        
        # Sort by match percentage (descending)
        matched_opportunities.sort(key=lambda x: x['match_data']['match_percentage'], reverse=True)
        
        return matched_opportunities[:limit]
    
    @staticmethod
    def get_matched_external_jobs(student_id: int, limit: int = 50, min_match: float = 0.0) -> List[Dict]:
        """Get all external jobs matched with student"""
        external_jobs = ExternalJob.query.filter_by(is_active=True).all()
        
        matched_jobs = []
        
        for job in external_jobs:
            match_data = SkillsMatchingService.calculate_external_job_match(student_id, job.id)
            
            if match_data['match_percentage'] >= min_match:
                job_dict = job.to_dict()
                job_dict['match_data'] = match_data
                matched_jobs.append(job_dict)
        
        # Sort by match percentage (descending)
        matched_jobs.sort(key=lambda x: x['match_data']['match_percentage'], reverse=True)
        
        return matched_jobs[:limit]
    
    @staticmethod
    def get_matching_students(opportunity_id: int, limit: int = 50, min_match: float = 0.0) -> List[Dict]:
        """Get all students matched with an opportunity (for companies)"""
        students = StudentProfile.query.all()
        
        matched_students = []
        
        for student in students:
            match_data = SkillsMatchingService.calculate_match_score(student.id, opportunity_id)
            
            if match_data['match_percentage'] >= min_match:
                student_dict = {
                    'id': student.id,
                    'name': f"{student.first_name} {student.last_name}",
                    'email': student.user.email if student.user else None,
                    'course': student.course,
                    'specialization': student.specialization,
                    'match_data': match_data
                }
                matched_students.append(student_dict)
        
        # Sort by match percentage (descending)
        matched_students.sort(key=lambda x: x['match_data']['match_percentage'], reverse=True)
        
        return matched_students[:limit]

