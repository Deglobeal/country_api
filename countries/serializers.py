from rest_framework import serializers
from .models import Country

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            'id', 'name', 'capital', 'region', 'population',
            'currency_code', 'exchange_rate', 'estimated_gdp',
            'flag_url', 'last_refreshed_at'
        ]
        read_only_fields = ['id', 'last_refreshed_at']

class StatusSerializer(serializers.Serializer):
    total_countries = serializers.IntegerField()
    last_refreshed_at = serializers.DateTimeField(required=False, allow_null=True)
    
    def create(self, validated_data):
        pass
    
    def update(self, instance, validated_data):
        pass

class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()
    details = serializers.DictField(required=False)