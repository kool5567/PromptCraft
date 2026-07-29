from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.core.security import decode_token, verify_token_type
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.models.user import UserRole
from app.repositories.user_repo import UserRepository

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    session: AsyncSession = Depends(get_session),
):
    if not credentials:
        raise UnauthorizedException("Authentication required")

    payload = decode_token(credentials.credentials)
    if not payload or not verify_token_type(payload, "access"):
        raise UnauthorizedException("Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    user_repo = UserRepository(session)
    user = await user_repo.get(UUID(user_id))
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    session: AsyncSession = Depends(get_session),
):
    if not credentials:
        return None

    payload = decode_token(credentials.credentials)
    if not payload or not verify_token_type(payload, "access"):
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user_repo = UserRepository(session)
    user = await user_repo.get(UUID(user_id))
    if not user or not user.is_active:
        return None

    return user


async def require_admin(current_user=Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise ForbiddenException("Admin access required")
    return current_user


async def require_superadmin(current_user=Depends(get_current_user)):
    if current_user.role != UserRole.SUPERADMIN:
        raise ForbiddenException("Superadmin access required")
    return current_user
