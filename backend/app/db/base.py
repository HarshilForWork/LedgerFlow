from app.db.session import Base

# Import models so SQLAlchemy can discover all metadata before create_all.
from app.models import category, employee, permission, role, role_permission, transaction  # noqa: F401

