# Chatbot UI Specification (Phase III)

## Overview

This document defines the chat interface components for the AI Chatbot feature. The UI follows the existing purple theme and Shadcn/ui patterns established in the application.

## Design Principles

1. **Consistency**: Match existing purple theme and Tailwind patterns
2. **Responsiveness**: Mobile-first design with desktop enhancements
3. **Accessibility**: Proper ARIA labels and keyboard navigation
4. **Performance**: Optimistic UI updates and loading states

## Page Structure

### Chat Page (`/chat`)

```
┌─────────────────────────────────────────────────────┐
│                    Header                           │
│  [Logo]  Dashboard  Chat with AI  [User] [Logout]   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │              Chat Container                   │  │
│  │                                               │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │         Message History Area            │  │  │
│  │  │                                         │  │  │
│  │  │  [User Message]                         │  │  │
│  │  │                    [Assistant Message]  │  │  │
│  │  │  [User Message]                         │  │  │
│  │  │                    [Assistant Message]  │  │  │
│  │  │                                         │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  │                                               │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │  [Message Input]          [Send Button] │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Components

### 1. ChatPage (`/app/chat/page.tsx`)

Main chat page component with conversation state management.

**Props**: None (uses auth context for user)

**State**:
```typescript
interface ChatPageState {
  messages: Message[];
  conversationId: number | null;
  isLoading: boolean;
  error: string | null;
  inputValue: string;
}
```

**Features**:
- Protected route (requires authentication)
- Conversation persistence via `conversation_id`
- Auto-scroll to latest message
- New conversation button

### 2. ChatContainer (`/components/chat/chat-container.tsx`)

Container for the entire chat interface.

**Props**:
```typescript
interface ChatContainerProps {
  children: React.ReactNode;
}
```

**Styling**:
```css
/* Glass-morphism card matching existing theme */
border-purple-50 bg-white/90 shadow-lg backdrop-blur-sm rounded-2xl
```

### 3. ChatMessage (`/components/chat/chat-message.tsx`)

Individual message bubble component.

**Props**:
```typescript
interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}
```

**Styling**:
| Role | Alignment | Background | Text |
|------|-----------|------------|------|
| User | Right | `bg-purple-600` | `text-white` |
| Assistant | Left | `bg-purple-50` | `text-gray-800` |

### 4. ChatInput (`/components/chat/chat-input.tsx`)

Message input with send button.

**Props**:
```typescript
interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled?: boolean;
  placeholder?: string;
}
```

**Features**:
- Auto-resize textarea
- Send on Enter (Shift+Enter for newline)
- Disabled state while loading
- Character limit indicator (4000 chars)

### 5. ChatHeader (`/components/chat/chat-header.tsx`)

Header with conversation info and actions.

**Props**:
```typescript
interface ChatHeaderProps {
  conversationId: number | null;
  onNewConversation: () => void;
}
```

### 6. TypingIndicator (`/components/chat/typing-indicator.tsx`)

Animated dots shown while AI is responding.

**Animation**:
```css
/* Three bouncing dots */
@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-6px); }
}
```

## API Integration

### Chat Service Functions (`/lib/api.ts`)

```typescript
// Send message to chatbot
export async function sendChatMessage(
  userId: string,
  message: string,
  conversationId?: number
): Promise<ChatResponse>

// Get user's conversations
export async function getConversations(
  userId: string
): Promise<ConversationListResponse>

// Get conversation messages
export async function getConversationMessages(
  userId: string,
  conversationId: number
): Promise<MessagesResponse>
```

### Request Headers

```typescript
{
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${token}`  // JWT from localStorage
}
```

## TypeScript Interfaces

```typescript
// Chat message
interface ChatMessage {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  created_at?: string;
}

// Chat request
interface ChatRequest {
  conversation_id?: number;
  message: string;
}

// Chat response
interface ChatResponse {
  conversation_id: number;
  message: {
    role: 'assistant';
    content: string;
  };
  created_at: string;
}

// Conversation summary
interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

// Conversation list
interface ConversationListResponse {
  conversations: Conversation[];
  total: number;
}
```

## Styling Guide

### Color Palette (Purple Theme)

| Element | Class |
|---------|-------|
| User bubble | `bg-purple-600 text-white` |
| Assistant bubble | `bg-purple-50 text-gray-800` |
| Send button | `bg-purple-600 hover:bg-purple-700` |
| Input focus | `focus:border-purple-400 focus:ring-purple-100` |
| Container | `bg-white/90 border-purple-50` |
| Timestamps | `text-gray-400 text-xs` |

### Layout Classes

```css
/* Chat container */
.chat-container {
  @apply flex flex-col h-[calc(100vh-12rem)] max-w-4xl mx-auto;
}

/* Messages area */
.messages-area {
  @apply flex-1 overflow-y-auto p-4 space-y-4;
}

/* Input area */
.input-area {
  @apply border-t border-purple-100 p-4;
}

/* Message bubble */
.message-bubble {
  @apply max-w-[80%] rounded-2xl px-4 py-2 shadow-sm;
}
```

## User Flows

### 1. Start New Conversation

```
1. User navigates to /chat
2. Empty state shown with welcome message
3. User types message and clicks Send
4. Loading indicator shown
5. API creates new conversation, returns response
6. Messages displayed with new conversation_id stored
```

### 2. Continue Conversation

```
1. User returns to /chat with stored conversation_id
2. Previous messages loaded from API
3. User types new message
4. Message sent with conversation_id
5. Response appended to history
```

### 3. Error Handling

```
1. Network error: Show toast, keep input enabled
2. API error: Show error message in chat
3. Auth error (401): Redirect to login
```

## Accessibility

- `role="log"` on messages container
- `aria-live="polite"` for new messages
- `aria-busy="true"` while loading
- Focus management after sending
- Keyboard navigation (Tab, Enter, Escape)

## Mobile Considerations

- Full-width messages on mobile
- Fixed input bar at bottom
- Touch-friendly send button (min 44x44px)
- Responsive text sizes

## File Structure

```
frontend/src/
├── app/
│   └── chat/
│       └── page.tsx           # Chat page
├── components/
│   └── chat/
│       ├── chat-container.tsx # Main container
│       ├── chat-message.tsx   # Message bubble
│       ├── chat-input.tsx     # Input component
│       ├── chat-header.tsx    # Header with actions
│       ├── typing-indicator.tsx # Loading animation
│       └── index.ts           # Exports
├── lib/
│   └── api.ts                 # Add chat functions
└── types/
    └── index.ts               # Add chat types
```
