from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.dependencies.auth import get_current_user
from app.schemas.import_job import ImportGithubRequest, ImportJobResponse
from app.services.import_service import ImportService

router = APIRouter()


@router.post("/github", response_model=ImportJobResponse, status_code=201)
async def import_from_github(
    request: ImportGithubRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = ImportService(session)
    job = await service.import_from_github(
        user_id=current_user.id,
        repo_url=request.repo_url,
        branch=request.branch,
        file_pattern=request.file_pattern,
        category_id=UUID(request.category_id) if request.category_id else None,
        model_id=UUID(request.model_id) if request.model_id else None,
        tags=request.tags,
        is_public=request.is_public,
    )
    return _job_to_response(job)


@router.post("/file", response_model=ImportJobResponse)
async def import_from_file(
    file: UploadFile = File(...),
    category_id: str = Form(None),
    model_id: str = Form(None),
    is_public: bool = Form(False),
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    content = await file.read()
    text_content = content.decode("utf-8")
    service = ImportService(session)

    if file.filename and file.filename.endswith(".csv"):
        job = await service.import_from_csv(
            user_id=current_user.id, csv_content=text_content,
            category_id=UUID(category_id) if category_id else None,
            model_id=UUID(model_id) if model_id else None,
            is_public=is_public,
        )
    else:
        job = await service.import_from_json(
            user_id=current_user.id, json_content=text_content,
            category_id=UUID(category_id) if category_id else None,
            model_id=UUID(model_id) if model_id else None,
            is_public=is_public,
        )

    return _job_to_response(job)


@router.get("/jobs", response_model=list[ImportJobResponse])
async def list_imports(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = ImportService(session)
    jobs = await service.get_user_imports(current_user.id)
    return [_job_to_response(j) for j in jobs]


@router.get("/jobs/{job_id}", response_model=ImportJobResponse)
async def get_import_job(
    job_id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    service = ImportService(session)
    job = await service.get_import_job(job_id)
    return _job_to_response(job)


@router.get("/export")
async def export_prompts(
    format: str = "json",
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    from app.repositories.prompt_repo import PromptRepository
    repo = PromptRepository(session)
    prompts, _ = await repo.get_user_prompts(current_user.id)
    data = [
        {"title": p.title, "content": p.content, "description": p.description}
        for p in prompts
    ]
    return {"format": format, "count": len(data), "data": data}


def _job_to_response(job) -> ImportJobResponse:
    return ImportJobResponse(
        id=str(job.id),
        user_id=str(job.user_id),
        source_type=job.source_type.value if hasattr(job.source_type, "value") else job.source_type,
        source_url=job.source_url,
        status=job.status.value if hasattr(job.status, "value") else job.status,
        items_total=job.items_total,
        items_imported=job.items_imported,
        items_failed=job.items_failed,
        error_log=job.error_log,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
    )
