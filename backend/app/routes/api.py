from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlmodel import Session, select
from datetime import datetime, timedelta
from typing import Optional, List
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

from app.database import get_session
from app.models_schema import (
    User, UserSession, UserRole,
    UserRegister, UserLogin, UserResponse, UserUpdate,
    Token, MessageResponse
)
from app.auth import (
    verify_password, get_password_hash, create_access_token,
    generate_session_token
)
from app.utility.dependencies import get_current_user, get_current_active_user
from app.config import settings
from app.repository import UserRepository, SessionRepository


router = APIRouter(prefix="/api", tags=["API"])


# OAuth Setup
config = Config(environ={
    "GOOGLE_CLIENT_ID": settings.google_client_id,
    "GOOGLE_CLIENT_SECRET": settings.google_client_secret,
})

oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


# ============================================================================
# Repository Dependencies
# ============================================================================

def get_user_repository(db: Session = Depends(get_session)) -> UserRepository:
    """Get UserRepository instance"""
    return UserRepository(db)


def get_session_repository(db: Session = Depends(get_session)) -> SessionRepository:
    """Get SessionRepository instance"""
    return SessionRepository(db)


# ============================================================================
# Authentication Routes
# ============================================================================

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Register a new user"""
    # Check if user already exists
    if user_repo.is_email_taken(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if user_repo.is_username_taken(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role if user_data.role else UserRole.USER
    )

    return user_repo.create(new_user)


@router.post("/auth/login", response_model=Token)
async def login(
    response: Response,
    request: Request,
    credentials: UserLogin,
    user_repo: UserRepository = Depends(get_user_repository),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """Login with email and password"""
    # Find user by email
    user = user_repo.get_by_email(credentials.email)

    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Create access token
    access_token = create_access_token(
        data={
            "sub": user.id,
            "email": user.email,
            "role": user.role.value
        }
    )

    # Create session
    session_token = generate_session_token()
    expires_at = datetime.now() + timedelta(minutes=settings.access_token_expire_minutes)

    session_repo.create_session(
        user_id=user.id,
        session_token=session_token,
        expires_at=expires_at,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    # Update last login
    user_repo.update_last_login(user.id)

    # Set session cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60
    )

    return Token(access_token=access_token)


@router.post("/auth/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    session_token: Optional[str] = None,
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """Logout user and invalidate session"""
    # Delete all user sessions
    session_repo.delete_user_sessions(current_user.id)

    # Clear session cookie
    response.delete_cookie("session_token")

    return MessageResponse(message="Logged out successfully")


# ============================================================================
# Google OAuth Routes
# ============================================================================

@router.get("/auth/google/login")
async def google_login(request: Request):
    """Initiate Google OAuth login"""
    redirect_uri = settings.google_redirect_uri
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback")
async def google_callback(
    request: Request,
    response: Response,
    user_repo: UserRepository = Depends(get_user_repository),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """Handle Google OAuth callback"""
    try:
        from starlette.responses import RedirectResponse

        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')

        if not user_info:
            # Redirect to frontend with error
            return RedirectResponse(url="http://localhost:3000/login?error=Failed to get user info")

        email = user_info.get('email')
        google_id = user_info.get('sub')
        full_name = user_info.get('name')

        # Check if user exists
        user = user_repo.get_by_email(email) or user_repo.get_by_google_id(google_id)

        if not user:
            # Create new user
            username = email.split('@')[0]
            # Ensure username is unique
            base_username = username
            counter = 1
            while user_repo.is_username_taken(username):
                username = f"{base_username}{counter}"
                counter += 1

            user = User(
                email=email,
                username=username,
                full_name=full_name,
                google_id=google_id,
                is_google_user=True,
                role=UserRole.USER
            )
            user = user_repo.create(user)
        else:
            # Update existing user with Google info if not set
            if not user.google_id:
                user.google_id = google_id
                user.is_google_user = True
                user = user_repo.update(user)

        # Create access token
        access_token = create_access_token(
            data={
                "sub": user.id,
                "email": user.email,
                "role": user.role.value
            }
        )

        # Create session
        session_token = generate_session_token()
        expires_at = datetime.now() + timedelta(minutes=settings.access_token_expire_minutes)

        session_repo.create_session(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )

        # Update last login
        user_repo.update_last_login(user.id)

        # Set session cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=settings.access_token_expire_minutes * 60
        )

        # Redirect to frontend callback with token
        return RedirectResponse(url=f"http://localhost:3000/auth/callback?token={access_token}")

    except Exception as e:
        # Redirect to frontend with error
        return RedirectResponse(url=f"http://localhost:3000/login?error={str(e)}")


# ============================================================================
# User Profile Routes
# ============================================================================

@router.get("/user/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile"""
    return current_user


