from fastapi import FastAPI


app = FastAPI()


@app.post("/users")
def create_user():
    pass


@app.post("/loans")
def create_loan():
    pass


@app.get("/loans/{loan_id}")
def fetch_loan_schedule(loan_id: str):
    pass


@app.get("/loans/{loan_id}/summary")
def fetch_loan_summary(loan_id: str, month: int):
    pass


@app.get("/users/{user_id}/loans")
def fetch_loans_for_user(user_id: str):
    pass
