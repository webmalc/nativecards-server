from rest_framework import serializers

from .models import Card, Deck


class DeckSerializer(serializers.HyperlinkedModelSerializer):
    """
    The deck serializer
    """

    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Deck
        fields = ('id', 'title', 'description', 'is_default', 'is_enabled',
                  'remote_image', 'image', 'created', 'modified', 'created_by',
                  'modified_by')


class CardSerializer(serializers.HyperlinkedModelSerializer):
    """
    The card serializer
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
        fields['deck'].queryset = Deck.objects.filter(
            created_by=self.context['request'].user)
        return fields

    class Meta:
        model = Card
        fields = ('id', 'word', 'definition', 'examples', 'translation',
                  'pronunciation', 'complete', 'priority', 'deck', 'image',
                  'remote_image', 'is_enabled', 'last_showed_at', 'created',
                  'modified', 'created_by', 'modified_by')
