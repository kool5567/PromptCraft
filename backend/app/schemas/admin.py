from pydantic import BaseModel
from datetime import datetime


class DashboardStatsResponse(BaseModel):
    total_users: int
    active_users_today: int
    total_prompts: int
    public_prompts: int
    total_generations: int
    total_imports: int
    premium_users: int
    pending_imports: int
    revenue_monthly: float
    storage_used_mb: float


class AdminUserUpdateRequest(BaseModel):
    role: str | None = None
    subscription_tier: str | None = None
    is_active: bool | None = None
    is_email_verified: bool | None = None


class AdminPromptUpdateRequest(BaseModel):
    status: str | None = None
    is_public: bool | None = None
    is_premium: bool | None = None
    featured: bool | None = None


class SiteSettingUpdateRequest(BaseModel):
    key: str
    value: dict
    type: str = "string"
    description: str | None = None


class SiteSettingResponse(BaseModel):
    id: str
    key: str
    value: dict
    type: str
    description: str | None = None
    updated_at: datetime


class AdminLogResponse(BaseModel):
    id: str
    admin_id: str
    action: str
    target_type: str | None = None
    target_id: str | None = None
    details: dict | None = None
    created_at: datetime


class SyncGithubRequest(BaseModel):
    repo_url: str
    branch: str = "main"
    file_pattern: str = "**/*.md"
    category_id: str | None = None
    auto_import: bool = True
    sync_interval_hours: int = 24
