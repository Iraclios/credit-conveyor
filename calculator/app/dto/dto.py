from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class LoanStatementRequestDto(CamelModel):
    amount: Decimal = Field(ge=30000, description="Сумма кредита")
    term: int = Field(ge=6, description="Срок кредита в месяцах")
    first_name: str = Field(min_length=2, max_length=30, pattern=r"^[A-Za-z]+$")
    last_name: str = Field(min_length=2, max_length=30, pattern=r"^[A-Za-z]+$")
    middle_name: str | None = Field(default=None, min_length=2, max_length=30, pattern=r"^[A-Za-z]+$")
    email: str = Field(pattern=r"^[\w\.-]{2,50}@[\w\.-]+\.\w{2,}$")
    birthdate: date
    passport_series: str = Field(pattern=r"^\d{4}$")
    passport_number: str = Field(pattern=r"^\d{6}$")


class LoanOfferDto(CamelModel):
    statement_id: UUID
    requested_amount: Decimal
    total_amount: Decimal
    term: int
    monthly_payment: Decimal
    rate: Decimal
    is_insurance_enabled: bool
    is_salary_client: bool


class ScoringDataDto(CamelModel):
    amount: Decimal = Field(ge=30000, description="Сумма кредита")
    term: int = Field(ge=6, description="Срок кредита в месяцах")
    first_name: str = Field(min_length=2, max_length=30, pattern=r"^[A-Za-z]+$")
    last_name: str = Field(min_length=2, max_length=30, pattern=r"^[A-Za-z]+$")
    middle_name: str | None = Field(default=None, min_length=2, max_length=30, pattern=r"^[A-Za-z]+$")
    birthdate: date
    passport_series: str = Field(pattern=r"^\d{4}$")
    passport_number: str = Field(pattern=r"^\d{6}$")
    is_insurance_enabled: bool
    is_salary_client: bool


class PaymentScheduleElementDto(CamelModel):
    number: int
    date: date
    total_payment: Decimal
    interest_payment: Decimal
    debt_payment: Decimal
    remaining_debt: Decimal


class CreditDto(CamelModel):
    amount: Decimal
    term: int
    monthly_payment: Decimal
    rate: Decimal
    psk: Decimal
    is_insurance_enabled: bool
    is_salary_client: bool
    payment_schedule: list[PaymentScheduleElementDto]