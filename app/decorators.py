from functools import wraps
from flask import abort
from flask_login import current_user
from app.main.models import Permission


# decorator to check whether user has permission
def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.check_access(permission):
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator


# check the admin permission
def admin_required(func):
    return permission_required(Permission.ADMIN)(func)