from functools import wraps
from flask_login import current_user


def finish_registration_required(f):
    """This handful decoration check for user registration status"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.registration_completed():
            response = {
                "status": "error",
                "message": "You did not finish your registration process. Please update your profile to continue!",
                "data": current_user.to_json()
            }
            return response, 403

        return f(*args, **kwargs)

    return decorated_function
