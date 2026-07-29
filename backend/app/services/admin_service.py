from __future__ import annotations

import platform
from datetime import date, datetime, timezone
from time import time
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.prompt import PromptStatus
from app.repositories import (
    CategoryRepository,
    ImportLogRepository,
    PromptRepository,
    SiteSettingsRepository,
    SubscriptionRepository,
    UserRepository,
)
from app.schemas.admin import AdminUserUpdateRequest
from app.schemas.auth import UserResponse
from app.schemas.common import MessageResponse
from app.schemas.prompt import PromptResponse, PromptTagResponse


class AdminService:
    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)
        self.prompt_repo = PromptRepository(db)
        self.category_repo = CategoryRepository(db)
        self.sub_repo = SubscriptionRepository(db)
        self.import_repo = ImportLogRepository(db)
        self.settings_repo = SiteSettingsRepository(db)

    async def get_dashboard(self) -> dict:
        total_users = await self.user_repo.get_active_users_count()
        active_today = await self.user_repo.get_daily_active_users(date.today())
        sub_count = await self.sub_repo.get_subscription_count()
        premium_users = await self.user_repo.get_subscriber_count()

        public_prompts = await self.prompt_repo.count(
            filters={"status": PromptStatus.PUBLISHED, "is_public": True}
        )
        total_prompts = await self.prompt_repo.count()

        imports_list, _ = await self.import_repo.get_multi()
        total_imports = len(imports_list)
        pending_imports = len([i for i in imports_list if i.status == "processing"])

        return {
            "total_users": total_users,
            "active_users_today": active_today,
            "total_prompts": total_prompts,
            "public_prompts": public_prompts,
            "total_generations": 0,
            "total_imports": total_imports,
            "premium_users": premium_users,
            "pending_imports": pending_imports,
            "revenue_monthly": float(sub_count * 19.99),
            "storage_used_mb": 0.0,
        }

    async def get_settings(self) -> list[dict]:
        settings_list = await self.settings_repo.get_public_settings()
        return [
            {
                "id": str(s.id),
                "key": s.key,
                "value": s.value,
                "type": s.type,
                "description": s.description,
                "updated_at": s.updated_at.isoformat() if hasattr(s.updated_at, "isoformat") else str(s.updated_at),
            }
            for s in settings_list
        ]

    async def update_setting(self, key: str, value: str) -> MessageResponse:
        await self.settings_repo.upsert_setting(key=key, value=value)
        return MessageResponse(message=f"Setting '{key}' updated successfully")

    async def get_system_health(self) -> dict:
        import psutil

        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()

        return {
            "status": "healthy",
            "version": "1.0.0",
            "environment": "production",
            "uptime_seconds": int(time() - psutil.boot_time()),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "cpu": {
                "usage_percent": psutil.cpu_percent(interval=0.1),
                "cores_physical": psutil.cpu_count(logical=False),
                "cores_logical": psutil.cpu_count(logical=True),
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "usage_percent": memory.percent,
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": disk.percent,
            },
            "network": {
                "bytes_sent": net.bytes_sent,
                "bytes_received": net.bytes_recv,
            },
            "database": "connected",
            "cache": "connected",
        }

    async def manage_user(
        self, user_id: str, data: AdminUserUpdateRequest
    ) -> dict:
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException("User", user_id)

        update_data = {}
        if data.role is not None:
            update_data["role"] = data.role
        if data.subscription_tier is not None:
            update_data["subscription_tier"] = data.subscription_tier
        if data.is_active is not None:
            update_data["is_active"] = data.is_active
        if data.is_email_verified is not None:
            update_data["is_email_verified"] = data.is_email_verified

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

    async def get_recent_imports(self, limit: int = 10) -> list[dict]:
        imports = await self.import_repo.get_recent(limit=limit)
        return [
            {
                "id": imp.id,
                "uuid": imp.uuid,
                "source": imp.source,
                "source_url": imp.source_url,
                "total_items": imp.total_items,
                "imported_items": imp.imported_items,
                "failed_items": imp.failed_items,
                "status": imp.status,
                "error_message": imp.error_message,
                "imported_by": imp.imported_by,
                "started_at": imp.started_at.isoformat() if imp.started_at else None,
                "completed_at": imp.completed_at.isoformat() if imp.completed_at else None,
                "created_at": imp.created_at.isoformat() if hasattr(imp.created_at, "isoformat") else str(imp.created_at),
            }
            for imp in imports
        ]

    async def toggle_featured(self, prompt_id: str) -> PromptResponse:
        prompt = await self.prompt_repo.get_prompt_with_relations(prompt_id)
        if not prompt:
            raise NotFoundException("Prompt", prompt_id)

        if prompt.rating_avg >= 4.0 and prompt.rating_count >= 5:
            from app.models.prompt import Prompt
            await self.prompt_repo.update(prompt_id, is_template=not prompt.is_template)
        else:
            await self.prompt_repo.update(prompt_id, is_template=not prompt.is_template)

        prompt = await self.prompt_repo.get_prompt_with_relations(prompt_id)
        if not prompt:
            raise NotFoundException("Prompt", prompt_id)

        return PromptResponse(
            id=str(prompt.id),
            user_id=str(prompt.user_id),
            title=prompt.title,
            title_ar=prompt.title_ar,
            content=prompt.content,
            content_ar=prompt.content_ar,
            description=prompt.description,
            description_ar=prompt.description_ar,
            model_id=str(prompt.model_id) if prompt.model_id else None,
            category_id=str(prompt.category_id) if prompt.category_id else None,
            is_public=prompt.is_public,
            is_premium=prompt.is_premium,
            is_template=prompt.is_template,
            variables=prompt.variables,
            variables_ar=prompt.variables_ar,
            usage_count=prompt.usage_count,
            copy_count=prompt.copy_count,
            rating_avg=prompt.rating_avg,
            rating_count=prompt.rating_count,
            status=prompt.status.value if hasattr(prompt.status, "value") else prompt.status,
            version=prompt.version,
            tags=[
                PromptTagResponse(id=str(t.id), name=t.name, slug=t.slug)
                for t in getattr(prompt, "tags", []) or []
            ],
            created_at=prompt.created_at,
            updated_at=prompt.updated_at,
        )
