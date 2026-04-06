import logging
from decimal import Decimal
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.core.roles import VIEWER_ROLE_NAME
from app.exceptions.custom_exceptions import forbidden_exception, not_found_exception
from app.models.category import Category
from app.models.employee import Employee
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.utils.response import build_paginated_payload


logger = logging.getLogger(__name__)


def _is_viewer(user: Employee) -> bool:
	return user.role is not None and user.role.name == VIEWER_ROLE_NAME


def _base_query(db: Session):
	return db.query(Transaction).options(
		joinedload(Transaction.employee),
		joinedload(Transaction.category),
	)


def _active_transaction_query(db: Session):
	return _base_query(db).filter(Transaction.is_deleted.is_(False))


def _validate_filters(
	date_from: datetime | None,
	date_to: datetime | None,
	min_amount: Decimal | None,
	max_amount: Decimal | None,
) -> None:
	if date_from and date_to and date_from > date_to:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="date_from must be less than or equal to date_to.",
		)

	if min_amount is not None and max_amount is not None and min_amount > max_amount:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="min_amount must be less than or equal to max_amount.",
		)


def _apply_transaction_filters(
	query,
	tx_type: str | None,
	category_id: UUID | None,
	date_from: datetime | None,
	date_to: datetime | None,
	min_amount: Decimal | None,
	max_amount: Decimal | None,
	search: str | None,
):
	if tx_type:
		query = query.filter(Transaction.type == tx_type)
	if category_id:
		query = query.filter(Transaction.category_id == category_id)
	if date_from:
		query = query.filter(Transaction.transaction_date >= date_from)
	if date_to:
		query = query.filter(Transaction.transaction_date <= date_to)
	if min_amount is not None:
		query = query.filter(Transaction.amount >= min_amount)
	if max_amount is not None:
		query = query.filter(Transaction.amount <= max_amount)
	if search and search.strip():
		search_term = f"%{search.strip()}%"
		query = query.filter(
			or_(
				Transaction.note.ilike(search_term),
				Transaction.category.has(Category.name.ilike(search_term)),
			)
		)

	return query


def list_transactions(
	db: Session,
	current_user: Employee,
	page: int = 1,
	limit: int = 10,
	tx_type: str | None = None,
	category_id: UUID | None = None,
	date_from: datetime | None = None,
	date_to: datetime | None = None,
	min_amount: Decimal | None = None,
	max_amount: Decimal | None = None,
	search: str | None = None,
) -> dict:
	_validate_filters(date_from, date_to, min_amount, max_amount)

	query = _active_transaction_query(db)
	query = _apply_transaction_filters(
		query=query,
		tx_type=tx_type,
		category_id=category_id,
		date_from=date_from,
		date_to=date_to,
		min_amount=min_amount,
		max_amount=max_amount,
		search=search,
	)

	if _is_viewer(current_user):
		query = query.filter(Transaction.employee_id == current_user.id)

	total = query.order_by(None).count()
	items = (
		query.order_by(Transaction.transaction_date.desc())
		.offset((page - 1) * limit)
		.limit(limit)
		.all()
	)

	return build_paginated_payload(items=items, page=page, limit=limit, total=total)


def create_transaction(
	db: Session,
	payload: TransactionCreate,
	current_user: Employee,
) -> Transaction:
	if _is_viewer(current_user) and payload.employee_id != current_user.id:
		raise forbidden_exception("Viewer can only create their own transactions.")

	employee_exists = (
		db.query(Employee.id).filter(Employee.id == payload.employee_id).first() is not None
	)
	if not employee_exists:
		raise not_found_exception("Employee")

	category_exists = (
		db.query(Category.id).filter(Category.id == payload.category_id).first() is not None
	)
	if not category_exists:
		raise not_found_exception("Category")

	transaction = Transaction(**payload.model_dump())
	db.add(transaction)
	db.commit()
	logger.info(
		"Transaction created | transaction_id=%s employee_id=%s actor_user_id=%s",
		transaction.id,
		payload.employee_id,
		current_user.id,
	)
	return get_transaction_by_id(db, transaction.id)


def get_transaction_by_id(db: Session, transaction_id: UUID) -> Transaction:
	transaction = _active_transaction_query(db).filter(Transaction.id == transaction_id).first()
	if transaction is None:
		raise not_found_exception("Transaction")
	return transaction


def update_transaction(
	db: Session,
	transaction_id: UUID,
	payload: TransactionUpdate,
	current_user: Employee,
) -> Transaction:
	transaction = (
		db.query(Transaction)
		.filter(Transaction.id == transaction_id, Transaction.is_deleted.is_(False))
		.first()
	)
	if transaction is None:
		raise not_found_exception("Transaction")

	if _is_viewer(current_user) and transaction.employee_id != current_user.id:
		raise forbidden_exception("Viewer can only update their own transactions.")

	updates = payload.model_dump(exclude_unset=True)

	if _is_viewer(current_user) and "employee_id" in updates:
		if updates["employee_id"] != current_user.id:
			raise forbidden_exception("Viewer can only assign transactions to themselves.")

	if "employee_id" in updates:
		employee_exists = (
			db.query(Employee.id)
			.filter(Employee.id == updates["employee_id"])
			.first()
			is not None
		)
		if not employee_exists:
			raise not_found_exception("Employee")

	if "category_id" in updates:
		category_exists = (
			db.query(Category.id)
			.filter(Category.id == updates["category_id"])
			.first()
			is not None
		)
		if not category_exists:
			raise not_found_exception("Category")

	for field, value in updates.items():
		setattr(transaction, field, value)

	db.commit()
	return get_transaction_by_id(db, transaction.id)


def delete_transaction(
	db: Session,
	transaction_id: UUID,
	current_user: Employee,
) -> None:
	transaction = (
		db.query(Transaction)
		.filter(Transaction.id == transaction_id, Transaction.is_deleted.is_(False))
		.first()
	)
	if transaction is None:
		raise not_found_exception("Transaction")

	if _is_viewer(current_user) and transaction.employee_id != current_user.id:
		raise forbidden_exception("Viewer can only delete their own transactions.")

	transaction.is_deleted = True
	db.commit()

