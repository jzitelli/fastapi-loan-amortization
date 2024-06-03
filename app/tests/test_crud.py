from sqlmodel import Session, select
from fastapi.encoders import jsonable_encoder

from app import crud
from app.models import User, UserCreate, Loan, LoanCreate, LoanShare
from app.tests.utils.utils import random_email, random_lower_string


def test_create_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    authenticated_user = crud.authenticate(session=db, email=email, password=password)
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user = crud.authenticate(session=db, email=email, password=password)
    assert user is None


def test_check_if_user_is_active(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.is_active is True


def test_check_if_user_is_active_inactive(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, disabled=True)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.is_active


def test_check_if_user_is_superuser(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.is_superuser is True


def test_check_if_user_is_superuser_normal_user(db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.is_superuser is False


def test_get_user(db: Session) -> None:
    password = random_lower_string()
    username = random_email()
    user_in = UserCreate(email=username, password=password, is_superuser=True)
    user = crud.create_user(session=db, user_create=user_in)
    user_2 = db.get(User, user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_create_loan(db):
    loan_in = LoanCreate(amount='200000.00', annual_interest_rate='0.05', loan_term=30*12)
    loan = crud.create_loan(session=db, loan_in=loan_in, owner_id=400)
    assert loan.amount == loan_in.amount
    assert loan.annual_interest_rate == loan_in.annual_interest_rate
    assert loan.loan_term == loan_in.loan_term
    assert loan.owner_id == 400


def test_create_loan_share(db):
    user_1 = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    loan_in = LoanCreate(amount='200000.00', annual_interest_rate='0.05', loan_term=30*12)
    loan = crud.create_loan(session=db, loan_in=loan_in, owner_id=user_1.id)
    user_2 = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    db_item = crud.create_loan_share(session=db, loan_id=loan.id, user_id=user_2.id)
    loan_share = db.get(LoanShare, db_item.id)
    assert loan_share.loan_id == loan.id
    assert loan_share.user_id == user_2.id


def test_create_loan_share_is_idempotent(db):
    user_1 = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    user_2 = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    loan_in = LoanCreate(amount=1, annual_interest_rate=0, loan_term=30*12)
    loan = crud.create_loan(session=db, loan_in=loan_in, owner_id=user_1.id)
    crud.create_loan_share(session=db, loan_id=loan.id, user_id=user_2.id)
    crud.create_loan_share(session=db, loan_id=loan.id, user_id=user_2.id)
    statement = select(LoanShare).where(LoanShare.loan_id == loan.id, LoanShare.user_id == user_2.id)
    results = db.exec(statement)
    assert len(results.all()) == 1
