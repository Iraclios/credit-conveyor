from datetime import date
from decimal import Decimal

import pytest

from app.utils.service_utils import (add_months, build_schedule,
                                     insurance_price, money,
                                     monthly_payment, psk, calculate_age)


def test_money_rounds_half_up():
    assert money(Decimal("2.675")) == Decimal("2.68")


def test_insurance_price_minimum():
    assert insurance_price(Decimal("100000")) == Decimal("10000.00")


def test_insurance_price_percent():
    assert insurance_price(Decimal("500000")) == Decimal("25000.00")


def test_monthly_payment():
    assert monthly_payment(Decimal("100000"), Decimal("15"), 12) == Decimal("9025.83")


def test_monthly_payment_zero_rate():
    assert monthly_payment(Decimal("12000"), Decimal("0"), 12) == Decimal("1000.00")


def test_add_months_end_of_month():
    assert add_months(date(2027, 1, 31), 1) == date(2027, 2, 28)


def test_add_months_year_rollover():
    assert add_months(date(2026, 11, 21), 2) == date(2027, 1, 21)


def test_schedule_closes_debt():
    payment = monthly_payment(Decimal("100000"), Decimal("15"), 12)
    schedule = build_schedule(Decimal("100000"), Decimal("15"), 12, payment, date(2026, 11, 21))
    assert len(schedule) == 12
    assert schedule[-1].remaining_debt == Decimal("0.00")
    assert sum(r.debt_payment for r in schedule) == Decimal("100000.00")


def test_psk_equals_rate_without_extra_costs():
    payment = monthly_payment(Decimal("100000"), Decimal("15"), 12)
    schedule = build_schedule(Decimal("100000"), Decimal("15"), 12, payment, date(2026, 11, 21))
    assert psk(Decimal("100000"), [r.total_payment for r in schedule]) == Decimal("15.00")



def test_calculate_age():
    today = date.today()
    born = date(today.year - 30, today.month, today.day)
    assert calculate_age(born) == 30