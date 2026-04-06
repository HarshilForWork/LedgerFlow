from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DashboardSummaryResponse(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_income": "15000.00",
                "total_expense": "4200.50",
                "net_balance": "10799.50",
            }
        }
    )


class CategoryBreakdownItem(BaseModel):
    category_id: UUID
    category_name: str
    type: Literal["income", "expense"]
    total_amount: Decimal


class DashboardCategoryBreakdownResponse(BaseModel):
    items: list[CategoryBreakdownItem]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "category_id": "90843884-cbe7-4dd7-8d9b-a4ef700d4f6b",
                        "category_name": "Salary",
                        "type": "income",
                        "total_amount": "12000.00",
                    }
                ]
            }
        }
    )


class TrendItem(BaseModel):
    month: datetime
    type: Literal["income", "expense"]
    total_amount: Decimal


class DashboardTrendsResponse(BaseModel):
    items: list[TrendItem]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "month": "2026-03-01T00:00:00Z",
                        "type": "expense",
                        "total_amount": "3200.00",
                    }
                ]
            }
        }
    )
