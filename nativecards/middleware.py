"""
The nativecards middleware module
"""
from django.db.models import signals
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import curry
from django.utils.translation import activate
from rest_framework_simplejwt import authentication


class DisableAdminI18nMiddleware(MiddlewareMixin):
    """
    Disable the translation in the admin interface
    """
    def process_request(self, request):
        """
        Sets the locale to en in the admin interface
        """
        # pylint: disable=unused-argument, no-self-use
        resolver_match = resolve(request.path)
        if resolver_match.app_name == 'admin':
            activate('en')


class WhodidMiddleware(MiddlewareMixin):
    """
    Fill the created_by and updated_by fields
    """
    def process_request(self, request):
        """
        Processes request
        """
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            jwt_user = authentication.JWTAuthentication().authenticate(request)
            if jwt_user:
                request.user = jwt_user[0]
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
            else:
                user = None

            mark_whodid = curry(self.mark_whodid, user)
            signals.pre_save.connect(
                mark_whodid,
                dispatch_uid=(self.__class__, request),
                weak=False,
            )

    def process_response(self, request, response):
        """
        Processes response
        """
        signals.pre_save.disconnect(dispatch_uid=(self.__class__, request))
        return response

    def mark_whodid(self, user, sender, instance, **kwargs):
        """
        Sets created and modified fields
        """
        # pylint: disable=unused-argument, no-self-use
        if hasattr(instance, 'created_by_id') and not getattr(
                instance, 'created_by_id', None):
            instance.created_by = user
        if hasattr(instance, 'modified_by_id'):
            instance.modified_by = user
