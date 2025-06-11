import uuid

from tortoise import fields
from tortoise.models import Model


class ContractType(Model):
    id = fields.CharField(max_length=50, pk=True)
    name = fields.CharField(max_length=100)
    colour = fields.CharField(max_length=7)

    class Meta:
        table = "contract_types"


class Contract(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    number = fields.CharField(max_length=255)
    name = fields.CharField(max_length=255)
    date = fields.DateField()
    buyer_id = fields.UUIDField()
    seller_id = fields.UUIDField()
    company_id = fields.UUIDField()
    responsible_id = fields.UUIDField()

    contract_type = fields.ForeignKeyField(
        "models.ContractType", related_name="contracts"
    )

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    class Meta:
        table = "contracts"


class ContractFile(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255)
    extension = fields.CharField(max_length=10)
    s3_key = fields.CharField(max_length=255)
    contract = fields.ForeignKeyField("models.Contract", related_name="contract_files")

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_nowd=True)
    modified_by = fields.UUIDField()

    class Meta:
        table = "contract_files"
