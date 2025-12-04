"""
External Jobs Fetching Service - Fetches jobs from web APIs and stores them
"""
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from models import db, ExternalJob, ExternalJobSkill, Skill
from skills_matching import SkillsMatchingService
import json
import re


class ExternalJobsService:
    """Service for fetching and storing external jobs"""
    
    # API Configuration (set these in .env)
    JSEARCH_API_KEY = os.getenv('JSEARCH_API_KEY', '')
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '')
    
    @staticmethod
    def extract_skills_from_text(text: str) -> List[str]:
        """
        Extract skills from job description text using keyword matching
        This is a simple approach - can be enhanced with NLP later
        """
        if not text:
            return []
        
        text_lower = text.lower()
        
        # Common tech skills keywords
        skill_keywords = {
            # Programming Languages
            'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin',
            'typescript', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash',
            
            # Web Technologies
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
            'spring', 'laravel', 'rails', 'asp.net', 'jquery', 'bootstrap', 'sass', 'less',
            
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'cassandra',
            'elasticsearch', 'dynamodb', 'firebase',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd',
            'terraform', 'ansible', 'linux', 'nginx', 'apache',
            
            # Mobile
            'android', 'ios', 'react native', 'flutter', 'xamarin',
            
            # Data Science & ML
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'pandas', 'numpy',
            'scikit-learn', 'data science', 'data analysis', 'tableau', 'power bi',
            
            # Other
            'blockchain', 'solidity', 'ethereum', 'graphql', 'rest api', 'microservices',
            'agile', 'scrum', 'devops', 'ui/ux', 'figma', 'adobe', 'photoshop'
        }
        
        found_skills = []
        for skill in skill_keywords:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates
    
    @staticmethod
    def fetch_jobs_from_jsearch(query: str = "internship", location: str = "", 
                                num_pages: int = 1) -> List[Dict]:
        """
        Fetch jobs from JSearch API (RapidAPI)
        Requires JSEARCH_API_KEY in .env
        """
        if not ExternalJobsService.JSEARCH_API_KEY:
            return []
        
        jobs = []
        
        try:
            for page in range(num_pages):
                url = "https://jsearch.p.rapidapi.com/search"
                params = {
                    "query": query,
                    "page": str(page + 1),
                    "num_pages": "1",
                    "date_posted": "month"  # Recent jobs only
                }
                if location:
                    params["location"] = location
                
                headers = {
                    "X-RapidAPI-Key": ExternalJobsService.JSEARCH_API_KEY,
                    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data:
                        jobs.extend(data['data'])
                else:
                    print(f"JSearch API error: {response.status_code}")
                    break
                    
        except Exception as e:
            print(f"Error fetching from JSearch: {e}")
        
        return jobs
    
    @staticmethod
    def process_and_store_job(job_data: Dict, source: str = "jsearch") -> Optional[ExternalJob]:
        """
        Process job data from API and store in database
        """
        try:
            # Extract job details
            title = job_data.get('job_title', '')
            company = job_data.get('employer_name', '')
            description = job_data.get('job_description', '') or job_data.get('job_highlights', {}).get('Qualifications', [''])[0]
            location = job_data.get('job_city', '') + ', ' + job_data.get('job_state', '')
            job_type = job_data.get('job_employment_type', '').lower()
            salary = job_data.get('job_salary_range', '') or job_data.get('job_min_salary', '')
            application_url = job_data.get('job_apply_link', '') or job_data.get('job_google_link', '')
            source_id = job_data.get('job_id', '')
            
            # Parse dates
            posted_date = None
            if 'job_posted_at_datetime_utc' in job_data:
                try:
                    posted_date = datetime.fromisoformat(job_data['job_posted_at_datetime_utc'].replace('Z', '+00:00'))
                except:
                    pass
            
            # Check if job already exists
            existing_job = ExternalJob.query.filter_by(
                source=source,
                source_id=str(source_id)
            ).first()
            
            if existing_job:
                # Update existing job
                existing_job.title = title
                existing_job.company_name = company
                existing_job.description = description
                existing_job.location = location
                existing_job.job_type = job_type
                existing_job.salary_range = str(salary) if salary else None
                existing_job.application_url = application_url
                existing_job.posted_date = posted_date
                existing_job.updated_at = datetime.utcnow()
                db.session.flush()
                
                job = existing_job
            else:
                # Create new job
                job = ExternalJob(
                    title=title,
                    company_name=company,
                    description=description,
                    location=location,
                    job_type=job_type,
                    salary_range=str(salary) if salary else None,
                    application_url=application_url,
                    source=source,
                    source_id=str(source_id),
                    posted_date=posted_date,
                    is_active=True
                )
                db.session.add(job)
                db.session.flush()
            
            # Extract and store skills
            if description:
                skill_names = ExternalJobsService.extract_skills_from_text(description)
                
                # Clear existing skills
                ExternalJobSkill.query.filter_by(external_job_id=job.id).delete()
                
                # Add new skills
                for skill_name in skill_names:
                    skill = SkillsMatchingService.get_or_create_skill(skill_name)
                    job_skill = ExternalJobSkill(
                        external_job_id=job.id,
                        skill_id=skill.id,
                        confidence=0.8  # Medium confidence for keyword matching
                    )
                    db.session.add(job_skill)
            
            db.session.commit()
            return job
            
        except Exception as e:
            db.session.rollback()
            print(f"Error processing job: {e}")
            return None
    
    @staticmethod
    def fetch_and_store_jobs(query: str = "internship", location: str = "", 
                            num_pages: int = 1, source: str = "jsearch") -> Dict:
        """
        Fetch jobs from external API and store in database
        Returns summary of fetched jobs
        """
        if source == "jsearch":
            jobs_data = ExternalJobsService.fetch_jobs_from_jsearch(query, location, num_pages)
        else:
            return {'error': f'Unknown source: {source}'}
        
        processed = 0
        errors = 0
        
        for job_data in jobs_data:
            job = ExternalJobsService.process_and_store_job(job_data, source)
            if job:
                processed += 1
            else:
                errors += 1
        
        return {
            'total_fetched': len(jobs_data),
            'processed': processed,
            'errors': errors,
            'source': source
        }
    
    @staticmethod
    def cleanup_old_jobs(days_old: int = 30):
        """Mark old external jobs as inactive"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        old_jobs = ExternalJob.query.filter(
            ExternalJob.fetched_at < cutoff_date,
            ExternalJob.is_active == True
        ).all()
        
        for job in old_jobs:
            job.is_active = False
        
        db.session.commit()
        
        return len(old_jobs)


# CLI command to fetch jobs
if __name__ == "__main__":
    from app import app
    
    with app.app_context():
        print("Fetching external jobs...")
        result = ExternalJobsService.fetch_and_store_jobs(
            query="internship python react",
            location="",
            num_pages=2
        )
        print(f"Result: {result}")

