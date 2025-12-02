import React, { useEffect, useState } from 'react';
import { studentService } from '../../services/studentService';

type FormField = {
  name: string;
  label: string;
  type?: 'text' | 'textarea' | 'date' | 'tags';
  placeholder?: string;
  required?: boolean;
};

const NAV_TABS = [
  { key: 'basic', label: 'Basic Details', description: 'Personal profile & identifiers' },
  { key: 'education', label: 'Education', description: 'Academic achievements & CGPA' },
  { key: 'experiences', label: 'Professional Experience', description: 'Full-time or part-time roles' },
  { key: 'internships', label: 'Internships', description: 'Industry internships & mentors' },
  { key: 'projects', label: 'Projects', description: 'Capstone, personal & research work' },
  { key: 'trainings', label: 'Seminars / Trainings', description: 'Workshops, hackathons & courses' },
  { key: 'certifications', label: 'Certifications', description: 'Professional credentials' },
  { key: 'publications', label: 'Publications', description: 'Whitepapers & journals' },
  { key: 'positions', label: 'Positions of Responsibility', description: 'Clubs, committees & leads' },
  { key: 'offers', label: 'Offers', description: 'Final placement / internship offers' },
  { key: 'attachments', label: 'Attachments', description: 'Transcripts, offer letters, more' },
];

const SECTION_FIELDS: Record<string, FormField[]> = {
  education: [
    { name: 'degree', label: 'Degree', required: true },
    { name: 'institution', label: 'Institution', required: true },
    { name: 'course', label: 'Course' },
    { name: 'specialization', label: 'Specialization' },
    { name: 'start_date', label: 'Start Date', type: 'date' },
    { name: 'end_date', label: 'End Date', type: 'date' },
    { name: 'gpa', label: 'GPA / Percentage' },
    { name: 'achievements', label: 'Highlights', type: 'textarea' },
  ],
  experiences: [
    { name: 'company_name', label: 'Company', required: true },
    { name: 'designation', label: 'Designation', required: true },
    { name: 'employment_type', label: 'Employment Type' },
    { name: 'start_date', label: 'Start Date', type: 'date' },
    { name: 'end_date', label: 'End Date', type: 'date' },
    { name: 'location', label: 'Location' },
    { name: 'technologies', label: 'Technologies', type: 'tags', placeholder: 'React, Node, SQL' },
    { name: 'description', label: 'Summary', type: 'textarea' },
  ],
  internships: [
    { name: 'designation', label: 'Designation', required: true },
    { name: 'organization', label: 'Organisation', required: true },
    { name: 'industry_sector', label: 'Industry Sector' },
    { name: 'internship_type', label: 'Internship Type' },
    { name: 'stipend', label: 'Stipend' },
    { name: 'start_date', label: 'Start Date', type: 'date' },
    { name: 'end_date', label: 'End Date', type: 'date' },
    { name: 'mentor_name', label: 'Mentor' },
    { name: 'mentor_contact', label: 'Mentor Contact' },
    { name: 'mentor_designation', label: 'Mentor Designation' },
    { name: 'technologies', label: 'Skills', type: 'tags' },
    { name: 'description', label: 'Description', type: 'textarea' },
  ],
  projects: [
    { name: 'title', label: 'Project Title', required: true },
    { name: 'organization', label: 'Client / Organisation' },
    { name: 'role', label: 'Role' },
    { name: 'start_date', label: 'Start Date', type: 'date' },
    { name: 'end_date', label: 'End Date', type: 'date' },
    { name: 'technologies', label: 'Stack', type: 'tags', placeholder: 'React, Firebase' },
    { name: 'links', label: 'Links', type: 'textarea', placeholder: 'GitHub, Demo' },
    { name: 'description', label: 'Description', type: 'textarea' },
  ],
  trainings: [
    { name: 'title', label: 'Programme Title', required: true },
    { name: 'provider', label: 'Provider' },
    { name: 'mode', label: 'Mode' },
    { name: 'start_date', label: 'Start Date', type: 'date' },
    { name: 'end_date', label: 'End Date', type: 'date' },
    { name: 'description', label: 'Description', type: 'textarea' },
  ],
  certifications: [
    { name: 'name', label: 'Certification', required: true },
    { name: 'issuer', label: 'Issuer' },
    { name: 'issue_date', label: 'Issue Date', type: 'date' },
    { name: 'expiry_date', label: 'Expiry Date', type: 'date' },
    { name: 'credential_id', label: 'Credential ID' },
    { name: 'credential_url', label: 'Credential URL' },
    { name: 'description', label: 'Notes', type: 'textarea' },
  ],
  publications: [
    { name: 'title', label: 'Title', required: true },
    { name: 'publication_type', label: 'Type' },
    { name: 'publisher', label: 'Publisher' },
    { name: 'publication_date', label: 'Publication Date', type: 'date' },
    { name: 'url', label: 'URL' },
    { name: 'description', label: 'Abstract', type: 'textarea' },
  ],
  positions: [
    { name: 'title', label: 'Position', required: true },
    { name: 'organization', label: 'Organisation' },
    { name: 'start_date', label: 'Start Date', type: 'date' },
    { name: 'end_date', label: 'End Date', type: 'date' },
    { name: 'description', label: 'Contributions', type: 'textarea' },
  ],
  offers: [
    { name: 'company_name', label: 'Company', required: true },
    { name: 'role', label: 'Role' },
    { name: 'ctc', label: 'CTC' },
    { name: 'status', label: 'Status' },
    { name: 'offer_date', label: 'Offer Date', type: 'date' },
    { name: 'joining_date', label: 'Joining Date', type: 'date' },
    { name: 'notes', label: 'Notes', type: 'textarea' },
  ],
};

const StudentProfileWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = useState('basic');
  const [formState, setFormState] = useState<Record<string, any>>({});
  const [sections, setSections] = useState<Record<string, any[]>>({});
  const [stats, setStats] = useState<Record<string, number>>({});
  const [sectionForm, setSectionForm] = useState<Record<string, any>>({});
  const [editingEntry, setEditingEntry] = useState<number | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const data = await studentService.getFullProfile();
      setSections(data.sections || {});
      setStats(data.stats || {});
      setFormState({
        first_name: data.profile.first_name || '',
        middle_name: (data.profile as any).middle_name || '',
        last_name: data.profile.last_name || '',
        prn_number: (data.profile as any).prn_number || '',
        course: (data.profile as any).course || '',
        specialization: (data.profile as any).specialization || '',
        gender: (data.profile as any).gender || '',
        date_of_birth: data.profile.date_of_birth ? data.profile.date_of_birth.substring(0, 10) : '',
        phone: data.profile.phone || '',
        address: data.profile.address || '',
        bio: data.profile.bio || '',
        linkedin_url: data.profile.linkedin_url || '',
        github_url: data.profile.github_url || '',
        portfolio_url: data.profile.portfolio_url || '',
        skills: (data.profile.skills || []).join(', '),
        interests: (data.profile.interests || []).join(', '),
      });
    } finally {
      setLoading(false);
    }
  };

  const showToast = (message: string) => {
    setToast(message);
    setTimeout(() => setToast(null), 2500);
  };

  const saveProfile = async (event: React.FormEvent) => {
    event.preventDefault();
    await studentService.updateProfile({
      ...formState,
      skills: (formState.skills || '')
        .split(',')
        .map((item: string) => item.trim())
        .filter(Boolean),
      interests: (formState.interests || '')
        .split(',')
        .map((item: string) => item.trim())
        .filter(Boolean),
    });
    showToast('Profile updated');
    loadProfile();
  };

  const uploadResume = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    await studentService.uploadResume(file);
    showToast('Resume uploaded');
    loadProfile();
  };

  const downloadResume = async () => {
    const blob = await studentService.generateResumePdf();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'resume.pdf';
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleSectionSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const fields = SECTION_FIELDS[activeTab] || [];
    const payload: Record<string, any> = {};
    fields.forEach((field) => {
      const value = sectionForm[field.name];
      if (field.type === 'tags') {
        payload[field.name] = (value || '')
          .split(',')
          .map((item: string) => item.trim())
          .filter(Boolean);
      } else {
        payload[field.name] = value || '';
      }
    });
    if (editingEntry) {
      await studentService.updateSection(activeTab, editingEntry, payload);
      showToast('Entry updated');
    } else {
      await studentService.createSection(activeTab, payload);
      showToast('Entry added');
    }
    setSectionForm({});
    setEditingEntry(null);
    loadProfile();
  };

  const startEditing = (entry: Record<string, any>) => {
    const fields = SECTION_FIELDS[activeTab] || [];
    const patch: Record<string, any> = {};
    fields.forEach((field) => {
      const value = entry[field.name];
      if (field.type === 'tags') {
        patch[field.name] = Array.isArray(value) ? value.join(', ') : value || '';
      } else {
        patch[field.name] = value || '';
      }
    });
    setSectionForm(patch);
    setEditingEntry(entry.id);
  };

  const deleteEntry = async (id: number) => {
    if (!window.confirm('Delete this entry?')) return;
    await studentService.deleteSection(activeTab, id);
    showToast('Entry removed');
    loadProfile();
  };

  if (loading) return <div className="loading">Preparing workspace...</div>;

  return (
    <div className="profile-workspace">
      <aside className="profile-sidebar">
        <div className="sidebar-header">
          <span className="badge badge-info">Student Workspace</span>
          <h2>Profile Builder</h2>
          <p>Prepare a resume-ready profile</p>
        </div>
        <nav>
          {NAV_TABS.map((tab) => (
            <button
              key={tab.key}
              className={`sidebar-tab ${tab.key === activeTab ? 'active' : ''}`}
              onClick={() => {
                setActiveTab(tab.key);
                setSectionForm({});
                setEditingEntry(null);
              }}
            >
              <div>
                <strong>{tab.label}</strong>
                <p>{tab.description}</p>
              </div>
              {stats[tab.key] !== undefined && <span className="badge badge-pill">{stats[tab.key]}</span>}
            </button>
          ))}
        </nav>
      </aside>

      <section className="profile-content">
        {toast && <div className="alert alert-info">{toast}</div>}

        {activeTab === 'basic' && (
          <div className="profile-basic">
            <div className="profile-actions">
              <label className="btn btn-secondary">
                Upload Resume
                <input type="file" hidden accept=".pdf,.doc,.docx" onChange={uploadResume} />
              </label>
              <button className="btn btn-success" onClick={downloadResume}>
                Generate Resume
              </button>
            </div>
            <form className="profile-form" onSubmit={saveProfile}>
              <div className="grid-3">
                {['first_name', 'middle_name', 'last_name'].map((field) => (
                  <div className="form-group" key={field}>
                    <label>{field.replace('_', ' ').toUpperCase()}</label>
                    <input value={formState[field] || ''} onChange={(e) => setFormState({ ...formState, [field]: e.target.value })} />
                  </div>
                ))}
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input value={formState.phone || ''} onChange={(e) => setFormState({ ...formState, phone: e.target.value })} />
              </div>
              <div className="grid-3">
                <div className="form-group">
                  <label>PRN Number</label>
                  <input value={formState.prn_number || ''} onChange={(e) => setFormState({ ...formState, prn_number: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Branch</label>
                  <input
                    value={formState.course || ''}
                    onChange={(e) => setFormState({ ...formState, course: e.target.value })}
                    placeholder="Computer, IT, ENTC..."
                  />
                </div>
                <div className="form-group">
                  <label>Year / Division</label>
                  <input
                    value={formState.specialization || ''}
                    onChange={(e) => setFormState({ ...formState, specialization: e.target.value })}
                    placeholder="TE A, BE B..."
                  />
                </div>
              </div>
              <div className="grid-2">
                <div className="form-group">
                  <label>Date of Birth</label>
                  <input
                    type="date"
                    value={formState.date_of_birth || ''}
                    onChange={(e) => setFormState({ ...formState, date_of_birth: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Gender</label>
                  <select value={formState.gender || ''} onChange={(e) => setFormState({ ...formState, gender: e.target.value })}>
                    <option value="">Select</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                    <option value="Prefer not to say">Prefer not to say</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>Address</label>
                <textarea rows={3} value={formState.address || ''} onChange={(e) => setFormState({ ...formState, address: e.target.value })} />
              </div>
              <div className="form-group">
                <label>About / Bio</label>
                <textarea rows={3} value={formState.bio || ''} onChange={(e) => setFormState({ ...formState, bio: e.target.value })} />
              </div>
              <div className="grid-2">
                <div className="form-group">
                  <label>Skills</label>
                  <textarea rows={2} value={formState.skills || ''} onChange={(e) => setFormState({ ...formState, skills: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Interests</label>
                  <textarea rows={2} value={formState.interests || ''} onChange={(e) => setFormState({ ...formState, interests: e.target.value })} />
                </div>
              </div>
              <div className="grid-3">
                {['linkedin_url', 'github_url', 'portfolio_url'].map((field) => (
                  <div className="form-group" key={field}>
                    <label>{field.replace('_url', '').toUpperCase()}</label>
                    <input value={formState[field] || ''} onChange={(e) => setFormState({ ...formState, [field]: e.target.value })} />
                  </div>
                ))}
              </div>
              <button className="btn btn-primary" type="submit">
                Save Profile
              </button>
            </form>
          </div>
        )}

        {activeTab !== 'basic' && (
          <div className="section-wrapper">
            <div className="section-list">
              {(sections[activeTab] || []).length === 0 ? (
                <p className="empty-state">No records added yet.</p>
              ) : (
                (sections[activeTab] || []).map((entry) => (
                  <div className="section-card" key={entry.id}>
                    <div>
                      <h4>{entry.title || entry.designation || entry.company_name || entry.degree || entry.name}</h4>
                      {entry.organization && <p className="muted">{entry.organization}</p>}
                      {entry.company_name && <p className="muted">{entry.company_name}</p>}
                      {entry.description && <p className="muted">{entry.description}</p>}
                    </div>
                    <div className="section-card-actions">
                      <button className="btn btn-secondary" onClick={() => startEditing(entry)}>
                        Edit
                      </button>
                      <button className="btn btn-danger" onClick={() => deleteEntry(entry.id)}>
                        Delete
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>

            {activeTab !== 'attachments' && SECTION_FIELDS[activeTab] && (
              <form className="section-form" onSubmit={handleSectionSubmit}>
                <h4>{editingEntry ? 'Update Entry' : `Add ${NAV_TABS.find((tab) => tab.key === activeTab)?.label}`}</h4>
                {SECTION_FIELDS[activeTab].map((field) => (
                  <div className="form-group" key={field.name}>
                    <label>{field.label}</label>
                    {field.type === 'textarea' ? (
                      <textarea
                        rows={3}
                        value={sectionForm[field.name] || ''}
                        placeholder={field.placeholder}
                        onChange={(e) => setSectionForm({ ...sectionForm, [field.name]: e.target.value })}
                        required={field.required}
                      />
                    ) : (
                      <input
                        type={field.type === 'date' ? 'date' : 'text'}
                        value={sectionForm[field.name] || ''}
                        placeholder={field.placeholder}
                        onChange={(e) => setSectionForm({ ...sectionForm, [field.name]: e.target.value })}
                        required={field.required}
                      />
                    )}
                  </div>
                ))}
                <div className="section-form-actions">
                  {editingEntry && (
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => {
                        setSectionForm({});
                        setEditingEntry(null);
                      }}
                    >
                      Cancel
                    </button>
                  )}
                  <button className="btn btn-primary" type="submit">
                    {editingEntry ? 'Update Entry' : 'Add Entry'}
                  </button>
                </div>
              </form>
            )}

            {activeTab === 'attachments' && (
              <div className="section-form">
                <h4>Upload Attachment</h4>
                <input
                  type="file"
                  onChange={async (e) => {
                    const file = e.target.files?.[0];
                    if (!file) return;
                    const formData = new FormData();
                    formData.append('title', file.name);
                    formData.append('file', file);
                    await studentService.uploadAttachment(formData);
                    showToast('Attachment uploaded');
                    loadProfile();
                  }}
                />
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
};

export default StudentProfileWorkspace;

