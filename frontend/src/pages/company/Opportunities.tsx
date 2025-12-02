import React, { useState, useEffect } from 'react';
import { companyService } from '../../services/companyService';
import { Opportunity } from '../../types';

const CompanyOpportunities: React.FC = () => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingOpp, setEditingOpp] = useState<Opportunity | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    domain: '',
    required_skills: '',
    duration: '',
    stipend: '',
    location: '',
    work_type: 'remote' as 'remote' | 'onsite' | 'hybrid',
    prerequisites: '',
    application_deadline: '',
    start_date: '',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOpportunities();
  }, []);

  const loadOpportunities = async () => {
    try {
      const data = await companyService.getOpportunities();
      setOpportunities(data);
    } catch (error) {
      console.error('Error loading opportunities:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const opportunityData = {
        ...formData,
        required_skills: formData.required_skills.split(',').map(s => s.trim()).filter(s => s),
      };

      if (editingOpp) {
        await companyService.updateOpportunity(editingOpp.id, opportunityData);
      } else {
        await companyService.createOpportunity(opportunityData);
      }

      alert(`Opportunity ${editingOpp ? 'updated' : 'created'} successfully!`);
      setShowForm(false);
      setEditingOpp(null);
      resetForm();
      loadOpportunities();
    } catch (error: any) {
      alert(error.response?.data?.error || 'Failed to save opportunity');
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      domain: '',
      required_skills: '',
      duration: '',
      stipend: '',
      location: '',
      work_type: 'remote',
      prerequisites: '',
      application_deadline: '',
      start_date: '',
    });
  };

  const handleEdit = (opp: Opportunity) => {
    setEditingOpp(opp);
    setFormData({
      title: opp.title,
      description: opp.description,
      domain: opp.domain,
      required_skills: opp.required_skills.join(', '),
      duration: opp.duration,
      stipend: opp.stipend,
      location: opp.location,
      work_type: opp.work_type,
      prerequisites: opp.prerequisites || '',
      application_deadline: opp.application_deadline || '',
      start_date: opp.start_date || '',
    });
    setShowForm(true);
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div>
      <div style={styles.header}>
        <h1>My Opportunities</h1>
        <button className="btn btn-primary" onClick={() => { setShowForm(true); resetForm(); setEditingOpp(null); }}>
          + Create Opportunity
        </button>
      </div>

      {showForm && (
        <div className="card" style={styles.formCard}>
          <h2>{editingOpp ? 'Edit Opportunity' : 'Create New Opportunity'}</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Title *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Description *</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                required
              />
            </div>
            <div className="form-group">
              <label>Domain *</label>
              <input
                type="text"
                value={formData.domain}
                onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Required Skills (comma-separated) *</label>
              <input
                type="text"
                value={formData.required_skills}
                onChange={(e) => setFormData({ ...formData, required_skills: e.target.value })}
                placeholder="Python, JavaScript, React, ..."
                required
              />
            </div>
            <div style={styles.row}>
              <div className="form-group" style={styles.half}>
                <label>Duration</label>
                <input
                  type="text"
                  value={formData.duration}
                  onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
                  placeholder="e.g., 3 months"
                />
              </div>
              <div className="form-group" style={styles.half}>
                <label>Stipend</label>
                <input
                  type="text"
                  value={formData.stipend}
                  onChange={(e) => setFormData({ ...formData, stipend: e.target.value })}
                  placeholder="e.g., 15000-20000"
                />
              </div>
            </div>
            <div style={styles.row}>
              <div className="form-group" style={styles.half}>
                <label>Location</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                />
              </div>
              <div className="form-group" style={styles.half}>
                <label>Work Type</label>
                <select
                  value={formData.work_type}
                  onChange={(e) => setFormData({ ...formData, work_type: e.target.value as any })}
                >
                  <option value="remote">Remote</option>
                  <option value="onsite">Onsite</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>
            </div>
            <div className="form-group">
              <label>Prerequisites</label>
              <textarea
                value={formData.prerequisites}
                onChange={(e) => setFormData({ ...formData, prerequisites: e.target.value })}
                rows={2}
              />
            </div>
            <div style={styles.row}>
              <div className="form-group" style={styles.half}>
                <label>Application Deadline</label>
                <input
                  type="date"
                  value={formData.application_deadline}
                  onChange={(e) => setFormData({ ...formData, application_deadline: e.target.value })}
                />
              </div>
              <div className="form-group" style={styles.half}>
                <label>Start Date</label>
                <input
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                />
              </div>
            </div>
            <div style={styles.actions}>
              <button type="submit" className="btn btn-primary">
                {editingOpp ? 'Update' : 'Create'} Opportunity
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => { setShowForm(false); resetForm(); setEditingOpp(null); }}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div style={styles.grid}>
        {opportunities.map((opp) => (
          <div key={opp.id} className="card" style={styles.card}>
            <div style={styles.cardHeader}>
              <h3>{opp.title}</h3>
              <span className={`badge ${opp.is_active ? 'badge-success' : 'badge-danger'}`}>
                {opp.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <p><strong>Domain:</strong> {opp.domain}</p>
            <p><strong>Applications:</strong> {opp.applications_count}</p>
            <div style={styles.actions}>
              <a href={`/company/applicants/${opp.id}`} className="btn btn-secondary">
                View Applicants
              </a>
              <button className="btn btn-primary" onClick={() => handleEdit(opp)}>
                Edit
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '2rem',
  },
  formCard: {
    marginBottom: '2rem',
  },
  row: {
    display: 'flex',
    gap: '1rem',
  },
  half: {
    flex: 1,
  },
  actions: {
    display: 'flex',
    gap: '1rem',
    marginTop: '1rem',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '1.5rem',
  },
  card: {
    marginBottom: '1rem',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem',
  },
};

export default CompanyOpportunities;

