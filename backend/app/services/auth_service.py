from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
    verify_token_type,
)
from app.repositories import UserRepository
from app.schemas.auth import (
    AuthResponse,
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.common import MessageResponse


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)

    async def register(self, user_data: RegisterRequest) -> AuthResponse:
        existing = await self.user_repo.get_by_email(user_data.email)
        if existing:
            raise ConflictException("Email already registered")

        existing = await self.user_repo.get_by_username(user_data.username)
        if existing:
            raise ConflictException("Username already taken")

        password_hash = hash_password(user_data.password)
        user = await self.user_repo.create(
            email=user_data.email,
            username=user_data.username,
            password_hash=password_hash,
        )

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        token = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        user_resp = UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            role=user.role.value if hasattr(user.role, "value") else user.role,
            subscription_tier=user.subscription_tier.value if hasattr(user.subscription_tier, "value") else user.subscription_tier,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            profile_image=user.profile_image,
            created_at=user.created_at.isoformat() if hasattr(user.created_at, "isoformat") else str(user.created_at),
            updated_at=user.updated_at.isoformat() if hasattr(user.updated_at, "isoformat") else str(user.updated_at),
        )
        return AuthResponse(user=user_resp, token=token)

    async def login(self, credentials: LoginRequest) -> AuthResponse:
        user = await self.user_repo.get_by_email(credentials.email)
        if not user:
            raise UnauthorizedException("Invalid email or password")

        if not verify_password(credentials.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        await self.user_repo.increment_daily_count(user.id)

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        token = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        user_resp = UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            role=user.role.value if hasattr(user.role, "value") else user.role,
            subscription_tier=user.subscription_tier.value if hasattr(user.subscription_tier, "value") else user.subscription_tier,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            profile_image=user.profile_image,
            created_at=user.created_at.isoformat() if hasattr(user.created_at, "isoformat") else str(user.created_at),
            updated_at=user.updated_at.isoformat() if hasattr(user.updated_at, "isoformat") else str(user.updated_at),
        )
        return AuthResponse(user=user_resp, token=token)

    async def refresh_token(self, refresh_token_str: str) -> TokenResponse:
        payload = decode_token(refresh_token_str)
        if not payload:
            raise UnauthorizedException("Invalid or expired refresh token")

        if not verify_token_type(payload, "refresh"):
            raise UnauthorizedException("Token is not a refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid token payload")

        access_token = create_access_token({"sub": user_id})
        new_refresh_token = create_refresh_token({"sub": user_id})

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    async def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> MessageResponse:
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException("User", user_id)

        if not verify_password(current_password, user.password_hash):
            raise BadRequestException("Current password is incorrect")

        user.password_hash = hash_password(new_password)
        return MessageResponse(message="Password changed successfully")

    async def get_profile(self, user_id: str) -> UserResponse:
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException("User", user_id)

        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            role=user.role.value if hasattr(user.role, "value") else user.role,
            subscription_tier=user.subscription_tier.value if hasattr(user.subscription_tier, "value") else user.subscription_tier,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            profile_image=user.profile_image,
            created_at=user.created_at.isoformat() if hasattr(user.created_at, "isoformat") else str(user.created_at),
            updated_at=user.updated_at.isoformat() if hasattr(user.updated_at, "isoformat") else str(user.updated_at),
        )
