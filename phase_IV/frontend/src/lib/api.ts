import axios, { AxiosInstance } from 'axios';
import {
  Task,
  TaskListResponse,
  ChatRequest,
  ChatResponse,
  ConversationListResponse,
  ConversationMessagesResponse
} from '../types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor for Token
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// --- SERVICES EXPORTS (Ye missing thay) ---

export const taskService = {
  getTasks: () => api.get<TaskListResponse>('/tasks'),
  createTask: (data: Partial<Task>) => api.post<Task>('/tasks', data),
  updateTask: (id: string, data: Partial<Task>) => api.put<Task>(`/tasks/${id}`, data),
  deleteTask: (id: string) => api.delete(`/tasks/${id}`),
};

export const chatService = {
  getConversations: () => api.get<ConversationListResponse>('/chat/conversations'),
  getMessages: (conversationId: string) => api.get<ConversationMessagesResponse>(`/chat/conversations/${conversationId}/messages`),
  sendMessage: (data: ChatRequest) => api.post<ChatResponse>('/chat/message', data),
};
