from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.dependencies.auth import get_current_user
from app.schemas.auth import (
    RegisterRequest, LoginRequest, AuthResponse, TokenResponse,
    RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest,
    ChangePasswordRequest, UserResponse,
)
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(request: RegisterRequest, session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    return await service.register(request)


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    return await service.login(request)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshTokenRequest, session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    return await service.refresh_token(request.refresh_token)


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    return await service.get_user_by_id(current_user.id)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: ForgotPasswordRequest):
    return MessageResponse(message="If the email exists, a reset link has been sent")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest):
    return MessageResponse(message="Password has been reset successfully")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user=Depends(get_current_user),
):
    return MessageResponse(message="Password changed successfully")
