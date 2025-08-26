# app/security.py
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

from passlib.context import CryptContext

# ------------------------------------------------------------------------------
# Password hashing (bcrypt via Passlib)
# ------------------------------------------------------------------------------

# Single context reused across the app (thread-safe)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    """
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.
    """
    if not hashed_password:
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Covers malformed hashes or unsupported schemes
        return False

# ------------------------------------------------------------------------------
# JWT scaffolding (optional — enable when needed)
# ------------------------------------------------------------------------------
# To enable JWT, install: `pip install python-jose[cryptography]`
# And then uncomment imports and functions below.
#
# from jose import jwt, JWTError
#
# # NOTE: move secrets to environment variables or a settings module
# JWT_SECRET_KEY = "CHANGE_ME_use_env_var"
# JWT_ALGORITHM = "HS256"
# JWT_EXPIRES_MIN = 60
#
# def create_access_token(
#     data: dict[str, Any],
#     expires_delta: Optional[timedelta] = None
# ) -> str:
#     to_encode = data.copy()
#     expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=JWT_EXPIRES_MIN))
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
#
# def decode_access_token(token: str) -> dict[str, Any]:
#     try:
#         payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
#         return payload
#     except JWTError as e:
#         raise ValueError("Invalid or expired token") from e
