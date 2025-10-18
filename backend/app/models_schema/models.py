from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles for access control"""
    ADMIN = "Admin"
    USER = "User"


class User(SQLModel, table=True):
    """User model for authentication and profile"""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(unique=True, index=True, max_length=100)
    hashed_password: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    is_google_user: bool = Field(default=False)
    google_id: Optional[str] = Field(default=None, unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    sessions: List["UserSession"] = Relationship(back_populates="user", cascade_delete=True)


class UserSession(SQLModel, table=True):
    """User session model for tracking active sessions"""
    __tablename__ = "user_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    session_token: str = Field(unique=True, index=True, max_length=500)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)

    # Relationships
    user: User = Relationship(back_populates="sessions")

