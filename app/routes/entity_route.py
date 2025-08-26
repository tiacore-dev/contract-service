from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from tiacore_lib.config import get_settings
from tiacore_lib.handlers.auth_handler import get_current_user
from tiacore_lib.http.http_client import SharedHttpClient, get_auth_headers

from app.database.models import (
    Contract,
)
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
    headers = get_auth_headers(request)

    contract = await Contract.filter(id=contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="контракт не найден")

    seller, status_code = await http_client.request(
        "GET",
        f"{settings.REFERENCE_URL}/api/legal-entities/{contract.seller_id}",
        headers=headers,
    )
    buyer, status_code = await http_client.request(
        "GET",
        f"{settings.REFERENCE_URL}/api/legal-entities/{contract.buyer_id}",
        headers=headers,
    )
    return EntitySchema(seller_company_id=seller["company_id"], buyer_company_id=buyer["company_id"])
