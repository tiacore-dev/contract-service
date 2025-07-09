from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "contract_types" (
    "id" VARCHAR(50) NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "colour" VARCHAR(7) NOT NULL
);
CREATE TABLE IF NOT EXISTS "contracts" (
    "id" UUID NOT NULL PRIMARY KEY,
    "number" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "date" DATE NOT NULL,
    "buyer_id" UUID NOT NULL,
    "seller_id" UUID NOT NULL,
    "company_id" UUID NOT NULL,
    "responsible_id" UUID NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_by" UUID NOT NULL,
    "contract_type_id" VARCHAR(50) NOT NULL REFERENCES "contract_types" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "contract_files" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "extension" VARCHAR(10) NOT NULL,
    "s3_key" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL,
    "modified_by" UUID NOT NULL,
    "contract_id" UUID NOT NULL REFERENCES "contracts" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "entity_company_relations" (
    "id" UUID NOT NULL PRIMARY KEY,
    "company_id" UUID NOT NULL,
    "legal_entity_id" UUID NOT NULL,
    "relation_type" VARCHAR(10) NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
