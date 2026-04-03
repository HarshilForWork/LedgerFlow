from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_permission
from app.core.roles import Permissions
from app.models.employee import Employee
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate
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
	response_model=list[TransactionResponse],
	dependencies=[Depends(require_permission(Permissions.VIEW_TRANSACTION))],
)
def list_transactions_endpoint(
	tx_type: Literal["income", "expense"] | None = Query(default=None, alias="type"),
	category_id: UUID | None = None,
	start_date: datetime | None = None,
	end_date: datetime | None = None,
	current_user: Employee = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> list[TransactionResponse]:
	return list_transactions(
		db=db,
		current_user=current_user,
		tx_type=tx_type,
		category_id=category_id,
		start_date=start_date,
		end_date=end_date,
	)


@router.put(
	"/{transaction_id}",
	response_model=TransactionResponse,
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
	dependencies=[Depends(require_permission(Permissions.DELETE_TRANSACTION))],
)
def delete_transaction_endpoint(
	transaction_id: UUID,
	current_user: Employee = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> Response:
	delete_transaction(db, transaction_id, current_user)
	return Response(status_code=status.HTTP_204_NO_CONTENT)

