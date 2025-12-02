import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { companyService } from '../../services/companyService';
import { useAuth } from '../../context/AuthContext';
import { ToastContainer, ToastType } from '../../components/Toast';
import { 
  FiSave, 
  FiSend, 
  FiCalendar,
  FiX,
  FiPlus,
  FiBriefcase,
  FiUsers,
  FiFileText
} from 'react-icons/fi';
import './CreateInternship.css';

interface InternshipFormData {
  // Basic Info
  title: string;
  company_name: string;
  domain: string;
  industry_type: string;
  job_category: string;
  
  // Requirements
  required_skills: string[];
  preferred_skills: string[];
  experience_level: string;
  eligibility_criteria: {
    branch?: string;
    year?: string;
    cgpa?: string;
    other?: string;
  };
  
  // Job Details
  work_type: 'remote' | 'hybrid' | 'onsite';
  duration: string;
  start_date: string;
  end_date: string;
  stipend: string;
  working_hours: string;
  location: {
    country: string;
    state: string;
    city: string;
  };
  
  // Description
  description: string;
  responsibilities: string;
  perks_benefits: string;
  
  // Contact
  hr_name: string;
  hr_email: string;
  hr_phone: string;
  
  // Posting Options
  status: 'draft' | 'published' | 'scheduled';
  application_deadline: string;
  scheduled_date?: string;
}

