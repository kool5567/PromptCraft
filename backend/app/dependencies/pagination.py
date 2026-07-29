from fastapi import Query
from typing import Optional

from app.schemas.common import PaginationParams


async def get_pagination(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc or desc"),
) -> PaginationParams:
    return PaginationParams(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
