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
    deck = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=False,
        required=False,
        queryset=Deck.objects.all())

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        return self.fiter_field(fields, 'deck', Deck)

    class Meta:
        model = Card
        fields = ('id', 'word', 'definition', 'examples', 'translation',
                  'pronunciation', 'complete', 'priority', 'deck', 'image',
                  'remote_image', 'is_enabled', 'last_showed_at', 'created',
                  'modified', 'created_by', 'modified_by')


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