const CreateInternship: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const { profile } = useAuth();
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);
  const [toasts, setToasts] = useState<Array<{ id: string; message: string; type: ToastType }>>([]);
  const [activeSection, setActiveSection] = useState('basic');
  const [skillInput, setSkillInput] = useState('');
  const [preferredSkillInput, setPreferredSkillInput] = useState('');

  // Get company name from profile
  const getCompanyName = () => {
    if (!profile) return '';
    if ('name' in profile) return (profile as any).name;
    return '';
  };

  const [formData, setFormData] = useState<InternshipFormData>({
    title: '',
    company_name: getCompanyName(),
    domain: '',
    industry_type: '',
    job_category: '',
    required_skills: [],
    preferred_skills: [],
    experience_level: '',
    eligibility_criteria: {},
    work_type: 'remote',
    duration: '',
    start_date: '',
    end_date: '',
    stipend: '',
    working_hours: '',
    location: {
      country: 'India',
      state: '',
      city: '',
    },
    description: '',
    responsibilities: '',
    perks_benefits: '',
    hr_name: '',
    hr_email: '',
    hr_phone: '',
    status: 'draft',
    application_deadline: '',
  });

  useEffect(() => {
    if (id) {
      loadOpportunity();
    }
  }, [id]);

  const loadOpportunity = async () => {
    try {
      const opportunities = await companyService.getOpportunities();
      const opp = opportunities.find((o: any) => o.id === parseInt(id!));
      if (opp) {
        setFormData({
          title: opp.title || '',
          company_name: opp.company_name || formData.company_name,
          domain: opp.domain || '',
          industry_type: '',
          job_category: '',
          required_skills: opp.required_skills || [],
          preferred_skills: [],
          experience_level: '',
          eligibility_criteria: {},
          work_type: opp.work_type || 'remote',
          duration: opp.duration || '',
          start_date: opp.start_date || '',
          end_date: '',
          stipend: opp.stipend || '',
          working_hours: '',
          location: {
            country: 'India',
            state: '',
            city: opp.location || '',
          },
          description: opp.description || '',
          responsibilities: '',
          perks_benefits: '',
          hr_name: '',
          hr_email: '',
          hr_phone: '',
          status: opp.is_active ? 'published' : 'draft',
          application_deadline: opp.application_deadline || '',
        });
      }
    } catch (error) {
      addToast('Failed to load opportunity', 'error');
    }
  };

  const addToast = (message: string, type: ToastType = 'info') => {
    const toastId = Date.now().toString();
    setToasts((prev) => [...prev, { id: toastId, message, type }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const addSkill = (skill: string, type: 'required' | 'preferred') => {
    const trimmed = skill.trim();
    if (!trimmed) return;

    if (type === 'required') {
      if (!formData.required_skills.includes(trimmed)) {
        setFormData({
          ...formData,
          required_skills: [...formData.required_skills, trimmed],
        });
        setSkillInput('');
      }
    } else {
      if (!formData.preferred_skills.includes(trimmed)) {
        setFormData({
          ...formData,
          preferred_skills: [...formData.preferred_skills, trimmed],
        });
        setPreferredSkillInput('');
      }
    }
  };

  const removeSkill = (skill: string, type: 'required' | 'preferred') => {
    if (type === 'required') {
      setFormData({
        ...formData,
        required_skills: formData.required_skills.filter((s) => s !== skill),
      });
    } else {
      setFormData({
        ...formData,
        preferred_skills: formData.preferred_skills.filter((s) => s !== skill),
      });
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    if (name.startsWith('location.')) {
      const field = name.split('.')[1];
      setFormData({
        ...formData,
        location: {
          ...formData.location,
          [field]: value,
        },
      });
    } else if (name.startsWith('eligibility_criteria.')) {
      const field = name.split('.')[1];
      setFormData({
        ...formData,
        eligibility_criteria: {
          ...formData.eligibility_criteria,
          [field]: value,
        },
      });
    } else {
      setFormData({
        ...formData,
        [name]: value,
      });
    }
  };

  const validateForm = (): boolean => {
    if (!formData.title || !formData.domain || !formData.description) {
      addToast('Please fill in all required fields', 'error');
      return false;
    }
    if (formData.required_skills.length === 0) {
      addToast('Please add at least one required skill', 'error');
      return false;
    }
    return true;
  };

  const handleSave = async (status: 'draft' | 'published') => {
    if (status === 'published' && !validateForm()) {
      return;
    }

    setSaving(true);
    try {
      const opportunityData: any = {
        title: formData.title,
        description: formData.description,
        domain: formData.domain,
        required_skills: formData.required_skills,
        duration: formData.duration,
        stipend: formData.stipend,
        location: `${formData.location.city}, ${formData.location.state}, ${formData.location.country}`.replace(/^,\s*/, ''),
        work_type: formData.work_type,
        application_deadline: formData.application_deadline || null,
        start_date: formData.start_date || null,
        prerequisites: formData.responsibilities || '',
        is_active: status === 'published',
      };

      if (id) {
        await companyService.updateOpportunity(parseInt(id), opportunityData);
        addToast('Internship updated successfully!', 'success');
      } else {
        await companyService.createOpportunity(opportunityData);
        addToast('Internship created successfully!', 'success');
      }

      setTimeout(() => {
        navigate('/company/opportunities');
      }, 1500);
    } catch (error: any) {
      addToast(error.response?.data?.error || 'Failed to save internship', 'error');
    } finally {
      setSaving(false);
    }
  };

  const sections = [
    { id: 'basic', label: 'Basic Info', icon: FiBriefcase },
    { id: 'requirements', label: 'Requirements', icon: FiUsers },
    { id: 'details', label: 'Job Details', icon: FiFileText },
    { id: 'description', label: 'Description', icon: FiFileText },
    { id: 'contact', label: 'Contact', icon: FiUsers },
    { id: 'options', label: 'Options', icon: FiCalendar },
  ];

  return (
    <div className="create-internship-page">
      <ToastContainer toasts={toasts} removeToast={removeToast} />

      <div className="internship-header">
        <div>
          <h1>{id ? 'Edit Internship' : 'Create New Internship'}</h1>
          <p>Fill in the details to post your internship opportunity</p>
        </div>
        <div className="header-actions">
          <button
            className="btn btn-secondary"
            onClick={() => navigate('/company/opportunities')}
          >
            Cancel
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => handleSave('draft')}
            disabled={saving}
          >
            <FiSave size={18} />
            Save Draft
          </button>
          <button
            className="btn btn-primary"
            onClick={() => handleSave('published')}
            disabled={saving}
          >
            {saving ? (
              <>
                <div className="spinner" />
                {id ? 'Updating...' : 'Publishing...'}
              </>
            ) : (
              <>
                <FiSend size={18} />
                {id ? 'Update' : 'Publish'} Internship
              </>
            )}
          </button>
        </div>
      </div>

      <div className="internship-form-layout">
        {/* Sidebar Navigation */}
        <aside className="form-sidebar">
          {sections.map((section) => {
            const Icon = section.icon;
            return (
              <button
                key={section.id}
                className={`sidebar-item ${activeSection === section.id ? 'active' : ''}`}
                onClick={() => setActiveSection(section.id)}
              >
                <Icon size={18} />
                <span>{section.label}</span>
              </button>
            );
          })}
        </aside>

        {/* Form Content */}
        <div className="form-content">
          <AnimatePresence mode="wait">
            {activeSection === 'basic' && (
              <BasicInfoSection
                key="basic"
                formData={formData}
                onChange={handleInputChange}
              />
            )}
            {activeSection === 'requirements' && (
              <RequirementsSection
                key="requirements"
                formData={formData}
                onChange={handleInputChange}
                skillInput={skillInput}
                setSkillInput={setSkillInput}
                preferredSkillInput={preferredSkillInput}
                setPreferredSkillInput={setPreferredSkillInput}
                addSkill={addSkill}
                removeSkill={removeSkill}
              />
            )}
            {activeSection === 'details' && (
              <JobDetailsSection
                key="details"
                formData={formData}
                onChange={handleInputChange}
              />
            )}
            {activeSection === 'description' && (
              <DescriptionSection
                key="description"
                formData={formData}
                onChange={handleInputChange}
              />
            )}
            {activeSection === 'contact' && (
              <ContactSection
                key="contact"
                formData={formData}
                onChange={handleInputChange}
              />
            )}
            {activeSection === 'options' && (
              <OptionsSection
                key="options"
                formData={formData}
                onChange={handleInputChange}
              />
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

// Section Components
const BasicInfoSection: React.FC<any> = ({ formData, onChange }) => (
  <motion.div
    className="form-section"
    initial={{ opacity: 0, x: 20 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -20 }}
  >
    <h2>Basic Job Information</h2>
    <div className="form-grid">
      <div className="form-group">
        <label>Job Title <span className="required">*</span></label>
        <input
          type="text"
          name="title"
          value={formData.title}
          onChange={onChange}
          placeholder="e.g., Full Stack Developer Intern"
          required
        />
      </div>
      <div className="form-group">
        <label>Company Name</label>
        <input
          type="text"
          name="company_name"
          value={formData.company_name}
          onChange={onChange}
          disabled
        />
      </div>
      <div className="form-group">
        <label>Domain <span className="required">*</span></label>
        <input
          type="text"
          name="domain"
          value={formData.domain}
          onChange={onChange}
          placeholder="e.g., Software Development"
          required
        />
      </div>
      <div className="form-group">
        <label>Industry Type</label>
        <select name="industry_type" value={formData.industry_type} onChange={onChange}>
          <option value="">Select Industry</option>
          <option value="IT">Information Technology</option>
          <option value="Finance">Finance</option>
          <option value="Healthcare">Healthcare</option>
          <option value="Education">Education</option>
          <option value="Manufacturing">Manufacturing</option>
          <option value="Other">Other</option>
        </select>
      </div>
      <div className="form-group">
        <label>Job Category</label>
        <select name="job_category" value={formData.job_category} onChange={onChange}>
          <option value="">Select Category</option>
          <option value="Internship">Internship</option>
          <option value="Project">Project</option>
          <option value="Part-time">Part-time</option>
          <option value="Full-time">Full-time</option>
        </select>
      </div>
    </div>
  </motion.div>
);

const RequirementsSection: React.FC<any> = ({
  formData,
  onChange,
  skillInput,
  setSkillInput,
  preferredSkillInput,
  setPreferredSkillInput,
  addSkill,
  removeSkill,
}) => (
  <motion.div
    className="form-section"
    initial={{ opacity: 0, x: 20 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -20 }}
  >
    <h2>Job Requirements</h2>
    
    <div className="form-group">
      <label>Required Skills <span className="required">*</span></label>
      <div className="skill-input-wrapper">
        <input
          type="text"
          value={skillInput}
          onChange={(e) => setSkillInput(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              addSkill(skillInput, 'required');
            }
          }}
          placeholder="Type a skill and press Enter"
        />
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={() => addSkill(skillInput, 'required')}
        >
          <FiPlus size={16} />
        </button>
      </div>
      <div className="skills-list">
        {formData.required_skills.map((skill: string) => (
          <motion.span
            key={skill}
            className="skill-tag"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            whileHover={{ scale: 1.05 }}
          >
            {skill}
            <button
              type="button"
              onClick={() => removeSkill(skill, 'required')}
              className="tag-remove"
            >
              <FiX size={14} />
            </button>
          </motion.span>
        ))}
      </div>
    </div>

    <div className="form-group">
      <label>Preferred Skills</label>
      <div className="skill-input-wrapper">
        <input
          type="text"
          value={preferredSkillInput}
          onChange={(e) => setPreferredSkillInput(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              addSkill(preferredSkillInput, 'preferred');
            }
          }}
          placeholder="Type a skill and press Enter"
        />
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={() => addSkill(preferredSkillInput, 'preferred')}
        >
          <FiPlus size={16} />
        </button>
      </div>
      <div className="skills-list">
        {formData.preferred_skills.map((skill: string) => (
          <motion.span
            key={skill}
            className="skill-tag preferred"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            whileHover={{ scale: 1.05 }}
          >
            {skill}
            <button
              type="button"
              onClick={() => removeSkill(skill, 'preferred')}
              className="tag-remove"
            >
              <FiX size={14} />
            </button>
          </motion.span>
        ))}
      </div>
    </div>

    <div className="form-group">
      <label>Experience Level</label>
      <select name="experience_level" value={formData.experience_level} onChange={onChange}>
        <option value="">Select Level</option>
        <option value="Beginner">Beginner</option>
        <option value="Intermediate">Intermediate</option>
        <option value="Advanced">Advanced</option>
      </select>
    </div>

    <div className="form-group">
      <label>Eligibility Criteria</label>
      <div className="form-grid-2">
        <input
          type="text"
          name="eligibility_criteria.branch"
          value={formData.eligibility_criteria.branch || ''}
          onChange={onChange}
          placeholder="Branch (e.g., Computer Science)"
        />
        <input
          type="text"
          name="eligibility_criteria.year"
          value={formData.eligibility_criteria.year || ''}
          onChange={onChange}
          placeholder="Year (e.g., 2nd, 3rd, 4th)"
        />
        <input
          type="text"
          name="eligibility_criteria.cgpa"
          value={formData.eligibility_criteria.cgpa || ''}
          onChange={onChange}
          placeholder="Minimum CGPA (e.g., 7.0)"
        />
        <input
          type="text"
          name="eligibility_criteria.other"
          value={formData.eligibility_criteria.other || ''}
          onChange={onChange}
          placeholder="Other requirements"
        />
      </div>
    </div>
  </motion.div>
);

const JobDetailsSection: React.FC<any> = ({ formData, onChange }) => (
  <motion.div
    className="form-section"
    initial={{ opacity: 0, x: 20 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -20 }}
  >
    <h2>Job Details</h2>
    <div className="form-grid">
      <div className="form-group">
        <label>Internship Type <span className="required">*</span></label>
        <select name="work_type" value={formData.work_type} onChange={onChange} required>
          <option value="remote">Remote</option>
          <option value="hybrid">Hybrid</option>
          <option value="onsite">On-site</option>
        </select>
      </div>
      <div className="form-group">
        <label>Duration</label>
        <input
          type="text"
          name="duration"
          value={formData.duration}
          onChange={onChange}
          placeholder="e.g., 3 months, 6 months"
        />
      </div>
      <div className="form-group">
        <label>Start Date</label>
        <input
          type="date"
          name="start_date"
          value={formData.start_date}
          onChange={onChange}
        />
      </div>
      <div className="form-group">
        <label>End Date</label>
        <input
          type="date"
          name="end_date"
          value={formData.end_date}
          onChange={onChange}
        />
      </div>
      <div className="form-group">
        <label>Stipend / Salary Range</label>
        <input
          type="text"
          name="stipend"
          value={formData.stipend}
          onChange={onChange}
          placeholder="e.g., 15000-20000, Unpaid"
        />
      </div>
      <div className="form-group">
        <label>Working Hours</label>
        <input
          type="text"
          name="working_hours"
          value={formData.working_hours}
          onChange={onChange}
          placeholder="e.g., 40 hours/week"
        />
      </div>
    </div>

    <div className="form-group">
      <label>Location</label>
      <div className="form-grid-3">
        <input
          type="text"
          name="location.country"
          value={formData.location.country}
          onChange={onChange}
          placeholder="Country"
        />
        <input
          type="text"
          name="location.state"
          value={formData.location.state}
          onChange={onChange}
          placeholder="State"
        />
        <input
          type="text"
          name="location.city"
          value={formData.location.city}
          onChange={onChange}
          placeholder="City"
        />
      </div>
    </div>
  </motion.div>
);

const DescriptionSection: React.FC<any> = ({ formData, onChange }) => (
  <motion.div
    className="form-section"
    initial={{ opacity: 0, x: 20 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -20 }}
  >
    <h2>Description</h2>
    <div className="form-group">
      <label>Full Job Description <span className="required">*</span></label>
      <textarea
        name="description"
        value={formData.description}
        onChange={onChange}
        rows={8}
        placeholder="Describe the internship opportunity, what students will learn, company culture, etc."
        required
      />
    </div>
    <div className="form-group">
      <label>Responsibilities</label>
      <textarea
        name="responsibilities"
        value={formData.responsibilities}
        onChange={onChange}
        rows={6}
        placeholder="List the key responsibilities and tasks..."
      />
    </div>
    <div className="form-group">
      <label>Perks & Benefits</label>
      <textarea
        name="perks_benefits"
        value={formData.perks_benefits}
        onChange={onChange}
        rows={6}
        placeholder="List perks, benefits, learning opportunities, etc."
      />
    </div>
  </motion.div>
);

const ContactSection: React.FC<any> = ({ formData, onChange }) => (
  <motion.div
    className="form-section"
    initial={{ opacity: 0, x: 20 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -20 }}
  >
    <h2>Contact Information</h2>
    <div className="form-grid">
      <div className="form-group">
        <label>HR Name</label>
        <input
          type="text"
          name="hr_name"
          value={formData.hr_name}
          onChange={onChange}
          placeholder="Contact person name"
        />
      </div>
      <div className="form-group">
        <label>HR Email</label>
        <input
          type="email"
          name="hr_email"
          value={formData.hr_email}
          onChange={onChange}
          placeholder="hr@company.com"
        />
      </div>
      <div className="form-group">
        <label>HR Phone</label>
        <input
          type="tel"
          name="hr_phone"
          value={formData.hr_phone}
          onChange={onChange}
          placeholder="+91 1234567890"
        />
      </div>
    </div>
  </motion.div>
);

const OptionsSection: React.FC<any> = ({ formData, onChange }) => (
  <motion.div
    className="form-section"
    initial={{ opacity: 0, x: 20 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -20 }}
  >
    <h2>Posting Options</h2>
    <div className="form-group">
      <label>Status</label>
      <select name="status" value={formData.status} onChange={onChange}>
        <option value="draft">Save as Draft</option>
        <option value="published">Publish Immediately</option>
        <option value="scheduled">Schedule Publishing</option>
      </select>
    </div>
    <div className="form-group">
      <label>Application Deadline</label>
      <input
        type="date"
        name="application_deadline"
        value={formData.application_deadline}
        onChange={onChange}
      />
    </div>
    {formData.status === 'scheduled' && (
      <div className="form-group">
        <label>Scheduled Publishing Date</label>
        <input
          type="datetime-local"
          name="scheduled_date"
          value={formData.scheduled_date}
          onChange={onChange}
        />
      </div>
    )}
  </motion.div>
);

export default CreateInternship;

