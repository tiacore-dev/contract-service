from typing import List, Optional

from fastapi import Query
from pydantic import Field
from tiacore_lib.pydantic_models.clean_model import CleanableBaseModel


class ContractTypeSchema(CleanableBaseModel):
    id: str = Field(..., alias="contract_type_id")
    name: str = Field(..., alias="contract_type_name")
    colour: str = Field(..., min_length=7, max_length=7)

    class Config:
        from_attributes = True
        populate_by_name = True


class ContractTypeListResponse(CleanableBaseModel):
    total: int
    contract_types: List[ContractTypeSchema]


# ✅ Фильтры и параметры поиска
class FilterParams(CleanableBaseModel):
    contract_type_name: Optional[str] = Query(None, description="Фильтр по названию")
    sort_by: str = Query("name", description="Сортировка (по умолчанию name)")
    order: str = Query("asc", description="Порядок сортировки: asc/desc")
    page: int = Query(1, description="Номер страницы")
    page_size: int = Query(10, description="Размер страницы")
