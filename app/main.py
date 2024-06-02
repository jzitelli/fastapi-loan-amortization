from fastapi import FastAPI

from app.api.main import api_router
from app.core.config import settings


app = FastAPI()


app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/users/{user_id}/loans")
def fetch_loans_for_user(user_id: str):
    pass
