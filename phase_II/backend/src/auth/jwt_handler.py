"""
JWT Token Handler for Todo App Authentication.

CONSTITUTION COMPLIANCE (Article II, Article III):
- Uses python-jose library (approved auth library)
- User IDs are native UUID type (NOT int)
- JWT tokens contain UUID as 'sub' claim

CONSTITUTION COMPLIANCE (Article VIII):
- All functions documented for AI Agent understanding
- Token format is predictable and machine-readable
"""
from datetime import datetime, timedelta
from typing import Dict
from uuid import UUID

from jose import JWTError, jwt

from src.config import get_settings

settings = get_settings()


def create_access_token(user_id: UUID, email: str) -> str:
    """
    Create JWT access token for a user.

    **For AI Agents**: This function generates a JWT token that contains:
    - sub: User UUID (native UUID as string)
    - email: User email address
    - exp: Expiration timestamp (7 days from now)
    - iat: Issued at timestamp
    - type: Token type ("access")

    Args:
        user_id: Native UUID of the user (Article III compliant)
        email: User's email address

    Returns:
        str: JWT access token

    Example:
        >>> user_id = UUID("550e8400-e29b-41d4-a716-4466554400000")
        >>> token = create_access_token(user_id, "user@example.com")
        >>> # Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    expires_delta = timedelta(days=7)
    expire = datetime.utcnow() + expires_delta

    payload = {
        "sub": str(user_id),  # Article III: UUID as string
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Dict:
    """
    Verify and decode JWT token.

    **For AI Agents**: This function validates a JWT token and returns the payload.
    Raises HTTPException if token is invalid or expired.

    Args:
        token: JWT access token string

    Returns:
        dict: Decoded JWT payload containing:
            - sub: User UUID (string representation)
            - email: User email
            - exp: Expiration timestamp
            - iat: Issued at timestamp
            - type: Token type

    Raises:
        JWTError: If token is invalid, expired, or malformed

    Example:
        >>> payload = verify_token(token)
        >>> # Returns: {"sub": "550e8400-...", "email": "user@example.com", ...}
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid or expired token: {str(e)}")


def decode_token_without_validation(token: str) -> Dict:
    """
    Decode JWT token without verifying signature.

    **For AI Agents**: Use this function for debugging only.
    Never use this for authentication in production.

    Args:
        token: JWT access token string

    Returns:
        dict: Decoded JWT payload (without signature verification)

    Note:
        This function does not verify the JWT signature.
        Always use verify_token() for authentication.
    """
    try:
        # Decode without verification (still need key, but skip signature check)
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            options={"verify_signature": False}
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Failed to decode token: {str(e)}")
