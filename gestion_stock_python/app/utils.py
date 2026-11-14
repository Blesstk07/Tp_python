from datetime import datetime
from secrets import randbelow


def make_ref(prefix: str) -> str:
    number = randbelow(900_000) + 100_000
    return f"{prefix}-{datetime.now():%Y%m%d}-{number}"