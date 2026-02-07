'use client';

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/context/auth-context';
import ProtectedRoute from '@/components/protected-route';
import Header from '@/components/header';
import {
  ChatMessage,
  ChatInput,
  ChatHeader,
  TypingIndicator
} from '@/components/chat';
import { chatService } from '@/lib/api';
import { ChatMessage as ChatMessageType, Conversation } from '@/types';
import { MessageCircle } from 'lucide-react';

function ChatPageContent() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading]);

  // Load conversations on mount
  useEffect(() => {
    if (user?.id) {
      loadConversations();
    }
  }, [user?.id]);

  const loadConversations = async () => {
    if (!user?.id) return;
    try {
      const data = await chatService.getConversations(user.id);
      setConversations(data.conversations);
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  };

  const loadConversation = async (convId: number) => {
    if (!user?.id) return;
    try {
      setIsLoading(true);
      const data = await chatService.getConversationMessages(user.id, convId);
      setMessages(data.messages);
      setConversationId(convId);
      setShowHistory(false);
      setError(null);
    } catch (err) {
      console.error('Failed to load conversation:', err);
      setError('Failed to load conversation');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!user?.id || isLoading) return;

    // Add user message optimistically
    const userMessage: ChatMessageType = {
      role: 'user',
      content,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await chatService.sendMessage(
        user.id,
        content,
        conversationId ?? undefined
      );

      // Update conversation ID if new conversation
      if (!conversationId) {
        setConversationId(response.conversation_id);
        // Reload conversations to show new one
        loadConversations();
      }

      // Add assistant message
      const assistantMessage: ChatMessageType = {
        role: 'assistant',
        content: response.message.content,
        created_at: response.created_at
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: unknown) {
      console.error('Failed to send message:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message. Please try again.';
      setError(errorMessage);

      // Add error message as assistant response
      const errorAssistantMessage: ChatMessageType = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        created_at: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorAssistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    setShowHistory(false);
  };

  const handleShowHistory = () => {
    setShowHistory(!showHistory);
    loadConversations();
  };

  return (
    <div className="min-h-screen bg-[#fcfaff]">
      <Header />

      <main className="container mx-auto px-4 py-6 max-w-4xl">
        {/* Chat Container */}
        <div className="bg-white/90 border border-purple-50 rounded-2xl shadow-lg backdrop-blur-sm overflow-hidden flex flex-col h-[calc(100vh-10rem)]">
          {/* Chat Header */}
          <ChatHeader
            conversationId={conversationId}
            onNewConversation={handleNewConversation}
            onShowHistory={handleShowHistory}
          />

          {/* Conversation History Sidebar */}
          {showHistory && (
            <div className="border-b border-purple-100 bg-purple-50/50 p-4 max-h-48 overflow-y-auto">
              <h3 className="text-sm font-medium text-gray-700 mb-2">
                Previous Conversations
              </h3>
              {conversations.length === 0 ? (
                <p className="text-sm text-gray-500">No previous conversations</p>
              ) : (
                <div className="space-y-2">
                  {conversations.map((conv) => (
                    <button
                      key={conv.id}
                      onClick={() => loadConversation(conv.id)}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors
                        ${
                          conversationId === conv.id
                            ? 'bg-purple-200 text-purple-800'
                            : 'hover:bg-purple-100 text-gray-700'
                        }`}
                    >
                      <p className="font-medium truncate">{conv.title}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(conv.updated_at).toLocaleDateString()}
                      </p>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Messages Area */}
          <div
            ref={messagesContainerRef}
            className="flex-1 overflow-y-auto p-4 space-y-4"
            role="log"
            aria-live="polite"
            aria-busy={isLoading}
          >
            {messages.length === 0 && !isLoading && (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="bg-purple-100 p-4 rounded-full mb-4">
                  <MessageCircle className="h-8 w-8 text-purple-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  Welcome to AI Chat Assistant
                </h3>
                <p className="text-gray-500 max-w-md">
                  I can help you manage your tasks. Try asking me to:
                </p>
                <ul className="text-sm text-gray-500 mt-2 space-y-1">
                  <li>&quot;Show me my tasks&quot;</li>
                  <li>&quot;Add a task to buy groceries&quot;</li>
                  <li>&quot;Mark task 1 as done&quot;</li>
                  <li>&quot;Delete task 2&quot;</li>
                </ul>
              </div>
            )}

            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}

            {isLoading && <TypingIndicator />}

            {error && (
              <div className="bg-red-50 text-red-600 text-sm px-4 py-2 rounded-lg">
                {error}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input */}
          <ChatInput
            onSend={handleSendMessage}
            disabled={isLoading}
            placeholder="Ask me to manage your tasks..."
          />
        </div>
      </main>
    </div>
  );
}

export default function ChatPage() {
  return (
    <ProtectedRoute>
      <ChatPageContent />
    </ProtectedRoute>
  );
}
