"""
The users app views module
"""
from django.contrib.auth.models import User
from django.core.validators import ValidationError
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .jwt import get_user_token
from .managers import ProfileManager
from .serializers import (PasswordSerializer, UserSerializer,
                          VerificationSerializer)


class UsersViewSet(viewsets.GenericViewSet):
    """
    The user model viewset
    """

    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['register', 'verification']:
            return (AllowAny(), )
        return super().get_permissions()

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    @action(detail=False, methods=['get'])
    def get(self, request):
        """
        Get an user data
        """
        user = User.objects.get(pk=self.request.user.pk)
        serializer = self.get_serializer(user)

        return Response(serializer.data)

    @staticmethod
    @action(detail=False, methods=['post'])
    def verification(request):
        """
        Users email verification
        """
        serializer = VerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        profile = data['profile']
        profile.verification_code = None
        profile.is_verified = True
        profile.save()

        return Response({'status': True}, status=status.HTTP_200_OK)

    @staticmethod
    @action(detail=False, methods=['patch'])
    def password(request):
        """
        Change the current user password
        """
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user
        user.set_password(data['password'])
        user.save()

        return Response({'status': True}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Register a new user
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        email = data['email']
        password = data['password_new']
        language = data['language']

        try:
            user = ProfileManager.create_user(email, password, language)
        except ValidationError as error:
            raise serializers.ValidationError(error.message_dict)

        tokens = get_user_token(user)

        return Response(
            {
                'status': True,
                'token': tokens['access'],
                'refresh': tokens['refresh']
            },
            status=status.HTTP_201_CREATED,
        )
