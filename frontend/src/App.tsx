import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Login from './pages/Login';
import Register from './pages/Register';
import CompanyRegister from './pages/CompanyRegister';
import FacultyLogin from './pages/faculty/Login';
import StudentDashboard from './pages/student/Dashboard';
import StudentProfile from './pages/student/Profile';
import StudentOpportunities from './pages/student/Opportunities';
import StudentApplications from './pages/student/Applications';
import CompanyDashboard from './pages/company/Dashboard';
import CompanyProfile from './pages/company/Profile';
import CompanyOpportunities from './pages/company/Opportunities';
import CompanyApplicants from './pages/company/Applicants';
import CreateInternship from './pages/company/CreateInternship';
import FacultyDashboard from './pages/faculty/Dashboard';
import FacultyPlacements from './pages/faculty/Placements';
import FacultyCompanyDetail from './pages/faculty/CompanyDetail';
import FacultyInternships from './pages/faculty/Internships';
import FacultyReports from './pages/faculty/Reports';
import FacultySettings from './pages/faculty/Settings';
import Messages from './pages/Messages';
import Notifications from './pages/Notifications';
import Layout from './components/Layout';
import ErrorBoundary from './components/ErrorBoundary';

const PrivateRoute: React.FC<{ children: React.ReactElement; allowedRoles?: string[] }> = ({
  children,
  allowedRoles,
}) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" />;
  }

  return children;
};

const AppRoutes: React.FC = () => {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={!user ? <Login /> : <Navigate to="/dashboard" />} />
      <Route path="/register" element={!user ? <Register /> : <Navigate to="/dashboard" />} />
      <Route path="/company/register" element={!user ? <CompanyRegister /> : <Navigate to="/dashboard" />} />
      <Route path="/faculty/login" element={!user ? <FacultyLogin /> : <Navigate to="/dashboard" />} />
      
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Layout>
              {user?.role === 'student'
                ? <StudentDashboard />
                : user?.role === 'company'
                ? <CompanyDashboard />
                : <FacultyDashboard />}
            </Layout>
          </PrivateRoute>
        }
      />

      {/* Student Routes */}
      <Route
        path="/student/profile"
        element={
          <PrivateRoute allowedRoles={['student']}>
            <Layout>
              <StudentProfile />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/student/opportunities"
        element={
          <PrivateRoute allowedRoles={['student']}>
            <Layout>
              <StudentOpportunities />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/student/applications"
        element={
          <PrivateRoute allowedRoles={['student']}>
            <Layout>
              <StudentApplications />
            </Layout>
          </PrivateRoute>
        }
      />

      {/* Company/Faculty Routes */}
      <Route
        path="/company/profile"
        element={
          <PrivateRoute allowedRoles={['company', 'faculty']}>
            <Layout>
              <CompanyProfile />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/company/opportunities"
        element={
          <PrivateRoute allowedRoles={['company', 'faculty']}>
            <Layout>
              <CompanyOpportunities />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/company/opportunities/create"
        element={
          <PrivateRoute allowedRoles={['company', 'faculty']}>
            <Layout>
              <CreateInternship />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/company/opportunities/:id"
        element={
          <PrivateRoute allowedRoles={['company', 'faculty']}>
            <Layout>
              <CreateInternship />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/company/applicants/:opportunityId"
        element={
          <PrivateRoute allowedRoles={['company', 'faculty']}>
            <Layout>
              <CompanyApplicants />
            </Layout>
          </PrivateRoute>
        }
      />

      {/* Faculty Routes */}
      <Route
        path="/faculty/placements"
        element={
          <PrivateRoute allowedRoles={['faculty', 'admin']}>
            <Layout>
              <FacultyPlacements />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/faculty/companies/:companyName"
        element={
          <PrivateRoute allowedRoles={['faculty', 'admin']}>
            <Layout>
              <FacultyCompanyDetail />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/faculty/internships"
        element={
          <PrivateRoute allowedRoles={['faculty', 'admin']}>
            <Layout>
              <FacultyInternships />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/faculty/reports"
        element={
          <PrivateRoute allowedRoles={['faculty', 'admin']}>
            <Layout>
              <FacultyReports />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/faculty/settings"
        element={
          <PrivateRoute allowedRoles={['faculty', 'admin']}>
            <Layout>
              <FacultySettings />
            </Layout>
          </PrivateRoute>
        }
      />

      {/* Common Routes */}
      <Route
        path="/messages"
        element={
          <PrivateRoute>
            <Layout>
              <Messages />
            </Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/notifications"
        element={
          <PrivateRoute>
            <Layout>
              <Notifications />
            </Layout>
          </PrivateRoute>
        }
      />

      <Route path="/" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
};

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AuthProvider>
          <Router>
            <AppRoutes />
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
};

export default App;

