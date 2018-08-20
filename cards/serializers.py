from rest_framework import serializers

from .models import Deck


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
