from decimal import Decimal
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest
from sqlalchemy.exc import IntegrityError

from app.core.errors import ApiError, register_error_handlers
from app.models.catalog import Product
from app.schemas.products import ProductIn
from app.schemas.sales import SaleIn
from app.schemas.stock import StockEntryIn
from app.services.products import delete_product
from app.services.sales import create_sale


def test_product_rejects_negative_stock_quantity():
	with pytest.raises(ValidationError):
		ProductIn(
			category_id=1,
			name="Produit",
			sku="P-001",
			sale_price="12.50",
			quantity=-1,
		)


def test_sale_rejects_duplicate_product_lines():
	with pytest.raises(ValidationError):
		SaleIn(
			items=[
				{"product_id": 1, "quantity": 2},
				{"product_id": 1, "quantity": 1},
			]
		)


def test_supply_rejects_duplicate_product_lines():
	with pytest.raises(ValidationError):
		StockEntryIn(
			supplier_id=1,
			items=[
				{"product_id": 1, "quantity": 2, "unit_cost": "3.00"},
				{"product_id": 1, "quantity": 1, "unit_cost": "3.00"},
			],
		)


def test_sale_with_insufficient_stock_rolls_back():
	db = Mock()
	product = Product(
		id=1,
		category_id=1,
		name="Produit",
		sku="P-001",
		sale_price=Decimal("10.00"),
		quantity=1,
		min_quantity=0,
	)
	db.execute.return_value.scalars.return_value.all.return_value = [product]

	with pytest.raises(ApiError) as error:
		create_sale(
			db,
			SaleIn(items=[{"product_id": 1, "quantity": 2}]),
		)

	assert error.value.status_code == 409
	assert error.value.code == "INSUFFICIENT_STOCK"
	assert error.value.details == [
		{"product_id": 1, "requested": 2, "available": 1}
	]
	db.rollback.assert_called_once()
	db.commit.assert_not_called()


def test_delete_product_in_use_returns_conflict_and_rolls_back():
	db = Mock()
	db.get.return_value = Product(id=1)
	db.commit.side_effect = IntegrityError(
		"DELETE FROM products",
		{},
		Exception("foreign key constraint"),
	)

	with pytest.raises(ApiError) as error:
		delete_product(db, 1)

	assert error.value.status_code == 409
	assert error.value.code == "CONFLICT"
	db.rollback.assert_called_once()


@pytest.fixture
def error_client():
	app = FastAPI()
	register_error_handlers(app)

	@app.get("/conflict")
	def conflict():
		raise ApiError(409, "CONFLICT", "Ressource déjà utilisée")

	@app.get("/items/{item_id}")
	def get_item(item_id: int):
		return {"item_id": item_id}

	return TestClient(app)


def test_api_error_returns_contract_status_and_body(error_client):
	response = error_client.get("/conflict")

	assert response.status_code == 409
	assert response.json() == {
		"error": {
			"code": "CONFLICT",
			"message": "Ressource déjà utilisée",
		}
	}


def test_request_validation_uses_bad_request_contract(error_client):
	response = error_client.get("/items/not-an-integer")

	assert response.status_code == 400
	assert response.json()["error"]["code"] == "VALIDATION_ERROR"
	assert response.json()["error"]["details"]
