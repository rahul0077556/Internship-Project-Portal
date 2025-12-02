import api from './api';
import { Application } from '../types';

export const applicationService = {
  apply: async (opportunityId: number, coverLetter?: string): Promise<Application> => {
    const response = await api.post('/applications', {
      opportunity_id: opportunityId,
      cover_letter: coverLetter,
    });
    return response.data.application;
  },

  getById: async (id: number): Promise<Application> => {
    const response = await api.get(`/applications/${id}`);
    return response.data;
  },

  withdraw: async (id: number): Promise<void> => {
    await api.delete(`/applications/${id}`);
  },
};

