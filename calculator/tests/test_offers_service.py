from datetime import date
from decimal import Decimal

import pytest

from app.dto.dto import LoanStatementRequestDto
from app.service import offers_service


def make_request(birthdate="1995-05-20", amount=100000):
    return LoanStatementRequestDto(
        amount=amount, term=12, firstName="Ivan", lastName="Petrov",
        email="ivan@mail.ru", birthdate=birthdate,
        passportSeries="1234", passportNumber="567890")


def test_calculate_age():
    today = date.today()
    born = date(today.year - 30, today.month, today.day)
    assert offers_service.calculate_age(born) == 30


def test_prescoring_rejects_minor():
    with pytest.raises(ValueError):
        offers_service.prescoring(make_request(birthdate="2015-01-01"))


def test_get_offers_returns_four_sorted():
    offers = offers_service.get_offers(make_request())
    assert len(offers) == 4
    assert [o.rate for o in offers] == [Decimal(15), Decimal(14), Decimal(12), Decimal(11)]
    assert len({o.statement_id for o in offers}) == 1


def test_offer_with_insurance_increases_total():
    offers = offers_service.get_offers(make_request())
    insured = [o for o in offers if o.is_insurance_enabled]
    assert all(o.total_amount == Decimal("110000.00") for o in insured)


def test_get_offers_rejects_minor():
    with pytest.raises(ValueError):
        offers_service.get_offers(make_request(birthdate="2015-01-01"))