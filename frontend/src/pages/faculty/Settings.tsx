import React, { useEffect, useState } from 'react';
import { facultyService } from '../../services/facultyService';
import './faculty.css';

const FacultySettings: React.FC = () => {
  const [form, setForm] = useState({
    name: '',
    faculty_department: '',
    phone: '',
    website: '',
    description: '',
  });
  const [preferences, setPreferences] = useState(() => {
    const saved = localStorage.getItem('faculty_preferences');
    return saved
      ? JSON.parse(saved)
      : {
          academicYear: '2024-25',
          focusBatch: '2025',
          notifications: true,
        };
  });
  const [message, setMessage] = useState('');

  useEffect(() => {
    const load = async () => {
      const data = await facultyService.getProfile();
      setForm({
        name: data.profile?.name || '',
        faculty_department: data.profile?.faculty_department || '',
        phone: data.profile?.phone || '',
        website: data.profile?.website || '',
        description: data.profile?.description || '',
      });
    };
    load();
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await facultyService.updateProfile(form);
    setMessage('Profile updated successfully');
    setTimeout(() => setMessage(''), 3000);
  };

  const handlePreferencesSave = () => {
    localStorage.setItem('faculty_preferences', JSON.stringify(preferences));
    setMessage('Preferences saved locally');
    setTimeout(() => setMessage(''), 3000);
  };

  return (
    <div className="faculty-shell">
      <div className="faculty-heading">
        <h1>Faculty Settings</h1>
        <p>Control your profile, notification preferences, and academic focus.</p>
      </div>

      {message && <div className="badge">{message}</div>}

      <div className="settings-panel" style={{ marginTop: '1.5rem' }}>
        <div className="chart-card">
          <h3>Profile</h3>
          <form onSubmit={handleSubmit}>
            <label>
              Full Name
              <input
                value={form.name}
                onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
                required
              />
            </label>
            <label>
              Department
              <input
                value={form.faculty_department}
                onChange={(e) => setForm((prev) => ({ ...prev, faculty_department: e.target.value }))}
              />
            </label>
            <label>
              Contact Number
              <input
                value={form.phone}
                onChange={(e) => setForm((prev) => ({ ...prev, phone: e.target.value }))}
              />
            </label>
            <label>
              Website / LinkedIn
              <input
                value={form.website}
                onChange={(e) => setForm((prev) => ({ ...prev, website: e.target.value }))}
              />
            </label>
            <label>
              Faculty Bio
              <textarea
                value={form.description}
                onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
              />
            </label>
            <div className="settings-save">
              <button type="submit" className="btn-primary-gradient">
                Save Profile
              </button>
            </div>
          </form>
        </div>

        <div className="chart-card">
          <h3>Preferences</h3>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handlePreferencesSave();
            }}
          >
            <label>
              Academic Year
              <select
                value={preferences.academicYear}
                onChange={(e) => setPreferences((prev: any) => ({ ...prev, academicYear: e.target.value }))}
              >
                <option value="2024-25">2024-25</option>
                <option value="2025-26">2025-26</option>
                <option value="2026-27">2026-27</option>
              </select>
            </label>
            <label>
              Focus Batch
              <select
                value={preferences.focusBatch}
                onChange={(e) => setPreferences((prev: any) => ({ ...prev, focusBatch: e.target.value }))}
              >
                <option value="2025">2025 Batch</option>
                <option value="2026">2026 Batch</option>
                <option value="2027">2027 Batch</option>
              </select>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                checked={preferences.notifications}
                onChange={(e) => setPreferences((prev: any) => ({ ...prev, notifications: e.target.checked }))}
              />
              Enable proactive notifications
            </label>
            <div className="settings-save">
              <button type="submit" className="btn-soft">
                Save Preferences
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default FacultySettings;

