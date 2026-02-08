import axios, { AxiosInstance } from 'axios';
import {
  Task,
  TaskListResponse,
  ChatRequest,
  ChatResponse,
  ConversationListResponse,
  ConversationMessagesResponse
} from '../types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://mohammadtouqeer-todo-backend-phase4.hf.space';

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
  fetchTasks: async () => {
    const response = await api.get('/tasks');
    return { tasks: response.data };
  },
  addTask: async (title: string) => {
    const response = await api.post('/tasks', { title, completed: false });
    return response.data;
  },
  toggleTaskStatus: async (taskId: number) => {
    return api.post(`/tasks/${taskId}/toggle`); 
  },
  updateTask: async (id: number, data: any) => {
    const response = await api.put(`/tasks/${id}`, data);
    return response.data;
  },
  deleteTask: (id: number) => api.delete(`/tasks/${id}`),
  agentPrompt: async (prompt: string) => ({ response: "Assistant logic to be implemented" }),
  analyzeTask: async () => ({ 
    summary: "No analysis available", 
    insights: [], recommendations: [], patterns: [],
    stats: { total: 0, completed: 0, pending: 0, completion_rate: 0 }
  }),
};

export const chatService = {
  getConversations: () => api.get<ConversationListResponse>('/chat/conversations'),
  getMessages: (conversationId: string) => api.get<ConversationMessagesResponse>(`/chat/conversations/${conversationId}/messages`),
  sendMessage: (data: ChatRequest) => api.post<ChatResponse>('/chat/message', data),
};
