from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.dependencies.auth import get_current_user
from app.schemas.collection import (
    CollectionCreateRequest, CollectionUpdateRequest, CollectionResponse,
    AddToCollectionRequest,
)
from app.schemas.common import MessageResponse
from app.services.collection_service import CollectionService

router = APIRouter()


@router.get("/", response_model=list[CollectionResponse])
async def list_collections(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = CollectionService(session)
    return await service.get_user_collections(current_user.id)


@router.post("/", response_model=CollectionResponse, status_code=201)
async def create_collection(
    request: CollectionCreateRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = CollectionService(session)
    return await service.create_collection(current_user.id, request)


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = CollectionService(session)
    return await service.get_collection(collection_id, current_user.id)


@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: UUID,
    request: CollectionUpdateRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = CollectionService(session)
    return await service.update_collection(collection_id, current_user.id, request)


@router.delete("/{collection_id}", response_model=MessageResponse)
async def delete_collection(
    collection_id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = CollectionService(session)
    await service.delete_collection(collection_id, current_user.id)
    return MessageResponse(message="Collection deleted")


@router.post("/{collection_id}/prompts", response_model=MessageResponse)
async def add_to_collection(
    collection_id: UUID,
    request: AddToCollectionRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = CollectionService(session)
    await service.add_prompt(collection_id, UUID(request.prompt_id), current_user.id)
    return MessageResponse(message="Prompt added to collection")


@router.delete("/{collection_id}/prompts/{prompt_id}", response_model=MessageResponse)
async def remove_from_collection(
    collection_id: UUID,
    prompt_id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = CollectionService(session)
    await service.remove_prompt(collection_id, prompt_id, current_user.id)
    return MessageResponse(message="Prompt removed from collection")
