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
  (error) => {
    return Promise.reject(error);
  }
);

export const taskService = {
  fetchTasks: async () => {
    const res = await api.get<TaskListResponse>(`/api/v1/tasks`);
    return res.data;
  },
  addTask: async (title: string) => {
    const res = await api.post<Task>(`/api/v1/tasks`, { title });
    return res.data;
  },
  updateTask: async (taskId: number, data: { title?: string; description?: string; completed?: boolean }) => {
    const res = await api.put<Task>(`/api/v1/tasks/${taskId}`, data);
    return res.data;
  },
  toggleTaskStatus: async (taskId: number) => {
    const res = await api.patch<Task>(`/api/v1/tasks/${taskId}/toggle`);
    return res.data;
  },
  deleteTask: async (taskId: number) => {
    await api.delete(`/api/v1/tasks/${taskId}`);
  },
  agentPrompt: async (prompt: string) => {
    const res = await api.post<{ response: string }>(`/api/v1/agent/prompt`, { prompt });
    return res.data;
  },
  analyzeTask: async () => {
    const res = await api.post<{
      summary: string;
      insights: string[];
      recommendations: string[];
      patterns: string[];
      stats: {
        total: number;
        completed: number;
        pending: number;
        completion_rate: number;
      };
    }>(`/api/v1/agent/analyze`);
    return res.data;
  }
};

// Chat service (Phase III)
export const chatService = {
  /**
   * Send a message to the AI chatbot
   * @param userId - User's UUID
   * @param message - User's message content
   * @param conversationId - Optional conversation ID to continue existing conversation
   */
  sendMessage: async (userId: string, message: string, conversationId?: number): Promise<ChatResponse> => {
    const payload: ChatRequest = { message };
    if (conversationId) {
      payload.conversation_id = conversationId;
    }
    const res = await api.post<ChatResponse>(`/api/${userId}/chat`, payload);
    return res.data;
  },

  /**
   * Get all conversations for a user
   * @param userId - User's UUID
   */
  getConversations: async (userId: string): Promise<ConversationListResponse> => {
    const res = await api.get<ConversationListResponse>(`/api/${userId}/conversations`);
    return res.data;
  },

  /**
   * Get all messages in a conversation
   * @param userId - User's UUID
   * @param conversationId - Conversation ID
   */
  getConversationMessages: async (userId: string, conversationId: number): Promise<ConversationMessagesResponse> => {
    const res = await api.get<ConversationMessagesResponse>(`/api/${userId}/conversations/${conversationId}/messages`);
    return res.data;
  }
};
