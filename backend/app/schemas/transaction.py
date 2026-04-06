from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategorySummary(BaseModel):
	id: UUID
	name: str

	model_config = ConfigDict(from_attributes=True)


class EmployeeSummary(BaseModel):
	id: UUID
	name: str

	model_config = ConfigDict(from_attributes=True)


class TransactionBase(BaseModel):
	employee_id: UUID
	amount: Decimal = Field(..., decimal_places=2, max_digits=12)
	type: Literal["income", "expense"]
	category_id: UUID
	transaction_date: datetime
	note: Optional[str] = None

	model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"employee_id": "2c7f53af-065f-4ef0-a876-2f17cb67ee3f",
				"amount": "1250.50",
				"type": "income",
				"category_id": "641864fd-4adb-4d95-8f63-53f385ca0cc6",
				"transaction_date": "2026-04-01T09:15:00Z",
				"note": "April consulting retainer",
			}
		}
	)


class TransactionCreate(TransactionBase):
	pass


class TransactionUpdate(BaseModel):
	employee_id: Optional[UUID] = None
	amount: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=12)
	type: Optional[Literal["income", "expense"]] = None
	category_id: Optional[UUID] = None
	transaction_date: Optional[datetime] = None
	note: Optional[str] = None

	model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"amount": "980.00",
				"category_id": "641864fd-4adb-4d95-8f63-53f385ca0cc6",
				"note": "Updated after final invoice adjustment",
			}
		}
	)


class TransactionResponse(TransactionBase):
	id: UUID
	created_at: datetime
	updated_at: datetime
	employee: Optional[EmployeeSummary] = None
	category: Optional[CategorySummary] = None

	model_config = ConfigDict(from_attributes=True)


class TransactionListResponse(BaseModel):
	page: int
	limit: int
	total: int
	total_pages: int
	data: list[TransactionResponse]

	model_config = ConfigDict(
		json_schema_extra={
			"example": {
				"page": 1,
				"limit": 10,
				"total": 45,
				"total_pages": 5,
				"data": [],
			}
		}
	)

