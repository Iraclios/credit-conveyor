from decimal import Decimal, ROUND_HALF_UP
from app.dto.dto import PaymentScheduleElementDto
import datetime as dt
import calendar
import logging
from app.configuration import configuration as cfg

CENT = Decimal("0.01")

logger = logging.getLogger(__name__)

def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def insurance_price(amount: Decimal) -> Decimal:
    return money(max(Decimal("10000"), amount * Decimal("0.05")))


def monthly_payment(amount: Decimal, annual_rate: Decimal, term: int) -> Decimal:
    i = annual_rate / Decimal(100) / Decimal(12)
    if i.is_zero():
        return money(amount / term)
    k = i / (1 - (1 + i) ** -term)
    return money(amount * k)

def add_months(d: dt.date, months: int) -> dt.date:
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return dt.date(year, month, day)

def build_schedule(amount: Decimal, annual_rate: Decimal, term: int,
                   payment: Decimal, start: dt.date) -> list[PaymentScheduleElementDto]:
    i = annual_rate / Decimal(100) / Decimal(12)
    remaining = amount
    schedule = []
    for n in range(1, term + 1):
        interest = money(remaining * i)
        if n == term:
            debt = remaining
            total = money(debt + interest)
        else:
            total = payment
            debt = money(total - interest)
        remaining = money(remaining - debt)
        schedule.append(PaymentScheduleElementDto(
            number=n, date=add_months(start, n), total_payment=total,
            interest_payment=interest, debt_payment=debt, remaining_debt=remaining))
    return schedule

def calculate_age(birthdate: dt.date) -> int:
    today = dt.date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

def validate_loan_conditions(birthdate: dt.date, amount: Decimal, term: int) -> None:
    age = calculate_age(birthdate)
    if not cfg.MIN_AGE <= age <= cfg.MAX_AGE:
        logger.warning("Rejected: age=%s, allowed=%s-%s", age, cfg.MIN_AGE, cfg.MAX_AGE)
        raise ValueError(f"Возраст {age} вне допустимого диапазона")
    if amount > cfg.MAX_AMOUNT:
        logger.warning("Rejected: amount=%s, max=%s", amount, cfg.MAX_AMOUNT)
        raise ValueError("Сумма превышает допустимую")
    if term > cfg.MAX_TERM:
        logger.warning("Rejected: term=%s, max=%s", term, cfg.MAX_TERM)
        raise ValueError("Срок превышает допустимый")

def psk_simple(amount, payments, dates, start) -> Decimal:
    overpay = sum(payments) - amount
    years = Decimal(len(payments)) / Decimal(12)
    return money(overpay / amount / years * 100)


def psk_nominal(amount, payments, dates, start) -> Decimal:
    def npv(i: Decimal) -> Decimal:
        return sum(p / (1 + i) ** (k + 1) for k, p in enumerate(payments)) - amount

    low, high = Decimal("0"), Decimal("1")
    for _ in range(100):
        mid = (low + high) / 2
        if npv(mid) > 0:
            low = mid
        else:
            high = mid
    monthly = (low + high) / 2
    return money(monthly * 12 * 100)