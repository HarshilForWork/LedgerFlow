class Permissions:
	CREATE_TRANSACTION = "create_transaction"
	VIEW_TRANSACTION = "view_transaction"
	UPDATE_TRANSACTION = "update_transaction"
	DELETE_TRANSACTION = "delete_transaction"
	VIEW_DASHBOARD = "view_dashboard"
	VIEW_USERS = "view_users"
	CREATE_USER = "create_user"
	UPDATE_USER_ROLE = "update_user_role"
	UPDATE_USER_STATUS = "update_user_status"
	MANAGE_USERS = "manage_users"


VIEWER_ROLE_NAME = "viewer"


__all__ = ["Permissions", "VIEWER_ROLE_NAME"]

