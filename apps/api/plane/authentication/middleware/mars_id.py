import logging

from django.contrib.auth import login
from django.utils.deprecation import MiddlewareMixin

from plane.authentication.provider.credentials.mars_id import (
    MarsIdProvider,
    MARS_ID_SECRET,
)
from plane.authentication.adapter.error import AuthenticationException
from plane.authentication.utils.user_auth_workflow import post_user_auth_workflow
from plane.db.models import Profile

logger = logging.getLogger("plane.authentication")

MARS_ID_COOKIE = "__mars_id"


class MarsIdAutoLoginMiddleware(MiddlewareMixin):
    """Auto-login users who have a valid __mars_id JWT cookie but no Plane session."""

    def process_request(self, request):
        if not MARS_ID_SECRET:
            return

        # Skip if user already authenticated
        if hasattr(request, "user") and request.user.is_authenticated:
            return

        # Skip if already has a valid session
        if hasattr(request, "session") and request.session.session_key:
            user_id = request.session.get("_auth_user_id")
            if user_id:
                return

        # Check for Mars ID cookie
        token = request.COOKIES.get(MARS_ID_COOKIE)
        if not token:
            return

        # Skip static/health endpoints
        path = request.path
        if path.startswith(("/static/", "/health/", "/favicon")):
            return

        try:
            provider = MarsIdProvider(
                request=request,
                token=token,
                callback=post_user_auth_workflow,
            )
            user = provider.authenticate()

            # Ensure profile exists
            Profile.objects.get_or_create(user=user)

            # Login via Django auth
            login(request=request, user=user)
            request.session.save()

            logger.info(f"Mars ID auto-login: {user.email}")
        except AuthenticationException as e:
            logger.debug(f"Mars ID auto-login failed: {e.error_message}")
        except Exception as e:
            logger.warning(f"Mars ID auto-login error: {e}")
