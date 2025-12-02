from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import json

# db will be initialized in app.py
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'company', 'faculty', 'admin'
    is_approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    company_profile = db.relationship('CompanyProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_token(self):
        return create_access_token(identity=str(self.id), additional_claims={'role': self.role})
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'is_approved': self.is_approved,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.Text)
    prn_number = db.Column(db.String(50))
    course = db.Column(db.String(150))
    specialization = db.Column(db.String(150))
    gender = db.Column(db.String(20))
    education = db.Column(db.Text)  # JSON string
    skills = db.Column(db.Text)  # JSON array
    interests = db.Column(db.Text)  # JSON array
    resume_path = db.Column(db.String(255))
    profile_picture = db.Column(db.String(255))
    bio = db.Column(db.Text)
    linkedin_url = db.Column(db.String(255))
    github_url = db.Column(db.String(255))
    portfolio_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    applications = db.relationship('Application', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    educations = db.relationship('StudentEducation', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    internships = db.relationship('StudentInternship', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    experiences = db.relationship('StudentExperience', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    projects = db.relationship('StudentProject', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    trainings = db.relationship('StudentTraining', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    certifications = db.relationship('StudentCertification', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    publications = db.relationship('StudentPublication', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    positions = db.relationship('StudentPosition', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    attachments = db.relationship('StudentAttachment', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    offers = db.relationship('StudentOffer', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.user.email if self.user else None,  # Include email from user relationship
            'first_name': self.first_name,
            'last_name': self.last_name,
            'middle_name': self.middle_name,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'address': self.address,
            'prn_number': self.prn_number,
            'course': self.course,
            'specialization': self.specialization,
            'gender': self.gender,
            'education': json.loads(self.education) if self.education else [],
            'skills': json.loads(self.skills) if self.skills else [],
            'interests': json.loads(self.interests) if self.interests else [],
            'resume_path': self.resume_path,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'portfolio_url': self.portfolio_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class StudentEducation(db.Model):
    __tablename__ = 'student_education'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    degree = db.Column(db.String(150), nullable=False)
    institution = db.Column(db.String(255), nullable=False)
    course = db.Column(db.String(150))
    specialization = db.Column(db.String(150))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_current = db.Column(db.Boolean, default=False)
    gpa = db.Column(db.String(20))
    description = db.Column(db.Text)
    achievements = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'degree': self.degree,
            'institution': self.institution,
            'course': self.course,
            'specialization': self.specialization,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_current': self.is_current,
            'gpa': self.gpa,
            'description': self.description,
            'achievements': self.achievements
        }

class StudentExperience(db.Model):
    __tablename__ = 'student_experiences'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    designation = db.Column(db.String(255), nullable=False)
    employment_type = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_current = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(255))
    description = db.Column(db.Text)
    technologies = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'company_name': self.company_name,
            'designation': self.designation,
            'employment_type': self.employment_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_current': self.is_current,
            'location': self.location,
            'description': self.description,
            'technologies': json.loads(self.technologies) if self.technologies else []
        }

class StudentInternship(db.Model):
    __tablename__ = 'student_internships'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    designation = db.Column(db.String(255), nullable=False)
    organization = db.Column(db.String(255), nullable=False)
    industry_sector = db.Column(db.String(150))
    stipend = db.Column(db.String(100))
    internship_type = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_current = db.Column(db.Boolean, default=False)
    country = db.Column(db.String(100))
    state = db.Column(db.String(100))
    city = db.Column(db.String(100))
    mentor_name = db.Column(db.String(150))
    mentor_contact = db.Column(db.String(100))
    mentor_designation = db.Column(db.String(150))
    description = db.Column(db.Text)
    technologies = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'designation': self.designation,
            'organization': self.organization,
            'industry_sector': self.industry_sector,
            'stipend': self.stipend,
            'internship_type': self.internship_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_current': self.is_current,
            'country': self.country,
            'state': self.state,
            'city': self.city,
            'mentor_name': self.mentor_name,
            'mentor_contact': self.mentor_contact,
            'mentor_designation': self.mentor_designation,
            'description': self.description,
            'technologies': json.loads(self.technologies) if self.technologies else []
        }

class StudentProject(db.Model):
    __tablename__ = 'student_projects'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    organization = db.Column(db.String(255))
    role = db.Column(db.String(150))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)
    technologies = db.Column(db.Text)
    links = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'title': self.title,
            'organization': self.organization,
            'role': self.role,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'description': self.description,
            'technologies': json.loads(self.technologies) if self.technologies else [],
            'links': json.loads(self.links) if self.links else []
        }

class StudentTraining(db.Model):
    __tablename__ = 'student_trainings'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    provider = db.Column(db.String(255))
    mode = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'title': self.title,
            'provider': self.provider,
            'mode': self.mode,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'description': self.description
        }

class StudentCertification(db.Model):
    __tablename__ = 'student_certifications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    issuer = db.Column(db.String(255))
    issue_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    credential_id = db.Column(db.String(150))
    credential_url = db.Column(db.String(255))
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'issuer': self.issuer,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'credential_id': self.credential_id,
            'credential_url': self.credential_url,
            'description': self.description
        }

class StudentPublication(db.Model):
    __tablename__ = 'student_publications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    publication_type = db.Column(db.String(150))
    publisher = db.Column(db.String(255))
    publication_date = db.Column(db.Date)
    url = db.Column(db.String(255))
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'title': self.title,
            'publication_type': self.publication_type,
            'publisher': self.publisher,
            'publication_date': self.publication_date.isoformat() if self.publication_date else None,
            'url': self.url,
            'description': self.description
        }

class StudentPosition(db.Model):
    __tablename__ = 'student_positions'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    organization = db.Column(db.String(255))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'title': self.title,
            'organization': self.organization,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_current': self.is_current,
            'description': self.description
        }

class StudentAttachment(db.Model):
    __tablename__ = 'student_attachments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    attachment_type = db.Column(db.String(100))  # resume, transcript, offer_letter, etc.

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'title': self.title,
            'file_path': self.file_path,
            'attachment_type': self.attachment_type
        }

