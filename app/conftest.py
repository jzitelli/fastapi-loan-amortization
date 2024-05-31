from collections.abc import Generator
import pytest
from sqlmodel import Session, delete
from app.db import engine, init_db
from app.models import User, Loan


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(Loan)
        session.execute(statement)
        statement = delete(User)
        session.execute(statement)
        session.commit()
