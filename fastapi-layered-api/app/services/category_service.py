"""
Servicio de Categoría (capa de lógica de negocio).

Implementa las reglas de negocio para el recurso público/privado Categoría:
- Consulta abierta para cualquier cliente (listado y detalle).
- Validación de unicidad de nombre de categoría al crear o modificar.
- Lanza excepciones de dominio desacopladas de HTTP (CategoryNotFoundError, CategoryAlreadyExistsError).
"""

from typing import Optional

from app.core.exceptions import CategoryAlreadyExistsError, CategoryNotFoundError
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    async def list_categories(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        only_active: bool = True,
    ) -> tuple[list[Category], int]:
        """Consulta pública: permite a cualquier visitante listar las categorías."""
        offset = (page - 1) * page_size
        categories, total = await self._repository.list(
            only_active=only_active,
            offset=offset,
            limit=page_size,
        )
        return list(categories), total

    async def get_by_id(self, category_id: int) -> Category:
        """Consulta pública: obtiene una categoría por su ID."""
        category = await self._repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(f"Categoría con id={category_id} no encontrada.")
        return category

    async def create_category(self, data: CategoryCreate) -> Category:
        """Operación administrativa/protegida: crea una nueva categoría validando unicidad de nombre."""
        existing = await self._repository.get_by_name(data.name)
        if existing is not None:
            raise CategoryAlreadyExistsError(f"Ya existe una categoría con el nombre '{data.name}'.")

        return await self._repository.create(
            name=data.name,
            description=data.description,
            color=data.color,
            is_active=data.is_active,
        )

    async def update_category(self, category_id: int, data: CategoryUpdate) -> Category:
        """Operación administrativa/protegida: actualiza parcialmente una categoría."""
        category = await self.get_by_id(category_id)

        if data.name is not None and data.name != category.name:
            existing = await self._repository.get_by_name(data.name)
            if existing is not None:
                raise CategoryAlreadyExistsError(f"Ya existe una categoría con el nombre '{data.name}'.")

        return await self._repository.update(category, data)

    async def delete_category(self, category_id: int) -> None:
        """Operación administrativa/protegida: elimina una categoría."""
        category = await self.get_by_id(category_id)
        await self._repository.delete(category)
