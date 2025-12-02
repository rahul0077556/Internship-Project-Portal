import api from './api';
import { Notification } from '../types';

export const notificationService = {
  getAll: async (unreadOnly?: boolean, limit?: number): Promise<Notification[]> => {
    const response = await api.get('/notifications', {
      params: { unread_only: unreadOnly, limit },
    });
    return response.data;
  },

  markAsRead: async (id: number): Promise<void> => {
    await api.put(`/notifications/${id}/read`);
  },

  markAllAsRead: async (): Promise<void> => {
    await api.put('/notifications/read-all');
  },

  getUnreadCount: async (): Promise<number> => {
    const response = await api.get('/notifications/unread-count');
    return response.data.unread_count;
  },
};

