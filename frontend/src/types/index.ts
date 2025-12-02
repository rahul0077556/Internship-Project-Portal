export interface User {
  id: number;
  email: string;
  role: 'student' | 'company' | 'faculty' | 'admin';
  is_approved: boolean;
  is_active: boolean;
  created_at?: string;
}

export interface StudentProfile {
  id: number;
  user_id: number;
  first_name: string;
  last_name: string;
  email?: string;
  middle_name?: string;
  phone?: string;
  date_of_birth?: string;
  address?: string;
  prn_number?: string;
  course?: string;
  specialization?: string;
  gender?: string;
  education: Education[];
  skills: string[];
  interests: string[];
  resume_path?: string;
  profile_picture?: string;
  bio?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
}

export interface Education {
  id?: number;
  student_id?: number;
  degree: string;
  institution: string;
  course?: string;
  specialization?: string;
  start_date?: string;
  end_date?: string;
  is_current?: boolean;
  gpa?: string;
  description?: string;
  achievements?: string;
}

export interface CompanyProfile {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  website?: string;
  phone?: string;
  address?: string;
  industry?: string;
  company_size?: string;
  logo_path?: string;
  is_faculty: boolean;
  faculty_department?: string;
}

export interface Opportunity {
  id: number;
  company_id: number;
  company_name?: string;
  title: string;
  description: string;
  domain: string;
  required_skills: string[];
  duration: string;
  stipend: string;
  location: string;
  work_type: 'remote' | 'onsite' | 'hybrid';
  prerequisites?: string;
  application_deadline?: string;
  start_date?: string;
  is_active: boolean;
  is_approved: boolean;
  views_count: number;
  applications_count: number;
  created_at?: string;
  has_applied?: boolean;
}

export interface Application {
  id: number;
  student_id: number;
  student_name?: string;
  opportunity_id: number;
  opportunity_title?: string;
  resume_path?: string;
  cover_letter?: string;
  status: 'pending' | 'shortlisted' | 'rejected' | 'interview' | 'accepted' | 'withdrawn';
  ai_score?: number;
  skill_match_percentage?: number;
  notes?: string;
  applied_at?: string;
  student_profile?: StudentProfile;
}

export interface Message {
  id: number;
  sender_id: number;
  sender_email?: string;
  receiver_id: number;
  receiver_email?: string;
  subject?: string;
  content: string;
  is_read: boolean;
  message_type: 'message' | 'interview_invite' | 'status_update';
  related_application_id?: number;
  created_at?: string;
  middle_name?: string;
  prn_number?: string;
  course?: string;
  specialization?: string;
  gender?: string;
}

export interface Notification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  notification_type: 'new_opportunity' | 'application_status' | 'message' | 'deadline_reminder' | 'new_application';
  related_id?: number;
  is_read: boolean;
  created_at?: string;
}

export interface AIRecommendation {
  opportunity: Opportunity;
  score: number;
  skill_match: number;
  matched_skills: string[];
}

export interface ResumeScore {
  overall_score: number;
  skill_match: number;
  resume_score: number;
  matched_skills: string[];
  missing_skills: string[];
  suggestions: string[];
}

export interface StudentAttachment {
  id: number;
  student_id: number;
  title: string;
  file_path: string;
  attachment_type?: string;
}

export interface StudentFullProfileResponse {
  profile: StudentProfile;
  sections: Record<string, any[]>;
  resume_path?: string;
  stats?: Record<string, number>;
}

export interface JobOpportunityCard {
  id: number;
  title: string;
  company?: string | null;
  job_type?: string;
  ctc?: string;
  location?: string;
  tags: string[];
  eligible: boolean;
  match: number;
  status: string;
  applied: boolean;
  application_status?: string | null;
  application_id?: number | null;
  posted_on?: string | null;
}

export interface JobApplicationCard {
  id: number;
  title: string;
  company?: string | null;
  location?: string | null;
  status: string;
  job_type?: string | null;
  ctc?: string | null;
  submitted_on?: string | null;
  tags: string[];
}

export interface JobOfferCard {
  id: number;
  company_name: string;
  role?: string;
  ctc?: string;
  status: string;
  offer_date?: string | null;
  joining_date?: string | null;
  location?: string | null;
  notes?: string | null;
}

export interface JobsSummary {
  opportunities: JobOpportunityCard[];
  applications: JobApplicationCard[];
  offers: JobOfferCard[];
  stats: {
    eligible: number;
    applications: number;
    offers: number;
    opportunities: number;
  };
  popular_tags: { tag: string; count: number }[];
}

export interface StudentOffer {
  id: number;
  company_name: string;
  role?: string;
  ctc?: string;
  status: string;
  offer_date?: string;
  joining_date?: string;
  location?: string;
  notes?: string;
}

export interface FacultyDashboardResponse {
  stats: {
    total_students: number;
    placed_students: number;
    unplaced_students: number;
    total_internships: number;
    highest_package_lpa: number;
    average_package_lpa: number;
    total_companies: number;
  };
  charts: {
    company_wise: Array<{ company: string; placed: number }>;
    branch_wise: Array<{ branch: string; placed: number; total: number; percentage: number }>;
    package_distribution: Array<{ range: string; count: number }>;
    batch_trends: Array<{ year: string; placed: number }>;
  };
}

export interface PlacementRow {
  student_name: string;
  prn?: string | null;
  branch?: string | null;
  company?: string | null;
  ctc?: string | null;
  ctc_lpa?: number | null;
  role?: string | null;
  location?: string | null;
  joining_date?: string | null;
  offer_date?: string | null;
  ppo?: boolean;
}

export interface PlacementFilters {
  branch?: string;
  company?: string;
  min_ctc?: number;
  max_ctc?: number;
}

export interface InternshipRow {
  student_name: string;
  branch?: string | null;
  organization: string;
  designation: string;
  domain?: string | null;
  stipend?: string | null;
  internship_type?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  is_paid: boolean;
  technologies?: string[];
}

export interface FacultyReportPayload {
  generated_at: string;
  report_type: string;
  summary: Record<string, any>;
  table: Array<Record<string, any>>;
}

