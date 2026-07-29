from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.dependencies.auth import get_current_user
from app.schemas.generator import (
    GenerateRequest, GenerateResponse, EnhanceRequest,
    TranslateRequest, CompleteRequest,
)
from app.services.generator_service import GeneratorService

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate_prompt(
    request: GenerateRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = GeneratorService(session)
    return await service.generate_prompt(current_user.id, request)


@router.post("/enhance", response_model=GenerateResponse)
async def enhance_prompt(
    request: EnhanceRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = GeneratorService(session)
    return await service.enhance_prompt(request)


@router.post("/translate", response_model=GenerateResponse)
async def translate_prompt(
    request: TranslateRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = GeneratorService(session)
    return await service.enhance_prompt(
        EnhanceRequest(prompt_content=request.prompt_content, instructions=f"Translate this prompt to {request.target_language}")
    )


@router.post("/complete", response_model=GenerateResponse)
async def complete_prompt(
    request: CompleteRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = GeneratorService(session)
    enhance_req = EnhanceRequest(
        prompt_content=request.partial_prompt,
        instructions=f"Complete this partial prompt. Context: {request.context or 'No additional context'}"
    )
    return await service.enhance_prompt(enhance_req)
