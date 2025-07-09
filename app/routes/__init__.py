from fastapi import FastAPI
from tiacore_lib.routes.company_route import company_router
from tiacore_lib.routes.user_route import user_router

from .contract_route import contract_router
from .contract_type_route import contract_type_router
from .entity_company_relation_route import entity_relation_router
from .legal_entity_route import entity_router
from .monitoring_route import monitoring_router


def register_routes(app: FastAPI):
    app.include_router(user_router, prefix="/api/users", tags=["Users"])
    app.include_router(company_router, prefix="/api/companies", tags=["Companies"])
    app.include_router(monitoring_router, tags=["Monitoring"])
    app.include_router(contract_type_router, prefix="/api/contract-types", tags=["ContractTypes"])
    app.include_router(contract_router, prefix="/api/contracts", tags=["Contracts"])
    app.include_router(entity_router, prefix="/api/legal-entities", tags=["LegalEntities"])
    app.include_router(
        entity_relation_router,
        prefix="/api/entity-company-relations",
        tags=["EntityCompanyRelations"],
    )
