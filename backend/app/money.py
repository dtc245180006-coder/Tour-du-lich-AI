"""Whole Vietnamese dong; Decimal storage without binary floating point."""
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.types import TypeDecorator, Numeric

def vnd(value):
    return int(Decimal(str(value)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

class Money(TypeDecorator):
    impl = Numeric(18, 0)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return None if value is None else Decimal(vnd(value))

    def process_result_value(self, value, dialect):
        return None if value is None else vnd(value)
