# LedgerFlow Backend

Backend data layer for a finance dashboard system built with FastAPI, SQLAlchemy, and PostgreSQL (Neon).

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL (Neon)
- Pydantic v2
- bcrypt

## Project Structure

```text
backend/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── roles.py
│   │   └── security.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dependency.py
│   │   ├── init_db.py
│   │   └── session.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── category.py
│   │   ├── employee.py
│   │   ├── permission.py
│   │   ├── role.py
│   │   ├── role_permission.py
│   │   ├── transaction.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── category.py
│   │   ├── employee.py
│   │   ├── permission.py
│   │   ├── role.py
│   │   ├── role_permission.py
│   │   ├── transaction.py
│   │   └── user.py
│   └── utils/
│       └── common.py
├── .env
├── .env.example
├── requirements.txt
└── tests/
```

## Environment

Use `.env.example` as a template and create your local `.env` file.

Example:

```env
DATABASE_URL=postgresql://<user>:<password>@<host>/<db>?sslmode=require
JWT_SECRET_KEY=<long-random-secret>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

Required keys:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `JWT_EXPIRE_MINUTES`

The app normalizes this URL to `postgresql+psycopg2://` in the DB session layer.

## Install Dependencies

```bash
uv pip install -r requirements.txt
```

Current dependencies in `requirements.txt`:

- bcrypt
- fastapi
- PyJWT
- psycopg2-binary
- pydantic[email]>=2,<3
- pydantic-settings>=2,<3
- python-dotenv
- sqlalchemy

## Database Layer

### Session and Base

- `app/db/session.py` defines:
	- `engine = create_engine(...)`
	- `SessionLocal = sessionmaker(...)`
	- `Base = declarative_base()`

### FastAPI DB Dependency

- `app/db/dependency.py` defines `get_db()` generator.
- Uses `try/finally` to guarantee session close.

### Metadata Bootstrap

- `app/db/base.py` imports model modules so SQLAlchemy metadata is fully registered.
- `app/db/init_db.py` exposes `init_db()` and runs `Base.metadata.create_all(bind=engine)`.

## SQLAlchemy Models

Implemented under `app/models/` with UUID PKs and PostgreSQL UUID columns.

### roles

- `id` UUID PK
- `name` VARCHAR(50), unique, not null

### permissions

- `id` UUID PK
- `name` VARCHAR(100), unique, not null

### role_permissions

- `role_id` UUID FK -> roles.id
- `permission_id` UUID FK -> permissions.id
- Composite PK (`role_id`, `permission_id`)

### employees

- `id` UUID PK
- `name` VARCHAR(100), not null
- `email` VARCHAR(255), unique, not null
- `phone` VARCHAR(15), unique, nullable
- `password_hash` TEXT, not null
- `role_id` UUID FK -> roles.id
- `status` VARCHAR(20), default active
- `created_at`, `updated_at` TIMESTAMP
- Check constraint: status in (active, inactive, suspended)

### categories

- `id` UUID PK
- `name` VARCHAR(50), unique, not null
- `created_at` TIMESTAMP

### transactions

- `id` UUID PK
- `employee_id` UUID FK -> employees.id
- `amount` NUMERIC(12,2), not null
- `type` VARCHAR(10), not null
- `category_id` UUID FK -> categories.id
- `transaction_date` TIMESTAMP, not null
- `note` TEXT
- `created_at`, `updated_at` TIMESTAMP
- Check constraint: type in (income, expense)

## Relationships

- Employee -> Role: many-to-one (`Employee.role`, `Role.employees`)
- Role <-> Permission: many-to-many via `role_permissions`
	- `Role.role_permissions` / `Permission.role_permissions`
	- `Role.permissions` / `Permission.roles` (secondary relation)
- Employee -> Transactions: one-to-many (`Employee.transactions`, `Transaction.employee`)
- Transaction -> Category: many-to-one (`Transaction.category`, `Category.transactions`)

All relationships use `back_populates` for bidirectional mapping.

## Pydantic Schemas (v2)

Implemented under `app/schemas/` using `ConfigDict(from_attributes=True)` for response models.

### Auth

- `LoginRequest`
- `TokenResponse`

### Role

- `RoleCreate`
- `RoleUpdate`
- `RoleResponse`

### Permission

- `PermissionCreate`
- `PermissionUpdate`
- `PermissionResponse`

### RolePermission

- `RolePermissionCreate`
- `RolePermissionResponse`

### Category

- `CategoryCreate`
- `CategoryUpdate`
- `CategoryResponse`

### Employee

- `EmployeeCreate`
- `EmployeeUpdate`
- `EmployeeResponse`

Notes:

- `EmployeeCreate` accepts `password` (plain text input).
- `EmployeeResponse` never exposes `password_hash`.
- Includes nested role summary (`id`, `name`) in responses.

### Transaction

- `TransactionCreate`
- `TransactionUpdate`
- `TransactionResponse`

Notes:

- `amount` uses decimal validation (`max_digits=12`, `decimal_places=2`).
- Includes nested employee and category summaries in response.

## Security Utilities

- `app/utils/common.py`:
	- `hash_password(plain_password: str) -> str`
	- `verify_password(plain_password: str, hashed_password: str) -> bool`
- `app/core/security.py` re-exports these helpers.

## How to Initialize DB Tables

```python
from app.db.init_db import init_db

init_db()
```

This creates all SQLAlchemy tables registered on `Base.metadata`.

## Notes

- This layer intentionally contains data modeling, schema validation, and DB utilities only.
- Service/business logic and route handlers can be built on top of this foundation.
