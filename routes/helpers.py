from flask_jwt_extended import get_jwt_identity


def get_user_id():
    """
    Returns the current JWT identity as an integer when possible.
    """
    identity = get_jwt_identity()
    if identity is None:
        return None
    try:
        return int(identity)
    except (TypeError, ValueError):
        return identity

