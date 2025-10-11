"""
Example test file for Repository Pattern implementation.

This file demonstrates how to write unit tests for the repository classes
using pytest and mocking.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from sqlmodel import Session

from app.repository import UserRepository, SessionRepository
from app.models_schema.models import User, UserSession, UserRole


class TestUserRepository:
    """Test cases for UserRepository"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_session = Mock(spec=Session)
        self.user_repo = UserRepository(self.mock_session)
    
    def test_get_by_email(self):
        """Test getting user by email"""
        # Arrange
        email = "test@example.com"
        expected_user = User(
            id=1,
            email=email,
            username="testuser",
            role=UserRole.USER
        )
        
        mock_statement = Mock()
        self.mock_session.exec.return_value.first.return_value = expected_user
        
        # Act
        result = self.user_repo.get_by_email(email)
        
        # Assert
        assert result == expected_user
        self.mock_session.exec.assert_called_once()
    
    def test_get_by_username(self):
        """Test getting user by username"""
        # Arrange
        username = "testuser"
        expected_user = User(
            id=1,
            email="test@example.com",
            username=username,
            role=UserRole.USER
        )
        
        self.mock_session.exec.return_value.first.return_value = expected_user
        
        # Act
        result = self.user_repo.get_by_username(username)
        
        # Assert
        assert result == expected_user
        self.mock_session.exec.assert_called_once()
    
    def test_is_email_taken(self):
        """Test checking if email is taken"""
        # Arrange
        email = "test@example.com"
        self.mock_session.exec.return_value.first.return_value = User()  # User exists
        
        # Act
        result = self.user_repo.is_email_taken(email)
        
        # Assert
        assert result is True
        self.mock_session.exec.assert_called_once()
    
    def test_is_email_not_taken(self):
        """Test checking if email is not taken"""
        # Arrange
        email = "test@example.com"
        self.mock_session.exec.return_value.first.return_value = None  # User doesn't exist
        
        # Act
        result = self.user_repo.is_email_taken(email)
        
        # Assert
        assert result is False
        self.mock_session.exec.assert_called_once()
    
    def test_create_user(self):
        """Test creating a new user"""
        # Arrange
        new_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            role=UserRole.USER
        )
        
        self.mock_session.add = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.refresh = Mock()
        
        # Act
        result = self.user_repo.create(new_user)
        
        # Assert
        assert result == new_user
        self.mock_session.add.assert_called_once_with(new_user)
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once_with(new_user)
    
    def test_get_user_stats(self):
        """Test getting user statistics"""
        # Arrange
        # Mock different query results
        self.mock_session.exec.side_effect = [
            [User()] * 10,  # total_users
            [User()] * 8,   # active_users
            [User()] * 2,   # admin_users
            [User()] * 3,   # google_users
        ]
        
        # Act
        stats = self.user_repo.get_user_stats()
        
        # Assert
        assert stats["total_users"] == 10
        assert stats["active_users"] == 8
        assert stats["admin_users"] == 2
        assert stats["google_users"] == 3
        assert stats["inactive_users"] == 2  # 10 - 8
        assert stats["regular_users"] == 8   # 10 - 2
        assert stats["email_users"] == 7     # 10 - 3


class TestSessionRepository:
    """Test cases for SessionRepository"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_session = Mock(spec=Session)
        self.session_repo = SessionRepository(self.mock_session)
    
    def test_get_by_token(self):
        """Test getting session by token"""
        # Arrange
        session_token = "test_token_123"
        expected_session = UserSession(
            id=1,
            user_id=1,
            session_token=session_token,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        
        self.mock_session.exec.return_value.first.return_value = expected_session
        
        # Act
        result = self.session_repo.get_by_token(session_token)
        
        # Assert
        assert result == expected_session
        self.mock_session.exec.assert_called_once()
    
    def test_create_session(self):
        """Test creating a new session"""
        # Arrange
        user_id = 1
        session_token = "test_token_123"
        expires_at = datetime.utcnow() + timedelta(hours=1)
        ip_address = "192.168.1.1"
        user_agent = "Mozilla/5.0..."
        
        self.mock_session.add = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.refresh = Mock()
        
        # Act
        result = self.session_repo.create_session(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Assert
        assert isinstance(result, UserSession)
        assert result.user_id == user_id
        assert result.session_token == session_token
        assert result.expires_at == expires_at
        assert result.ip_address == ip_address
        assert result.user_agent == user_agent
        
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    def test_delete_session(self):
        """Test deleting a session"""
        # Arrange
        session_token = "test_token_123"
        mock_session_obj = UserSession(
            id=1,
            user_id=1,
            session_token=session_token
        )
        
        self.mock_session.exec.return_value.first.return_value = mock_session_obj
        self.mock_session.delete = Mock()
        self.mock_session.commit = Mock()
        
        # Act
        result = self.session_repo.delete_session(session_token)
        
        # Assert
        assert result is True
        self.mock_session.delete.assert_called_once_with(mock_session_obj)
        self.mock_session.commit.assert_called_once()
    
    def test_delete_nonexistent_session(self):
        """Test deleting a non-existent session"""
        # Arrange
        session_token = "nonexistent_token"
        self.mock_session.exec.return_value.first.return_value = None
        
        # Act
        result = self.session_repo.delete_session(session_token)
        
        # Assert
        assert result is False
        self.mock_session.delete.assert_not_called()
        self.mock_session.commit.assert_not_called()
    
    def test_get_session_stats(self):
        """Test getting session statistics"""
        # Arrange
        user_id = 1
        now = datetime.utcnow()
        
        # Mock different query results
        self.mock_session.exec.side_effect = [
            [UserSession()] * 5,  # total_sessions
            [UserSession()] * 3,  # active_sessions
        ]
        
        # Act
        stats = self.session_repo.get_session_stats(user_id)
        
        # Assert
        assert stats["total_sessions"] == 5
        assert stats["active_sessions"] == 3
        assert stats["expired_sessions"] == 2  # 5 - 3


class TestRepositoryIntegration:
    """Integration tests for repository pattern"""
    
    def test_user_and_session_workflow(self):
        """Test complete user and session workflow"""
        # This would be an integration test that uses a real database
        # For now, we'll just demonstrate the pattern
        
        # Arrange
        mock_session = Mock(spec=Session)
        user_repo = UserRepository(mock_session)
        session_repo = SessionRepository(mock_session)
        
        # Mock user creation
        mock_user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            role=UserRole.USER
        )
        
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.refresh = Mock()
        
        # Act - Create user
        created_user = user_repo.create(mock_user)
        
        # Act - Create session for user
        session_token = "test_token_123"
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        created_session = session_repo.create_session(
            user_id=created_user.id,
            session_token=session_token,
            expires_at=expires_at
        )
        
        # Assert
        assert created_user.id == 1
        assert created_session.user_id == 1
        assert created_session.session_token == session_token


# Example of how to run these tests
if __name__ == "__main__":
    print("Repository Pattern Test Examples")
    print("=" * 50)
    print("To run these tests, use: pytest examples/test_repositories.py")
    print("Make sure to install pytest: pip install pytest")
    print("=" * 50)
