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

export const taskService = {
  fetchTasks: async () => {
    const response = await api.get('/tasks');
    // Backend List[Task] bhej raha hai, humein use { tasks: [...] } format mein dena hai
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
  
  // AI FUNCTIONS FIXED (Now calling real backend)
  agentPrompt: async (prompt: string) => {
    const response = await api.post('/agent/prompt', { prompt });
    return response.data;
  },
  analyzeTask: async () => {
    const response = await api.get('/tasks/analyze');
    return response.data;
  },
};

export const chatService = {
  // Added .then to handle empty data gracefully
  getConversations: () => api.get('/chat/conversations').then(res => res.data),
  getMessages: (conversationId: string) => api.get(`/chat/conversations/${conversationId}/messages`).then(res => res.data),
  sendMessage: (data: ChatRequest) => api.post('/chat/message', data).then(res => res.data),
};
