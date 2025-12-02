import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FiShield, FiMail, FiLock, FiLoader } from 'react-icons/fi';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './faculty.css';
import './FacultyLogin.css';

const FacultyLogin: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password, { audience: 'faculty' });
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="faculty-login-shell">
      <div className="faculty-login-backdrop">
        <div className="orb orb-one" />
        <div className="orb orb-two" />
      </div>
      <motion.div
        className="faculty-login-card"
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="faculty-login-header">
          <motion.div
            className="logo"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            <FiShield size={28} />
          </motion.div>
          <div>
            <h1>RNSSS Faculty Console</h1>
            <p>Secure analytics access for placement coordinators</p>
          </div>
        </div>

        {error && (
          <motion.div
            className="faculty-login-error"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {error}
          </motion.div>
        )}

        <form className="faculty-login-form" onSubmit={handleSubmit}>
          <label>
            Email Address
            <div className="input-wrapper">
              <FiMail />
              <input
                type="email"
                placeholder="faculty@pict.edu"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </label>
          <label>
            Password
            <div className="input-wrapper">
              <FiLock />
              <input
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>
          </label>
          <div className="login-meta">
            <Link to="#" className="link">
              Forgot password?
            </Link>
          </div>

          <motion.button
            type="submit"
            className="cta-button"
            disabled={loading}
            whileHover={!loading ? { scale: 1.01 } : {}}
            whileTap={!loading ? { scale: 0.98 } : {}}
          >
            {loading ? (
              <>
                <FiLoader className="spinner" />
                Securing access...
              </>
            ) : (
              'Enter Faculty Dashboard'
            )}
          </motion.button>
        </form>

        <div className="login-footer">
          <p>
            Need a faculty account? Contact the placement cell administrator.
          </p>
          <p>
            Looking for student or company login?{' '}
            <Link to="/login" className="link">
              Go to main portal
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default FacultyLogin;

