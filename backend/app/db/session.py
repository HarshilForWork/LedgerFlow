from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings


def _normalize_database_url(database_url: str) -> str:
	if database_url.startswith("postgresql+psycopg2://"):
		return database_url
	if database_url.startswith("postgresql://"):
		return database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
	if database_url.startswith("postgres://"):
		return database_url.replace("postgres://", "postgresql+psycopg2://", 1)
	return database_url


settings = get_settings()
DATABASE_URL = _normalize_database_url(settings.database_url)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

