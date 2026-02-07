# Authentication Specification

## Overview

This document defines the JWT-based authentication strategy for the Todo App, enabling secure communication between Better Auth (frontend) and FastAPI (backend).

## JWT Shared Secret Strategy

### Concept

Both the frontend (Better Auth) and backend (FastAPI) share a common JWT secret key. This allows:
- Frontend to create and validate sessions
- Backend to verify incoming requests from authenticated users
- No need for complex token exchange mechanisms

### Security Note

**Important**: The shared secret must be a strong, randomly generated string (minimum 32 characters). In production, use environment variables and secure secret management.

## Environment Variables

```env
# Required - Must be identical in frontend and backend
JWT_SECRET=your-super-secret-key-min-32-chars-long

# Optional - Token expiration
JWT_EXPIRY=7d

# Optional - Algorithm
JWT_ALGORITHM=HS256
```

## JWT Token Structure

### Payload

```json
{
  "sub": "1",           // User ID
  "email": "user@example.com",
  "exp": 1704067200,    // Expiration timestamp
  "iat": 1703462400,    // Issued at timestamp
  "type": "access"      // Token type
}
```

### Claims

| Claim | Type | Description |
|-------|------|-------------|
| sub | string | User ID (subject) |
| email | string | User's email address |
| exp | int | Expiration time (Unix timestamp) |
| iat | int | Issued at time (Unix timestamp) |
| type | string | Token type ("access") |

## Backend Implementation (FastAPI)

### Dependencies

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

security = HTTPBearer()
```

### Token Verification

```python
def verify_token(token: str) -> dict:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
```

### Dependency for Protected Routes

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token)
    return payload
```

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed: str) -> bool:
    return pwd_context.verify(plain_password, hashed)
```

### Token Generation

```python
def create_access_token(user_id: int, email: str) -> str:
    """Create JWT access token."""
    expires = datetime.utcnow() + timedelta(days=7)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expires,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
```

## Frontend Implementation (Better Auth)

### Configuration

```typescript
// better-auth.config.ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  database: [
    "postgresql://...",
    {
      provider: "postgresql",
    }
  ],
  secret: process.env.JWT_SECRET,
  advanced: {
    cookiePrefix: "todo-app",
  },
});
```

### API Client with Auth

```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL;

async function fetchWithAuth(
  endpoint: string,
  options: RequestInit = {}
) {
  const token = await getSessionToken();

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error("Request failed");
  }

  return response.json();
}
```

## Authentication Flow

### Login Flow

```
1. User submits email/password to frontend
2. Frontend calls POST /auth/login
3. Backend validates credentials
4. Backend generates JWT with user info
5. Backend returns token in response
6. Frontend stores token (cookies/localStorage)
7. Frontend includes token in subsequent requests
```

### API Request Flow

```
1. Frontend makes API call with Authorization header
2. Backend extracts and verifies JWT
3. Backend extracts user_id from token
4. Backend queries tasks for that user_id
5. Backend returns task data
```

### Token Refresh

```
1. Frontend detects expired token
2. Frontend calls POST /auth/refresh
3. Backend validates refresh token
4. Backend issues new access token
5. Frontend updates stored token
```

## Security Best Practices

1. **HTTPS Only**: Always use HTTPS in production
2. **Short Expiry**: Set reasonable token expiry (7 days max)
3. **Secure Cookies**: Set `HttpOnly`, `Secure`, `SameSite=Strict`
4. **Password Requirements**: Minimum 8 characters
5. **Rate Limiting**: Limit login attempts
6. **Input Validation**: Validate all inputs on both sides

## Validation Rules

### Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (!@#$%^&*)

### Email Requirements

- Valid email format
- Maximum 255 characters
- Unique per user

## Error Handling

| Error | Status | Action |
|-------|--------|--------|
| Missing token | 401 | Redirect to login |
| Invalid token | 401 | Redirect to login |
| Expired token | 401 | Attempt refresh |
| Invalid credentials | 401 | Show error message |
