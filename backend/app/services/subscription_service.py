from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.repositories import SubscriptionRepository
from app.schemas.common import MessageResponse


PLANS = [
    {
        "id": "free",
        "name": "Free",
        "price": 0.0,
        "currency": "USD",
        "interval": "month",
        "features": [
            "5 generations per day",
            "50 saved prompts",
            "Community prompts access",
            "Basic support",
        ],
        "is_popular": False,
    },
    {
        "id": "basic",
        "name": "Basic",
        "price": 9.99,
        "currency": "USD",
        "interval": "month",
        "features": [
            "100 generations per day",
            "500 saved prompts",
            "Advanced prompt templates",
            "Priority support",
            "Export prompts",
        ],
        "is_popular": False,
    },
    {
        "id": "pro",
        "name": "Pro",
        "price": 19.99,
        "currency": "USD",
        "interval": "month",
        "features": [
            "Unlimited generations",
            "Unlimited saved prompts",
            "All AI providers",
            "Priority support",
            "Advanced analytics",
            "Team collaboration",
        ],
        "is_popular": True,
    },
    {
        "id": "enterprise",
        "name": "Enterprise",
        "price": 99.99,
        "currency": "USD",
        "interval": "month",
        "features": [
            "Everything in Pro",
            "Custom AI model fine-tuning",
            "Dedicated support",
            "SSO & SAML",
            "Custom integrations",
            "SLA guarantee",
        ],
        "is_popular": False,
    },
]

FEATURE_ACCESS = {
    "unlimited_generations": ["pro", "enterprise"],
    "advanced_templates": ["basic", "pro", "enterprise"],
    "export": ["basic", "pro", "enterprise"],
    "analytics": ["pro", "enterprise"],
    "team_collaboration": ["pro", "enterprise"],
    "custom_models": ["enterprise"],
    "sso": ["enterprise"],
}


class SubscriptionService:
    def __init__(self, db: AsyncSession) -> None:
        self.sub_repo = SubscriptionRepository(db)
        self.quota_repo = UsageQuotaRepository(db)

    async def get_current_subscription(self, user_id: str) -> dict:
        subscription = await self.sub_repo.get_by_user(user_id)
        if not subscription:
            return {
                "id": None,
                "user_id": user_id,
                "plan_type": "free",
                "status": "active",
                "start_date": None,
                "end_date": None,
                "trial_end": None,
                "auto_renew": False,
                "created_at": None,
                "updated_at": None,
            }

        return {
            "id": str(subscription.id),
            "user_id": str(subscription.user_id),
            "plan_type": subscription.plan_type.value if hasattr(subscription.plan_type, "value") else subscription.plan_type,
            "status": subscription.status.value if hasattr(subscription.status, "value") else subscription.status,
            "start_date": subscription.start_date,
            "end_date": subscription.end_date,
            "trial_end": subscription.trial_end,
            "auto_renew": subscription.auto_renew,
            "created_at": subscription.created_at,
            "updated_at": subscription.updated_at,
        }

    async def get_usage(self, user_id: str) -> dict:
        today = date.today()
        quota = await self.quota_repo.get_or_create(user_id, today)

        from datetime import timedelta
        start = today - timedelta(days=30)
        history = await self.quota_repo.get_usage_for_period(user_id, start, today)

        total_generated = sum(q.prompts_generated for q in history)
        total_saved = sum(q.prompts_saved for q in history)
        total_api = sum(q.api_calls for q in history)

        subscription = await self.sub_repo.get_by_user(user_id)
        if subscription and subscription.is_active:
            daily_limit = -1
        else:
            from app.core.config import settings
            daily_limit = settings.free_daily_generations

        return {
            "daily_generations_used": quota.prompts_generated,
            "daily_generations_limit": daily_limit,
            "total_prompts_generated_30d": total_generated,
            "total_prompts_saved_30d": total_saved,
            "total_api_calls_30d": total_api,
            "history": [
                {
                    "date": q.date.isoformat(),
                    "prompts_generated": q.prompts_generated,
                    "prompts_saved": q.prompts_saved,
                    "api_calls": q.api_calls,
                }
                for q in history
            ],
        }

    async def get_available_plans(self) -> list[dict]:
        return PLANS

    async def upgrade(self, user_id: str, plan_type: str) -> dict:
        valid_plans = {"basic", "pro", "enterprise"}
        if plan_type not in valid_plans:
            raise BadRequestException(f"Invalid plan type: {plan_type}")

        existing = await self.sub_repo.get_by_user(user_id)
        if existing and existing.is_active:
            raise BadRequestException("You already have an active subscription")

        from app.models.subscription import PlanType, SubscriptionStatus

        plan_enum = PlanType[plan_type.upper()]
        sub = await self.sub_repo.create(
            user_id=user_id,
            plan_type=plan_enum,
            status=SubscriptionStatus.ACTIVE,
            start_date=datetime.now(timezone.utc),
            auto_renew=True,
        )

        return {
            "id": str(sub.id),
            "user_id": str(sub.user_id),
            "plan_type": sub.plan_type.value if hasattr(sub.plan_type, "value") else sub.plan_type,
            "status": sub.status.value if hasattr(sub.status, "value") else sub.status,
            "start_date": sub.start_date,
            "end_date": sub.end_date,
            "trial_end": sub.trial_end,
            "auto_renew": sub.auto_renew,
            "created_at": sub.created_at,
            "updated_at": sub.updated_at,
        }

    async def cancel(self, user_id: str) -> MessageResponse:
        sub = await self.sub_repo.cancel_subscription(user_id)
        if not sub:
            raise NotFoundException("Active subscription not found")

        return MessageResponse(message="Subscription cancelled successfully")

    async def check_access(self, user_id: str, required_feature: str) -> bool:
        allowed_tiers = FEATURE_ACCESS.get(required_feature, [])
        if not allowed_tiers:
            return True

        subscription = await self.sub_repo.get_by_user(user_id)
        if not subscription or not subscription.is_active:
            return "free" in allowed_tiers or not allowed_tiers

        tier = subscription.plan_type.value if hasattr(subscription.plan_type, "value") else subscription.plan_type
        return tier in allowed_tiers
