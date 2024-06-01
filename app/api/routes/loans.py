from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models import Loan, LoanCreate, LoanPublic
from app.amortization_calculator import calc_amortization_schedule


router = APIRouter()


@router.post("/", response_model=LoanPublic)
def create_loan(
    *, session: SessionDep, current_user: CurrentUser, loan_in: LoanCreate
) -> Any:
    """
    Create new loan.
    """
    loan = Loan.model_validate(loan_in, update={"owner_id": current_user.id})
    session.add(loan)
    session.commit()
    session.refresh(loan)
    return loan


@router.get("/{id}/schedule")
def fetch_loan_schedule(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get loan schedule by ID.
    """
    loan = session.get(Loan, id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if not current_user.is_superuser and (loan.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return calc_amortization_schedule(loan.amount, loan.annual_interest_rate, loan.loan_term)
