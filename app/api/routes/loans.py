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
    if not loan or (not current_user.is_superuser and (loan.owner_id != current_user.id)):
        raise HTTPException(status_code=404, detail="Loan not found")
    schedule = calc_amortization_schedule(loan.amount, loan.annual_interest_rate, loan.loan_term)
    for r in schedule:
        r.pop('monthly_accrued_interest')
    return schedule


@router.get("/{id}/summary")
def fetch_loan_summary(session: SessionDep, current_user: CurrentUser, id: int, month: int) -> Any:
    """
    Get loan summary for a given month.
    """
    loan = session.get(Loan, id)
    if not loan or (not current_user.is_superuser and (loan.owner_id != current_user.id)):
        raise HTTPException(status_code=404, detail="Loan not found")
    schedule = calc_amortization_schedule(loan.amount, loan.annual_interest_rate, loan.loan_term)
    return {
        'remaining_balance': schedule[month-1]['remaining_balance'],
        'aggregate_principal_paid': loan.amount - schedule[month-1]['remaining_balance'],
        'aggregate_interest_paid': sum(r['monthly_accrued_interest'] for r in schedule[:month])
    }
