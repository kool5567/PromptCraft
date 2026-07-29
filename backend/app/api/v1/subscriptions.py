from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.dependencies.auth import get_current_user
from app.schemas.subscription import (
    SubscriptionPlanResponse, SubscribeRequest, SubscriptionResponse, ChangePlanRequest,
)

router = APIRouter()


PLANS = [
    SubscriptionPlanResponse(
        id="basic", name="Basic", price=9.99, currency="USD", interval="month",
        features=["50 generations/day", "500 prompts", "Full templates", "GitHub import"],
        is_popular=False,
    ),
    SubscriptionPlanResponse(
        id="pro", name="Pro", price=19.99, currency="USD", interval="month",
        features=["Unlimited generations", "Unlimited prompts", "Premium prompts", "API access", "Priority support"],
        is_popular=True,
    ),
    SubscriptionPlanResponse(
        id="enterprise", name="Enterprise", price=49.99, currency="USD", interval="month",
        features=["Everything in Pro", "Team accounts (10+)", "Custom branding", "24/7 support"],
        is_popular=False,
    ),
]


@router.get("/plans", response_model=list[SubscriptionPlanResponse])
async def list_plans():
    return PLANS


@router.post("/subscribe", response_model=SubscriptionResponse)
async def subscribe(
    request: SubscribeRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    from datetime import datetime, timezone, timedelta
    from app.models.subscription import Subscription, SubscriptionStatus
    from app.models.user import SubscriptionTier

    existing = await session.get(Subscription, current_user.id)
    if existing:
        existing.plan_type = request.plan_type
        existing.status = SubscriptionStatus.ACTIVE
        existing.start_date = datetime.now(timezone.utc)
        existing.end_date = datetime.now(timezone.utc) + timedelta(days=30)
        existing.payment_provider = request.payment_provider
    else:
        sub = Subscription(
            user_id=current_user.id,
            plan_type=request.plan_type,
            status=SubscriptionStatus.ACTIVE,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=30),
            payment_provider=request.payment_provider,
        )
        session.add(sub)

    tier_map = {"basic": SubscriptionTier.BASIC, "pro": SubscriptionTier.PRO, "enterprise": SubscriptionTier.ENTERPRISE}
    current_user.subscription_tier = tier_map.get(request.plan_type, SubscriptionTier.PRO)
    await session.flush()

    return await get_my_subscription(current_user, session)


@router.get("/my", response_model=SubscriptionResponse)
async def get_my_subscription(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    from app.models.subscription import Subscription
    sub = await session.get(Subscription, current_user.id)
    if not sub:
        return SubscriptionResponse(
            id="", user_id=str(current_user.id), plan_type="free",
            status="inactive", start_date=datetime.now(),
            auto_renew=False, created_at=datetime.now(), updated_at=datetime.now(),
        )
    return SubscriptionResponse(
        id=str(sub.id), user_id=str(sub.user_id),
        plan_type=sub.plan_type.value if hasattr(sub.plan_type, "value") else sub.plan_type,
        status=sub.status.value if hasattr(sub.status, "value") else sub.status,
        start_date=sub.start_date, end_date=sub.end_date,
        trial_end=sub.trial_end, auto_renew=sub.auto_renew,
        created_at=sub.created_at, updated_at=sub.updated_at,
    )


@router.post("/cancel", response_model=dict)
async def cancel_subscription(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    from app.models.subscription import Subscription, SubscriptionStatus
    from app.models.user import SubscriptionTier

    sub = await session.get(Subscription, current_user.id)
    if sub:
        sub.status = SubscriptionStatus.CANCELED
        current_user.subscription_tier = SubscriptionTier.FREE
        await session.flush()

    return {"message": "Subscription cancelled"}


@router.post("/change-plan", response_model=SubscriptionResponse)
async def change_plan(
    request: ChangePlanRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    from datetime import datetime
    from app.models.subscription import Subscription

    sub = await session.get(Subscription, current_user.id)
    if sub:
        sub.plan_type = request.plan_type
        await session.flush()

    return await get_my_subscription(current_user, session)
