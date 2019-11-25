from django.contrib.auth.models import User


def get_user_token(user: User) -> str:
    """
    Generate the user JWT token
    """
    # jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    # jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    # payload = jwt_payload_handler(user)
    # token = jwt_encode_handler(payload)

    # return token
