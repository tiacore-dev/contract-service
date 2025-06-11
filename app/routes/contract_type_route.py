from fastapi import APIRouter, Depends
from loguru import logger
from tiacore_lib.handlers.auth_handler import get_current_user
from tortoise.expressions import Q

from app.database.models import ContractType
from app.pydantic_models.contract_type_models import (
    ContractTypeListResponse,
    ContractTypeSchema,
    FilterParams,
)

contract_type_router = APIRouter()


@contract_type_router.get(
    "/all",
    response_model=ContractTypeListResponse,
    summary="Получение списка типов юр. лиц с фильтрацией",
)
async def get_contract_types(
    filters: FilterParams = Depends(),
    _: str = Depends(get_current_user),
):
    logger.info(f"Запрос на список типов юр. лиц: {filters}")

    query = Q()

    if filters.contract_type_name:
        query &= Q(name__icontains=filters.contract_type_name)

    order = filters.order
    sort_by = filters.sort_by
    order_by = f"{'-' if order == 'desc' else ''}{sort_by}"

    page = filters.page
    page_size = filters.page_size

    total_count = await ContractType.filter(query).count()

    contract_types = [
        ContractTypeSchema(**p)
        for p in await ContractType.filter(query)
        .order_by(order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .values("id", "name", "colour")
    ]

    if not contract_types:
        logger.info("Список разрешений пуст")
    return ContractTypeListResponse(total=total_count, contract_types=contract_types)
