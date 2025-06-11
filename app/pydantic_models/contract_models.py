import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import Field
from tiacore_lib.pydantic_models.clean_model import CleanableBaseModel


class ContractCreateSchema(CleanableBaseModel):
    name: str = Field(..., min_length=3, max_length=100, alias="contract_name")
    number: str = Field(..., alias="contract_number")
    date: datetime.date = Field(...)
    buyer_id: UUID = Field(...)
    seller_id: UUID = Field(...)
    contract_type_id: str = Field(...)
    company_id: UUID = Field(...)
    responsible_id: UUID = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class ContractEditSchema(CleanableBaseModel):
    name: Optional[str] = Field(
        None, min_length=3, max_length=100, alias="contract_name"
    )
    number: Optional[str] = Field(None, alias="contract_number")
    date: Optional[datetime.date] = Field(None)
    buyer_id: Optional[UUID] = Field(None)
    seller_id: Optional[UUID] = Field(None)
    contract_type_id: Optional[str] = Field(None)
    company_id: Optional[UUID] = Field(None)
    responsible_id: Optional[UUID] = Field(None)

    class Config:
        from_attributes = True
        populate_by_name = True


class ContractSchema(CleanableBaseModel):
    id: UUID = Field(..., alias="contract_id")
    name: str = Field(..., alias="contract_name")
    number: str = Field(..., alias="contract_number")
    date: datetime.date = Field(...)
    buyer_id: UUID = Field(...)
    seller_id: UUID = Field(...)
    contract_type_id: str = Field(...)
    company_id: UUID = Field(...)
    responsible_id: UUID = Field(...)
    created_at: datetime.datetime = Field(...)
    created_by: UUID = Field(...)
    modified_by: UUID = Field(...)
    modified_at: datetime.datetime = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class ContractResponseSchema(CleanableBaseModel):
    contract_id: UUID


class ContractListResponseSchema(CleanableBaseModel):
    total: int
    contracts: List[ContractSchema]


def Contract_filter_params(
    contract_name: Optional[str] = Query(
        None, description="Фильтр по названию промпта"
    ),
    contract_number: Optional[str] = Query(None, description="Фильтр по тексту"),
    date: Optional[str] = Query(None, description="Фильтр по тексту"),
    sort_by: Optional[str] = Query("name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
):
    return {
        "contract_name": contract_name,
        "contract_number": contract_number,
        "date": date,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
