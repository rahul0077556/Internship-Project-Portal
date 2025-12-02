import api from './api';
import {
  FacultyDashboardResponse,
  PlacementRow,
  PlacementFilters,
  InternshipRow,
  FacultyReportPayload,
} from '../types';

export const facultyService = {
  login: async (email: string, password: string) => {
    const response = await api.post('/faculty/login', { email, password });
    if (response.data?.token) {
      localStorage.setItem('token', response.data.token);
    }
    return response.data;
  },

  getDashboard: async (): Promise<FacultyDashboardResponse> => {
    const response = await api.get('/faculty/stats');
    return response.data;
  },

  getPlacementStats: async () => {
    const response = await api.get('/faculty/placements/stats');
    return response.data;
  },

  getPlacements: async (filters?: PlacementFilters): Promise<PlacementRow[]> => {
    const response = await api.get('/faculty/placements/all', { params: filters });
    return response.data;
  },

  getCompanyBreakdown: async (companyName: string) => {
    const response = await api.get(`/faculty/placements/company/${encodeURIComponent(companyName)}`);
    return response.data;
  },

  getBranchBreakdown: async (branchName: string) => {
    const response = await api.get(`/faculty/placements/branch/${encodeURIComponent(branchName)}`);
    return response.data;
  },

  getStudentPlacement: async (prn: string) => {
    const response = await api.get(`/faculty/placements/student/${encodeURIComponent(prn)}`);
    return response.data;
  },

  getInternshipStats: async () => {
    const response = await api.get('/faculty/internships/stats');
    return response.data;
  },

  getInternships: async (params?: Record<string, any>): Promise<InternshipRow[]> => {
    const response = await api.get('/faculty/internships/all', { params });
    return response.data;
  },

  getFilterBranches: async () => {
    const response = await api.get('/faculty/filters/branches');
    return response.data;
  },

  getFilterCompanies: async () => {
    const response = await api.get('/faculty/filters/companies');
    return response.data;
  },

  getFilterPackages: async () => {
    const response = await api.get('/faculty/filters/packages');
    return response.data;
  },

  getFilterSkills: async () => {
    const response = await api.get('/faculty/filters/skills');
    return response.data;
  },

  getFilterBatches: async () => {
    const response = await api.get('/faculty/filters/batches');
    return response.data;
  },

  getFilterDomains: async () => {
    const response = await api.get('/faculty/filters/domains');
    return response.data;
  },

  getFilterGenders: async () => {
    const response = await api.get('/faculty/filters/genders');
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get('/faculty/profile');
    return response.data;
  },

  updateProfile: async (payload: Record<string, any>) => {
    const response = await api.patch('/faculty/profile/update', payload);
    return response.data;
  },

  downloadReport: async (
    type: 'placement' | 'internship' | 'branch' | 'company' | 'yearly',
    format: 'json' | 'csv' = 'json'
  ): Promise<FacultyReportPayload | Blob> => {
    const response = await api.get(`/faculty/reports/${type}`, {
      params: { format },
      responseType: format === 'csv' ? 'blob' : 'json',
    });
    return response.data;
  },
};

