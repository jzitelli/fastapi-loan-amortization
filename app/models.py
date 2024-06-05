from decimal import Decimal
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
# TODO replace email str with EmailStr when sqlmodel supports it
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# Properties to receive via API on update, all are optional
# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdate(UserBase):
    email: str | None = None  # type: ignore
    password: str | None = None


class LoanShare(SQLModel, table=True):
    loan_id: int | None = Field(default=None, foreign_key="loan.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    loans: list["Loan"] = Relationship(back_populates="owner")
    shared_loans: list["Loan"] = Relationship(back_populates="shared_users", link_model=LoanShare)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: int


class LoanBase(SQLModel):
    amount: Decimal = Field(decimal_places=2, gt=0)
    annual_interest_rate: Decimal = Field(ge=0)
    loan_term: int = Field(gt=0)


class LoanCreate(LoanBase):
    pass


class Loan(LoanBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="loans")
    shared_users: list[User] = Relationship(back_populates="shared_loans", link_model=LoanShare)


# Properties to return via API, id is always required
class LoanPublic(LoanBase):
    id: int
    owner_id: int


class LoansPublic(SQLModel):
    data: list[LoanPublic]
    count: int


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: int | None = None
