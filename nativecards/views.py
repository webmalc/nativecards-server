from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from nativecards.viewsets import UserViewSetMixin

from .models import Settings
from .serializers import SettingsSerializer


class SettingsViewSet(viewsets.GenericViewSet, UserViewSetMixin):

    serializer_class = SettingsSerializer

    def get_queryset(self):
        return self.filter_by_user(Settings.objects.all())

    @action(detail=False, methods=['get'])
    @cache_response()
    def get(self, request):
        settings = Settings.objects.get_by_user(request.user)
        serializer = self.get_serializer(settings)

        return Response(serializer.data)

    @action(detail=False, methods=['PATCH'])
    def save(self, request):
        settings = Settings.objects.get_by_user(request.user)
        serializer = self.get_serializer(
            settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
