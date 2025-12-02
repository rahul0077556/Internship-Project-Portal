import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { JobOpportunityCard } from '../types';
import { studentService } from '../services/studentService';
import { FiX, FiFileText, FiTrendingUp, FiCheckCircle } from 'react-icons/fi';
import './ApplicationModal.css';

interface ApplicationModalProps {
  opportunity: JobOpportunityCard;
  onClose: () => void;
  onSubmit: (coverLetter: string) => Promise<void>;
}

const ApplicationModal: React.FC<ApplicationModalProps> = ({
  opportunity,
  onClose,
  onSubmit,
}) => {
  const [coverLetter, setCoverLetter] = useState('');
  const [profileComplete, setProfileComplete] = useState(0);
  const [skillMatch, setSkillMatch] = useState(opportunity.match || 0);
  const [loading, setLoading] = useState(false);
  const [resumePath, setResumePath] = useState<string | null>(null);

  useEffect(() => {
    loadProfileData();
  }, []);

  const calculateSkillMatch = (studentSkills: string[], requiredTags: string[]): number => {
    if (!requiredTags || requiredTags.length === 0) return 100;
    if (!studentSkills || studentSkills.length === 0) return 0;
    
    const studentSkillsLower = studentSkills.map(s => s.toLowerCase().trim());
    const requiredTagsLower = requiredTags.map(t => t.toLowerCase().trim());
    
    const matched = requiredTagsLower.filter(tag => 
      studentSkillsLower.some(skill => 
        skill.includes(tag) || tag.includes(skill)
      )
    ).length;
    
    return Math.round((matched / requiredTags.length) * 100);
  };

  const loadProfileData = async () => {
    try {
      const profile = await studentService.getProfile();
      // Calculate profile completeness (more lenient)
      let complete = 0;
      const fields = {
        name: (profile.first_name && profile.last_name) ? 15 : 0,
        email: profile.email ? 5 : 0,
        phone: profile.phone ? 10 : 0,
        date_of_birth: profile.date_of_birth ? 5 : 0,
        course: profile.course ? 10 : 0,
        skills: (profile.skills && profile.skills.length > 0) ? 15 : 0,
        education: (profile.education && profile.education.length > 0) ? 10 : 0,
        resume_path: profile.resume_path ? 20 : 0,
        bio: profile.bio ? 5 : 0,
        address: profile.address ? 5 : 0,
      };
      complete = Object.values(fields).reduce((sum, val) => sum + val, 0);
      setProfileComplete(complete);
      setResumePath(profile.resume_path || null);
      
      // Calculate skill match if not provided
      if (!opportunity.match && opportunity.tags && profile.skills) {
        const match = calculateSkillMatch(profile.skills, opportunity.tags);
        setSkillMatch(match);
      }
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (profileComplete < 60) {
      alert('Please complete at least 60% of your profile before applying. Update your profile to increase your chances.');
      return;
    }
    if (!resumePath) {
      const confirm = window.confirm('You haven\'t uploaded a resume. It\'s highly recommended to upload one. Do you want to continue anyway?');
      if (!confirm) return;
    }
    setLoading(true);
    try {
      await onSubmit(coverLetter);
    } finally {
      setLoading(false);
    }
  };

  const canApply = profileComplete >= 60;

  return (
    <AnimatePresence>
      <motion.div
        className="modal-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="modal-content"
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="modal-header">
            <div>
              <h2>Apply for Position</h2>
              <p className="modal-subtitle">{opportunity.title} at {opportunity.company || 'Company'}</p>
            </div>
            <button
              className="modal-close"
              onClick={onClose}
              aria-label="Close modal"
            >
              <FiX size={24} />
            </button>
          </div>

          {/* Profile Completeness Check */}
          <div className="profile-check">
            <div className="profile-check-header">
              <h3>Profile Completeness</h3>
              <span className={`completeness-badge ${canApply ? 'complete' : 'incomplete'}`}>
                {profileComplete}%
              </span>
            </div>
            <div className="progress-bar">
              <motion.div
                className="progress-fill"
                initial={{ width: 0 }}
                animate={{ width: `${profileComplete}%` }}
                transition={{ duration: 0.5 }}
                style={{
                  background: canApply
                    ? 'linear-gradient(90deg, var(--success) 0%, #10b981 100%)'
                    : 'linear-gradient(90deg, var(--warning) 0%, #f59e0b 100%)',
                }}
              />
            </div>
            {!canApply && (
              <p className="profile-warning">
                Complete at least 60% of your profile to apply. 
                <a href="/student/profile"> Update Profile</a>
              </p>
            )}
            {canApply && profileComplete < 80 && (
              <p className="profile-info" style={{ color: '#f59e0b', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                💡 Tip: Completing more of your profile (aim for 80%+) increases your chances of being selected.
              </p>
            )}
          </div>

          {/* Skill Match */}
          <div className="skill-match">
            <div className="skill-match-header">
              <FiTrendingUp size={20} />
              <span>Skill Match</span>
              <span className="match-percentage">{skillMatch}%</span>
            </div>
            <div className="match-bar">
              <motion.div
                className="match-fill"
                initial={{ width: 0 }}
                animate={{ width: `${skillMatch}%` }}
                transition={{ duration: 0.5, delay: 0.2 }}
              />
            </div>
            <p className="match-description">
              Your skills match {skillMatch}% of the required skills for this position.
            </p>
          </div>

          {/* Resume Preview */}
          {resumePath && (
            <div className="resume-preview">
              <div className="resume-preview-header">
                <FiFileText size={18} />
                <span>Resume</span>
              </div>
              <div className="resume-preview-content">
                <div>
                  <p className="resume-filename">Resume attached:</p>
                  <p className="resume-path">{resumePath.split(/[/\\]/).pop()}</p>
                </div>
                <a
                  href={`/api/uploads/resumes/${encodeURIComponent(resumePath.split(/[/\\]/).pop() || '')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="resume-link"
                >
                  View Resume
                </a>
              </div>
            </div>
          )}

          {/* Cover Letter */}
          <form onSubmit={handleSubmit} className="application-form">
            <div className="form-group">
              <label htmlFor="coverLetter">
                Cover Letter <span className="optional">(Optional)</span>
              </label>
              <textarea
                id="coverLetter"
                value={coverLetter}
                onChange={(e) => setCoverLetter(e.target.value)}
                placeholder="Write a brief note about why you're interested in this position..."
                rows={6}
                className="cover-letter-input"
              />
              <p className="form-hint">
                A personalized cover letter increases your chances of being selected.
              </p>
            </div>

            <div className="modal-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={onClose}
                disabled={loading}
              >
                Cancel
              </button>
              <motion.button
                type="submit"
                className="btn btn-primary"
                disabled={loading || !canApply}
                whileHover={!loading && canApply ? { scale: 1.02 } : {}}
                whileTap={!loading && canApply ? { scale: 0.98 } : {}}
              >
                {loading ? (
                  <>
                    <div className="spinner" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <FiCheckCircle size={18} />
                    Submit Application
                  </>
                )}
              </motion.button>
            </div>
          </form>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ApplicationModal;

