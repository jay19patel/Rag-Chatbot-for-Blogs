from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlmodel import Session, select
from datetime import datetime, timedelta
from typing import Optional
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from itsdangerous import URLSafeTimedSerializer

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

# CSRF token serializer
csrf_serializer = URLSafeTimedSerializer(settings.csrf_secret_key)


def generate_csrf_token() -> tuple[str, str]:
    """Generate a new CSRF token pair (raw_token, signed_token)"""
    import secrets
    raw_token = secrets.token_hex(16)
    signed_token = csrf_serializer.dumps(raw_token)
    return raw_token, signed_token


# ============================================================================
# CSRF Token Endpoint
# ============================================================================

@router.get("/auth/csrf-token")
async def get_csrf_token(response: Response):
    """Get a CSRF token for authentication"""
    raw_token, signed_token = generate_csrf_token()
    
    # Set raw token in cookie
    response.set_cookie(
        key="csrf_token",
        value=raw_token,
        httponly=False,  # Allow JavaScript to access it if needed
        secure=False,  # Set to True in production with HTTPS
        samesite="strict",
        max_age=3600  # 1 hour
    )
    
    # Return signed token to be used in headers
    return {"csrf_token": signed_token}


# ============================================================================
# Authentication Routes
# ============================================================================

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_session)
):
    """Register a new user"""
    # Check if user already exists
    statement = select(User).where(
        (User.email == user_data.email) | (User.username == user_data.username)
    )
    existing_user = db.exec(statement).first()

    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
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

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/auth/login", response_model=Token)
async def login(
    response: Response,
    request: Request,
    credentials: UserLogin,
    db: Session = Depends(get_session)
):
    """Login with email and password"""
    # Find user by email
    statement = select(User).where(User.email == credentials.email)
    user = db.exec(statement).first()

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
    expires_at = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    user_session = UserSession(
        user_id=user.id,
        session_token=session_token,
        expires_at=expires_at,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    db.add(user_session)
    db.commit()

    # Set session cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60
    )
    
    # Generate and set CSRF token
    raw_token, signed_token = generate_csrf_token()
    response.set_cookie(
        key="csrf_token",
        value=raw_token,
        httponly=False,  # Allow JavaScript to access it if needed
        secure=False,  # Set to True in production with HTTPS
        samesite="strict",
        max_age=3600  # 1 hour
    )

    return Token(access_token=access_token, csrf_token=signed_token)


@router.post("/auth/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    session_token: Optional[str] = None,
    db: Session = Depends(get_session)
):
    """Logout user and invalidate session"""
    # Delete all user sessions
    statement = select(UserSession).where(UserSession.user_id == current_user.id)
    sessions = db.exec(statement).all()

    for session in sessions:
        db.delete(session)

    db.commit()

    # Clear session cookie
    response.delete_cookie("session_token")
    
    # Clear CSRF token cookie
    response.delete_cookie("csrf_token")

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
    db: Session = Depends(get_session)
):
    """Handle Google OAuth callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )

        email = user_info.get('email')
        google_id = user_info.get('sub')
        full_name = user_info.get('name')

        # Check if user exists
        statement = select(User).where(
            (User.email == email) | (User.google_id == google_id)
        )
        user = db.exec(statement).first()

        if not user:
            # Create new user
            username = email.split('@')[0]
            # Ensure username is unique
            base_username = username
            counter = 1
            while True:
                stmt = select(User).where(User.username == username)
                if not db.exec(stmt).first():
                    break
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
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update existing user with Google info if not set
            if not user.google_id:
                user.google_id = google_id
                user.is_google_user = True
                db.add(user)
                db.commit()
                db.refresh(user)

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
        expires_at = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

        user_session = UserSession(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )

        db.add(user_session)
        db.commit()

        # Create redirect response
        from fastapi.responses import RedirectResponse
        redirect_response = RedirectResponse(url="/profile", status_code=302)

        # Set session cookie
        redirect_response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=settings.access_token_expire_minutes * 60
        )
        
        # Generate and set CSRF token
        raw_token, signed_token = generate_csrf_token()
        redirect_response.set_cookie(
            key="csrf_token",
            value=raw_token,
            httponly=False,  # Allow JavaScript to access it if needed
            secure=False,  # Set to True in production with HTTPS
            samesite="strict",
            max_age=3600  # 1 hour
        )

        return redirect_response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )


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
    db: Session = Depends(get_session)
):
    """Update current user profile"""
    # Check if username is already taken
    if user_update.username and user_update.username != current_user.username:
        statement = select(User).where(User.username == user_update.username)
        existing_user = db.exec(statement).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = user_update.username

    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name

    current_user.updated_at = datetime.utcnow()

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

