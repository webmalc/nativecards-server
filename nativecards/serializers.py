"""
The nativecards serializers module
"""
from rest_framework import serializers

from .models import Settings


class SettingsSerializer(serializers.HyperlinkedModelSerializer):
    """
    The settings class serializer
    """

    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Settings
        fields = ('id', 'attempts_to_remember', 'cards_per_lesson',
                  'cards_to_repeat', 'lesson_latest_days', 'lessons_per_day',
                  'attempts_per_day', 'play_audio_on_open', 'created',
                  'modified', 'created_by', 'modified_by')
