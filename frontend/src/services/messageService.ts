import api from './api';
import { Message } from '../types';

export const messageService = {
  getAll: async (conversationWith?: number, type?: string): Promise<Message[]> => {
    const response = await api.get('/messages', {
      params: { conversation_with: conversationWith, type },
    });
    return response.data;
  },

  send: async (
    receiverId: number,
    content: string,
    subject?: string,
    messageType?: string,
    relatedApplicationId?: number
  ): Promise<Message> => {
    const response = await api.post('/messages', {
      receiver_id: receiverId,
      content,
      subject,
      message_type: messageType,
      related_application_id: relatedApplicationId,
    });
    return response.data.data;
  },

  markAsRead: async (id: number): Promise<void> => {
    await api.put(`/messages/${id}/read`);
  },

  getConversations: async (): Promise<any[]> => {
    const response = await api.get('/messages/conversations');
    return response.data;
  },
};

