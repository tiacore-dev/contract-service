from uuid import UUID

from pydantic import BaseModel


class EntitySchema(BaseModel):
    seller_company_id: UUID
    buyer_company_id: UUID

    class Config:
        from_attributes = True
        populate_by_name = True
