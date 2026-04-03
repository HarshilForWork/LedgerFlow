from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.roles import VIEWER_ROLE_NAME
from app.models.category import Category
from app.models.employee import Employee
from app.models.transaction import Transaction


def _apply_common_filters(
	query,
	current_user: Employee,
	start_date: datetime | None,
	end_date: datetime | None,
):
	if start_date and end_date and start_date > end_date:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="start_date must be less than or equal to end_date.",
		)

	if start_date:
		query = query.filter(Transaction.transaction_date >= start_date)
	if end_date:
		query = query.filter(Transaction.transaction_date <= end_date)

	if current_user.role is not None and current_user.role.name == VIEWER_ROLE_NAME:
		query = query.filter(Transaction.employee_id == current_user.id)

	return query


def get_dashboard_summary(
	db: Session,
	current_user: Employee,
	start_date: datetime | None = None,
	end_date: datetime | None = None,
) -> dict:
	income_expr = func.coalesce(
		func.sum(case((Transaction.type == "income", Transaction.amount), else_=0)),
		0,
	)
	expense_expr = func.coalesce(
		func.sum(case((Transaction.type == "expense", Transaction.amount), else_=0)),
		0,
	)

	query = db.query(income_expr.label("income"), expense_expr.label("expense"))
	query = _apply_common_filters(query, current_user, start_date, end_date)
	result = query.one()

	total_income = Decimal(result.income)
	total_expense = Decimal(result.expense)
	return {
		"total_income": total_income,
		"total_expense": total_expense,
		"net_balance": total_income - total_expense,
	}


def get_category_breakdown(
	db: Session,
	current_user: Employee,
	start_date: datetime | None = None,
	end_date: datetime | None = None,
) -> list[dict]:
	query = (
		db.query(
			Category.id.label("category_id"),
			Category.name.label("category_name"),
			Transaction.type.label("type"),
			func.coalesce(func.sum(Transaction.amount), 0).label("total_amount"),
		)
		.join(Category, Transaction.category_id == Category.id)
		.group_by(Category.id, Category.name, Transaction.type)
		.order_by(Category.name.asc())
	)

	query = _apply_common_filters(query, current_user, start_date, end_date)
	rows = query.all()

	return [
		{
			"category_id": row.category_id,
			"category_name": row.category_name,
			"type": row.type,
			"total_amount": Decimal(row.total_amount),
		}
		for row in rows
	]


def get_monthly_trends(
	db: Session,
	current_user: Employee,
	start_date: datetime | None = None,
	end_date: datetime | None = None,
) -> list[dict]:
	month_expr = func.date_trunc("month", Transaction.transaction_date)
	query = (
		db.query(
			month_expr.label("month"),
			Transaction.type.label("type"),
			func.coalesce(func.sum(Transaction.amount), 0).label("total_amount"),
		)
		.group_by(month_expr, Transaction.type)
		.order_by(month_expr.asc())
	)

	query = _apply_common_filters(query, current_user, start_date, end_date)
	rows = query.all()

	return [
		{
			"month": row.month,
			"type": row.type,
			"total_amount": Decimal(row.total_amount),
		}
		for row in rows
	]

