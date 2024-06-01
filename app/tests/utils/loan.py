from sqlmodel import Session

from app import crud
from app.models import Loan, LoanCreate
from app.tests.utils.user import create_random_user


def create_loan(db: Session, **kwargs) -> Loan:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    loan_in = LoanCreate(**kwargs)
    return crud.create_loan(session=db, loan_in=loan_in, owner_id=owner_id)
