from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_session
from app.dependencies.auth import get_current_user
from app.schemas.auth import UserResponse, ChangePasswordRequest
from app.schemas.user import ProfileUpdateRequest, ProfileResponse, UserStatsResponse
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService
from app.repositories import PromptRepository, FavoriteRepository, CollectionRepository

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    u = current_user
    return UserResponse(
        id=str(u.id), email=u.email, username=u.username,
        role=u.role.value if hasattr(u.role, "value") else u.role,
        subscription_tier=u.subscription_tier.value if hasattr(u.subscription_tier, "value") else u.subscription_tier,
        is_active=u.is_active, is_email_verified=u.is_email_verified,
        profile_image=u.profile_image,
        created_at=u.created_at.isoformat() if u.created_at else "",
        updated_at=u.updated_at.isoformat() if u.updated_at else "",
    )


@router.put("/me", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = AuthService(session)
    return await service.update_profile(current_user.id, request.model_dump(exclude_none=True))


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_stats(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    prompt_repo = PromptRepository(session)
    fav_repo = FavoriteRepository(session)
    coll_repo = CollectionRepository(session)
    uid = current_user.id
    total_prompts = await prompt_repo.count(filters={"user_id": uid})
    total_public = await prompt_repo.count(filters={"user_id": uid, "is_public": True})
    total_collections = await coll_repo.count(filters={"user_id": uid})
    total_favorites = await fav_repo.count(filters={"user_id": uid})
    return UserStatsResponse(
        total_prompts=total_prompts, total_public_prompts=total_public,
        total_collections=total_collections, total_favorites=total_favorites,
        total_generations=0, total_copies=0,
    )


@router.delete("/me", response_model=MessageResponse)
async def delete_account(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    from app.repositories import UserRepository
    repo = UserRepository(session)
    await repo.update(current_user.id, is_active=False)
    return MessageResponse(message="Account deactivated")


@router.put("/me/password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = AuthService(session)
    await service.change_password(current_user.id, request.current_password, request.new_password)
    return MessageResponse(message="Password changed successfully")
