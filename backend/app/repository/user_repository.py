from typing import Optional, List
from sqlmodel import Session, select
from datetime import datetime

from .base_repository import BaseRepository
from app.models_schema.models import User, UserRole


class UserRepository(BaseRepository[User]):
    """Repository for User model with specific user operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        statement = select(User).where(User.username == username)
        return self.session.exec(statement).first()
    
    def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID"""
        statement = select(User).where(User.google_id == google_id)
        return self.session.exec(statement).first()
    
    def get_by_email_or_username(self, email_or_username: str) -> Optional[User]:
        """Get user by email or username"""
        statement = select(User).where(
            (User.email == email_or_username) | (User.username == email_or_username)
        )
        return self.session.exec(statement).first()
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users"""
        statement = select(User).where(User.is_active == True).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
    
    def get_users_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role"""
        statement = select(User).where(User.role == role).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
    
    def get_google_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users who signed up with Google"""
        statement = select(User).where(User.is_google_user == True).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
    
    def search_users(self, query: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Search users by email, username, or full name"""
        statement = select(User).where(
            (User.email.contains(query)) |
            (User.username.contains(query)) |
            (User.full_name.contains(query))
        ).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
    
    def update_last_login(self, user_id: int) -> Optional[User]:
        """Update user's last login time"""
        user = self.get_by_id(user_id)
        if user:
            user.updated_at = datetime.now()
            return self.update(user)
        return None
    
    def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate a user account"""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = False
            user.updated_at = datetime.now()
            return self.update(user)
        return None
    
    def activate_user(self, user_id: int) -> Optional[User]:
        """Activate a user account"""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = True
            user.updated_at = datetime.now()
            return self.update(user)
        return None
    
    def change_user_role(self, user_id: int, new_role: UserRole) -> Optional[User]:
        """Change user role"""
        user = self.get_by_id(user_id)
        if user:
            user.role = new_role
            user.updated_at = datetime.now()
            return self.update(user)
        return None
    
    def is_email_taken(self, email: str, exclude_user_id: Optional[int] = None) -> bool:
        """Check if email is already taken by another user"""
        statement = select(User).where(User.email == email)
        if exclude_user_id:
            statement = statement.where(User.id != exclude_user_id)
        return self.session.exec(statement).first() is not None
    
    def is_username_taken(self, username: str, exclude_user_id: Optional[int] = None) -> bool:
        """Check if username is already taken by another user"""
        statement = select(User).where(User.username == username)
        if exclude_user_id:
            statement = statement.where(User.id != exclude_user_id)
        return self.session.exec(statement).first() is not None
    
    def get_user_stats(self) -> dict:
        """Get user statistics"""
        total_users = self.count()
        active_users = len(self.get_active_users())
        admin_users = len(self.get_users_by_role(UserRole.ADMIN))
        google_users = len(self.get_google_users())
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "admin_users": admin_users,
            "regular_users": total_users - admin_users,
            "google_users": google_users,
            "email_users": total_users - google_users
        }
