import api from './api';
import { CompanyProfile, Opportunity, Application } from '../types';

export const companyService = {
  getProfile: async (): Promise<CompanyProfile> => {
    const response = await api.get('/company/profile');
    return response.data;
  },

  updateProfile: async (profile: Partial<CompanyProfile>): Promise<CompanyProfile> => {
    const response = await api.put('/company/profile', profile);
    return response.data.profile;
  },

  createOpportunity: async (opportunity: Partial<Opportunity>): Promise<Opportunity> => {
    const response = await api.post('/company/opportunities', opportunity);
    return response.data.opportunity;
  },

  getOpportunities: async (): Promise<Opportunity[]> => {
    const response = await api.get('/company/opportunities');
    return response.data;
  },

  updateOpportunity: async (id: number, opportunity: Partial<Opportunity>): Promise<Opportunity> => {
    const response = await api.put(`/company/opportunities/${id}`, opportunity);
    return response.data.opportunity;
  },

  getApplicants: async (opportunityId: number, status?: string): Promise<Application[]> => {
    const response = await api.get(`/company/opportunities/${opportunityId}/applicants`, {
      params: { status },
    });
    return response.data;
  },

  updateApplicationStatus: async (
    applicationId: number,
    status: string,
    notes?: string
  ): Promise<Application> => {
    const response = await api.put(`/company/applications/${applicationId}/status`, {
      status,
      notes,
    });
    return response.data.application;
  },

  getDashboard: async () => {
    const response = await api.get('/company/dashboard');
    return response.data;
  },

  screenApplicants: async (opportunityId: number): Promise<Application[]> => {
    const response = await api.get(`/ai/screening/${opportunityId}`);
    return response.data;
  },
};

