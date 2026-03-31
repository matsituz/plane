from django.http import HttpResponseRedirect
from django.views import View

from plane.authentication.provider.credentials.mars_id import MarsIdProvider
from plane.authentication.utils.login import user_login
from plane.authentication.utils.host import base_host
from plane.authentication.utils.redirection_path import get_redirection_path
from plane.authentication.utils.user_auth_workflow import post_user_auth_workflow
from plane.authentication.adapter.error import (
    AuthenticationException,
    AUTHENTICATION_ERROR_CODES,
)
from plane.license.models import Instance
from plane.utils.path_validator import get_safe_redirect_url


MARS_ID_COOKIE = "__mars_id"


class MarsIdAuthEndpoint(View):
    """Explicit Mars ID login endpoint. Reads __mars_id cookie and creates a Plane session."""

    def get(self, request):
        next_path = request.GET.get("next_path", "")

        instance = Instance.objects.first()
        if instance is None or not instance.is_setup_done:
            exc = AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["INSTANCE_NOT_CONFIGURED"],
                error_message="INSTANCE_NOT_CONFIGURED",
            )
            params = exc.get_error_dict()
            url = get_safe_redirect_url(
                base_url=base_host(request=request, is_app=True),
                next_path=next_path,
                params=params,
            )
            return HttpResponseRedirect(url)

        token = request.COOKIES.get(MARS_ID_COOKIE)
        if not token:
            # No Mars ID cookie — redirect to Mars ID login
            mars_id_url = "https://id.marshub.uz/login"
            redirect_back = request.build_absolute_uri()
            return HttpResponseRedirect(f"{mars_id_url}?redirect={redirect_back}")

        try:
            provider = MarsIdProvider(
                request=request,
                token=token,
                callback=post_user_auth_workflow,
            )
            user = provider.authenticate()
            user_login(request=request, user=user, is_app=True)

            if next_path:
                path = next_path
            else:
                path = get_redirection_path(user=user)

            url = get_safe_redirect_url(
                base_url=base_host(request=request, is_app=True),
                next_path=path,
                params={},
            )
            return HttpResponseRedirect(url)
        except AuthenticationException as e:
            params = e.get_error_dict()
            url = get_safe_redirect_url(
                base_url=base_host(request=request, is_app=True),
                next_path=next_path,
                params=params,
            )
            return HttpResponseRedirect(url)
