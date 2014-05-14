from rest_framework import serializers

from .models import Link


class LinkSerializer(serializers.HyperlinkedModelSerializer):
    dataset = serializers.RelatedField(many=False)
    format = serializers.RelatedField(many=False)
    link = serializers.URLField(source='get_fully_qualified_url')

    class Meta:
        model = Link
        fields = ('dataset', 'title', 'link', 'format', 'notes')
