import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.database.models import Contract


@pytest.mark.asyncio
async def test_add_contract(
    test_app: AsyncClient, jwt_token_admin: dict, seed_contract_type
):
    """Тест добавления нового промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "contract_name": "Test Contract",
        "contract_number": "11111",
        "contract_type_id": seed_contract_type.id,
        "date": datetime.date.today().isoformat(),
        "buyer_id": str(uuid4()),
        "seller_id": str(uuid4()),
        "company_id": str(uuid4()),
        "responsible_id": str(uuid4()),
    }

    response = await test_app.post("/api/contracts/add", headers=headers, json=data)
    assert response.status_code == 201, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    contract = await Contract.filter(name="Test Contract").first()

    assert contract is not None, "Промпт не был сохранён в БД"
    assert response_data["contract_id"] == str(contract.id)


@pytest.mark.asyncio
async def test_edit_contract(
    test_app: AsyncClient, jwt_token_admin: dict, seed_contract: Contract
):
    """Тест редактирования промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {"contract_name": "Updated Contract"}

    response = await test_app.patch(
        f"/api/contracts/{seed_contract.id}", headers=headers, json=data
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    contract = await Contract.filter(id=seed_contract.id).first()

    assert contract is not None, "Промпт не найден в базе"
    assert contract.name == "Updated Contract"


@pytest.mark.asyncio
async def test_view_contract(
    test_app: AsyncClient, jwt_token_admin: dict, seed_contract: Contract
):
    """Тест просмотра промпта по ID."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/contracts/{seed_contract.id}", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    assert response_data["contract_id"] == str(seed_contract.id)
    assert response_data["contract_name"] == seed_contract.name


@pytest.mark.asyncio
async def test_delete_contract(
    test_app: AsyncClient, jwt_token_admin: dict, seed_contract: Contract
):
    """Тест удаления промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/contracts/{seed_contract.id}", headers=headers
    )

    assert response.status_code == 204, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    contract = await Contract.filter(id=seed_contract.id).first()
    assert contract is None, "Промпт не был удалён из базы"


@pytest.mark.asyncio
async def test_get_contracts(
    test_app: AsyncClient, jwt_token_admin: dict, seed_contract: Contract
):
    """Тест получения списка промптов с фильтрацией."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/contracts/all", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    contracts = response_data.get("contracts")
    assert isinstance(contracts, list), "Ответ должен быть списком"
    assert response_data.get("total") > 0

    contract_ids = [contract["contract_id"] for contract in contracts]
    assert str(seed_contract.id) in contract_ids, "Тестовый промпт отсутствует в списке"
