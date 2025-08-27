from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from tiacore_lib.config import get_settings
from tiacore_lib.handlers.auth_handler import get_current_user
from tiacore_lib.http.http_client import SharedHttpClient, get_auth_headers

from app.database.models import Contract, EntityCompanyRelation
from app.pydantic_models.entity_models import EntitySchema, GetPriceIDSchema

legal_entity_router = APIRouter()
http_client = SharedHttpClient()


@legal_entity_router.post(
    "/{contract_id}",
    response_model=EntitySchema,
    summary="Получение компаний по контракту",
)
async def get_ids(
    request: Request,
    contract_id: UUID,
    data: GetPriceIDSchema,
    context: dict = Depends(get_current_user),
    settings=Depends(get_settings),
):
    contract = await Contract.filter(id=contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="контракт не найден")

    sellers = await EntityCompanyRelation.filter(legal_entity_id=contract.seller_id, relation_type="seller").all()
    buyers = await EntityCompanyRelation.filter(legal_entity_id=contract.buyer_id, relation_type="buyer").all()

    price_data = data.model_dump(mode="json")
    price_data["price_set_id"] = str(contract.price_set_id)
    headers = get_auth_headers(request)
    response_data, status_code = await http_client.request(
        "POST",
        f"{settings.PRICE_URL}/api/get-price-id",
        headers=headers,
        json=price_data,
    )

    return EntitySchema(
        seller_company_ids=[seller.company_id for seller in sellers],
        buyer_company_ids=[buyer.company_id for buyer in buyers],
        price_id=response_data["price_id"],
    )
