from fastapi import FastAPI
from tiacore_lib.routes.auth_route import auth_router
from tiacore_lib.routes.company_route import company_router

from .contract_route import contract_router
from .contract_type_route import contract_type_router
from .monitoring_route import monitoring_router


def register_routes(app: FastAPI):
    app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
    app.include_router(company_router, prefix="/api/companies", tags=["Companies"])
    app.include_router(monitoring_router, tags=["Monitoring"])
    app.include_router(
        contract_type_router, prefix="/api/contract-types", tags=["ContractTypes"]
    )
    app.include_router(contract_router, prefix="/api/contracts", tags=["LegalEntities"])
