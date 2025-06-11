import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import (
    Contract,
    ContractType,
)
from app.pydantic_models.contract_models import (
    Contract_filter_params,
    ContractCreateSchema,
    ContractEditSchema,
    ContractListResponseSchema,
    ContractResponseSchema,
    ContractSchema,
)

contract_router = APIRouter()


@contract_router.post(
    "/add",
    response_model=ContractResponseSchema,
    summary="Добавить контракт",
    status_code=status.HTTP_201_CREATED,
)
async def add_contract(
    data: ContractCreateSchema,
    context=Depends(require_permission_in_context("add_contract")),
):
    await validate_exists(ContractType, data.contract_type_id, "Тип Контракта")

    contract = await Contract.create(
        created_by=context["user_id"],
        modified_by=context["user_id"],
        **data.model_dump(),
    )
    return ContractResponseSchema(contract_id=contract.id)


@contract_router.patch(
    "/{contract_id}",
    response_model=ContractResponseSchema,
    summary="Изменить контракт",
)
async def update_contract(
    contract_id: UUID,
    data: ContractEditSchema,
    context=Depends(require_permission_in_context("edit_contract")),
):
    contract = await Contract.filter(id=contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="контракт не найден")

    update_data = data.model_dump(exclude_unset=True)

    if "contract_type_id" in update_data:
        await validate_exists(ContractType, data.contract_type_id, "Тип Контракта")
    contract.modified_by = context["user_id"]
    await contract.update_from_dict(update_data)
    await contract.save()

    return ContractResponseSchema(contract_id=contract.id)


@contract_router.delete(
    "/{contract_id}",
    summary="Удалить контракт",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_contract(
    contract_id: UUID,
    _=Depends(require_permission_in_context("delete_contract")),
):
    contract = await Contract.filter(id=contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="контракт не найден")

    await contract.delete()
    return


@contract_router.get(
    "/all",
    response_model=ContractListResponseSchema,
    summary="Получение списка контрактов",
)
async def get_contracts(
    filters: dict = Depends(Contract_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_contracts")),
):
    query = Q()

    if filters.get("contract_name"):
        query &= Q(name__icontains=filters["contract_name"])

    if filters.get("contract_number"):
        try:
            query &= Q(number=int(filters["contract_number"]))
        except ValueError:
            raise HTTPException(status_code=400, detail="Некорректный номер контракта")

    if filters.get("date"):
        try:
            parsed_date = datetime.datetime.strptime(filters["date"], "%Y-%m-%d").date()
            query &= Q(date=parsed_date)
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Некорректная дата (ожидается YYYY-MM-DD)"
            )

    sort_by = filters["sort_by"]
    order = filters["order"]
    ordering = f"-{sort_by}" if order == "desc" else sort_by

    page = filters["page"]
    page_size = filters["page_size"]
    offset = (page - 1) * page_size

    total = await Contract.filter(query).count()
    contracts = (
        await Contract.filter(query)
        .order_by(ordering)
        .offset(offset)
        .limit(page_size)
        .prefetch_related("contract_type")
    )

    contract_list = [
        ContractSchema(
            contract_id=contract.id,
            contract_name=contract.name,
            contract_number=contract.number,
            date=contract.date,
            buyer_id=contract.buyer_id,
            seller_id=contract.seller_id,
            contract_type_id=contract.contract_type.id,
            company_id=contract.company_id,
            responsible_id=contract.responsible_id,
            modified_by=contract.modified_by,
            modified_at=contract.modified_at,
            created_at=contract.created_at,
            created_by=contract.created_by,
        )
        for contract in contracts
    ]

    return ContractListResponseSchema(total=total, contracts=contract_list)


@contract_router.get(
    "/{contract_id}",
    response_model=ContractSchema,
    summary="Просмотр одного юридического лица",
)
async def get_contract(
    contract_id: UUID,
    _: dict = Depends(require_permission_in_context("view_contract")),
):
    contract = (
        await Contract.filter(id=contract_id).prefetch_related("contract_type").first()
    )

    if not contract:
        raise HTTPException(status_code=404, detail="контракт не найден")

    return ContractSchema(
        contract_id=contract.id,
        contract_name=contract.name,
        contract_number=contract.number,
        date=contract.date,
        buyer_id=contract.buyer_id,
        seller_id=contract.seller_id,
        contract_type_id=contract.contract_type.id,
        company_id=contract.company_id,
        responsible_id=contract.responsible_id,
        modified_by=contract.modified_by,
        modified_at=contract.modified_at,
        created_at=contract.created_at,
        created_by=contract.created_by,
    )
