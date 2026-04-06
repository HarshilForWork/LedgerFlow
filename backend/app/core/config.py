from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	environment: str = Field("development", alias="ENVIRONMENT")
	debug: bool = Field(False, alias="DEBUG")
	log_level: str = Field("INFO", alias="LOG_LEVEL")
	response_envelope_default: bool = Field(False, alias="RESPONSE_ENVELOPE_DEFAULT")
	database_url: str = Field(..., alias="DATABASE_URL")
	jwt_secret_key: str = Field(
		"change-this-secret-in-production",
		alias="JWT_SECRET_KEY",
	)
	jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
	jwt_expire_minutes: int = Field(30, alias="JWT_EXPIRE_MINUTES")

	@field_validator("environment")
	@classmethod
	def validate_environment(cls, value: str) -> str:
		return value.strip().lower()

	@field_validator("log_level")
	@classmethod
	def validate_log_level(cls, value: str) -> str:
		allowed_levels = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
		normalized = value.strip().upper()
		if normalized not in allowed_levels:
			raise ValueError("LOG_LEVEL must be one of CRITICAL, ERROR, WARNING, INFO, DEBUG.")
		return normalized

	@model_validator(mode="after")
	def validate_security_defaults(self):
		if self.jwt_expire_minutes <= 0:
			raise ValueError("JWT_EXPIRE_MINUTES must be greater than 0.")

		if (
			self.environment == "production"
			and self.jwt_secret_key == "change-this-secret-in-production"
		):
			raise ValueError("Set a strong JWT_SECRET_KEY in production.")

		return self

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		extra="ignore",
	)


@lru_cache
def get_settings() -> Settings:
	return Settings()

