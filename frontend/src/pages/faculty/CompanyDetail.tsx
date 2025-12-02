import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { facultyService } from '../../services/facultyService';
import './faculty.css';

const FacultyCompanyDetail: React.FC = () => {
  const { companyName = '' } = useParams();
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        if (!companyName) return;
        const payload = await facultyService.getCompanyBreakdown(companyName);
        setData(payload);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Unable to load company analytics');
      }
    };
    load();
  }, [companyName]);

  if (error) {
    return (
      <div className="faculty-shell">
        <div className="faculty-heading">
          <h1>Company Insights</h1>
          <p className="faculty-error">{error}</p>
        </div>
        <Link to="/faculty/placements" className="link">
          ← Back to placements
        </Link>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="faculty-shell">
        <div className="faculty-heading">
          <h1>Company Insights</h1>
          <p>Loading snapshot...</p>
        </div>
      </div>
    );
  }

  const { summary, students } = data;

  return (
    <div className="faculty-shell">
      <div className="faculty-heading">
        <h1>{summary.company}</h1>
        <p>
          {summary.total_students} students placed • Average Package {summary.avg_package_lpa || '—'} LPA
        </p>
        <Link to="/faculty/placements" className="link">
          ← Back to placements
        </Link>
      </div>

      <div className="faculty-grid three">
        <motion.div className="stat-card">
          <h3>Min Package</h3>
          <strong>{summary.min_package_lpa || '—'} LPA</strong>
        </motion.div>
        <motion.div className="stat-card">
          <h3>Max Package</h3>
          <strong>{summary.max_package_lpa || '—'} LPA</strong>
        </motion.div>
        <motion.div className="stat-card">
          <h3>Roles Offered</h3>
          <strong>{summary.roles.length}</strong>
        </motion.div>
      </div>

      <div className="chart-card" style={{ marginTop: '1.5rem' }}>
        <h3>Branch Distribution</h3>
        <div className="faculty-grid two">
          {summary.branch_breakdown.map((branch: any) => (
            <div key={branch.branch} className="report-card">
              <h4>{branch.branch}</h4>
              <p>{branch.count} students</p>
            </div>
          ))}
        </div>
      </div>

      <div className="table-card" style={{ marginTop: '1.5rem' }}>
        <h3>Student List</h3>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Branch</th>
                <th>Role</th>
                <th>Package</th>
                <th>Location</th>
                <th>Joining</th>
              </tr>
            </thead>
            <tbody>
              {students.map((student: any) => (
                <tr key={`${student.prn}-${student.company}`}>
                  <td>{student.student_name}</td>
                  <td>{student.branch}</td>
                  <td>{student.role}</td>
                  <td>{student.package_lpa ? `${student.package_lpa} LPA` : '—'}</td>
                  <td>{student.location}</td>
                  <td>{student.joining_date ? new Date(student.joining_date).toLocaleDateString() : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default FacultyCompanyDetail;

