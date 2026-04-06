from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_permission
from app.core.roles import Permissions
from app.models.employee import Employee
from app.schemas.dashboard import (
	DashboardCategoryBreakdownResponse,
	DashboardSummaryResponse,
	DashboardTrendsResponse,
)
from app.services.analytics_service import (
	get_category_breakdown,
	get_dashboard_summary,
	get_monthly_trends,
)


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(
	"/summary",
	response_model=DashboardSummaryResponse,
	summary="Dashboard summary",
	description="Return total income, total expense, and net balance for the selected date range.",
	dependencies=[Depends(require_permission(Permissions.VIEW_DASHBOARD))],
)
def dashboard_summary_endpoint(
	start_date: datetime | None = None,
	end_date: datetime | None = None,
	current_user: Employee = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> DashboardSummaryResponse:
	data = get_dashboard_summary(db, current_user, start_date, end_date)
	return DashboardSummaryResponse(**data)


@router.get(
	"/category-breakdown",
	response_model=DashboardCategoryBreakdownResponse,
	summary="Category breakdown",
	description="Return income and expense totals grouped by category.",
	dependencies=[Depends(require_permission(Permissions.VIEW_DASHBOARD))],
)
def dashboard_category_breakdown_endpoint(
	start_date: datetime | None = None,
	end_date: datetime | None = None,
	current_user: Employee = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> DashboardCategoryBreakdownResponse:
	items = get_category_breakdown(db, current_user, start_date, end_date)
	return DashboardCategoryBreakdownResponse(items=items)


@router.get(
	"/trends",
	response_model=DashboardTrendsResponse,
	summary="Monthly trends",
	description="Return month-wise income and expense trend totals.",
	dependencies=[Depends(require_permission(Permissions.VIEW_DASHBOARD))],
)
def dashboard_trends_endpoint(
	start_date: datetime | None = None,
	end_date: datetime | None = None,
	current_user: Employee = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> DashboardTrendsResponse:
	items = get_monthly_trends(db, current_user, start_date, end_date)
	return DashboardTrendsResponse(items=items)

