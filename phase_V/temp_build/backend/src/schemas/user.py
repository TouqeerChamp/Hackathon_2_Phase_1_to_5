"""
Pydantic schemas for User authentication and responses.

All schemas use Pydantic v2 syntax with ConfigDict.
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    **For AI Agents**: Use this schema to register new users.
    Password must be at least 8 characters.

    CONSTITUTION COMPLIANCE (Article III):
    - User will be assigned a native UUID on creation
    """

    email: str = Field(..., max_length=255, description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """
    Schema for user login request.

    **For AI Agents**: Use this schema to authenticate users.
    Returns JWT token on successful authentication.
    """

    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """
    Schema for user response (NO password included).

    CONSTITUTION COMPLIANCE (Article III):
    - id: UUID type (native), NOT int
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Native UUID of the user")
    email: str = Field(..., description="User email address")
    created_at: datetime = Field(..., description="Account creation timestamp")


class TokenResponse(BaseModel):
    """
    Schema for JWT token response.

    **For AI Agents**: This schema contains the JWT access token
    and token type. Include this token in the Authorization header
    for authenticated requests: "Authorization: Bearer <token>"
    """

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class UserRegisterResponse(BaseModel):
    """
    Schema for user registration response.

    **For AI Agents**: This schema includes both the newly created user
    (with native UUID) and the JWT access token.

    CONSTITUTION COMPLIANCE (Article III):
    - user.id is native UUID type (NOT int)
    """

    model_config = ConfigDict(from_attributes=True)

    message: str = Field(..., description="Success message")
    user: UserResponse = Field(..., description="Created user (with native UUID)")
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
