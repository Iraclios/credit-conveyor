import logging

from fastapi import APIRouter, HTTPException

from app.dto.dto import *
from app.service import offers_service, credit_service

router = APIRouter(prefix="/calculator", tags=["Calculator"])
logger = logging.getLogger(__name__)


@router.post("/offers", response_model=list[LoanOfferDto],
             summary="Расчет кредитных предложений")
def offers(request: LoanStatementRequestDto) -> list[LoanOfferDto]:
    try:
        return offers_service.get_offers(request)
    except ValueError as e:
        logger.warning("Request rejected: %s", e)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/calc", response_model=CreditDto, summary="Полный расчёт кредита")
def calc(data: ScoringDataDto) -> CreditDto:
    try:
        return credit_service.calculate_credit(data)
    except ValueError as e:
        logger.warning("Request rejected: %s", e)
        raise HTTPException(status_code=400, detail=str(e))