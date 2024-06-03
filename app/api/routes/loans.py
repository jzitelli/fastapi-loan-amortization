from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Loan, LoanCreate, LoanPublic, LoansPublic
from app.amortization_calculator import calc_amortization_schedule, calc_monthly_summary
from app.crud import get_user_by_email, create_loan_share


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


@router.get("/", response_model=LoansPublic)
def fetch_loans(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Fetch all loans owned by current user.
    """
    count_statement = (
        select(func.count())
        .select_from(Loan)
        .where(Loan.owner_id == current_user.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Loan)
        .where(Loan.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    loans = session.exec(statement).all()
    return LoansPublic(data=loans, count=count)


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
def fetch_loan_summary(session: SessionDep, current_user: CurrentUser, id: int,
                       month: Annotated[int, Query(title="month number", gt=0)]) -> Any:
    """
    Get loan summary for a given month.
    """
    loan = session.get(Loan, id)
    if not loan or (not current_user.is_superuser and (loan.owner_id != current_user.id)):
        raise HTTPException(status_code=404, detail="Loan not found")
    if month > loan.loan_term:
        raise HTTPException(status_code=422, detail="month number exceeds loan term")
    return calc_monthly_summary(loan.amount, loan.annual_interest_rate, loan.loan_term, month)


@router.put("/{id}/share")
def share_loan(session: SessionDep, current_user: CurrentUser, id: int,
               email: Annotated[str, Query(title="user email")]) -> Any:
    """
    Grant read access to a loan to another user.
    """
    loan = session.get(Loan, id)
    if not loan or (not current_user.is_superuser and (loan.owner_id != current_user.id)):
        return
    user = get_user_by_email(session=session, email=email)
    if user and user.id != current_user.id:
        create_loan_share(session=session, loan_id=loan.id, user_id=user.id)
