from rest_framework import serializers
from .models import MoodCheckin, PseudonymSalt

class MoodCheckinSerializer(serializers.ModelSerializer):
    """
    Serializer para check-ins de humor
    """
    class Meta:
        model = MoodCheckin
        fields = ['id', 'created_at', 'day', 'score', 'comment', 'tags']
        read_only_fields = ['id', 'created_at', 'day']
    
    def validate_score(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Score deve estar entre 1 e 5.")
        return value
    
    def validate_tags(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Tags deve ser uma lista.")
        return value


class MoodCheckinCreateSerializer(serializers.Serializer):
    """
    Serializer para criação de check-in (sem pseudônimo exposto)
    """
    score = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )


class MoodSummarySerializer(serializers.Serializer):
    """
    Serializer para resumo de humor (respeitando k-anonimato)
    """
    collecting = serializers.BooleanField()
    collecting_progress = serializers.CharField()
    count = serializers.IntegerField()
    avg_score = serializers.FloatField(allow_null=True)
    clima_index = serializers.FloatField(allow_null=True)
    distribution = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Se ainda coletando, não expor métricas detalhadas
        if data['collecting']:
            return {
                'collecting': data['collecting'],
                'collecting_progress': data['collecting_progress'],
                'count': data['count'],
                'threshold': 5  # K_ANONYMITY_THRESHOLD
            }
        
        return data


class MyMoodHistorySerializer(serializers.Serializer):
    """
    Serializer para histórico pessoal de humor
    """
    weekly_avg = serializers.FloatField(allow_null=True)
    monthly_avg = serializers.FloatField(allow_null=True)
    total_checkins = serializers.IntegerField()
    daily_history = serializers.ListField(
        child=serializers.DictField()
    )


class PseudonymSaltSerializer(serializers.ModelSerializer):
    """
    Serializer para salts de pseudônimos (apenas admin)
    """
    class Meta:
        model = PseudonymSalt
        fields = ['id', 'label', 'created_at']
        # salt não é exposto por segurança
