'use client';

import { Button } from './ui/button';
import { MessageSquarePlus, History } from 'lucide-react';

interface ChatHeaderProps {
  conversationId: number | null;
  onNewConversation: () => void;
  onShowHistory?: () => void;
}

export function ChatHeader({
  conversationId,
  onNewConversation,
  onShowHistory
}: ChatHeaderProps) {
  return (
    <div className="border-b border-purple-100 bg-white/80 backdrop-blur-sm px-4 py-3">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-800">
            Chat with AI Assistant
          </h2>
          <p className="text-xs text-gray-500">
            {conversationId
              ? `Conversation #${conversationId}`
              : 'Start a new conversation'}
          </p>
        </div>

        <div className="flex items-center gap-2">
          {onShowHistory && (
            <Button
              variant="outline"
              size="sm"
              onClick={onShowHistory}
              className="border-purple-200 text-purple-600 hover:bg-purple-50"
            >
              <History className="h-4 w-4 mr-1" />
              History
            </Button>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={onNewConversation}
            className="border-purple-200 text-purple-600 hover:bg-purple-50"
          >
            <MessageSquarePlus className="h-4 w-4 mr-1" />
            New Chat
          </Button>
        </div>
      </div>
    </div>
  );
}
