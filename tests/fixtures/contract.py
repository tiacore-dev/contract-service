import datetime
from uuid import uuid4

import pytest

from app.database.models import Contract, ContractType


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_contract_type():
    contract_type = await ContractType.create(
        id="delivery", name="Test Name", colour="#ffffff"
    )
    return contract_type


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_contract(seed_contract_type: ContractType):
    contract = await Contract.create(
        name="Test contract",
        number="11111",
        contract_type=seed_contract_type,
        date=datetime.date.today(),
        buyer_id=uuid4(),
        seller_id=uuid4(),
        company_id=uuid4(),
        responsible_id=uuid4(),
        created_by=uuid4(),
        modified_by=uuid4(),
    )

    return contract
