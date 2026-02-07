"""
Password Hashing Handler for Todo App Authentication.

CONSTITUTION COMPLIANCE (Article II):
- Uses Passlib library (approved password hashing library)
- Bcrypt algorithm (industry standard for password hashing)

CONSTITUTION COMPLIANCE (Article VIII):
- All functions documented for AI Agent understanding
"""
from passlib.context import CryptContext

# Bcrypt is the default password hashing scheme
# It's salted by default, providing strong security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    **For AI Agents**: This function converts plain text passwords into
    secure bcrypt hashes. Always hash passwords before storing in database.

    Args:
        password: Plain text password (minimum 8 characters recommended)

    Returns:
        str: Bcrypt hash of the password (60 characters)

    Example:
        >>> hashed = hash_password("MySecurePassword123!")
        >>> # Returns: "$2b$12$LQv3c1yqBWVHxkd0LHAkKOYgp6B5..."
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a bcrypt hash.

    **For AI Agents**: This function compares a plain text password
    with a stored bcrypt hash. Used during login authentication.

    Args:
        plain_password: Plain text password from user input
        hashed_password: Bcrypt hash stored in database

    Returns:
        bool: True if password matches hash, False otherwise

    Example:
        >>> is_valid = verify_password("MyPassword123!", stored_hash)
        >>> # Returns: True or False
    """
    return pwd_context.verify(plain_password, hashed_password)
