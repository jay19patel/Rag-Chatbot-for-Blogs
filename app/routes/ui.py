from fastapi import APIRouter, Request, Depends, Response, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional

from app.utility.dependencies import get_optional_user, get_current_user
from app.models_schema import User
from app.config import settings


router = APIRouter(tags=["UI"])
templates = Jinja2Templates(directory="app/templates")


# ============================================================================
# Public Pages
# ============================================================================

@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    user: Optional[User] = Depends(get_optional_user)
):
    """Home page - shows welcome page for all users"""
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "settings": settings,
            "user": user
        }
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    user: Optional[User] = Depends(get_optional_user)
):
    """Login page"""
    if user:
        return RedirectResponse(url="/profile", status_code=302)

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "settings": settings,
            "user": None
        }
    )


@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    user: Optional[User] = Depends(get_optional_user)
):
    """Registration page"""
    if user:
        return RedirectResponse(url="/profile", status_code=302)

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "settings": settings,
            "user": None
        }
    )


# ============================================================================
# Protected Pages
# ============================================================================

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    user: User = Depends(get_current_user)
):
    """User profile page (protected)"""
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "settings": settings,
            "user": user
        }
    )


# ============================================================================
# Error Pages (These routes are not used - errors are handled by exception handlers in main.py)
# ============================================================================

