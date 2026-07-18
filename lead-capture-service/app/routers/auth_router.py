from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.config import settings
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth/google", tags=["auth"])


@router.get("/login")
def google_login():
    return RedirectResponse(AuthService.build_google_login_url())


@router.get("/callback")
def google_callback(code: str):
    user_info = AuthService.exchange_code_for_user(code)
    token = AuthService.create_access_token(user_info["email"])
    return RedirectResponse(f"{settings.FRONTEND_URL}/auth/success?token={token}")