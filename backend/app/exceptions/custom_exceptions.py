from fastapi import HTTPException, status


def unauthorized_exception(detail: str = "Could not validate credentials.") -> HTTPException:
	return HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail=detail,
		headers={"WWW-Authenticate": "Bearer"},
	)


def forbidden_exception(detail: str = "You do not have enough permissions.") -> HTTPException:
	return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def not_found_exception(resource_name: str = "Resource") -> HTTPException:
	return HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=f"{resource_name} not found.",
	)

