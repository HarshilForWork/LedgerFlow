import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Role(Base):
	__tablename__ = "roles"

	id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	name = Column(String(50), unique=True, nullable=False)

	employees = relationship("Employee", back_populates="role")
	role_permissions = relationship(
		"RolePermission", back_populates="role", cascade="all, delete-orphan"
	)
	permissions = relationship(
		"Permission",
		secondary="role_permissions",
		back_populates="roles",
		viewonly=True,
	)

