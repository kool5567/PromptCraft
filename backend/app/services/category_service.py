from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ConflictException
from app.repositories.category_repo import CategoryRepository
from app.schemas.category import CategoryCreateRequest, CategoryUpdateRequest, CategoryResponse


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.repo = CategoryRepository(session)

    async def get_all_categories(self) -> list[CategoryResponse]:
        categories = await self.repo.get_with_children()
        return [self._to_response(c) for c in categories]

    async def get_category_by_slug(self, slug: str) -> CategoryResponse:
        category = await self.repo.get_by_slug(slug)
        if not category:
            raise NotFoundException("Category", slug)
        return self._to_response(category)

    async def create_category(self, request: CategoryCreateRequest) -> CategoryResponse:
        existing = await self.repo.get_by_slug(request.slug)
        if existing:
            raise ConflictException(f"Category with slug '{request.slug}' already exists")

        category = await self.repo.create(
            name=request.name,
            name_ar=request.name_ar,
            slug=request.slug,
            description=request.description,
            description_ar=request.description_ar,
            parent_id=UUID(request.parent_id) if request.parent_id else None,
            icon=request.icon,
            color=request.color,
            sort_order=request.sort_order,
        )
        return self._to_response(category)

    async def update_category(self, category_id: UUID, request: CategoryUpdateRequest) -> CategoryResponse:
        category = await self.repo.get(category_id)
        if not category:
            raise NotFoundException("Category", category_id)

        update_data = request.model_dump(exclude_none=True)
        if "parent_id" in update_data and update_data["parent_id"]:
            update_data["parent_id"] = UUID(update_data["parent_id"])

        await self.repo.update(category_id, **update_data)
        return self._to_response(await self.repo.get(category_id))

    async def delete_category(self, category_id: UUID) -> None:
        category = await self.repo.get(category_id)
        if not category:
            raise NotFoundException("Category", category_id)
        await self.repo.delete(category_id)

    def _to_response(self, category) -> CategoryResponse:
        children = []
        if hasattr(category, "children") and category.children:
            children = [self._to_response(c) for c in category.children]

        return CategoryResponse(
            id=str(category.id),
            name=category.name,
            name_ar=category.name_ar,
            slug=category.slug,
            description=category.description,
            description_ar=category.description_ar,
            parent_id=str(category.parent_id) if category.parent_id else None,
            icon=category.icon,
            color=category.color,
            sort_order=category.sort_order,
            is_active=category.is_active,
            children=children,
            created_at=category.created_at.isoformat() if category.created_at else "",
            updated_at=category.updated_at.isoformat() if category.updated_at else "",
        )
