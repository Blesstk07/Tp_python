from decimal import Decimal

import pytest
from pydantic import TypeAdapter, ValidationError

from app.schemas.common import Money, TotalMoney


@pytest.mark.parametrize(
	("money_type", "value", "expected"),
	[
		(Money, Decimal("1200"), '"1200.00"'),
		(Money, Decimal("0.5"), '"0.50"'),
		(TotalMoney, Decimal("42500.00"), '"42500.00"'),
	],
)
def test_money_serializes_as_two_decimal_string(money_type, value, expected):
	assert TypeAdapter(money_type).dump_json(value).decode() == expected


@pytest.mark.parametrize("money_type", [Money, TotalMoney])
@pytest.mark.parametrize("value", [Decimal("-0.01"), Decimal("1.234")])
def test_money_rejects_negative_or_more_than_two_decimal_places(
	money_type,
	value,
):
	with pytest.raises(ValidationError):
		TypeAdapter(money_type).validate_python(value)


def test_total_money_accepts_fourteen_digits():
	value = Decimal("999999999999.99")
	assert TypeAdapter(TotalMoney).validate_python(value) == value


def test_total_money_rejects_more_than_fourteen_digits():
	with pytest.raises(ValidationError):
		TypeAdapter(TotalMoney).validate_python(Decimal("1000000000000.00"))
