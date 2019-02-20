from rest_framework import serializers

from .models import Attempt, Card, Deck


class UserSerializerMixin():
    def fiter_field(self, fields, key, Model):
        fields[key].queryset = Model.objects.filter(
            created_by=self.context['request'].user)
        return fields


class DeckSerializer(serializers.HyperlinkedModelSerializer):
    """
    The deck class serializer
    """

    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Deck
        fields = ('id', 'title', 'description', 'is_default', 'is_enabled',
                  'remote_image', 'image', 'created', 'modified', 'created_by',
                  'modified_by')


class CardSerializer(serializers.HyperlinkedModelSerializer,
                     UserSerializerMixin):
    """
    The card class serializer
    """

    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)
    priority_display = serializers.CharField(
        source='get_priority_display', required=False)
    category_display = serializers.CharField(
        source='get_category_display', required=False)
    deck = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=False,
        required=True,
        queryset=Deck.objects.all())

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        return self.fiter_field(fields, 'deck', Deck)

    class Meta:
        model = Card
        fields = ('id', 'word', 'category', 'category_display', 'definition',
                  'examples', 'synonyms', 'antonyms', 'translation',
                  'transcription', 'pronunciation', 'complete', 'priority',
                  'priority_display', 'deck', 'note', 'image', 'remote_image',
                  'is_enabled', 'last_showed_at', 'created', 'modified',
                  'created_by', 'modified_by')


class LessonCardSerializer(CardSerializer):
    """
    The card serializer for the user lesson
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['form'] = serializers.CharField(read_only=True)
        self.fields['choices'] = serializers.ListField(
            child=serializers.CharField(),
            read_only=True,
        )

    class Meta(CardSerializer.Meta):
        pass


class AttemptSerializer(serializers.HyperlinkedModelSerializer,
                        UserSerializerMixin):
    """
    The attempt class serializer
    """
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)
    card = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=False,
        required=False,
        queryset=Card.objects.all())

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        return self.fiter_field(fields, 'card', Card)

    class Meta:
        model = Attempt
        fields = ('id', 'card', 'form', 'is_correct', 'is_hint', 'answer',
                  'score', 'created', 'modified', 'created_by', 'modified_by')
