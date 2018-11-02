from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Profile


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

    class Meta:
        model = User
        fields = ('email', 'profile', 'password_new')
