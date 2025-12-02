import React, { useEffect, useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { applicationService } from '../../services/applicationService';
import { studentService } from '../../services/studentService';
import { JobsSummary, JobOpportunityCard } from '../../types';
import { ToastContainer, ToastType } from '../../components/Toast';
import ApplicationModal from '../../components/ApplicationModal';
import { 
  FiSearch, 
  FiX, 
  FiMapPin, 
  FiDollarSign, 
  FiClock, 
  FiTrendingUp,
  FiCheckCircle
} from 'react-icons/fi';
import './Opportunities.css';

const Opportunities: React.FC = () => {
  const [summary, setSummary] = useState<JobsSummary | null>(null);
  const [activeTab, setActiveTab] = useState<'opportunities' | 'applications' | 'offers'>('opportunities');
  const [search, setSearch] = useState('');
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [workTypeFilter, setWorkTypeFilter] = useState<string>('all');
  const [stipendFilter, setStipendFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'latest' | 'match' | 'deadline'>('latest');
  const [loading, setLoading] = useState(true);
  const [selectedOpportunity, setSelectedOpportunity] = useState<JobOpportunityCard | null>(null);
  const [showApplicationModal, setShowApplicationModal] = useState(false);
  const [toasts, setToasts] = useState<Array<{ id: string; message: string; type: ToastType }>>([]);

  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    setLoading(true);
    try {
      const data = await studentService.getJobsSummary();
      setSummary(data);
    } catch (error: any) {
      addToast('Failed to load opportunities', 'error');
    } finally {
      setLoading(false);
    }
  };

  const addToast = (message: string, type: ToastType = 'info') => {
    const id = Date.now().toString();
    setToasts((prev) => [...prev, { id, message, type }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const filteredOpportunities = useMemo(() => {
    if (!summary) return [];
    
    let filtered = summary.opportunities.filter((opp) => {
      // Search filter
      if (search) {
        const searchLower = search.toLowerCase();
        if (
          !opp.title.toLowerCase().includes(searchLower) &&
          !(opp.company || '').toLowerCase().includes(searchLower)
        ) {
          return false;
        }
      }

      // Tag filter
      if (selectedTag && !opp.tags.includes(selectedTag)) {
        return false;
      }

      // Work type filter
      if (workTypeFilter !== 'all') {
        const jobType = opp.job_type?.toLowerCase() || '';
        if (workTypeFilter === 'remote' && !jobType.includes('remote')) return false;
        if (workTypeFilter === 'onsite' && !jobType.includes('onsite') && !jobType.includes('on-site')) return false;
        if (workTypeFilter === 'hybrid' && !jobType.includes('hybrid')) return false;
      }

      // Stipend filter
      if (stipendFilter !== 'all') {
        const ctc = opp.ctc?.toLowerCase() || '';
        if (stipendFilter === 'paid' && (ctc.includes('unpaid') || ctc.includes('0'))) return false;
        if (stipendFilter === 'unpaid' && !ctc.includes('unpaid') && !ctc.includes('0')) return false;
      }

      return true;
    });

    // Sort
    filtered.sort((a, b) => {
      if (sortBy === 'match') {
        return (b.match || 0) - (a.match || 0);
      }
      if (sortBy === 'deadline') {
        // Assuming there's a deadline field - adjust as needed
        return 0;
      }
      // Latest (default) - would need created_at field
      return 0;
    });

    return filtered;
  }, [summary, search, selectedTag, workTypeFilter, stipendFilter, sortBy]);

  const handleApply = (opportunity: JobOpportunityCard) => {
    setSelectedOpportunity(opportunity);
    setShowApplicationModal(true);
  };

  const handleApplicationSubmit = async (coverLetter: string) => {
    if (!selectedOpportunity) return;

    try {
      await applicationService.apply(selectedOpportunity.id, coverLetter);
      addToast('Application submitted successfully!', 'success');
      setShowApplicationModal(false);
      setSelectedOpportunity(null);
      loadSummary();
    } catch (error: any) {
      addToast(error.response?.data?.error || 'Failed to submit application', 'error');
    }
  };

  const handleTagClick = (tag: string) => {
    setSelectedTag(selectedTag === tag ? null : tag);
  };

  if (loading) {
    return (
      <div className="opportunities-loading">
        <motion.div
          className="spinner"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        />
        <p>Loading opportunities...</p>
      </div>
    );
  }

  if (!summary) {
    return <div className="opportunities-error">Failed to load opportunities</div>;
  }

  return (
    <div className="opportunities-page">
      <ToastContainer toasts={toasts} removeToast={removeToast} />

      {/* Header */}
      <motion.header
        className="opportunities-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div>
          <h1>Opportunities</h1>
          <p>Discover internships and projects tailored for you</p>
        </div>
        <div className="opportunities-stats">
          <motion.div
            className="stat-card"
            whileHover={{ scale: 1.05 }}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
          >
            <p>Total</p>
            <h3>{summary.stats.opportunities}</h3>
          </motion.div>
          <motion.div
            className="stat-card"
            whileHover={{ scale: 1.05 }}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <p>Eligible</p>
            <h3>{summary.stats.eligible}</h3>
          </motion.div>
          <motion.div
            className="stat-card"
            whileHover={{ scale: 1.05 }}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
          >
            <p>Applied</p>
            <h3>{summary.stats.applications}</h3>
          </motion.div>
          <motion.div
            className="stat-card"
            whileHover={{ scale: 1.05 }}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
          >
            <p>Offers</p>
            <h3>{summary.stats.offers}</h3>
          </motion.div>
        </div>
      </motion.header>

      {/* Tabs */}
      <div className="opportunities-tabs">
        {(['opportunities', 'applications', 'offers'] as const).map((tab) => (
          <motion.button
            key={tab}
            className={`tab-button ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </motion.button>
        ))}
      </div>

      <div className="opportunities-layout">
        {/* Main Content */}
        <div className="opportunities-main">
          {activeTab === 'opportunities' && (
            <>
              {/* Filters */}
              <motion.div
                className="opportunities-filters"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="search-wrapper">
                  <FiSearch className="search-icon" />
                  <input
                    type="text"
                    placeholder="Search by role, company, or skills..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="search-input"
                  />
                  {search && (
                    <button
                      className="clear-search"
                      onClick={() => setSearch('')}
                      aria-label="Clear search"
                    >
                      <FiX size={18} />
                    </button>
                  )}
                </div>

                <div className="filter-group">
                  <select
                    value={workTypeFilter}
                    onChange={(e) => setWorkTypeFilter(e.target.value)}
                    className="filter-select"
                  >
                    <option value="all">All Work Types</option>
                    <option value="remote">Remote</option>
                    <option value="hybrid">Hybrid</option>
                    <option value="onsite">On-site</option>
                  </select>

                  <select
                    value={stipendFilter}
                    onChange={(e) => setStipendFilter(e.target.value)}
                    className="filter-select"
                  >
                    <option value="all">All Stipends</option>
                    <option value="paid">Paid</option>
                    <option value="unpaid">Unpaid</option>
                  </select>

                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
                    className="filter-select"
                  >
                    <option value="latest">Latest First</option>
                    <option value="match">Best Match</option>
                    <option value="deadline">Deadline</option>
                  </select>
                </div>

                {selectedTag && (
                  <motion.div
                    className="active-filter-tag"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                  >
                    <span>Filtered by: {selectedTag}</span>
                    <button onClick={() => setSelectedTag(null)} aria-label="Remove filter">
                      <FiX size={16} />
                    </button>
                  </motion.div>
                )}
              </motion.div>

              {/* Opportunities List */}
              <AnimatePresence mode="wait">
                <motion.div
                  key="opportunities-list"
                  className="opportunities-list"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  {filteredOpportunities.length === 0 ? (
                    <motion.div
                      className="empty-state"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                    >
                      <p>No opportunities found matching your criteria.</p>
                      <button
                        className="btn btn-secondary"
                        onClick={() => {
                          setSearch('');
                          setSelectedTag(null);
                          setWorkTypeFilter('all');
                          setStipendFilter('all');
                        }}
                      >
                        Clear Filters
                      </button>
                    </motion.div>
                  ) : (
                    filteredOpportunities.map((opp, index) => (
                      <OpportunityCard
                        key={opp.id}
                        opportunity={opp}
                        onApply={handleApply}
                        index={index}
                      />
                    ))
                  )}
                </motion.div>
              </AnimatePresence>
            </>
          )}

          {activeTab === 'applications' && summary && (
            <ApplicationsTab applications={summary.applications || []} />
          )}

          {activeTab === 'offers' && summary && (
            <OffersTab offers={summary.offers || []} />
          )}
        </div>

        {/* Sidebar */}
        {summary && (
          <aside className="opportunities-sidebar">
            <PopularTags
              tags={summary.popular_tags || []}
              selectedTag={selectedTag}
              onTagClick={handleTagClick}
            />
          </aside>
        )}
      </div>

      {/* Application Modal */}
      {showApplicationModal && selectedOpportunity && (
        <ApplicationModal
          opportunity={selectedOpportunity}
          onClose={() => {
            setShowApplicationModal(false);
            setSelectedOpportunity(null);
          }}
          onSubmit={handleApplicationSubmit}
        />
      )}
    </div>
  );
};

// Opportunity Card Component
const OpportunityCard: React.FC<{
  opportunity: JobOpportunityCard;
  onApply: (opp: JobOpportunityCard) => void;
  index: number;
}> = ({ opportunity, onApply, index }) => {
  return (
    <motion.div
      className="opportunity-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ y: -4, boxShadow: 'var(--shadow-xl)' }}
    >
      <div className="opportunity-card-header">
        <div>
          <h3>{opportunity.title}</h3>
          <p className="company-name">{opportunity.company || 'Company'}</p>
        </div>
        {opportunity.applied ? (
          <span className="badge badge-success">
            <FiCheckCircle size={14} />
            Applied
          </span>
        ) : (
          <span className="badge badge-primary">Match: {opportunity.match}%</span>
        )}
      </div>

      <div className="opportunity-card-meta">
        <span>
          <FiMapPin size={14} />
          {opportunity.location || 'Remote'}
        </span>
        <span>
          <FiDollarSign size={14} />
          {opportunity.ctc || 'Not specified'}
        </span>
        <span>
          <FiClock size={14} />
          {opportunity.job_type || 'Full-time'}
        </span>
        {opportunity.posted_on && (
          <span>
            Posted {new Date(opportunity.posted_on).toLocaleDateString()}
          </span>
        )}
      </div>

      <div className="opportunity-card-tags">
        {opportunity.tags.slice(0, 8).map((tag) => (
          <span key={tag} className="tag tag-primary">
            {tag}
          </span>
        ))}
        {opportunity.tags.length > 8 && (
          <span className="tag">+{opportunity.tags.length - 8} more</span>
        )}
      </div>

      <div className="opportunity-card-actions">
        {opportunity.applied ? (
          <span className="applied-badge">
            <FiCheckCircle size={16} />
            Application Submitted
          </span>
        ) : (
          <motion.button
            className="btn btn-primary"
            onClick={() => onApply(opportunity)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Apply Now
          </motion.button>
        )}
      </div>
    </motion.div>
  );
};

// Popular Tags Component
const PopularTags: React.FC<{
  tags: Array<{ tag: string; count: number }>;
  selectedTag: string | null;
  onTagClick: (tag: string) => void;
}> = ({ tags, selectedTag, onTagClick }) => {
  return (
    <motion.div
      className="popular-tags-card card"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.3 }}
    >
      <div className="popular-tags-header">
        <FiTrendingUp size={20} />
        <h4>Popular Skills</h4>
      </div>
      <div className="popular-tags-list">
        {tags.map(({ tag, count }) => (
          <motion.button
            key={tag}
            className={`popular-tag ${selectedTag === tag ? 'active' : ''}`}
            onClick={() => onTagClick(tag)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <span>{tag}</span>
            <span className="tag-count">{count}</span>
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
};

// Applications Tab Component
const ApplicationsTab: React.FC<{ applications: any[] }> = ({ applications }) => {
  const statusColors: Record<string, string> = {
    pending: 'badge-warning',
    shortlisted: 'badge-info',
    rejected: 'badge-danger',
    interview: 'badge-info',
    accepted: 'badge-success',
    withdrawn: 'badge-secondary',
  };

  return (
    <motion.div
      className="applications-tab"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {applications.length === 0 ? (
        <div className="empty-state">
          <p>You haven't applied to any opportunities yet.</p>
        </div>
      ) : (
        <div className="applications-list">
          {applications.map((app, index) => (
            <motion.div
              key={app.id}
              className="application-card card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <div className="application-card-header">
                <div>
                  <h3>{app.title}</h3>
                  <p className="company-name">{app.company || 'Company'}</p>
                </div>
                <span className={`badge ${statusColors[app.status?.toLowerCase()] || 'badge-secondary'}`}>
                  {app.status}
                </span>
              </div>
              <div className="application-card-meta">
                <span>
                  <FiMapPin size={14} />
                  {app.location || 'Remote'}
                </span>
                <span>
                  <FiClock size={14} />
                  Applied {app.submitted_on ? new Date(app.submitted_on).toLocaleDateString() : '—'}
                </span>
              </div>
              {app.tags && app.tags.length > 0 && (
                <div className="application-card-tags">
                  {app.tags.slice(0, 6).map((tag: string) => (
                    <span key={tag} className="tag">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
};

// Offers Tab Component
const OffersTab: React.FC<{ offers: any[] }> = ({ offers }) => {
  return (
    <motion.div
      className="offers-tab"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {offers.length === 0 ? (
        <div className="empty-state">
          <p>No offers received yet.</p>
        </div>
      ) : (
        <div className="offers-list">
          {offers.map((offer, index) => (
            <motion.div
              key={offer.id}
              className="offer-card card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <div className="offer-card-header">
                <div>
                  <h3>{offer.company_name}</h3>
                  <p className="role-name">{offer.role}</p>
                </div>
                <span className="badge badge-success">Offer Received</span>
              </div>
              <div className="offer-card-details">
                <div className="offer-detail">
                  <FiDollarSign size={18} />
                  <div>
                    <p className="detail-label">CTC</p>
                    <p className="detail-value">{offer.ctc || 'Not specified'}</p>
                  </div>
                </div>
                <div className="offer-detail">
                  <FiMapPin size={18} />
                  <div>
                    <p className="detail-label">Location</p>
                    <p className="detail-value">{offer.location || 'TBD'}</p>
                  </div>
                </div>
                {offer.offer_date && (
                  <div className="offer-detail">
                    <FiClock size={18} />
                    <div>
                      <p className="detail-label">Offer Date</p>
                      <p className="detail-value">
                        {new Date(offer.offer_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                )}
              </div>
              {offer.notes && (
                <div className="offer-notes">
                  <p>{offer.notes}</p>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
};

export default Opportunities;
