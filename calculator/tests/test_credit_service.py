from decimal import Decimal

import pytest

from app.dto.dto import ScoringDataDto
from app.service import credit_service


def make_data(**overrides):
    data = dict(amount=100000, term=12, firstName="Ivan", lastName="Petrov",
                birthdate="1995-05-20", passportSeries="1234", passportNumber="567890",
                isInsuranceEnabled=False, isSalaryClient=False)
    data.update(overrides)
    return ScoringDataDto(**data)


def test_calculate_credit_basic():
    credit = credit_service.calculate_credit(make_data())
    assert credit.rate == Decimal(15)
    assert credit.monthly_payment == Decimal("9025.83")
    assert len(credit.payment_schedule) == 12
    assert credit.payment_schedule[-1].remaining_debt == Decimal("0.00")


def test_calculate_credit_with_flags():
    credit = credit_service.calculate_credit(
        make_data(isInsuranceEnabled=True, isSalaryClient=True))
    assert credit.rate == Decimal(11)
    assert credit.amount == Decimal("110000.00")
    assert credit.psk > credit.rate


@pytest.mark.parametrize("birthdate", ["2015-01-01", "1940-01-01"])
def test_scoring_rejects_bad_age(birthdate):
    with pytest.raises(ValueError):
        credit_service.scoring(make_data(birthdate=birthdate))


def test_scoring_rejects_big_amount():
    with pytest.raises(ValueError):
        credit_service.scoring(make_data(amount=6000000))


def test_scoring_rejects_long_term():
    with pytest.raises(ValueError):
        credit_service.scoring(make_data(term=400))