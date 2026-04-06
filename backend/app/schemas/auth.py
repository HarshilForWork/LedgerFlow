from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
	email: EmailStr
	password: str = Field(..., min_length=8, max_length=128)

	model_config = {
		"json_schema_extra": {
			"example": {
				"email": "admin@ledgerflow.com",
				"password": "StrongPass123!",
			}
		}
	}


class TokenResponse(BaseModel):
	access_token: str
	token_type: str = "bearer"

	model_config = {
		"json_schema_extra": {
			"example": {
				"access_token": "<jwt-token>",
				"token_type": "bearer",
			}
		}
	}