class StudentOffer(db.Model):
    __tablename__ = 'student_offers'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255))
    ctc = db.Column(db.String(100))
    status = db.Column(db.String(50), default='pending')  # pending, accepted, declined
    offer_date = db.Column(db.Date)
    joining_date = db.Column(db.Date)
    location = db.Column(db.String(255))
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'company_name': self.company_name,
            'role': self.role,
            'ctc': self.ctc,
            'status': self.status,
            'offer_date': self.offer_date.isoformat() if self.offer_date else None,
            'joining_date': self.joining_date.isoformat() if self.joining_date else None,
            'location': self.location,
            'notes': self.notes
        }

class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    website = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    industry = db.Column(db.String(100))
    company_size = db.Column(db.String(50))
    logo_path = db.Column(db.String(255))
    is_faculty = db.Column(db.Boolean, default=False)
    faculty_department = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    opportunities = db.relationship('Opportunity', backref='company', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'website': self.website,
            'phone': self.phone,
            'address': self.address,
            'industry': self.industry,
            'company_size': self.company_size,
            'logo_path': self.logo_path,
            'is_faculty': self.is_faculty,
            'faculty_department': self.faculty_department,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Opportunity(db.Model):
    __tablename__ = 'opportunities'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    domain = db.Column(db.String(100), nullable=False)
    required_skills = db.Column(db.Text)  # JSON array
    duration = db.Column(db.String(50))  # e.g., "3 months", "6 months"
    stipend = db.Column(db.String(100))  # e.g., "5000-10000", "Unpaid"
    location = db.Column(db.String(200))  # e.g., "Remote", "Pune, Maharashtra"
    work_type = db.Column(db.String(20))  # 'remote', 'onsite', 'hybrid'
    prerequisites = db.Column(db.Text)
    application_deadline = db.Column(db.Date)
    start_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    applications_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    applications = db.relationship('Application', backref='opportunity', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'title': self.title,
            'description': self.description,
            'domain': self.domain,
            'required_skills': json.loads(self.required_skills) if self.required_skills else [],
            'duration': self.duration,
            'stipend': self.stipend,
            'location': self.location,
            'work_type': self.work_type,
            'prerequisites': self.prerequisites,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'is_active': self.is_active,
            'is_approved': self.is_approved,
            'views_count': self.views_count,
            'applications_count': self.applications_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'), nullable=False)
    resume_path = db.Column(db.String(255))
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'shortlisted', 'rejected', 'interview', 'accepted', 'withdrawn'
    ai_score = db.Column(db.Float)  # AI matching score
    skill_match_percentage = db.Column(db.Float)
    notes = db.Column(db.Text)  # Internal notes from recruiter
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'opportunity_id', name='unique_application'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': f"{self.student.first_name} {self.student.last_name}" if self.student else None,
            'opportunity_id': self.opportunity_id,
            'opportunity_title': self.opportunity.title if self.opportunity else None,
            'resume_path': self.resume_path,
            'cover_letter': self.cover_letter,
            'status': self.status,
            'ai_score': self.ai_score,
            'skill_match_percentage': self.skill_match_percentage,
            'notes': self.notes,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None
        }

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    message_type = db.Column(db.String(20), default='message')  # 'message', 'interview_invite', 'status_update'
    related_application_id = db.Column(db.Integer, db.ForeignKey('applications.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'sender_email': self.sender.email if self.sender else None,
            'receiver_id': self.receiver_id,
            'receiver_email': self.receiver.email if self.receiver else None,
            'subject': self.subject,
            'content': self.content,
            'is_read': self.is_read,
            'message_type': self.message_type,
            'related_application_id': self.related_application_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))  # 'new_opportunity', 'application_status', 'message', 'deadline_reminder'
    related_id = db.Column(db.Integer)  # ID of related opportunity, application, etc.
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'related_id': self.related_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Blacklist(db.Model):
    __tablename__ = 'blacklist'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

