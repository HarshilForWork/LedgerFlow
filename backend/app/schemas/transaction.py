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


class TransactionCreate(TransactionBase):
	pass


class TransactionUpdate(BaseModel):
	employee_id: Optional[UUID] = None
	amount: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=12)
	type: Optional[Literal["income", "expense"]] = None
	category_id: Optional[UUID] = None
	transaction_date: Optional[datetime] = None
	note: Optional[str] = None


class TransactionResponse(TransactionBase):
	id: UUID
	created_at: datetime
	updated_at: datetime
	employee: Optional[EmployeeSummary] = None
	category: Optional[CategorySummary] = None

	model_config = ConfigDict(from_attributes=True)

