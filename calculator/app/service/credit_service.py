import logging
from datetime import date

from app.configuration import configuration as cfg
from app.dto.dto import CreditDto, ScoringDataDto
from app.service.offers_service import calculate_age
from app.utils.service_utils import (build_schedule, insurance_price, money,
                                     monthly_payment, psk)

logger = logging.getLogger(__name__)


def scoring(data: ScoringDataDto) -> None:
    age = calculate_age(data.birthdate)
    if not cfg.MIN_AGE <= age <= cfg.MAX_AGE:
        logger.warning("Scoring failed: age=%s, allowed=%s-%s", age, cfg.MIN_AGE, cfg.MAX_AGE)
        raise ValueError(f"Возраст {age} вне допустимого диапазона")
    if data.amount > cfg.MAX_AMOUNT:
        logger.warning("Scoring failed: amount=%s, max=%s", data.amount, cfg.MAX_AMOUNT)
        raise ValueError("Сумма превышает допустимую")
    if data.term > cfg.MAX_TERM:
        logger.warning("Scoring failed: term=%s, max=%s", data.term, cfg.MAX_TERM)
        raise ValueError("Срок превышает допустимый")
    logger.info("Scoring passed: age=%s, amount=%s, term=%s", age, data.amount, data.term)

def calculate_credit(data: ScoringDataDto) -> CreditDto:
    logger.info("Calc request: %s", data)
    scoring(data)
    rate = cfg.BASE_RATE
    total = data.amount
    if data.is_insurance_enabled:
        price = insurance_price(data.amount)
        rate -= cfg.INSURANCE_RATE_DISCOUNT
        total += insurance_price(data.amount)
        logger.debug("Insurance applied: price=%s, rate=%s", price, rate)
    if data.is_salary_client:
        rate -= cfg.SALARY_RATE_DISCOUNT
        logger.debug("Salary client discount applied: rate=%s", rate)
    logger.info("Final rate=%s, total amount=%s", rate, total)
    payment = monthly_payment(total, rate, data.term)
    logger.info("Monthly payment=%s", payment)
    schedule = build_schedule(total, rate, data.term, payment, date.today())
    logger.info("Schedule built: %s payments, first=%s, last=%s",
                len(schedule), schedule[0].date, schedule[-1].date)
    psk_value = psk(data.amount, [row.total_payment for row in schedule])
    logger.info("PSK=%s", psk_value)
    result = CreditDto(
        amount=money(total), term=data.term, monthly_payment=payment, rate=rate,
        psk=psk(data.amount, [row.total_payment for row in schedule]),
        is_insurance_enabled=data.is_insurance_enabled,
        is_salary_client=data.is_salary_client, payment_schedule=schedule)
    logger.info("Credit calculated: %s", result)
    return result