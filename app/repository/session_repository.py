from typing import Optional, List
from sqlmodel import Session, select
from datetime import datetime, timedelta

from .base_repository import BaseRepository
from app.models_schema.models import UserSession, User


class SessionRepository(BaseRepository[UserSession]):
    """Repository for UserSession model with specific session operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, UserSession)
    
    def get_by_token(self, session_token: str) -> Optional[UserSession]:
        """Get session by token"""
        statement = select(UserSession).where(UserSession.session_token == session_token)
        return self.session.exec(statement).first()
    
    def get_by_user_id(self, user_id: int) -> List[UserSession]:
        """Get all sessions for a user"""
        statement = select(UserSession).where(UserSession.user_id == user_id)
        return list(self.session.exec(statement).all())
    
    def get_active_sessions(self, user_id: int) -> List[UserSession]:
        """Get active (non-expired) sessions for a user"""
        now = datetime.utcnow()
        statement = select(UserSession).where(
            (UserSession.user_id == user_id) & (UserSession.expires_at > now)
        )
        return list(self.session.exec(statement).all())
    
    def get_expired_sessions(self, user_id: int) -> List[UserSession]:
        """Get expired sessions for a user"""
        now = datetime.utcnow()
        statement = select(UserSession).where(
            (UserSession.user_id == user_id) & (UserSession.expires_at <= now)
        )
        return list(self.session.exec(statement).all())
    
    def create_session(
        self, 
        user_id: int, 
        session_token: str, 
        expires_at: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """Create a new user session"""
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return self.create(session)
    
    def delete_session(self, session_token: str) -> bool:
        """Delete session by token"""
        session = self.get_by_token(session_token)
        if session:
            return self.delete_object(session)
        return False
    
    def delete_user_sessions(self, user_id: int) -> int:
        """Delete all sessions for a user"""
        sessions = self.get_by_user_id(user_id)
        deleted_count = 0
        for session in sessions:
            if self.delete_object(session):
                deleted_count += 1
        return deleted_count
    
    def delete_expired_sessions(self, user_id: Optional[int] = None) -> int:
        """Delete expired sessions for a user or all users"""
        now = datetime.utcnow()
        statement = select(UserSession).where(UserSession.expires_at <= now)
        
        if user_id:
            statement = statement.where(UserSession.user_id == user_id)
        
        expired_sessions = list(self.session.exec(statement).all())
        deleted_count = 0
        
        for session in expired_sessions:
            if self.delete_object(session):
                deleted_count += 1
        
        return deleted_count
    
    def extend_session(self, session_token: str, new_expires_at: datetime) -> Optional[UserSession]:
        """Extend session expiration time"""
        session = self.get_by_token(session_token)
        if session:
            session.expires_at = new_expires_at
            return self.update(session)
        return None
    
    def get_session_with_user(self, session_token: str) -> Optional[tuple[UserSession, User]]:
        """Get session with associated user"""
        statement = select(UserSession, User).join(User).where(UserSession.session_token == session_token)
        result = self.session.exec(statement).first()
        if result:
            return result
        return None
    
    def get_active_sessions_count(self, user_id: int) -> int:
        """Get count of active sessions for a user"""
        now = datetime.utcnow()
        statement = select(UserSession).where(
            (UserSession.user_id == user_id) & (UserSession.expires_at > now)
        )
        return len(list(self.session.exec(statement).all()))
    
    def get_sessions_by_ip(self, ip_address: str) -> List[UserSession]:
        """Get sessions by IP address"""
        statement = select(UserSession).where(UserSession.ip_address == ip_address)
        return list(self.session.exec(statement).all())
    
    def get_recent_sessions(self, user_id: int, hours: int = 24) -> List[UserSession]:
        """Get recent sessions within specified hours"""
        since = datetime.utcnow() - timedelta(hours=hours)
        statement = select(UserSession).where(
            (UserSession.user_id == user_id) & (UserSession.created_at >= since)
        ).order_by(UserSession.created_at.desc())
        return list(self.session.exec(statement).all())
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """Clean up sessions older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        statement = select(UserSession).where(UserSession.created_at < cutoff_date)
        old_sessions = list(self.session.exec(statement).all())
        
        deleted_count = 0
        for session in old_sessions:
            if self.delete_object(session):
                deleted_count += 1
        
        return deleted_count
    
    def get_session_stats(self, user_id: Optional[int] = None) -> dict:
        """Get session statistics"""
        now = datetime.utcnow()
        
        # Total sessions
        total_statement = select(UserSession)
        if user_id:
            total_statement = total_statement.where(UserSession.user_id == user_id)
        total_sessions = len(list(self.session.exec(total_statement).all()))
        
        # Active sessions
        active_statement = select(UserSession).where(UserSession.expires_at > now)
        if user_id:
            active_statement = active_statement.where(UserSession.user_id == user_id)
        active_sessions = len(list(self.session.exec(active_statement).all()))
        
        # Expired sessions
        expired_sessions = total_sessions - active_sessions
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": expired_sessions
        }
