"""
Chat request and response schemas for the AI Chatbot.

Pydantic models for validating chat API requests and responses.
"""
from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Request body for POST /api/{user_id}/chat endpoint.

    Attributes:
        conversation_id: Optional existing conversation to continue
        message: User's message to the chatbot (required)
    """
    conversation_id: int | None = Field(
        default=None,
        description="Optional conversation ID to continue an existing conversation"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User's message to the chatbot"
    )


class MessageResponse(BaseModel):
    """
    Individual message in a chat response.

    Attributes:
        role: Message role ('user' or 'assistant')
        content: Message text content
    """
    role: str = Field(
        description="Message role: 'user' or 'assistant'"
    )
    content: str = Field(
        description="Message text content"
    )


class ChatResponse(BaseModel):
    """
    Response body for POST /api/{user_id}/chat endpoint.

    Attributes:
        conversation_id: ID of the conversation
        message: Assistant's response message
        created_at: Timestamp of the response
    """
    conversation_id: int = Field(
        description="ID of the conversation"
    )
    message: MessageResponse = Field(
        description="Assistant's response message"
    )
    created_at: datetime = Field(
        description="Timestamp when the response was created"
    )


class ConversationInfo(BaseModel):
    """
    Basic conversation information.

    Attributes:
        id: Conversation ID
        title: Conversation title
        created_at: When the conversation was created
        updated_at: When the conversation was last updated
    """
    id: int
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    """
    Response for listing user's conversations.

    Attributes:
        conversations: List of conversation summaries
        total: Total count
    """
    conversations: list[ConversationInfo]
    total: int
