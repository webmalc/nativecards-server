from django.contrib.auth.middleware import get_user
from django.db.models import signals
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject, curry
from django.utils.translation import activate
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class AuthenticationMiddlewareJWT(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = SimpleLazyObject(
            lambda: self.__class__.get_jwt_user(request))
        return self.get_response(request)

    @staticmethod
    def get_jwt_user(request):
        user = get_user(request)
        if user.is_authenticated:
            return user
        jwt_authentication = JSONWebTokenAuthentication()
        if jwt_authentication.get_jwt_value(request):
            user, jwt = jwt_authentication.authenticate(request)
        return user


class DisableAdminI18nMiddleware(MiddlewareMixin):
    """
    Disable the translation in the admin interface
    """

    def process_request(self, request):
        resolver_match = resolve(request.path)
        if resolver_match.app_name == 'admin':
            activate('en')


class WhodidMiddleware(MiddlewareMixin):
    """
    Fill the created_by and updated_by fields
    """

    def process_request(self, request):
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
            else:
                user = None

            mark_whodid = curry(self.mark_whodid, user)
            signals.pre_save.connect(
                mark_whodid,
                dispatch_uid=(
                    self.__class__,
                    request,
                ),
                weak=False)

    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid=(
            self.__class__,
            request,
        ))
        return response

    def mark_whodid(self, user, sender, instance, **kwargs):
        if hasattr(instance, 'created_by_id') and not getattr(
                instance, 'created_by_id', None):
            instance.created_by = user
        if hasattr(instance, 'modified_by_id'):
            instance.modified_by = user
