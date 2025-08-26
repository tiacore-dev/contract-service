from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from tiacore_lib.config import get_settings
from tiacore_lib.handlers.auth_handler import get_current_user
from tiacore_lib.http.http_client import SharedHttpClient

from app.database.models import Contract, EntityCompanyRelation
from app.pydantic_models.entity_models import (
    EntitySchema,
)

legal_entity_router = APIRouter()
http_client = SharedHttpClient()


@legal_entity_router.get(
    "/{contract_id}",
    response_model=EntitySchema,
    summary="Получение компаний по контракту",
)
async def get_ids(
    request: Request,
    contract_id: UUID,
    context: dict = Depends(get_current_user),
    settings=Depends(get_settings),
):
    contract = await Contract.filter(id=contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="контракт не найден")

    sellers = await EntityCompanyRelation.filter(legal_entity_id=contract.seller_id, relation_type="seller").all()
    buyers = await EntityCompanyRelation.filter(legal_entity_id=contract.buyer_id, relation_type="buyer").all()
    return EntitySchema(
        seller_company_ids=[seller.company_id for seller in sellers],
        buyer_company_ids=[buyer.company_id for buyer in buyers],
    )
