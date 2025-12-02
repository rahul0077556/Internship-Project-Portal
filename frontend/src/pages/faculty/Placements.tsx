import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { FiDownload, FiX } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';
import { facultyService } from '../../services/facultyService';
import { PlacementRow } from '../../types';
import './faculty.css';

const PAGE_SIZE = 12;

const FacultyPlacements: React.FC = () => {
  const [placements, setPlacements] = useState<PlacementRow[]>([]);
  const [filters, setFilters] = useState({
    branches: [] as string[],
    companies: [] as string[],
    batches: [] as string[],
    gender: '',
    minPackage: '',
    maxPackage: '',
    type: 'all',
  });
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState<keyof PlacementRow>('student_name');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<any>(null);
  const [filtersData, setFiltersData] = useState({
    branches: [] as string[],
    companies: [] as string[],
    batches: [] as string[],
  });

  useEffect(() => {
    const load = async () => {
      const [rows, branches, companies, batches] = await Promise.all([
        facultyService.getPlacements(),
        facultyService.getFilterBranches(),
        facultyService.getFilterCompanies(),
        facultyService.getFilterBatches(),
      ]);
      setPlacements(rows);
      setFiltersData({
        branches,
        companies,
        batches,
      });
    };
    load();
  }, []);

  const handleMultiSelect = (event: React.ChangeEvent<HTMLSelectElement>, key: 'branches' | 'companies' | 'batches') => {
    const selectedOptions = Array.from(event.target.selectedOptions).map((option) => option.value);
    setFilters((prev) => ({ ...prev, [key]: selectedOptions }));
    setPage(1);
  };

  const filteredData = useMemo(() => {
    let rows = [...placements];
    if (search) {
      rows = rows.filter((placement) =>
        placement.student_name.toLowerCase().includes(search.toLowerCase()) ||
        (placement.company || '').toLowerCase().includes(search.toLowerCase()) ||
        (placement.branch || '').toLowerCase().includes(search.toLowerCase())
      );
    }
    if (filters.branches.length > 0) {
      rows = rows.filter((row) => row.branch && filters.branches.includes(row.branch));
    }
    if (filters.companies.length > 0) {
      rows = rows.filter((row) => row.company && filters.companies.includes(row.company));
    }
    if (filters.batches.length > 0) {
      rows = rows.filter((row) => {
        const dateSource = row.joining_date || row.offer_date;
        if (!dateSource) return false;
        const year = new Date(dateSource).getFullYear().toString();
        return filters.batches.includes(year);
      });
    }
    if (filters.minPackage) {
      rows = rows.filter((row) => (row.ctc_lpa || 0) >= Number(filters.minPackage));
    }
    if (filters.maxPackage) {
      rows = rows.filter((row) => (row.ctc_lpa || 0) <= Number(filters.maxPackage));
    }
    rows.sort((a: any, b: any) => {
      const valueA = a[sortKey] || '';
      const valueB = b[sortKey] || '';
      if (valueA < valueB) return sortDirection === 'asc' ? -1 : 1;
      if (valueA > valueB) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
    return rows;
  }, [placements, search, filters, sortDirection, sortKey]);

  const paginated = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return filteredData.slice(start, start + PAGE_SIZE);
  }, [filteredData, page]);

  const totalPages = Math.ceil(filteredData.length / PAGE_SIZE) || 1;

  const handleSort = (key: keyof PlacementRow) => {
    if (sortKey === key) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  const handleRowClick = async (row: PlacementRow) => {
    if (!row.prn) return;
    try {
      const detail = await facultyService.getStudentPlacement(row.prn);
      setSelected(detail);
    } catch (error) {
      const [firstName, ...rest] = row.student_name.split(' ');
      setSelected({
        student: {
          first_name: firstName,
          last_name: rest.join(' '),
          prn_number: row.prn,
          course: row.branch,
        },
        offers: [row],
        internships: [],
      });
    }
  };

  const downloadCsv = async () => {
    const blob = (await facultyService.downloadReport('placement', 'csv')) as Blob;
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `placement-report.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const downloadJson = async () => {
    const payload = (await facultyService.downloadReport('placement', 'json')) as any;
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `placement-report.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="faculty-shell">
      <div className="faculty-heading">
        <h1>Placement Intelligence</h1>
        <p>Search, filter, and audit every student placement record in seconds.</p>
      </div>

      <div className="filters-card">
        <h3>Advanced Filters</h3>
        <div className="filters-grid">
          <label>
            Branch
            <select multiple value={filters.branches} onChange={(e) => handleMultiSelect(e, 'branches')}>
              {filtersData.branches.map((branch) => (
                <option value={branch} key={branch}>
                  {branch}
                </option>
              ))}
            </select>
          </label>
          <label>
            Company
            <select multiple value={filters.companies} onChange={(e) => handleMultiSelect(e, 'companies')}>
              {filtersData.companies.map((company) => (
                <option value={company} key={company}>
                  {company}
                </option>
              ))}
            </select>
          </label>
          <label>
            Batch (year)
            <select multiple value={filters.batches} onChange={(e) => handleMultiSelect(e, 'batches')}>
              {filtersData.batches.map((batch) => (
                <option value={batch} key={batch}>
                  {batch}
                </option>
              ))}
            </select>
          </label>
          <label>
            Min Package (LPA)
            <input
              type="number"
              placeholder="0"
              value={filters.minPackage}
              onChange={(e) => setFilters({ ...filters, minPackage: e.target.value })}
            />
          </label>
          <label>
            Max Package (LPA)
            <input
              type="number"
              placeholder="30"
              value={filters.maxPackage}
              onChange={(e) => setFilters({ ...filters, maxPackage: e.target.value })}
            />
          </label>
          <label>
            Placement Type
            <select
              value={filters.type}
              onChange={(e) => setFilters((prev) => ({ ...prev, type: e.target.value }))}
            >
              <option value="all">All</option>
              <option value="full-time">Full-Time</option>
              <option value="internship">Internship</option>
              <option value="ppo">Internship → PPO</option>
            </select>
          </label>
        </div>

        <div className="filters-actions">
          <button className="btn-primary-gradient" onClick={() => setPage(1)}>
            Apply Filters
          </button>
          <button
            className="btn-soft"
            onClick={() =>
              setFilters({
                branches: [],
                companies: [],
                batches: [],
                gender: '',
                minPackage: '',
                maxPackage: '',
                type: 'all',
              })
            }
          >
            Clear Filters
          </button>
          <button className="btn-soft" onClick={downloadCsv}>
            <FiDownload /> Export Excel
          </button>
          <button className="btn-soft" onClick={downloadJson}>
            <FiDownload /> Export JSON
          </button>
        </div>
      </div>

      <div className="table-card" style={{ marginTop: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <input
            type="text"
            className="search-input"
            placeholder="Search by name, PRN, company..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
          <span className="badge">{filteredData.length} records</span>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                {[
                  { key: 'student_name', label: 'Student' },
                  { key: 'prn', label: 'PRN' },
                  { key: 'branch', label: 'Branch' },
                  { key: 'company', label: 'Company' },
                  { key: 'role', label: 'Role' },
                  { key: 'ctc', label: 'Package' },
                  { key: 'location', label: 'Location' },
                  { key: 'joining_date', label: 'Joining' },
                ].map((column) => (
                  <th key={column.key} onClick={() => handleSort(column.key as keyof PlacementRow)}>
                    {column.label}
                  </th>
                ))}
                <th>Insights</th>
              </tr>
            </thead>
            <tbody>
              {paginated.map((row) => (
                <tr key={`${row.prn}-${row.company}`} onClick={() => handleRowClick(row)}>
                  <td>{row.student_name}</td>
                  <td>{row.prn}</td>
                  <td>{row.branch}</td>
                  <td>{row.company}</td>
                  <td>{row.role}</td>
                  <td>{row.ctc || `${row.ctc_lpa ?? '-'} LPA`}</td>
                  <td>{row.location}</td>
                  <td>{row.joining_date ? new Date(row.joining_date).toLocaleDateString() : '—'}</td>
                  <td>
                    {row.company && (
                      <Link to={`/faculty/companies/${encodeURIComponent(row.company)}`} className="link" onClick={(e) => e.stopPropagation()}>
                        View
                      </Link>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="pagination">
          <button disabled={page === 1} onClick={() => setPage((prev) => Math.max(prev - 1, 1))}>
            Prev
          </button>
          <span>
            Page {page} of {totalPages}
          </span>
          <button disabled={page === totalPages} onClick={() => setPage((prev) => Math.min(prev + 1, totalPages))}>
            Next
          </button>
        </div>
      </div>

      <AnimatePresence>
        {selected && (
          <motion.div
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelected(null)}
          >
            <motion.div
              className="modal-card"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <button className="modal-close" onClick={() => setSelected(null)}>
                <FiX />
              </button>
              <h2>
                {selected.student?.first_name
                  ? `${selected.student.first_name} ${selected.student.last_name || ''}`.trim()
                  : selected.student_name || 'Student'}
              </h2>
              <p>
                PRN: {selected.student?.prn_number || selected.student?.prn || '—'} • Branch:{' '}
                {selected.student?.course || selected.student?.branch || '—'}
              </p>

              <h3>Offers</h3>
              <ul>
                {(selected.offers || []).map((offer: any) => (
                  <li key={offer.id || offer.company}>
                    <strong>{offer.company_name || offer.company}</strong> — {offer.role}{' '}
                    ({offer.ctc || (offer.ctc_lpa ? `${offer.ctc_lpa} LPA` : '—')})
                  </li>
                ))}
              </ul>

              <h3>Internships</h3>
              <ul>
                {(selected.internships || []).length === 0 && <li>No internships recorded.</li>}
                {(selected.internships || []).map((intern: any) => (
                  <li key={intern.id}>
                    {intern.designation} @ {intern.organization} ({intern.internship_type})
                  </li>
                ))}
              </ul>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FacultyPlacements;

