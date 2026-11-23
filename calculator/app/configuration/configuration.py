from decimal import Decimal

NAME_PATTERN = r"^[A-Za-zА-Яа-яЁё-]+$"
BASE_RATE = Decimal("15")
INSURANCE_RATE_DISCOUNT = Decimal("3")
SALARY_RATE_DISCOUNT = Decimal("1")
MIN_AGE = 18
MAX_AMOUNT = Decimal("5000000")
MAX_TERM = 360
MAX_AGE = 65
PSK_METHOD = "effective_grid"