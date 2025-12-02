import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { companyService } from '../../services/companyService';
import { Application } from '../../types';

const CompanyApplicants: React.FC = () => {
  const { opportunityId } = useParams<{ opportunityId: string }>();
  const [applicants, setApplicants] = useState<Application[]>([]);
  const [screenedApplicants, setScreenedApplicants] = useState<Application[]>([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [showScreening, setShowScreening] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (opportunityId) {
      loadApplicants();
    }
  }, [opportunityId, statusFilter]);

  const loadApplicants = async () => {
    try {
      const data = await companyService.getApplicants(parseInt(opportunityId!), statusFilter || undefined);
      setApplicants(data);
    } catch (error) {
      console.error('Error loading applicants:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAIScreening = async () => {
    try {
      const data = await companyService.screenApplicants(parseInt(opportunityId!));
      setScreenedApplicants(data);
      setShowScreening(true);
    } catch (error) {
      console.error('Error screening applicants:', error);
    }
  };

  const handleStatusUpdate = async (appId: number, status: string, notes?: string) => {
    try {
      await companyService.updateApplicationStatus(appId, status, notes);
      alert('Application status updated');
      loadApplicants();
      if (showScreening) {
        handleAIScreening();
      }
    } catch (error: any) {
      alert(error.response?.data?.error || 'Failed to update status');
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  const displayApplicants = showScreening && screenedApplicants.length > 0 ? screenedApplicants : applicants;

  return (
    <div>
      <div style={styles.header}>
        <h1>Applicants</h1>
        <div style={styles.actions}>
          <button className="btn btn-primary" onClick={handleAIScreening}>
            AI-Powered Screening
          </button>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={styles.filter}
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="shortlisted">Shortlisted</option>
            <option value="rejected">Rejected</option>
            <option value="interview">Interview</option>
            <option value="accepted">Accepted</option>
          </select>
        </div>
      </div>

      {showScreening && screenedApplicants.length > 0 && (
        <div className="card" style={styles.infoCard}>
          <h3>AI Screening Results (Ranked by Fit)</h3>
          <p>Applicants are ranked by skill match percentage and AI score.</p>
        </div>
      )}

      <div>
        {displayApplicants.map((app) => (
          <div key={app.id} className="card" style={styles.card}>
            <div style={styles.cardHeader}>
              <div>
                <h3>{app.student_name || app.student_profile?.first_name} {app.student_profile?.last_name}</h3>
                <p>{app.student_name ? `${app.student_name.split(' ')[0]}@student.pict.edu` : 'N/A'}</p>
              </div>
              <span className={`badge badge-${getStatusColor(app.status)}`}>
                {app.status}
              </span>
            </div>

            {app.student_profile && (
              <div style={styles.studentInfo}>
                <p><strong>Skills:</strong> {app.student_profile.skills.join(', ')}</p>
                {app.student_profile.bio && <p><strong>Bio:</strong> {app.student_profile.bio}</p>}
              </div>
            )}

            {app.skill_match_percentage && (
              <div style={styles.scores}>
                <span className="badge badge-info">Skill Match: {app.skill_match_percentage.toFixed(1)}%</span>
                {app.ai_score && (
                  <span className="badge badge-info">AI Score: {app.ai_score.toFixed(1)}%</span>
                )}
              </div>
            )}

            {app.cover_letter && (
              <div style={styles.coverLetter}>
                <strong>Cover Letter:</strong>
                <p>{app.cover_letter}</p>
              </div>
            )}

            <div style={styles.statusActions}>
              <select
                value={app.status}
                onChange={(e) => handleStatusUpdate(app.id, e.target.value)}
                style={styles.statusSelect}
              >
                <option value="pending">Pending</option>
                <option value="shortlisted">Shortlisted</option>
                <option value="rejected">Rejected</option>
                <option value="interview">Interview</option>
                <option value="accepted">Accepted</option>
              </select>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const getStatusColor = (status: string) => {
  const colors: { [key: string]: string } = {
    pending: 'warning',
    shortlisted: 'info',
    rejected: 'danger',
    interview: 'info',
    accepted: 'success',
  };
  return colors[status] || 'warning';
};

const styles: { [key: string]: React.CSSProperties } = {
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '2rem',
  },
  actions: {
    display: 'flex',
    gap: '1rem',
  },
  filter: {
    padding: '0.5rem',
    borderRadius: '0.5rem',
    border: '1px solid #cbd5e1',
  },
  infoCard: {
    background: '#f0f9ff',
    marginBottom: '2rem',
  },
  card: {
    marginBottom: '1rem',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '1rem',
  },
  studentInfo: {
    marginTop: '1rem',
    padding: '1rem',
    background: '#f8fafc',
    borderRadius: '0.5rem',
  },
  scores: {
    display: 'flex',
    gap: '0.5rem',
    marginTop: '1rem',
  },
  coverLetter: {
    marginTop: '1rem',
    padding: '1rem',
    background: '#f8fafc',
    borderRadius: '0.5rem',
  },
  statusActions: {
    marginTop: '1rem',
  },
  statusSelect: {
    padding: '0.5rem',
    borderRadius: '0.5rem',
    border: '1px solid #cbd5e1',
  },
};

export default CompanyApplicants;

