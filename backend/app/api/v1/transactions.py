from decimal import Decimal
from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_permission
from app.core.roles import Permissions
from app.models.employee import Employee
from app.schemas.transaction import (
	TransactionCreate,
	TransactionListResponse,
	TransactionResponse,
	TransactionUpdate,
)
from app.services.transaction_service import (
	create_transaction,
	delete_transaction,
	list_transactions,
	update_transaction,
)


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post(
	"",
	response_model=TransactionResponse,
	status_code=status.HTTP_201_CREATED,
	summary="Create transaction",
	description="Create a new income or expense transaction.",
	dependencies=[Depends(require_permission(Permissions.CREATE_TRANSACTION))],
)
def create_transaction_endpoint(
	payload: TransactionCreate,
	current_user: Employee = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> TransactionResponse:
	return create_transaction(db, payload, current_user)


@router.get(
	"",
	response_model=TransactionListResponse,
	summary="List transactions",
	description="List transactions with pagination, advanced filters, and search.",
	dependencies=[Depends(require_permission(Permissions.VIEW_TRANSACTION))],
)
def list_transactions_endpoint(
	page: int = Query(default=1, ge=1),
	limit: int = Query(default=10, ge=1, le=100),
	tx_type: Literal["income", "expense"] | None = Query(default=None, alias="type"),
	category_id: UUID | None = None,
	date_from: datetime | None = None,
	date_to: datetime | None = None,
	start_date: datetime | None = Query(default=None, deprecated=True),
	end_date: datetime | None = Query(default=None, deprecated=True),
	min_amount: Decimal | None = Query(default=None, ge=0),
	max_amount: Decimal | None = Query(default=None, ge=0),
	search: str | None = Query(default=None, min_length=1),
	current_user: Employee = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> TransactionListResponse:
	effective_date_from = date_from or start_date
	effective_date_to = date_to or end_date

	return list_transactions(
		db=db,
		current_user=current_user,
		page=page,
		limit=limit,
		tx_type=tx_type,
		category_id=category_id,
		date_from=effective_date_from,
		date_to=effective_date_to,
		min_amount=min_amount,
		max_amount=max_amount,
		search=search,
	)


@router.put(
	"/{transaction_id}",
	response_model=TransactionResponse,
	summary="Update transaction",
	description="Update fields of an existing transaction by ID.",
	dependencies=[Depends(require_permission(Permissions.UPDATE_TRANSACTION))],
)
def update_transaction_endpoint(
	transaction_id: UUID,
	payload: TransactionUpdate,
	current_user: Employee = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> TransactionResponse:
	return update_transaction(db, transaction_id, payload, current_user)


@router.delete(
	"/{transaction_id}",
	status_code=status.HTTP_204_NO_CONTENT,
	summary="Soft delete transaction",
	description="Soft delete a transaction by setting is_deleted=true.",
	dependencies=[Depends(require_permission(Permissions.DELETE_TRANSACTION))],
)
def delete_transaction_endpoint(
	transaction_id: UUID,
	current_user: Employee = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> Response:
	delete_transaction(db, transaction_id, current_user)
	return Response(status_code=status.HTTP_204_NO_CONTENT)

