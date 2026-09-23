"""
Repositorio de Categoría (patrón Repository).

Responsabilidad única: operaciones CRUD asíncronas sobre la tabla 'categories'.
Desacoplado de FastAPI y de las reglas de negocio.
"""

from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryUpdate


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        return await self._session.get(Category, category_id)

    async def get_by_name(self, name: str) -> Optional[Category]:
        result = await self._session.execute(select(Category).where(Category.name == name))
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        only_active: bool = True,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Category], int]:
        query = select(Category)
        count_query = select(func.count()).select_from(Category)

        if only_active:
            query = query.where(Category.is_active.is_(True))
            count_query = count_query.where(Category.is_active.is_(True))

        query = query.order_by(Category.id.asc()).offset(offset).limit(limit)

        items_result = await self._session.execute(query)
        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        return items_result.scalars().all(), total

    async def create(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        color: Optional[str] = "#6B7280",
        is_active: bool = True,
    ) -> Category:
        category = Category(
            name=name,
            description=description,
            color=color,
            is_active=is_active,
        )
        self._session.add(category)
        await self._session.flush()
        await self._session.refresh(category)
        return category

    async def update(self, category: Category, data: CategoryUpdate) -> Category:
        if data.name is not None:
            category.name = data.name
        if data.description is not None:
            category.description = data.description
        if data.color is not None:
            category.color = data.color
        if data.is_active is not None:
            category.is_active = data.is_active

        await self._session.flush()
        await self._session.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        await self._session.delete(category)
        await self._session.flush()
