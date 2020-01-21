"""
The users serializers module
"""
import django.contrib.auth.password_validation as password_validators
from django.contrib.auth.models import User
from django.core.validators import ValidationError
from rest_framework import serializers

from .models import Profile


class VerificationSerializer(serializers.Serializer):
    """
    The user verification token serializer
    """

    # pylint: disable=abstract-method

    profile = serializers.CharField(max_length=200, min_length=50)

    def validate(self, attrs):
        profile = Profile.objects.get_by_code(attrs['profile'])
        if not profile:
            raise serializers.ValidationError('Invalid verification token')
        attrs['profile'] = profile
        return attrs


class PasswordSerializer(serializers.Serializer):
    """
    The user password serializer
    """

    # pylint: disable=abstract-method

    password = serializers.CharField(max_length=40, min_length=8)
    password_two = serializers.CharField(max_length=40, min_length=8)

    def validate(self, attrs):
        """
        Validate a password
        """
        try:
            password_validators.validate_password(password=attrs['password'],
                                                  user=User)
        except ValidationError as error:
            raise serializers.ValidationError({'password': error.messages})
        if attrs['password'] != attrs['password_two']:
            raise serializers.ValidationError('Passwords don\'t match.')
        return attrs


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    """
    The user profile class serializer
    """
    class Meta:
        model = Profile
        fields = ('is_verified', )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    The user class serializer
    """

    profile = ProfileSerializer(read_only=True)
    password_new = serializers.CharField(required=False)
    language = serializers.CharField(required=True, write_only=True)

    @staticmethod
    def _validate_email(email: str) -> None:
        """
        Validate an email
        """
        if User.objects.filter(email=email).count():
            raise serializers.ValidationError([{
                'email': ['A user with that email already exists.']
            }])

    @staticmethod
    def _validate_password(password: str) -> None:
        """
        Validate a password
        """
        try:
            password_validators.validate_password(password=password, user=User)
        except ValidationError as error:
            raise serializers.ValidationError({'password': error.messages})

    def validate(self, attrs):
        """
        Validate an user
        """
        super().validate(attrs)
        self._validate_email(attrs['email'])
        self._validate_password(attrs['password_new'])

        return attrs

    class Meta:
        model = User
        fields = ('email', 'profile', 'password_new', 'language')
