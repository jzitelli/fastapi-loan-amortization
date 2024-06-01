from fastapi import APIRouter

from app.api.routes import login, users, loans

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(loans.router, prefix="/loans", tags=["loans"])
#api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
