import logging
import uuid
from datetime import date

from app.configuration import configuration as cfg
from app.dto.dto import LoanOfferDto, LoanStatementRequestDto
from app.utils.service_utils import insurance_price, money, monthly_payment

logger = logging.getLogger(__name__)


def calculate_age(birthdate: date) -> int:
    today = date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))


def prescoring(request: LoanStatementRequestDto) -> None:
    age = calculate_age(request.birthdate)
    if age < cfg.MIN_AGE:
        logger.warning("Prescoring failed: age %s", age)
        raise ValueError(f"Возраст должен быть не менее {cfg.MIN_AGE} лет")
    logger.info("Prescoring passed: age=%s", age)


def build_offer(request: LoanStatementRequestDto, statement_id: uuid.UUID,
                insurance: bool, salary: bool) -> LoanOfferDto:
    rate = cfg.BASE_RATE
    total = request.amount
    if insurance:
        price = insurance_price(request.amount)
        rate -= cfg.INSURANCE_RATE_DISCOUNT
        total += insurance_price(request.amount)
        logger.debug("Insurance applied: price=%s, rate=%s", price, rate)
    if salary:
        rate -= cfg.SALARY_RATE_DISCOUNT
        logger.debug("Salary client discount applied: rate=%s", rate)
    payment = monthly_payment(total, rate, request.term)
    logger.info("Offer built: insurance=%s, salary=%s, rate=%s, total=%s, payment=%s",
                insurance, salary, rate, total, payment)
    return LoanOfferDto(
        statement_id=statement_id,
        requested_amount=request.amount,
        total_amount=money(total),
        term=request.term,
        monthly_payment=monthly_payment(total, rate, request.term),
        rate=rate,
        is_insurance_enabled=insurance,
        is_salary_client=salary,
    )


def get_offers(request: LoanStatementRequestDto) -> list[LoanOfferDto]:
    logger.info("Offers request: %s", request)
    prescoring(request)
    statement_id = uuid.uuid4()
    logger.debug("Statement id generated: %s", statement_id)
    offers = [build_offer(request, statement_id, ins, sal)
              for ins in (False, True) for sal in (False, True)]
    offers.sort(key=lambda o: o.rate, reverse=True)
    logger.info("Offers calculated: %s", offers)
    return offers