from rest_framework import serializers

from .models import Package


class PackageSerializer(serializers.ModelSerializer):
    usage_count = serializers.IntegerField()

    def transform_usage_count(self, obj, value):
        return obj.usage_count

    class Meta:
        model = Package
        fields = ('id',
                  'slug',
                  'title',
                  'description',
                  'usage_count')