@router.put("/user/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Update current user profile"""
    # Check if username is already taken
    if user_update.username and user_update.username != current_user.username:
        if user_repo.is_username_taken(user_update.username, exclude_user_id=current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = user_update.username

    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name

    current_user.updated_at = datetime.now()

    return user_repo.update(current_user)


# ============================================================================
# Admin Routes
# ============================================================================

@router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Get all users (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return user_repo.get_all(skip=skip, limit=limit)


@router.get("/admin/users/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Get user statistics (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return user_repo.get_user_stats()


@router.get("/admin/sessions/stats")
async def get_session_stats(
    user_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """Get session statistics (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return session_repo.get_session_stats(user_id)


@router.delete("/admin/sessions/cleanup")
async def cleanup_expired_sessions(
    user_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """Clean up expired sessions (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    deleted_count = session_repo.delete_expired_sessions(user_id)
    return {"message": f"Cleaned up {deleted_count} expired sessions"}


@router.put("/admin/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Activate user account (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = user_repo.activate_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User activated successfully"}


@router.put("/admin/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Deactivate user account (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = user_repo.deactivate_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deactivated successfully"}


# ============================================================================
# User Search Endpoint (Mock Data)
# ============================================================================

@router.get("/users/search")
async def search_users(
    search: Optional[str] = None,
    filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
):
    """
    Search users with filters and pagination
    Returns mock data for demonstration
    """
    # Mock data
    mock_users = [
        {
            "name": "Jay Patel",
            "skills": ["Python", "FastAPI", "React", "PostgreSQL"],
            "address": "Mumbai, India",
            "image": "https://i.pravatar.cc/400?img=1",
            "role": "Admin",
            "description": "Full-stack developer with 5 years of experience in building scalable web applications using Python and modern JavaScript frameworks.",
            "date_of_birth": "1995-05-15"
        },
        {
            "name": "Priya Sharma",
            "skills": ["JavaScript", "Node.js", "MongoDB", "AWS"],
            "address": "Bangalore, India",
            "image": "https://i.pravatar.cc/400?img=5",
            "role": "User",
            "description": "Backend engineer specializing in microservices architecture and cloud infrastructure management.",
            "date_of_birth": "1998-08-22"
        },
        {
            "name": "Rahul Kumar",
            "skills": ["Java", "Spring Boot", "Docker", "Kubernetes"],
            "address": "Delhi, India",
            "image": "https://i.pravatar.cc/400?img=12",
            "role": "Admin",
            "description": "DevOps expert with strong background in containerization and orchestration technologies.",
            "date_of_birth": "1992-03-10"
        },
        {
            "name": "Sneha Reddy",
            "skills": ["UI/UX Design", "Figma", "Adobe XD", "HTML/CSS"],
            "address": "Hyderabad, India",
            "image": "https://i.pravatar.cc/400?img=9",
            "role": "User",
            "description": "Creative designer focused on creating intuitive and beautiful user experiences for web and mobile applications.",
            "date_of_birth": "1996-11-30"
        },
        {
            "name": "Amit Singh",
            "skills": ["Python", "Machine Learning", "TensorFlow", "Data Science"],
            "address": "Pune, India",
            "image": "https://i.pravatar.cc/400?img=13",
            "role": "User",
            "description": "Data scientist with expertise in building ML models and extracting insights from complex datasets.",
            "date_of_birth": "1994-07-18"
        },
        {
            "name": "Neha Gupta",
            "skills": ["React Native", "iOS", "Android", "Firebase"],
            "address": "Chennai, India",
            "image": "https://i.pravatar.cc/400?img=10",
            "role": "User",
            "description": "Mobile app developer creating cross-platform applications with focus on performance and user engagement.",
            "date_of_birth": "1997-09-05"
        },
        {
            "name": "Vikram Mehta",
            "skills": ["PHP", "Laravel", "MySQL", "Vue.js"],
            "address": "Ahmedabad, India",
            "image": "https://i.pravatar.cc/400?img=15",
            "role": "Admin",
            "description": "Senior developer with extensive experience in building enterprise-level web applications.",
            "date_of_birth": "1990-12-25"
        },
        {
            "name": "Anjali Desai",
            "skills": ["Angular", "TypeScript", "GraphQL", "RxJS"],
            "address": "Surat, India",
            "image": "https://i.pravatar.cc/400?img=20",
            "role": "User",
            "description": "Frontend specialist passionate about building reactive and scalable single-page applications.",
            "date_of_birth": "1999-04-12"
        },
        {
            "name": "Karan Joshi",
            "skills": ["Go", "gRPC", "Redis", "Microservices"],
            "address": "Jaipur, India",
            "image": "https://i.pravatar.cc/400?img=33",
            "role": "User",
            "description": "Backend architect designing high-performance distributed systems and APIs.",
            "date_of_birth": "1993-06-08"
        },
        {
            "name": "Pooja Iyer",
            "skills": ["QA Testing", "Selenium", "JIRA", "Automation"],
            "address": "Kolkata, India",
            "image": "https://i.pravatar.cc/400?img=23",
            "role": "User",
            "description": "Quality assurance engineer ensuring software reliability through comprehensive testing strategies.",
            "date_of_birth": "1995-02-28"
        },
        {
            "name": "Rohan Nair",
            "skills": ["Blockchain", "Solidity", "Web3", "Ethereum"],
            "address": "Kochi, India",
            "image": "https://i.pravatar.cc/400?img=51",
            "role": "Admin",
            "description": "Blockchain developer building decentralized applications and smart contracts.",
            "date_of_birth": "1996-10-14"
        },
        {
            "name": "Divya Pillai",
            "skills": ["Content Writing", "SEO", "Digital Marketing", "Analytics"],
            "address": "Trivandrum, India",
            "image": "https://i.pravatar.cc/400?img=29",
            "role": "User",
            "description": "Content strategist and digital marketer driving online engagement and brand visibility.",
            "date_of_birth": "1998-01-20"
        },
        {
            "name": "Arjun Rao",
            "skills": ["C++", "Game Development", "Unity", "Unreal Engine"],
            "address": "Mysore, India",
            "image": "https://i.pravatar.cc/400?img=60",
            "role": "User",
            "description": "Game developer creating immersive gaming experiences with cutting-edge graphics and mechanics.",
            "date_of_birth": "1994-08-03"
        },
        {
            "name": "Shruti Kapoor",
            "skills": ["Product Management", "Agile", "Scrum", "Leadership"],
            "address": "Chandigarh, India",
            "image": "https://i.pravatar.cc/400?img=26",
            "role": "Admin",
            "description": "Product manager leading cross-functional teams to deliver innovative software solutions.",
            "date_of_birth": "1991-05-17"
        },
        {
            "name": "Sanjay Verma",
            "skills": ["Cybersecurity", "Penetration Testing", "Network Security", "Ethical Hacking"],
            "address": "Noida, India",
            "image": "https://i.pravatar.cc/400?img=68",
            "role": "User",
            "description": "Security expert protecting systems and data through comprehensive vulnerability assessments.",
            "date_of_birth": "1992-11-09"
        }
    ]

    # Filter by search term
    filtered_users = mock_users
    if search:
        search_lower = search.lower()
        filtered_users = [
            user for user in filtered_users
            if search_lower in user["name"].lower() or
               search_lower in user["address"].lower() or
               any(search_lower in skill.lower() for skill in user["skills"]) or
               search_lower in user["description"].lower()
        ]

    # Filter by filter parameter
    if filter:
        filters = [f.strip() for f in filter.split(',') if f.strip()]
        if filters:
            # For simplicity, filter by skills containing filter terms
            filtered_users = [
                user for user in filtered_users
                if any(
                    any(filter_term.lower() in skill.lower() for skill in user["skills"])
                    or filter_term.lower() in user["role"].lower()
                    for filter_term in filters
                )
            ]

    # Get total count
    total = len(filtered_users)

    # Apply pagination
    paginated_users = filtered_users[skip:skip + limit]

    return {
        "users": paginated_users,
        "total": total,
        "skip": skip,
        "limit": limit
    }


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ============================================================================
# Public Content: Testimonials & FAQs
# ============================================================================

@router.get("/content/testimonials")
async def get_testimonials():
    """Return a list of testimonials (public)."""
    return {
        "testimonials": [
            {
                "name": "Aisha Khan",
                "title": "Product Manager",
                "company": "Nimbus Tech",
                "avatar": "https://i.pravatar.cc/150?img=32",
                "quote": "This platform made it effortless to find top talent. The search and filtering are spot on!"
            },
            {
                "name": "Rohit Verma",
                "title": "Senior Developer",
                "company": "CoreStack",
                "avatar": "https://i.pravatar.cc/150?img=14",
                "quote": "The UX is clean, fast, and the profiles are rich with just the right info. Loved it."
            },
            {
                "name": "Neha Patel",
                "title": "UI/UX Designer",
                "company": "DesignForge",
                "avatar": "https://i.pravatar.cc/150?img=47",
                "quote": "Beautifully designed and a joy to use. I found collaborators in minutes!"
            }
        ]
    }


@router.get("/content/faqs")
async def get_faqs():
    """Return a list of FAQs (public)."""
    return {
        "faqs": [
            {
                "question": "How do I create an account?",
                "answer": "Click on Register, fill in your details, and verify your email to get started."
            },
            {
                "question": "Is my data secure?",
                "answer": "We use industry-standard security practices including hashed passwords and secure sessions."
            },
            {
                "question": "How can I contact support?",
                "answer": "Reach out via the Contact page or email support@example.com. We usually respond within 24 hours."
            }
        ]
    }

