import React, { useState, useEffect } from 'react';
import { companyService } from '../../services/companyService';
import { CompanyProfile as CompanyProfileType } from '../../types';

const CompanyProfile: React.FC = () => {
  const [profile, setProfile] = useState<CompanyProfileType | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    website: '',
    phone: '',
    address: '',
    industry: '',
    company_size: '',
    faculty_department: '',
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await companyService.getProfile();
      setProfile(data);
      setFormData({
        name: data.name || '',
        description: data.description || '',
        website: data.website || '',
        phone: data.phone || '',
        address: data.address || '',
        industry: data.industry || '',
        company_size: data.company_size || '',
        faculty_department: data.faculty_department || '',
      });
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      await companyService.updateProfile(formData);
      alert('Profile updated successfully!');
      loadProfile();
    } catch (error: any) {
      alert(error.response?.data?.error || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div>
      <h1>Company Profile</h1>
      
      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={4}
            />
          </div>
          <div className="form-group">
            <label>Website</label>
            <input
              type="url"
              value={formData.website}
              onChange={(e) => setFormData({ ...formData, website: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Phone</label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Address</label>
            <textarea
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              rows={2}
            />
          </div>
          <div className="form-group">
            <label>Industry</label>
            <input
              type="text"
              value={formData.industry}
              onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Company Size</label>
            <select
              value={formData.company_size}
              onChange={(e) => setFormData({ ...formData, company_size: e.target.value })}
            >
              <option value="">Select Size</option>
              <option value="1-10">1-10</option>
              <option value="11-50">11-50</option>
              <option value="51-100">51-100</option>
              <option value="101-500">101-500</option>
              <option value="500+">500+</option>
            </select>
          </div>
          {profile?.is_faculty && (
            <div className="form-group">
              <label>Department</label>
              <input
                type="text"
                value={formData.faculty_department}
                onChange={(e) => setFormData({ ...formData, faculty_department: e.target.value })}
              />
            </div>
          )}
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Saving...' : 'Update Profile'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CompanyProfile;

