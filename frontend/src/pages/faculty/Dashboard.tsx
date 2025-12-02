import React, { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts';
import { FiUsers, FiTrendingUp, FiAward, FiBriefcase, FiLayers, FiActivity } from 'react-icons/fi';
import { facultyService } from '../../services/facultyService';
import { FacultyDashboardResponse } from '../../types';
import './faculty.css';

const chartColors = ['#5b21b6', '#c084fc', '#38bdf8', '#34d399', '#f97316', '#ef4444'];

const FacultyDashboard: React.FC = () => {
  const [dashboard, setDashboard] = useState<FacultyDashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const data = await facultyService.getDashboard();
        setDashboard(data);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Unable to load analytics');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const statCards = useMemo(() => {
    if (!dashboard) return [];
    return [
      {
        label: 'Total Placed Students',
        value: dashboard.stats.placed_students,
        icon: <FiUsers />,
        accent: '#22c55e',
      },
      {
        label: 'Students Seeking Opportunities',
        value: dashboard.stats.unplaced_students,
        icon: <FiActivity />,
        accent: '#f97316',
      },
      {
        label: 'Internships Completed',
        value: dashboard.stats.total_internships,
        icon: <FiBriefcase />,
        accent: '#0ea5e9',
      },
      {
        label: 'Highest Package (LPA)',
        value: dashboard.stats.highest_package_lpa,
        icon: <FiAward />,
        accent: '#fcd34d',
      },
      {
        label: 'Average Package (LPA)',
        value: dashboard.stats.average_package_lpa,
        icon: <FiTrendingUp />,
        accent: '#5b21b6',
      },
      {
        label: 'Companies Visited',
        value: dashboard.stats.total_companies,
        icon: <FiLayers />,
        accent: '#06b6d4',
      },
    ];
  }, [dashboard]);

  if (loading) {
    return (
      <div className="faculty-shell">
        <div className="faculty-heading">
          <h1>Faculty Analytics</h1>
          <p>Loading placement intelligence…</p>
        </div>
        <div className="faculty-grid three">
          {[...Array(6)].map((_, idx) => (
            <div key={idx} className="stat-card" style={{ opacity: 0.4 }}>
              <div className="skeleton skeleton-text" />
              <div className="skeleton skeleton-number" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !dashboard) {
    return (
      <div className="faculty-shell">
        <div className="faculty-heading">
          <h1>Faculty Analytics</h1>
          <p className="faculty-error">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="faculty-shell">
      <div className="faculty-heading">
        <h1>Faculty Analytics Control Room</h1>
        <p>Monitor placements, internships, and trends for every batch</p>
      </div>

      <div className="faculty-grid three">
        {statCards.map((card) => (
          <motion.div
            key={card.label}
            className="stat-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h3 style={{ color: card.accent }}>
              {card.icon}
              {card.label}
            </h3>
            <strong>{card.value}</strong>
            <span className="stat-trend">Live</span>
          </motion.div>
        ))}
      </div>

      <div className="faculty-grid two" style={{ marginTop: '1.5rem' }}>
        <div className="chart-card">
          <h3>Company-wise Placements</h3>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={dashboard.charts.company_wise}>
              <XAxis dataKey="company" hide />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="placed" fill="#5b21b6" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Branch Placement Distribution</h3>
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Pie
                data={dashboard.charts.branch_wise}
                dataKey="placed"
                nameKey="branch"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={4}
              >
                {dashboard.charts.branch_wise.map((entry, index) => (
                  <Cell key={entry.branch} fill={chartColors[index % chartColors.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => `${value} students`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="faculty-grid two" style={{ marginTop: '1.5rem' }}>
        <div className="chart-card">
          <h3>Package Distribution (LPA)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={dashboard.charts.package_distribution}>
              <XAxis dataKey="range" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#34d399" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Batch-wise Placement Trends</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={dashboard.charts.batch_trends}>
              <XAxis dataKey="year" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="placed"
                stroke="#0ea5e9"
                strokeWidth={3}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default FacultyDashboard;

