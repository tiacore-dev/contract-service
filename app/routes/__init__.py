from fastapi import FastAPI
from tiacore_lib.routes.auth_route import auth_router
from tiacore_lib.routes.company_route import company_router
from tiacore_lib.routes.invite_route import invite_router
from tiacore_lib.routes.register_route import register_router
from tiacore_lib.routes.user_route import user_router

from .contract_route import contract_router
from .contract_type_route import contract_type_router
from .monitoring_route import monitoring_router


def register_routes(app: FastAPI):
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(invite_router, prefix="/api", tags=["Invite"])
    app.include_router(register_router, prefix="/api", tags=["Register"])
    app.include_router(user_router, prefix="/api/users", tags=["Users"])
    app.include_router(company_router, prefix="/api/companies", tags=["Companies"])
    app.include_router(monitoring_router, tags=["Monitoring"])
    app.include_router(
        contract_type_router, prefix="/api/contract-types", tags=["ContractTypes"]
    )
    app.include_router(contract_router, prefix="/api/contracts", tags=["LegalEntities"])
