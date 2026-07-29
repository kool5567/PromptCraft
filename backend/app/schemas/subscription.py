from pydantic import BaseModel
from datetime import datetime


class SubscriptionPlanResponse(BaseModel):
    id: str
    name: str
    price: float
    currency: str = "USD"
    interval: str = "month"
    features: list[str]
    is_popular: bool = False


class SubscribeRequest(BaseModel):
    plan_type: str
    payment_provider: str = "stripe"
    payment_token: str


class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    plan_type: str
    status: str
    start_date: datetime
    end_date: datetime | None = None
    trial_end: datetime | None = None
    auto_renew: bool
    created_at: datetime
    updated_at: datetime


class ChangePlanRequest(BaseModel):
    plan_type: str
