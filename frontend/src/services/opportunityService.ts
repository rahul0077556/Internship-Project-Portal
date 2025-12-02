import api from './api';
import { Opportunity } from '../types';

export const opportunityService = {
  getAll: async (filters?: {
    domain?: string;
    work_type?: string;
    search?: string;
    page?: number;
    per_page?: number;
  }): Promise<{ opportunities: Opportunity[]; pagination: any }> => {
    const response = await api.get('/opportunities', { params: filters });
    return response.data;
  },

  getById: async (id: number): Promise<Opportunity> => {
    const response = await api.get(`/opportunities/${id}`);
    return response.data;
  },

  getDomains: async (): Promise<string[]> => {
    const response = await api.get('/opportunities/domains');
    return response.data;
  },
};

