from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.dependencies.auth import get_current_user, require_admin
from app.schemas.category import CategoryCreateRequest, CategoryUpdateRequest, CategoryResponse
from app.services.category_service import CategoryService

router = APIRouter()


@router.get("/", response_model=list[CategoryResponse])
async def list_categories(session: AsyncSession = Depends(get_session)):
    service = CategoryService(session)
    return await service.get_all_categories()


@router.get("/{slug}", response_model=CategoryResponse)
async def get_category(slug: str, session: AsyncSession = Depends(get_session)):
    service = CategoryService(session)
    return await service.get_category_by_slug(slug)


@router.post("/", response_model=CategoryResponse, status_code=201)
async def create_category(
    request: CategoryCreateRequest,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    service = CategoryService(session)
    return await service.create_category(request)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    request: CategoryUpdateRequest,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    service = CategoryService(session)
    return await service.update_category(category_id, request)


@router.delete("/{category_id}")
async def delete_category(
    category_id: UUID,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    service = CategoryService(session)
    await service.delete_category(category_id)
    return {"message": "Category deleted"}
