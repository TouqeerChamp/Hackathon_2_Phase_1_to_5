'use client';

export function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-purple-50 rounded-2xl px-4 py-3 shadow-sm">
        <div className="flex items-center gap-1">
          <span className="text-sm text-gray-500 mr-2">AI is thinking</span>
          <div className="flex gap-1">
            <span
              className="h-2 w-2 rounded-full bg-purple-400 animate-bounce"
              style={{ animationDelay: '0ms' }}
            />
            <span
              className="h-2 w-2 rounded-full bg-purple-400 animate-bounce"
              style={{ animationDelay: '150ms' }}
            />
            <span
              className="h-2 w-2 rounded-full bg-purple-400 animate-bounce"
              style={{ animationDelay: '300ms' }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
