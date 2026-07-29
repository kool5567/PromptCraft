from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.repositories import UserRepository
from app.schemas.auth import UserResponse
from app.schemas.user import UserUpdateRequest


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)

    async def get_user(self, user_id: str) -> UserResponse:
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

    async def update_user(self, user_id: str, data: UserUpdateRequest) -> UserResponse:
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException("User", user_id)

        if data.username is not None and data.username != user.username:
            existing = await self.user_repo.get_by_username(data.username)
            if existing:
                raise ConflictException("Username already taken")

        update_data = {}
        if data.username is not None:
            update_data["username"] = data.username
        if data.profile_image is not None:
            update_data["profile_image"] = data.profile_image

        if update_data:
            user = await self.user_repo.update(user_id, **update_data)
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

    async def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[UserResponse]:
        if search:
            users = await self.user_repo.search_users(search, skip=skip, limit=limit)
        else:
            users, _ = await self.user_repo.get_multi(skip=skip, limit=limit)

        return [
            UserResponse(
                id=str(u.id),
                email=u.email,
                username=u.username,
                role=u.role.value if hasattr(u.role, "value") else u.role,
                subscription_tier=u.subscription_tier.value if hasattr(u.subscription_tier, "value") else u.subscription_tier,
                is_active=u.is_active,
                is_email_verified=u.is_email_verified,
                profile_image=u.profile_image,
                created_at=u.created_at.isoformat() if hasattr(u.created_at, "isoformat") else str(u.created_at),
                updated_at=u.updated_at.isoformat() if hasattr(u.updated_at, "isoformat") else str(u.updated_at),
            )
            for u in users
        ]
