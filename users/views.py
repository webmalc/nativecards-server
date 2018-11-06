from time import time_ns

from django.contrib.auth.models import User
from django.core.validators import ValidationError
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from nativecards.lib.messengers import mailer

from .serializers import (PasswordSerializer, UserSerializer,
                          VerificationSerializer)


class UsersViewSet(viewsets.GenericViewSet):

    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['register', 'verification']:
            return (AllowAny(), )
        else:
            return super().get_permissions()

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    @action(detail=False, methods=['get'])
    def get(self, request):
        user = User.objects.get(pk=self.request.user.pk)
        serializer = self.get_serializer(user)

        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def verification(self, request):
        serializer = VerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        profile = data['profile']
        profile.verification_code = None
        profile.is_verified = True
        profile.save()

        return Response({'status': True}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'])
    def password(self, request):
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user
        user.set_password(data['password'])
        user.save()

        return Response({'status': True}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        email = data['email']
        password = data['password_new']

        user = User()
        user.username = email
        user.email = email
        user.set_password(password)
        try:
            user.full_clean()
            user.save()
            code = User.objects.make_random_password(60) + str(time_ns())
            user.profile.verification_code = code
            user.profile.is_verified = False
            user.profile.save()

        except ValidationError as error:
            raise serializers.ValidationError(error)

        mailer.mail_user(
            subject='Welcome to Nativecards',
            template='emails/registration.html',
            data={
                'url': code,
                'username': user.username
            },
            user=user)

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        return Response(
            {
                'status': True,
                'token': token
            }, status=status.HTTP_201_CREATED)
