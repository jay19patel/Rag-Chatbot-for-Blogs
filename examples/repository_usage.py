"""
Example usage of the Repository Pattern in the AI Chatbot application.

This file demonstrates how to use the UserRepository and SessionRepository
classes for common operations.
"""

from sqlmodel import Session
from app.database import get_session
from app.repository import UserRepository, SessionRepository
from app.models_schema.models import User, UserRole
from datetime import datetime, timedelta


def example_user_operations():
    """Example of user repository operations"""
    # Get database session
    db: Session = next(get_session())
    
    # Initialize repositories
    user_repo = UserRepository(db)
    session_repo = SessionRepository(db)
    
    print("=== User Repository Examples ===")
    
    # 1. Create a new user
    new_user = User(
        email="john.doe@example.com",
        username="johndoe",
        hashed_password="hashed_password_here",
        full_name="John Doe",
        role=UserRole.USER
    )
    created_user = user_repo.create(new_user)
    print(f"Created user: {created_user.email}")
    
    # 2. Get user by email
    user = user_repo.get_by_email("john.doe@example.com")
    print(f"Found user by email: {user.username if user else 'Not found'}")
    
    # 3. Get user by username
    user = user_repo.get_by_username("johndoe")
    print(f"Found user by username: {user.email if user else 'Not found'}")
    
    # 4. Check if email is taken
    is_taken = user_repo.is_email_taken("john.doe@example.com")
    print(f"Email is taken: {is_taken}")
    
    # 5. Get all active users
    active_users = user_repo.get_active_users(limit=10)
    print(f"Active users count: {len(active_users)}")
    
    # 6. Search users
    search_results = user_repo.search_users("john")
    print(f"Search results for 'john': {len(search_results)} users")
    
    # 7. Get user statistics
    stats = user_repo.get_user_stats()
    print(f"User statistics: {stats}")
    
    # 8. Update user
    if user:
        user.full_name = "John Smith"
        updated_user = user_repo.update(user)
        print(f"Updated user: {updated_user.full_name}")
    
    # 9. Deactivate user
    if user:
        deactivated_user = user_repo.deactivate_user(user.id)
        print(f"User deactivated: {deactivated_user.is_active if deactivated_user else 'Failed'}")


def example_session_operations():
    """Example of session repository operations"""
    # Get database session
    db: Session = next(get_session())
    
    # Initialize repositories
    user_repo = UserRepository(db)
    session_repo = SessionRepository(db)
    
    print("\n=== Session Repository Examples ===")
    
    # 1. Get a user first
    user = user_repo.get_by_email("john.doe@example.com")
    if not user:
        print("User not found, skipping session examples")
        return
    
    # 2. Create a new session
    session_token = "example_session_token_123"
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    session = session_repo.create_session(
        user_id=user.id,
        session_token=session_token,
        expires_at=expires_at,
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0..."
    )
    print(f"Created session: {session.session_token}")
    
    # 3. Get session by token
    found_session = session_repo.get_by_token(session_token)
    print(f"Found session by token: {found_session is not None}")
    
    # 4. Get all sessions for user
    user_sessions = session_repo.get_by_user_id(user.id)
    print(f"User sessions count: {len(user_sessions)}")
    
    # 5. Get active sessions
    active_sessions = session_repo.get_active_sessions(user.id)
    print(f"Active sessions count: {len(active_sessions)}")
    
    # 6. Get session statistics
    stats = session_repo.get_session_stats(user.id)
    print(f"Session statistics: {stats}")
    
    # 7. Extend session
    new_expires_at = datetime.utcnow() + timedelta(hours=48)
    extended_session = session_repo.extend_session(session_token, new_expires_at)
    print(f"Session extended: {extended_session is not None}")
    
    # 8. Get recent sessions
    recent_sessions = session_repo.get_recent_sessions(user.id, hours=1)
    print(f"Recent sessions (last hour): {len(recent_sessions)}")
    
    # 9. Delete session
    deleted = session_repo.delete_session(session_token)
    print(f"Session deleted: {deleted}")


def example_admin_operations():
    """Example of admin operations using repositories"""
    # Get database session
    db: Session = next(get_session())
    
    # Initialize repositories
    user_repo = UserRepository(db)
    session_repo = SessionRepository(db)
    
    print("\n=== Admin Operations Examples ===")
    
    # 1. Get all users with pagination
    all_users = user_repo.get_all(skip=0, limit=10)
    print(f"All users (first 10): {len(all_users)}")
    
    # 2. Get users by role
    admin_users = user_repo.get_users_by_role(UserRole.ADMIN)
    print(f"Admin users: {len(admin_users)}")
    
    # 3. Get Google users
    google_users = user_repo.get_google_users()
    print(f"Google users: {len(google_users)}")
    
    # 4. Clean up expired sessions
    deleted_count = session_repo.delete_expired_sessions()
    print(f"Cleaned up expired sessions: {deleted_count}")
    
    # 5. Clean up old sessions (older than 30 days)
    old_sessions_deleted = session_repo.cleanup_old_sessions(days=30)
    print(f"Cleaned up old sessions: {old_sessions_deleted}")
    
    # 6. Get comprehensive statistics
    user_stats = user_repo.get_user_stats()
    session_stats = session_repo.get_session_stats()
    
    print(f"Comprehensive stats:")
    print(f"  Users: {user_stats}")
    print(f"  Sessions: {session_stats}")


if __name__ == "__main__":
    print("Repository Pattern Usage Examples")
    print("=" * 50)
    
    try:
        example_user_operations()
        example_session_operations()
        example_admin_operations()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure the database is set up and accessible.")
