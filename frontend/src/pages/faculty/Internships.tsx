import React, { useEffect, useMemo, useState } from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import { facultyService } from '../../services/facultyService';
import { InternshipRow } from '../../types';
import './faculty.css';

const palette = ['#5b21b6', '#a855f7', '#38bdf8', '#34d399', '#fbbf24', '#f87171'];

const FacultyInternships: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [internships, setInternships] = useState<InternshipRow[]>([]);
  const [domainFilter, setDomainFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');

  useEffect(() => {
    const load = async () => {
      const [statsPayload, internshipsPayload] = await Promise.all([
        facultyService.getInternshipStats(),
        facultyService.getInternships(),
      ]);
      setStats(statsPayload);
      setInternships(internshipsPayload);
    };
    load();
  }, []);

  const filtered = useMemo(() => {
    return internships.filter((internship) => {
      if (domainFilter && internship.domain !== domainFilter) return false;
      if (typeFilter !== 'all' && internship.internship_type !== typeFilter) return false;
      return true;
    });
  }, [internships, domainFilter, typeFilter]);

  const skillPopularity = useMemo(() => {
    const counts: Record<string, number> = {};
    internships.forEach((internship) => {
      (internship.technologies || []).forEach((tech) => {
        const key = tech.trim();
        if (!key) return;
        counts[key] = (counts[key] || 0) + 1;
      });
    });
    return Object.entries(counts)
      .map(([skill, count]) => ({ skill, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8);
  }, [internships]);

  return (
    <div className="faculty-shell">
      <div className="faculty-heading">
        <h1>Internship Intelligence</h1>
        <p>Track internship domains, stipend trends, and PPO conversion signals.</p>
      </div>

      {stats && (
        <div className="faculty-grid three">
          <div className="stat-card">
            <h3>Total Internships</h3>
            <strong>{stats.total_internships}</strong>
          </div>
          <div className="stat-card">
            <h3>Paid Internships</h3>
            <strong>{stats.paid}</strong>
          </div>
          <div className="stat-card">
            <h3>Unpaid Internships</h3>
            <strong>{stats.unpaid}</strong>
          </div>
        </div>
      )}

      <div className="faculty-grid two" style={{ marginTop: '1.5rem' }}>
        <div className="chart-card">
          <h3>Domain Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie dataKey="count" data={stats?.domain_wise || []} innerRadius={60} outerRadius={100}>
                {(stats?.domain_wise || []).map((entry: any, index: number) => (
                  <Cell key={entry.domain} fill={palette[index % palette.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-card">
          <h3>Skill Popularity</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={skillPopularity}>
              <XAxis dataKey="skill" hide />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#0ea5e9" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="filters-card" style={{ marginTop: '1.5rem' }}>
        <h3>Filter Internship Table</h3>
        <div className="filters-grid">
          <label>
            Domain
            <select value={domainFilter} onChange={(e) => setDomainFilter(e.target.value)}>
              <option value="">All</option>
              {(stats?.domain_wise || []).map((domain: any) => (
                <option key={domain.domain} value={domain.domain}>
                  {domain.domain}
                </option>
              ))}
            </select>
          </label>
          <label>
            Internship Type
            <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
              <option value="all">All</option>
              <option value="Remote">Remote</option>
              <option value="Onsite">Onsite</option>
              <option value="Hybrid">Hybrid</option>
            </select>
          </label>
        </div>
      </div>

      <div className="table-card" style={{ marginTop: '1.5rem' }}>
        <h3>Internship Roster ({filtered.length})</h3>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Branch</th>
                <th>Organization</th>
                <th>Domain</th>
                <th>Type</th>
                <th>Stipend</th>
                <th>Timeline</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((intern) => (
                <tr key={`${intern.student_name}-${intern.organization}-${intern.designation}`}>
                  <td>{intern.student_name}</td>
                  <td>{intern.branch}</td>
                  <td>{intern.organization}</td>
                  <td>{intern.domain}</td>
                  <td>{intern.internship_type}</td>
                  <td>{intern.is_paid ? intern.stipend || 'Paid' : 'Unpaid'}</td>
                  <td>
                    {intern.start_date ? new Date(intern.start_date).toLocaleDateString() : '—'} →{' '}
                    {intern.end_date ? new Date(intern.end_date).toLocaleDateString() : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default FacultyInternships;

