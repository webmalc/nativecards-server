import django.contrib.auth.password_validation as password_validators
from django.contrib.auth.models import User
from django.core.validators import ValidationError
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from nativecards.lib.messengers import mailer

from .serializers import UserSerializer


class UsersViewSet(viewsets.GenericViewSet):

    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    @action(detail=False, methods=['get'])
    def get(self, request):
        user = User.objects.get(pk=self.request.user.pk)
        serializer = self.get_serializer(user)

        return Response(serializer.data)

    # TODO: Add endpoints for changing password and account verification
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    @action(detail=False, methods=['post'])
    @permission_classes([])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        email = data['email']
        password = data['password_new']
        if User.objects.filter(email=email).count():
            raise serializers.ValidationError([{
                'email': ['A user with that email already exists.']
            }])
        try:
            password_validators.validate_password(password=password, user=User)
        except ValidationError as error:
            raise serializers.ValidationError({'password': error.messages})

        user = User()
        user.username = email
        user.email = email
        user.set_password(password)
        try:
            user.full_clean()
            user.save()
            code = User.objects.make_random_password(100)
            user.profile.verification_code = code
            user.profile.is_verified = False
            user.profile.save()

            # TODO: Add a default deck !!!!!!!!!!!!!!!!!!!!
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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
