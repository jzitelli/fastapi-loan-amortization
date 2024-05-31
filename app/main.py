from fastapi import FastAPI

from app.api.main import api_router
from app.core.config import settings


app = FastAPI()


app.include_router(api_router, prefix=settings.API_V1_STR)


@app.post("/loans")
def create_loan():
    pass


@app.get("/loans/{loan_id}/schedule")
def fetch_loan_schedule(loan_id: str):
    pass


@app.get("/loans/{loan_id}/summary")
def fetch_loan_summary(loan_id: str, month: int):
    pass


@app.get("/users/{user_id}/loans")
def fetch_loans_for_user(user_id: str):
    pass
