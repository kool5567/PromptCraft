from __future__ import annotations

from math import ceil
from typing import Any, Sequence

from app.schemas.common import PaginatedResponse, PaginationParams


class PaginationHelper:
    @staticmethod
    def paginate(items: Sequence[Any], total: int, params: PaginationParams) -> PaginatedResponse[Any]:
        total_pages = ceil(total / params.size) if params.size > 0 else 0
        return PaginatedResponse(
            items=list(items),
            total=total,
            page=params.page,
            size=params.size,
            pages=total_pages,
        )

    @staticmethod
    def get_skip_limit(page: int, page_size: int) -> tuple[int, int]:
        skip = (page - 1) * page_size
        return skip, page_size
