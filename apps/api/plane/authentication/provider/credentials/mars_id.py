import os
import uuid

import jwt
from plane.authentication.adapter.credential import CredentialAdapter
from plane.authentication.adapter.error import (
    AUTHENTICATION_ERROR_CODES,
    AuthenticationException,
)
from plane.db.models import User


MARS_ID_SECRET = os.environ.get("MARS_ID_SECRET", "")


class MarsIdProvider(CredentialAdapter):
    """Authenticate users via Mars ID JWT cookie (__mars_id)."""

    provider = "mars_id"

    def __init__(self, request, token, callback=None):
        super().__init__(request=request, provider=self.provider, callback=callback)
        self.token = token

    def _decode_token(self):
        if not MARS_ID_SECRET:
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES.get(
                    "AUTHENTICATION_FAILED_SIGN_IN", 5020
                ),
                error_message="MARS_ID_SECRET not configured",
            )
        try:
            return jwt.decode(
                self.token, MARS_ID_SECRET, algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES.get(
                    "AUTHENTICATION_FAILED_SIGN_IN", 5020
                ),
                error_message="Mars ID token expired",
            )
        except jwt.InvalidTokenError:
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES.get(
                    "AUTHENTICATION_FAILED_SIGN_IN", 5020
                ),
                error_message="Invalid Mars ID token",
            )

    def set_user_data(self):
        payload = self._decode_token()

        email = payload.get("email")
        handle = payload.get("handle")
        name = payload.get("name", "")

        if not email and handle:
            email = f"{handle}@marshub.uz"

        if not email:
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES.get(
                    "AUTHENTICATION_FAILED_SIGN_IN", 5020
                ),
                error_message="Mars ID token missing email and handle",
            )

        # Split name into first/last
        parts = name.split(maxsplit=1) if name else []
        first_name = parts[0] if parts else ""
        last_name = parts[1] if len(parts) > 1 else ""

        super().set_user_data(
            {
                "email": email,
                "user": {
                    "avatar": "",
                    "first_name": first_name,
                    "last_name": last_name,
                    "provider_id": payload.get("sub", ""),
                    "is_password_autoset": True,
                },
            }
        )
