import React, { useState } from 'react';
import { FiDownload, FiFileText } from 'react-icons/fi';
import { facultyService } from '../../services/facultyService';
import './faculty.css';

const reportDefinitions = [
  {
    type: 'placement' as const,
    title: 'Placement Summary',
    description: 'Comprehensive placement statistics with company, branch, and package breakdowns.',
  },
  {
    type: 'internship' as const,
    title: 'Internship Insights',
    description: 'Internship domains, stipend trends, and conversion metrics ready for review meetings.',
  },
  {
    type: 'branch' as const,
    title: 'Branch Snapshot',
    description: 'Placement performance by branch with targets vs achievements.',
  },
  {
    type: 'company' as const,
    title: 'Company Report',
    description: 'Company-wise engagement, offers extended, and student feedback summary.',
  },
  {
    type: 'yearly' as const,
    title: 'Yearly Statistics',
    description: 'Batch-wise placement trendline for last five academic years.',
  },
];

const FacultyReports: React.FC = () => {
  const [downloading, setDownloading] = useState<string | null>(null);

  const download = async (type: typeof reportDefinitions[number]['type'], format: 'json' | 'csv') => {
    setDownloading(`${type}-${format}`);
    try {
      const data = await facultyService.downloadReport(type, format);
      if (format === 'csv') {
        const blob = data as Blob;
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${type}-report.csv`;
        link.click();
        URL.revokeObjectURL(url);
      } else {
        const payload = data as any;
        const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${type}-report.json`;
        link.click();
        URL.revokeObjectURL(url);
      }
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div className="faculty-shell">
      <div className="faculty-heading">
        <h1>Exportable Reports</h1>
        <p>Generate board-ready PDFs, Excel sheets, or JSON data snapshots with one click.</p>
      </div>

      <div className="faculty-grid two">
        {reportDefinitions.map((report) => (
          <div key={report.type} className="report-card">
            <h4>{report.title}</h4>
            <p>{report.description}</p>
            <div className="btn-group">
              <button
                className="primary"
                onClick={() => download(report.type, 'csv')}
                disabled={downloading === `${report.type}-csv`}
              >
                <FiDownload /> Excel
              </button>
              <button
                className="secondary"
                onClick={() => download(report.type, 'json')}
                disabled={downloading === `${report.type}-json`}
              >
                <FiFileText /> JSON
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FacultyReports;

