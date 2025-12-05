import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { studentService } from '../../services/studentService';
import { Application, AIRecommendation } from '../../types';
import SkillsSetupModal from '../../components/SkillsSetupModal';

const StudentDashboard: React.FC = () => {
  const [dashboard, setDashboard] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [showSkillsModal, setShowSkillsModal] = useState(false);

  useEffect(() => {
    loadDashboard();
    loadRecommendations();
    
    // Check if user needs to set up skills (first-time login)
    checkSkillsSetup();
  }, []);

  const checkSkillsSetup = async () => {
    try {
      const data = await studentService.checkSkillsSetup();
      if (data.needs_setup || sessionStorage.getItem('show_skills_setup') === 'true') {
        setShowSkillsModal(true);
        sessionStorage.removeItem('show_skills_setup');
      }
    } catch (error) {
      console.error('Error checking skills setup:', error);
    }
  };

  const loadDashboard = async () => {
    try {
      const data = await studentService.getDashboard();
      setDashboard(data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRecommendations = async () => {
    try {
      const data = await studentService.getRecommendations();
      setRecommendations(data);
    } catch (error) {
      console.error('Error loading recommendations:', error);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (!dashboard) return <div>Error loading dashboard</div>;

  return (
    <div>
      <SkillsSetupModal
        isOpen={showSkillsModal}
        onClose={() => setShowSkillsModal(false)}
        onComplete={() => {
          setShowSkillsModal(false);
          loadDashboard(); // Reload to refresh stats
        }}
      />
      <h1>Student Dashboard</h1>
      
      {/* Stats */}
      <div style={styles.statsGrid}>
        <div className="card">
          <h3 style={styles.statValue}>{dashboard.stats?.total_applications || 0}</h3>
          <p style={styles.statLabel}>Total Applications</p>
        </div>
        <div className="card">
          <h3 style={styles.statValue}>{dashboard.stats?.pending || 0}</h3>
          <p style={styles.statLabel}>Pending</p>
        </div>
        <div className="card">
          <h3 style={styles.statValue}>{dashboard.stats?.shortlisted || 0}</h3>
          <p style={styles.statLabel}>Shortlisted</p>
        </div>
        <div className="card">
          <h3 style={styles.statValue}>{dashboard.stats?.interview || 0}</h3>
          <p style={styles.statLabel}>Interviews</p>
        </div>
      </div>

      {/* AI Recommendations */}
      <div style={styles.section}>
        <h2>AI-Powered Recommendations</h2>
        <div style={styles.grid}>
          {recommendations.slice(0, 6).map((rec) => (
            <div key={rec.opportunity.id} className="card" style={styles.oppCard}>
              <h3>{rec.opportunity.title}</h3>
              <p>{rec.opportunity.company_name}</p>
              <div style={styles.meta}>
                <span>📍 {rec.opportunity.location || 'Remote'}</span>
                <span>⏱️ {rec.opportunity.duration || 'N/A'}</span>
              </div>
              <div style={styles.score}>
                <span className="badge badge-info">Match: {rec.score.toFixed(0)}%</span>
                <span className="badge badge-success">Skills: {rec.skill_match.toFixed(0)}%</span>
              </div>
              <Link to={`/student/opportunities`} className="btn btn-primary" style={styles.btn}>
                View Details
              </Link>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Applications */}
      <div style={styles.section}>
        <h2>Recent Applications</h2>
        <div>
          {dashboard.applications?.slice(0, 5).map((app: Application) => (
            <div key={app.id} className="card" style={styles.appCard}>
              <div style={styles.appHeader}>
                <h3>{app.opportunity_title}</h3>
                <span className={`badge badge-${getStatusColor(app.status)}`}>
                  {app.status}
                </span>
              </div>
              <p>Applied on: {new Date(app.applied_at!).toLocaleDateString()}</p>
              {app.skill_match_percentage && (
                <p>Skill Match: {app.skill_match_percentage.toFixed(1)}%</p>
              )}
            </div>
          ))}
        </div>
        <Link to="/student/applications" className="btn btn-secondary">
          View All Applications
        </Link>
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
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '1.5rem',
    marginBottom: '2rem',
  },
  statValue: {
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#2563eb',
    margin: 0,
  },
  statLabel: {
    color: '#64748b',
    marginTop: '0.5rem',
  },
  section: {
    marginBottom: '3rem',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '1.5rem',
    marginTop: '1rem',
  },
  oppCard: {
    cursor: 'pointer',
  },
  meta: {
    display: 'flex',
    gap: '1rem',
    marginTop: '1rem',
    fontSize: '0.875rem',
    color: '#64748b',
  },
  score: {
    display: 'flex',
    gap: '0.5rem',
    marginTop: '1rem',
  },
  btn: {
    marginTop: '1rem',
    width: '100%',
  },
  appCard: {
    marginBottom: '1rem',
  },
  appHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '0.5rem',
  },
};

export default StudentDashboard;

