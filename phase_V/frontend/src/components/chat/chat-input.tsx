'use client';

import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Send } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  disabled = false,
  placeholder = 'Type your message...'
}: ChatInputProps) {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [value]);

  const handleSend = () => {
    const trimmed = value.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setValue('');
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const charCount = value.length;
  const maxChars = 4000;
  const isOverLimit = charCount > maxChars;

  return (
    <div className="border-t border-purple-100 bg-white p-4">
      <div className="flex items-end gap-3">
        <div className="relative flex-1">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className="w-full resize-none rounded-xl border border-purple-200 bg-white px-4 py-3 pr-12 text-sm
                       placeholder:text-gray-400
                       focus:border-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-100
                       disabled:cursor-not-allowed disabled:opacity-50
                       transition-colors"
            style={{ minHeight: '48px', maxHeight: '150px' }}
          />
          {/* Character count */}
          <span
            className={`absolute bottom-2 right-3 text-xs ${
              isOverLimit ? 'text-red-500' : 'text-gray-400'
            }`}
          >
            {charCount}/{maxChars}
          </span>
        </div>

        <Button
          onClick={handleSend}
          disabled={disabled || !value.trim() || isOverLimit}
          className="h-12 w-12 shrink-0 rounded-xl bg-purple-600 p-0
                     hover:bg-purple-700 disabled:opacity-50
                     shadow-md hover:shadow-lg transition-all"
          aria-label="Send message"
        >
          <Send className="h-5 w-5" />
        </Button>
      </div>

      {/* Helper text */}
      <p className="mt-2 text-xs text-gray-400">
        Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  );
}
