import React, { useState, useEffect, useMemo } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { notificationService } from '../services/notificationService';
import { 
  FiBriefcase, 
  FiFileText, 
  FiMessageSquare, 
  FiBell, 
  FiUser, 
  FiLogOut,
  FiSun,
  FiMoon,
  FiMenu,
  FiX,
  FiHome,
  FiLayers
} from 'react-icons/fi';
import './Layout.css';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [unreadCount, setUnreadCount] = useState(0);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    if (user) {
      loadUnreadCount();
      const interval = setInterval(loadUnreadCount, 30000);
      return () => clearInterval(interval);
    }
  }, [user]);

  const loadUnreadCount = async () => {
    try {
      const count = await notificationService.getUnreadCount();
      setUnreadCount(count);
    } catch (error) {
      console.error('Error loading unread count:', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  const navItems = useMemo(() => {
    if (!user) return [];
    if (user.role === 'student') {
      return [
        { path: '/dashboard', label: 'Dashboard', icon: FiHome },
        { path: '/student/opportunities', label: 'Opportunities', icon: FiBriefcase },
        { path: '/student/applications', label: 'Applications', icon: FiFileText },
        { path: '/student/profile', label: 'Profile', icon: FiUser },
      ];
    }
    if (user.role === 'faculty' || user.role === 'admin') {
      return [
        { path: '/dashboard', label: 'Dashboard', icon: FiHome },
        { path: '/faculty/placements', label: 'Placements', icon: FiBriefcase },
        { path: '/faculty/internships', label: 'Internships', icon: FiLayers },
        { path: '/faculty/reports', label: 'Reports', icon: FiFileText },
        { path: '/faculty/settings', label: 'Settings', icon: FiUser },
      ];
    }
    return [
      { path: '/dashboard', label: 'Dashboard', icon: FiHome },
      { path: '/company/opportunities', label: 'Opportunities', icon: FiBriefcase },
      { path: '/company/profile', label: 'Profile', icon: FiUser },
    ];
  }, [user]);

  const subtitle = user?.role === 'faculty' ? 'Faculty Analytics' : 'Student Portal';

  return (
    <div className="layout">
      <motion.nav 
        className="navbar"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="nav-container">
          <Link to="/dashboard" className="nav-logo">
            <span className="logo-text">RNSSS</span>
            <span className="logo-subtitle">{subtitle}</span>
          </Link>

          {/* Desktop Menu */}
          <div className="nav-menu">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
            
            <Link
              to="/messages"
              className={`nav-link ${isActive('/messages') ? 'active' : ''}`}
            >
              <FiMessageSquare size={18} />
              <span>Messages</span>
            </Link>
            
            <Link
              to="/notifications"
              className={`nav-link ${isActive('/notifications') ? 'active' : ''}`}
            >
              <FiBell size={18} />
              <span>Notifications</span>
              {unreadCount > 0 && (
                <motion.span
                  className="nav-badge"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                >
                  {unreadCount}
                </motion.span>
              )}
            </Link>

            <motion.button
              className="theme-toggle-btn"
              onClick={toggleTheme}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <FiSun size={18} /> : <FiMoon size={18} />}
            </motion.button>

            <motion.button
              className="logout-btn"
              onClick={handleLogout}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <FiLogOut size={18} />
              <span>Logout</span>
            </motion.button>
          </div>

          {/* Mobile Menu Toggle */}
          <button
            className="mobile-menu-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <motion.div
            className="mobile-menu"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`mobile-nav-link ${isActive(item.path) ? 'active' : ''}`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Icon size={20} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
            <Link
              to="/messages"
              className={`mobile-nav-link ${isActive('/messages') ? 'active' : ''}`}
              onClick={() => setMobileMenuOpen(false)}
            >
              <FiMessageSquare size={20} />
              <span>Messages</span>
            </Link>
            <Link
              to="/notifications"
              className={`mobile-nav-link ${isActive('/notifications') ? 'active' : ''}`}
              onClick={() => setMobileMenuOpen(false)}
            >
              <FiBell size={20} />
              <span>Notifications</span>
              {unreadCount > 0 && <span className="nav-badge">{unreadCount}</span>}
            </Link>
            <button
              className="mobile-nav-link"
              onClick={() => {
                toggleTheme();
                setMobileMenuOpen(false);
              }}
            >
              {theme === 'dark' ? <FiSun size={20} /> : <FiMoon size={20} />}
              <span>Toggle Theme</span>
            </button>
            <button
              className="mobile-nav-link"
              onClick={() => {
                handleLogout();
                setMobileMenuOpen(false);
              }}
            >
              <FiLogOut size={20} />
              <span>Logout</span>
            </button>
          </motion.div>
        )}
      </motion.nav>

      <main className="main-content">
        {children}
      </main>
    </div>
  );
};

export default Layout;
