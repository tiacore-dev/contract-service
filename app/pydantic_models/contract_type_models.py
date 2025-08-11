from typing import List, Literal, Optional

from fastapi import Query
from pydantic import BaseModel, Field


class ContractTypeSchema(BaseModel):
    id: str = Field(..., alias="contract_type_id")
    name: str = Field(..., alias="contract_type_name")
    colour: str = Field(..., min_length=7, max_length=7)

    class Config:
        from_attributes = True
        populate_by_name = True


class ContractTypeListResponse(BaseModel):
    total: int
    contract_types: List[ContractTypeSchema]


# ✅ Фильтры и параметры поиска
class FilterParams(BaseModel):
    contract_type_name: Optional[str] = Query(None, description="Фильтр по названию")
    sort_by: Literal["name", "created_at"] = Query("name", description="Сортировка (по умолчанию name)")
    order: Literal["asc", "desc"] = Query("asc", description="Порядок сортировки: asc/desc")
    page: int = Query(1, description="Номер страницы")
    page_size: int = Query(10, description="Размер страницы")
