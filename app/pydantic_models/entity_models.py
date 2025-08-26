from typing import List
from uuid import UUID

from pydantic import BaseModel


class EntitySchema(BaseModel):
    seller_company_ids: List[UUID]
    buyer_company_ids: List[UUID]

    class Config:
        from_attributes = True
        populate_by_name = True
