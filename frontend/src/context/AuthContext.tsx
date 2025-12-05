import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, StudentProfile, CompanyProfile } from '../types';
import { authService } from '../services/authService';
import { facultyService } from '../services/facultyService';

interface AuthContextType {
  user: User | null;
  profile: StudentProfile | CompanyProfile | null;
  loading: boolean;
  login: (email: string, password: string, options?: { audience?: 'faculty' | 'default' }) => Promise<void>;
  register: (email: string, password: string, role: string, profile: any) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<StudentProfile | CompanyProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const data = await authService.getCurrentUser();
        setUser(data.user);
        setProfile(data.profile);
      } catch (error) {
        localStorage.removeItem('token');
      }
    }
    setLoading(false);
  };

  const login = async (email: string, password: string, options?: { audience?: 'faculty' | 'default' }) => {
    const data = options?.audience === 'faculty'
      ? await facultyService.login(email, password)
      : await authService.login(email, password);
    setUser(data.user);
    setProfile(data.profile);
    return data; // Return data so Login component can check needs_skills_setup
  };

  const register = async (email: string, password: string, role: string, profileData: any) => {
    const data = await authService.register(email, password, role, profileData);
    if (data.token) {
      localStorage.setItem('token', data.token);
      setUser(data.user);
      setProfile(data.profile);
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setProfile(null);
  };

  const refreshUser = async () => {
    const data = await authService.getCurrentUser();
    setUser(data.user);
    setProfile(data.profile);
  };

  return (
    <AuthContext.Provider value={{ user, profile, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

