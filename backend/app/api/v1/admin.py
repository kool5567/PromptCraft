from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.dependencies.auth import require_admin, require_superadmin
from app.schemas.admin import (
    DashboardStatsResponse, AdminUserUpdateRequest, AdminPromptUpdateRequest,
    SiteSettingUpdateRequest, SiteSettingResponse, SyncGithubRequest,
    AdminLogResponse,
)
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.admin_service import AdminService
from app.services.import_service import ImportService

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard(
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    service = AdminService(session)
    return await service.get_dashboard_stats()


@router.get("/users", response_model=PaginatedResponse[dict])
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    service = AdminService(session)
    users, total = await service.list_users(page, size)
    return PaginatedResponse(
        items=users, total=total, page=page, size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )


@router.get("/users/{user_id}")
async def get_user(
    user_id: UUID,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    from app.repositories.user_repo import UserRepository
    repo = UserRepository(session)
    user = await repo.get(user_id)
    if not user:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("User", user_id)
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "role": user.role.value if hasattr(user.role, "value") else user.role,
        "subscription_tier": user.subscription_tier.value if hasattr(user.subscription_tier, "value") else user.subscription_tier,
        "is_active": user.is_active,
        "is_email_verified": user.is_email_verified,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }


@router.put("/users/{user_id}", response_model=dict)
async def update_user(
    user_id: UUID,
    request: AdminUserUpdateRequest,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    service = AdminService(session)
    return await service.update_user(user_id, request.model_dump(exclude_none=True), admin.id)


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: UUID,
    admin=Depends(require_superadmin),
    session: AsyncSession = Depends(get_session),
):
    service = AdminService(session)
    await service.delete_user(user_id, admin.id)
    return MessageResponse(message="User deactivated")


@router.get("/prompts", response_model=PaginatedResponse[dict])
async def list_prompts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    service = AdminService(session)
    prompts, total = await service.list_all_prompts(page, size)
    return PaginatedResponse(
        items=prompts, total=total, page=page, size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )


@router.put("/prompts/{prompt_id}/status", response_model=dict)
async def update_prompt_status(
    prompt_id: UUID,
    request: AdminPromptUpdateRequest,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    service = AdminService(session)
    if request.status:
        return await service.update_prompt_status(prompt_id, request.status, admin.id)
    from app.repositories.prompt_repo import PromptRepository
    repo = PromptRepository(session)
    update_data = request.model_dump(exclude_none=True, exclude={"status"})
    await repo.update(prompt_id, **update_data)
    return {"id": str(prompt_id), "message": "Prompt updated"}


@router.delete("/prompts/{prompt_id}", response_model=MessageResponse)
async def delete_prompt(
    prompt_id: UUID,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    from app.repositories.prompt_repo import PromptRepository
    repo = PromptRepository(session)
    await repo.delete(prompt_id)
    return MessageResponse(message="Prompt deleted")


@router.get("/imports", response_model=list[dict])
async def list_imports(
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    from app.repositories.import_repo import ImportRepository
    repo = ImportRepository(session)
    jobs = await repo.get_recent_imports(50)
    return [
        {
            "id": str(j.id),
            "user_id": str(j.user_id),
            "source_type": j.source_type.value if hasattr(j.source_type, "value") else j.source_type,
            "source_url": j.source_url,
            "status": j.status.value if hasattr(j.status, "value") else j.status,
            "items_imported": j.items_imported,
            "items_failed": j.items_failed,
            "created_at": j.created_at.isoformat(),
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
        }
        for j in jobs
    ]


@router.post("/sync-github", response_model=dict)
async def sync_github(
    request: SyncGithubRequest,
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    service = ImportService(session)
    job = await service.import_from_github(
        user_id=admin.id,
        repo_url=request.repo_url,
        branch=request.branch,
        file_pattern=request.file_pattern,
        category_id=UUID(request.category_id) if request.category_id else None,
    )
    return {
        "job_id": str(job.id),
        "status": job.status.value if hasattr(job.status, "value") else job.status,
        "message": "GitHub sync started",
    }


@router.get("/settings", response_model=dict)
async def get_settings(
    admin=Depends(require_superadmin),
    session: AsyncSession = Depends(get_session),
):
    service = AdminService(session)
    return await service.get_settings()


@router.put("/settings", response_model=dict)
async def update_settings(
    request: SiteSettingUpdateRequest,
    admin=Depends(require_superadmin),
    session: AsyncSession = Depends(get_session),
):
    service = AdminService(session)
    return await service.update_setting(
        key=request.key,
        value=request.value,
        type=request.type,
        description=request.description,
        admin_id=admin.id,
    )


@router.get("/analytics", response_model=dict)
async def get_analytics(
    admin=Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    service = AdminService(session)
    stats = await service.get_dashboard_stats()
    return {
        "stats": stats.model_dump(),
        "charts": {
            "users_growth": [],
            "prompts_growth": [],
            "generations_daily": [],
        },
    }


@router.get("/logs", response_model=PaginatedResponse[dict])
async def get_logs(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    admin=Depends(require_superadmin),
    session: AsyncSession = Depends(get_session),
):
    service = AdminService(session)
    logs, total = await service.get_admin_logs(page, size)
    return PaginatedResponse(
        items=logs, total=total, page=page, size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )


@router.post("/seed-models", response_model=MessageResponse)
async def seed_models(
    admin=Depends(require_superadmin),
    session: AsyncSession = Depends(get_session),
):
    from app.models.ai_model import AiModel, ModelCategory
    import uuid

    models_data = [
        {"name": "ChatGPT", "slug": "chatgpt", "provider": "OpenAI", "category": ModelCategory.CHAT, "logo_url": "https://img.icons8.com/color/96/chatgpt.png", "sort_order": 1},
        {"name": "GPT-4", "slug": "gpt-4", "provider": "OpenAI", "category": ModelCategory.CHAT, "logo_url": "https://img.icons8.com/color/96/chatgpt.png", "sort_order": 2},
        {"name": "Gemini", "slug": "gemini", "provider": "Google", "category": ModelCategory.CHAT, "logo_url": "https://img.icons8.com/color/96/google-gemini.png", "sort_order": 3},
        {"name": "Claude", "slug": "claude", "provider": "Anthropic", "category": ModelCategory.CHAT, "logo_url": "https://img.icons8.com/color/96/claude-ai.png", "sort_order": 4},
        {"name": "Grok", "slug": "grok", "provider": "xAI", "category": ModelCategory.CHAT, "logo_url": "", "sort_order": 5},
        {"name": "DeepSeek", "slug": "deepseek", "provider": "DeepSeek", "category": ModelCategory.CHAT, "logo_url": "", "sort_order": 6},
        {"name": "Qwen", "slug": "qwen", "provider": "Alibaba", "category": ModelCategory.CHAT, "logo_url": "", "sort_order": 7},
        {"name": "Llama", "slug": "llama", "provider": "Meta", "category": ModelCategory.CHAT, "logo_url": "", "sort_order": 8},
        {"name": "Mistral", "slug": "mistral", "provider": "Mistral AI", "category": ModelCategory.CHAT, "logo_url": "", "sort_order": 9},
        {"name": "Perplexity", "slug": "perplexity", "provider": "Perplexity", "category": ModelCategory.CHAT, "logo_url": "", "sort_order": 10},
        {"name": "Copilot", "slug": "copilot", "provider": "Microsoft", "category": ModelCategory.CODE, "logo_url": "", "sort_order": 11},
        {"name": "DALL-E", "slug": "dall-e", "provider": "OpenAI", "category": ModelCategory.IMAGE, "logo_url": "", "sort_order": 12},
        {"name": "Midjourney", "slug": "midjourney", "provider": "Midjourney", "category": ModelCategory.IMAGE, "logo_url": "", "sort_order": 13},
        {"name": "Stable Diffusion", "slug": "stable-diffusion", "provider": "Stability AI", "category": ModelCategory.IMAGE, "logo_url": "", "sort_order": 14},
    ]

    for data in models_data:
        existing = await session.get(AiModel, data["slug"])
        if not existing:
            session.add(AiModel(id=uuid.uuid4(), **data))

    await session.flush()
    return MessageResponse(message=f"Seeded {len(models_data)} AI models")


@router.post("/seed-categories", response_model=MessageResponse)
async def seed_categories(
    admin=Depends(require_superadmin),
    session: AsyncSession = Depends(get_session),
):
    from app.models.category import Category
    import uuid

    categories = [
        {"name": "Creative Writing", "name_ar": "الكتابة الإبداعية", "slug": "creative-writing", "icon": "edit", "color": "#6366f1", "sort_order": 1},
        {"name": "Code Generation", "name_ar": "توليد الأكواد", "slug": "code-generation", "icon": "code", "color": "#22c55e", "sort_order": 2},
        {"name": "Business", "name_ar": "الأعمال", "slug": "business", "icon": "briefcase", "color": "#f59e0b", "sort_order": 3},
        {"name": "Education", "name_ar": "التعليم", "slug": "education", "icon": "book", "color": "#3b82f6", "sort_order": 4},
        {"name": "Marketing", "name_ar": "التسويق", "slug": "marketing", "icon": "megaphone", "color": "#ec4899", "sort_order": 5},
        {"name": "Data Analysis", "name_ar": "تحليل البيانات", "slug": "data-analysis", "icon": "chart", "color": "#8b5cf6", "sort_order": 6},
        {"name": "Image Generation", "name_ar": "توليد الصور", "slug": "image-generation", "icon": "image", "color": "#14b8a6", "sort_order": 7},
        {"name": "Video & Audio", "name_ar": "الفيديو والصوت", "slug": "video-audio", "icon": "video", "color": "#ef4444", "sort_order": 8},
        {"name": "Research", "name_ar": "البحث العلمي", "slug": "research", "icon": "search", "color": "#f97316", "sort_order": 9},
        {"name": "Social Media", "name_ar": "وسائل التواصل", "slug": "social-media", "icon": "share", "color": "#06b6d4", "sort_order": 10},
        {"name": "Translation", "name_ar": "الترجمة", "slug": "translation", "icon": "globe", "color": "#a855f7", "sort_order": 11},
        {"name": "Role Play", "name_ar": "تمثيل الأدوار", "slug": "role-play", "icon": "users", "color": "#e11d48", "sort_order": 12},
    ]

    for data in categories:
        existing = await session.execute(
            __import__("sqlalchemy").select(Category).where(Category.slug == data["slug"])
        )
        if not existing.scalar_one_or_none():
            session.add(Category(id=uuid.uuid4(), **data))

    await session.flush()
    return MessageResponse(message=f"Seeded {len(categories)} categories")
