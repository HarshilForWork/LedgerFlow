import uuid
from datetime import datetime

from sqlalchemy import (
	Boolean,
	CheckConstraint,
	Column,
	DateTime,
	ForeignKey,
	Numeric,
	String,
	Text,
	text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Transaction(Base):
	__tablename__ = "transactions"
	__table_args__ = (
		CheckConstraint("type IN ('income', 'expense')", name="ck_transactions_type"),
	)

	id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
	amount = Column(Numeric(12, 2), nullable=False)
	type = Column(String(10), nullable=False)
	category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
	transaction_date = Column(DateTime, nullable=False)
	note = Column(Text, nullable=True)
	is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("false"), index=True)
	created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
	updated_at = Column(
		DateTime,
		nullable=False,
		default=datetime.utcnow,
		onupdate=datetime.utcnow,
	)

	employee = relationship("Employee", back_populates="transactions")
	category = relationship("Category", back_populates="transactions")

