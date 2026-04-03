from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal


class CategoryBreakdownItem(BaseModel):
    category_id: UUID
    category_name: str
    type: Literal["income", "expense"]
    total_amount: Decimal


class DashboardCategoryBreakdownResponse(BaseModel):
    items: list[CategoryBreakdownItem]


class TrendItem(BaseModel):
    month: datetime
    type: Literal["income", "expense"]
    total_amount: Decimal


class DashboardTrendsResponse(BaseModel):
    items: list[TrendItem]
