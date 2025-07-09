from tortoise import Tortoise
from tortoise.transactions import in_transaction


async def drop_all_tables():
    conn = Tortoise.get_connection("default")
    tables = await conn.execute_query_dict("""
        SELECT tablename FROM pg_tables WHERE schemaname = 'public';
    """)
    async with in_transaction() as tx:
        for table in tables:
            await tx.execute_query(f'DROP TABLE IF EXISTS "{table["tablename"]}" CASCADE;')


async def create_data():
    from app.database.models import ContractType

    try:
        await ContractType.get_or_create(id="delivery", name="Договор оказания курьерских услуг", colour="#b70094")

    except Exception as e:
        print(f"Exception: {e}")
