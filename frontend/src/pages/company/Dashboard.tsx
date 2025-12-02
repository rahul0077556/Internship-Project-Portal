import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { companyService } from '../../services/companyService';
import { Opportunity } from '../../types';
import { 
  FiBriefcase, 
  FiUsers, 
  FiCheckCircle, 
  FiXCircle, 
  FiClock,
  FiTrendingUp,
  FiPlus,
  FiEye
} from 'react-icons/fi';
import './Dashboard.css';

const CompanyDashboard: React.FC = () => {
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const data = await companyService.getDashboard();
      setDashboard(data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="company-dashboard-loading">
        <motion.div
          className="spinner"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        />
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (!dashboard) {
    return <div className="company-dashboard-error">Failed to load dashboard</div>;
  }

  const stats = dashboard.stats || {};
  const opportunities = dashboard.opportunities || [];

  return (
    <div className="company-dashboard">
      {/* Header */}
      <motion.header
        className="dashboard-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div>
          <h1>Company Dashboard</h1>
          <p>Manage your internships and track applications</p>
        </div>
        <Link to="/company/opportunities/create" className="btn btn-primary create-btn">
          <FiPlus size={18} />
          Post New Internship
        </Link>
      </motion.header>

      {/* Stats Grid */}
      <div className="dashboard-stats">
        <motion.div
          className="stat-card"
          whileHover={{ scale: 1.05, y: -4 }}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          <div className="stat-icon" style={{ background: 'rgba(99, 102, 241, 0.1)', color: 'var(--primary)' }}>
            <FiBriefcase size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">Total Internships</p>
            <h3 className="stat-value">{stats.total_opportunities || 0}</h3>
          </div>
        </motion.div>

        <motion.div
          className="stat-card"
          whileHover={{ scale: 1.05, y: -4 }}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
        >
          <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)' }}>
            <FiCheckCircle size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">Active Postings</p>
            <h3 className="stat-value">{stats.active_opportunities || 0}</h3>
          </div>
        </motion.div>

        <motion.div
          className="stat-card"
          whileHover={{ scale: 1.05, y: -4 }}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className="stat-icon" style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)' }}>
            <FiXCircle size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">Closed Postings</p>
            <h3 className="stat-value">{stats.closed_opportunities || 0}</h3>
          </div>
        </motion.div>

        <motion.div
          className="stat-card"
          whileHover={{ scale: 1.05, y: -4 }}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
        >
          <div className="stat-icon" style={{ background: 'rgba(59, 130, 246, 0.1)', color: 'var(--info)' }}>
            <FiUsers size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">Total Applicants</p>
            <h3 className="stat-value">{stats.total_applications || 0}</h3>
          </div>
        </motion.div>

        <motion.div
          className="stat-card"
          whileHover={{ scale: 1.05, y: -4 }}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5 }}
        >
          <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning)' }}>
            <FiClock size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">In Review</p>
            <h3 className="stat-value">{stats.pending_applications || 0}</h3>
          </div>
        </motion.div>

        <motion.div
          className="stat-card"
          whileHover={{ scale: 1.05, y: -4 }}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6 }}
        >
          <div className="stat-icon" style={{ background: 'rgba(139, 92, 246, 0.1)', color: 'var(--accent)' }}>
            <FiTrendingUp size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">Shortlisted</p>
            <h3 className="stat-value">{stats.shortlisted_applications || 0}</h3>
          </div>
        </motion.div>
      </div>

      {/* Recent Opportunities */}
      <motion.section
        className="dashboard-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
      >
        <div className="section-header">
          <h2>Recent Internships</h2>
          <Link to="/company/opportunities" className="section-link">
            View All
          </Link>
        </div>

        {opportunities.length === 0 ? (
          <div className="empty-state">
            <FiBriefcase size={48} />
            <h3>No internships posted yet</h3>
            <p>Start by creating your first internship posting</p>
            <Link to="/company/opportunities/create" className="btn btn-primary">
              <FiPlus size={18} />
              Create First Internship
            </Link>
          </div>
        ) : (
          <div className="opportunities-grid">
            {opportunities.slice(0, 6).map((opp: Opportunity, index: number) => (
              <OpportunityCard key={opp.id} opportunity={opp} index={index} />
            ))}
          </div>
        )}
      </motion.section>
    </div>
  );
};

// Opportunity Card Component
const OpportunityCard: React.FC<{ opportunity: Opportunity; index: number }> = ({ opportunity, index }) => {
  return (
    <motion.div
      className="opportunity-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ y: -4, boxShadow: 'var(--shadow-xl)' }}
    >
      <div className="card-header">
        <div>
          <h3>{opportunity.title}</h3>
          <p className="card-meta">
            <span>📍 {opportunity.location || 'Remote'}</span>
            <span>⏱️ {opportunity.duration || 'N/A'}</span>
          </p>
        </div>
        <span className={`status-badge ${opportunity.is_active ? 'active' : 'inactive'}`}>
          {opportunity.is_active ? 'Active' : 'Closed'}
        </span>
      </div>

      <div className="card-body">
        <div className="card-stats">
          <div className="card-stat">
            <FiUsers size={16} />
            <span>{opportunity.applications_count || 0} Applications</span>
          </div>
          <div className="card-stat">
            <FiTrendingUp size={16} />
            <span>{opportunity.views_count || 0} Views</span>
          </div>
        </div>

        {opportunity.required_skills && opportunity.required_skills.length > 0 && (
          <div className="card-tags">
            {opportunity.required_skills.slice(0, 4).map((skill: string) => (
              <span key={skill} className="tag">
                {skill}
              </span>
            ))}
            {opportunity.required_skills.length > 4 && (
              <span className="tag">+{opportunity.required_skills.length - 4}</span>
            )}
          </div>
        )}
      </div>

      <div className="card-actions">
        <Link
          to={`/company/applicants/${opportunity.id}`}
          className="btn btn-secondary btn-sm"
        >
          <FiUsers size={16} />
          View Applicants
        </Link>
        <Link
          to={`/company/opportunities/${opportunity.id}`}
          className="btn btn-primary btn-sm"
        >
          <FiEye size={16} />
          View Details
        </Link>
      </div>
    </motion.div>
  );
};

export default CompanyDashboard;
