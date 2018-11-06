import django.contrib.auth.password_validation as password_validators
from django.contrib.auth.models import User
from django.core.validators import ValidationError
from rest_framework import serializers

from .models import Profile


class VerificationSerializer(serializers.Serializer):
    """
    The user verification token serializer
    """
    profile = serializers.CharField(max_length=200, min_length=50)

    def validate(self, data):
        profile = Profile.objects.get_by_code(data['profile'])
        if not profile:
            raise serializers.ValidationError('Invalid verification token')
        data['profile'] = profile
        return data


class PasswordSerializer(serializers.Serializer):
    """
    The user password serializer
    """
    password = serializers.CharField(max_length=40, min_length=8)
    password_two = serializers.CharField(max_length=40, min_length=8)

    def validate(self, data):
        try:
            password_validators.validate_password(
                password=data['password'], user=User)
        except ValidationError as error:
            raise serializers.ValidationError({'password': error.messages})
        if data['password'] != data['password_two']:
            raise serializers.ValidationError('Passwords don\'t match.')
        return data


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

    def validate(self, data):
        super().validate(data)
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
        return data

    class Meta:
        model = User
        fields = ('email', 'profile', 'password_new')
