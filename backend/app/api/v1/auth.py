from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.exceptions.custom_exceptions import unauthorized_exception
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import authenticate_user
from app.utils.jwt import create_access_token


router = APIRouter(prefix="/auth", tags=["auth"])
@router.post(
	"/login",
	response_model=TokenResponse,
	summary="Login",
	description="Authenticate user credentials and return a JWT access token.",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
	user = authenticate_user(db, payload.email, payload.password)
	if user is None:
		raise unauthorized_exception("Invalid email or password.")

	token = create_access_token(subject=str(user.id))
	return TokenResponse(access_token=token)

