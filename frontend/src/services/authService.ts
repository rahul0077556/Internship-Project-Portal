import api from './api';
import { User, StudentProfile, CompanyProfile } from '../types';

export const authService = {
  register: async (email: string, password: string, role: string, profile: any) => {
    const response = await api.post('/auth/register', { email, password, role, profile });
    return response.data;
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    localStorage.setItem('token', response.data.token);
    return response.data;
  },

  getCurrentUser: async (): Promise<{ user: User; profile: StudentProfile | CompanyProfile | null }> => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
  },
};

