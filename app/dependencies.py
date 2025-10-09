from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from typing import Optional
from app.database import get_session
from app.models import User, UserSession, UserRole
from app.security import decode_access_token
from datetime import datetime


security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session_token: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_session)
) -> User:
    """
    Dependency to get the current authenticated user.
    Supports both JWT Bearer tokens and session cookies.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = None

    # Try JWT token first
    if credentials:
        token_data = decode_access_token(credentials.credentials)
        if token_data:
            statement = select(User).where(User.id == token_data.user_id)
            user = db.exec(statement).first()

    # Try session token if JWT not found
    if not user and session_token:
        statement = select(UserSession).where(
            UserSession.session_token == session_token,
            UserSession.expires_at > datetime.utcnow()
        )
        user_session = db.exec(statement).first()
        if user_session:
            user = user_session.user

    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to ensure user is an admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session_token: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_session)
) -> Optional[User]:
    """
    Dependency to get the current user if authenticated, None otherwise.
    Useful for pages that can be accessed by both authenticated and anonymous users.
    """
    try:
        user = None

        if credentials:
            token_data = decode_access_token(credentials.credentials)
            if token_data:
                statement = select(User).where(User.id == token_data.user_id)
                user = db.exec(statement).first()

        if not user and session_token:
            statement = select(UserSession).where(
                UserSession.session_token == session_token,
                UserSession.expires_at > datetime.utcnow()
            )
            user_session = db.exec(statement).first()
            if user_session:
                user = user_session.user

        return user if user and user.is_active else None
    except:
        return None
