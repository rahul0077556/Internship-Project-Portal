import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { FiMail, FiLock, FiBriefcase, FiUser, FiPhone, FiGlobe, FiUpload, FiSun, FiMoon, FiLoader, FiX } from 'react-icons/fi';
import './CompanyRegister.css';

const CompanyRegister: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    companyName: '',
    hrName: '',
    hrPhone: '',
    website: '',
  });
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        setError('Logo file size must be less than 5MB');
        return;
      }
      if (!file.type.startsWith('image/')) {
        setError('Please upload an image file');
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        setLogoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const validateForm = () => {
    if (!formData.email || !formData.password || !formData.companyName || !formData.hrName) {
      setError('Please fill in all required fields');
      return false;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return false;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }

    if (formData.website && !/^https?:\/\/.+/.test(formData.website)) {
      setError('Please enter a valid website URL (starting with http:// or https://)');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const profile: any = {
        name: formData.companyName,
        website: formData.website || undefined,
        phone: formData.hrPhone || undefined,
      };

      // If logo is uploaded, we'll need to handle it separately after registration
      // For now, we'll register without logo and allow upload later in profile settings

      await register(formData.email, formData.password, 'company', profile);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="company-register-container">
      {/* Theme Toggle */}
      <motion.button
        className="theme-toggle"
        onClick={toggleTheme}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        aria-label="Toggle theme"
      >
        {theme === 'dark' ? <FiSun size={20} /> : <FiMoon size={20} />}
      </motion.button>

      {/* Animated Background */}
      <div className="register-background">
        <div className="gradient-orb orb-1" />
        <div className="gradient-orb orb-2" />
        <div className="gradient-orb orb-3" />
      </div>

      {/* Register Card */}
      <motion.div
        className="register-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <motion.div
          className="register-header"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
        >
          <h1 className="register-brand">RNSSS</h1>
          <p className="register-subtitle">Company Registration</p>
        </motion.div>

        {/* Error Message */}
        {error && (
          <motion.div
            className="register-error"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            {error}
            <button onClick={() => setError('')} className="error-close">
              <FiX size={16} />
            </button>
          </motion.div>
        )}

        {/* Registration Form */}
        <form onSubmit={handleSubmit} className="register-form">
          {/* Company Logo Upload */}
          <motion.div
            className="form-group logo-upload-group"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <label htmlFor="logo">Company Logo</label>
            <div className="logo-upload-wrapper">
              {logoPreview ? (
                <div className="logo-preview">
                  <img src={logoPreview} alt="Logo preview" />
                  <button
                    type="button"
                    className="remove-logo"
                    onClick={() => {
                      setLogoPreview(null);
                      // no-op for now
                    }}
                  >
                    <FiX size={18} />
                  </button>
                </div>
              ) : (
                <label htmlFor="logo" className="logo-upload-label">
                  <FiUpload size={24} />
                  <span>Upload Logo</span>
                  <span className="logo-hint">Max 5MB, PNG/JPG</span>
                </label>
              )}
              <input
                id="logo"
                type="file"
                accept="image/*"
                onChange={handleLogoChange}
                className="logo-input"
              />
            </div>
          </motion.div>

          {/* Company Name */}
          <motion.div
            className="form-group"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <label htmlFor="companyName">
              Company Name <span className="required">*</span>
            </label>
            <div className="input-wrapper">
              <FiBriefcase className="input-icon" />
              <input
                id="companyName"
                name="companyName"
                type="text"
                value={formData.companyName}
                onChange={handleInputChange}
                placeholder="Enter your company name"
                required
              />
            </div>
          </motion.div>

          {/* HR Name */}
          <motion.div
            className="form-group"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <label htmlFor="hrName">
              HR/Contact Person Name <span className="required">*</span>
            </label>
            <div className="input-wrapper">
              <FiUser className="input-icon" />
              <input
                id="hrName"
                name="hrName"
                type="text"
                value={formData.hrName}
                onChange={handleInputChange}
                placeholder="Enter HR name"
                required
              />
            </div>
          </motion.div>

          {/* Email */}
          <motion.div
            className="form-group"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <label htmlFor="email">
              HR Email <span className="required">*</span>
            </label>
            <div className="input-wrapper">
              <FiMail className="input-icon" />
              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="hr@company.com"
                required
              />
            </div>
          </motion.div>

          {/* HR Phone */}
          <motion.div
            className="form-group"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <label htmlFor="hrPhone">HR Phone Number</label>
            <div className="input-wrapper">
              <FiPhone className="input-icon" />
              <input
                id="hrPhone"
                name="hrPhone"
                type="tel"
                value={formData.hrPhone}
                onChange={handleInputChange}
                placeholder="+91 1234567890"
              />
            </div>
          </motion.div>

          {/* Website */}
          <motion.div
            className="form-group"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <label htmlFor="website">Company Website</label>
            <div className="input-wrapper">
              <FiGlobe className="input-icon" />
              <input
                id="website"
                name="website"
                type="url"
                value={formData.website}
                onChange={handleInputChange}
                placeholder="https://www.company.com"
              />
            </div>
          </motion.div>

          {/* Password */}
          <motion.div
            className="form-group"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
          >
            <label htmlFor="password">
              Password <span className="required">*</span>
            </label>
            <div className="input-wrapper">
              <FiLock className="input-icon" />
              <input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Minimum 6 characters"
                required
                minLength={6}
              />
            </div>
          </motion.div>

          {/* Confirm Password */}
          <motion.div
            className="form-group"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.0 }}
          >
            <label htmlFor="confirmPassword">
              Confirm Password <span className="required">*</span>
            </label>
            <div className="input-wrapper">
              <FiLock className="input-icon" />
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                placeholder="Re-enter your password"
                required
                minLength={6}
              />
            </div>
          </motion.div>

          {/* Submit Button */}
          <motion.button
            type="submit"
            className="btn btn-primary btn-block register-button"
            disabled={loading}
            whileHover={{ scale: loading ? 1 : 1.02 }}
            whileTap={{ scale: loading ? 1 : 0.98 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.1 }}
          >
            {loading ? (
              <>
                <FiLoader className="spinner" />
                Creating Account...
              </>
            ) : (
              'Create Company Account'
            )}
          </motion.button>
        </form>

        {/* Footer Links */}
        <motion.div
          className="register-footer"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
        >
          <p>
            Already have an account?{' '}
            <Link to="/login" className="register-link">
              Sign In
            </Link>
          </p>
          <p className="register-note">
            By registering, you agree to our Terms of Service and Privacy Policy
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default CompanyRegister;

