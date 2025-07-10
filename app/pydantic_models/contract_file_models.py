import datetime
from typing import List, Optional, Union
from uuid import UUID

from fastapi import File, Form, Query, UploadFile
from pydantic import Field
from tiacore_lib.pydantic_models.clean_model import CleanableBaseModel
from tiacore_lib.utils.validate_helpers import normalize_form_field


class ContractFileCreateSchema(CleanableBaseModel):
    contract_file_name: str
    file: UploadFile
    contract_id: UUID

    @classmethod
    def as_form(
        cls,
        contract_file_name: str = Form(..., min_length=3, max_length=100),
        contract_id: UUID = Form(...),
        file: UploadFile = File(...),
    ):
        return cls(
            contract_file_name=contract_file_name,
            contract_id=contract_id,
            file=file,
        )


class ContractFileEditSchema(CleanableBaseModel):
    file: Optional[UploadFile] = None
    contract_id: Optional[UUID] = None

    @classmethod
    def as_form(
        cls,
        contract_id: Optional[UUID] = Form(None),
        file: Optional[Union[str, UploadFile]] = File(None),
    ):
        return cls(
            contract_id=normalize_form_field(contract_id, UUID),  # type: ignore[arg-type]
            file=None if isinstance(file, str) and file.strip() == "" else file,  # type: ignore[arg-type]
        )


class ContractFileSchema(CleanableBaseModel):
    contract_file_id: UUID = Field(...)
    contract_file_name: str = Field(...)
    contract_id: UUID = Field(...)
    created_at: datetime.datetime = Field(...)
    created_by: UUID = Field(...)
    modified_by: UUID = Field(...)
    modified_at: datetime.datetime = Field(...)

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        populate_by_name = True


class ContractFileResponseSchema(CleanableBaseModel):
    contract_file_id: UUID


class ContractFileListResponseSchema(CleanableBaseModel):
    total: int
    contract_files: List[ContractFileSchema]


def contract_file_filter_params(
    contract_file_name: Optional[str] = Query(None, description="Фильтр по названию промпта"),
    sort_by: Optional[str] = Query("name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
):
    return {
        "contract_file_name": contract_file_name,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
