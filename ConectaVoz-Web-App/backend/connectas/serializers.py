from rest_framework import serializers
from django.utils import timezone
from .models import Connecta, ConnectaPreference, ConnectaHomologation
from users.serializers import UserBasicSerializer

class ConnectaSerializer(serializers.ModelSerializer):
    """
    Serializer para Conectas
    """
    user_details = UserBasicSerializer(source='user', read_only=True)
    
    class Meta:
        model = Connecta
        fields = [
            'id', 'user', 'user_details', 'active', 'mandate_start', 'mandate_end',
            'capacity_max', 'assigned_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'assigned_count']
    
    def validate_capacity_max(self, value):
        if value < 1 or value > 50:
            raise serializers.ValidationError("Capacidade deve estar entre 1 e 50.")
        return value


class ConnectaPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer para preferências de Conecta
    """
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    preferred_connecta_name = serializers.CharField(source='preferred_connecta.get_full_name', read_only=True)
    can_change = serializers.SerializerMethodField()
    days_until_change = serializers.SerializerMethodField()
    
    class Meta:
        model = ConnectaPreference
        fields = [
            'id', 'employee', 'employee_name', 'preferred_connecta', 
            'preferred_connecta_name', 'chosen_at', 'next_change_at',
            'effective', 'vote_count', 'can_change', 'days_until_change'
        ]
        read_only_fields = [
            'id', 'chosen_at', 'next_change_at', 'effective', 'vote_count',
            'employee_name', 'preferred_connecta_name'
        ]
    
    def get_can_change(self, obj):
        return obj.can_change()
    
    def get_days_until_change(self, obj):
        if obj.can_change():
            return 0
        
        delta = obj.next_change_at - timezone.now()
        return max(0, delta.days)


class ConnectaHomologationSerializer(serializers.ModelSerializer):
    """
    Serializer para homologações de Conecta
    """
    homologated_by_name = serializers.CharField(source='homologated_by.get_full_name', read_only=True)
    
    class Meta:
        model = ConnectaHomologation
        fields = [
            'id', 'homologated_at', 'homologated_by', 'homologated_by_name',
            'total_preferences', 'approved_connectas', 'rejected_preferences',
            'notes'
        ]
        read_only_fields = ['id', 'homologated_at', 'homologated_by_name']


class ConnectaChoiceSerializer(serializers.Serializer):
    """
    Serializer para escolha de Conecta
    """
    preferred_connecta_id = serializers.IntegerField()
    
    def validate_preferred_connecta_id(self, value):
        from users.models import User
        
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado.")
        
        # Verificar se pode ser Conecta (mesmo departamento/equipe)
        request_user = self.context['request'].user
        
        if request_user.team and user.team != request_user.team:
            raise serializers.ValidationError(
                "Só é possível escolher Conectas da mesma equipe."
            )
        elif request_user.department and user.department != request_user.department:
            raise serializers.ValidationError(
                "Só é possível escolher Conectas do mesmo departamento."
            )
        
        return value


class AvailableConnectaSerializer(serializers.Serializer):
    """
    Serializer para Conectas disponíveis
    """
    id = serializers.IntegerField()
    name = serializers.CharField()
    username = serializers.CharField()
    department = serializers.CharField(allow_null=True)
    team = serializers.CharField(allow_null=True)
    capacity_used = serializers.CharField()
    available = serializers.BooleanField()


class ConnectaScopeSerializer(serializers.Serializer):
    """
    Serializer para escopo do Conecta
    """
    assigned_employees = serializers.ListField(
        child=serializers.DictField()
    )
    total_assigned = serializers.IntegerField()
    voice_stats = serializers.ListField(
        child=serializers.DictField()
    )
    capacity = serializers.DictField()


class VoteCountSerializer(serializers.Serializer):
    """
    Serializer para contagem de votos
    """
    preferred_connecta = serializers.IntegerField()
    preferred_connecta_name = serializers.CharField()
    votes = serializers.IntegerField()
    eligible = serializers.BooleanField()
    
    def to_representation(self, instance):
        from users.models import User
        
        data = super().to_representation(instance)
        
        # Adicionar nome do Conecta
        try:
            user = User.objects.get(id=data['preferred_connecta'])
            data['preferred_connecta_name'] = user.get_full_name()
        except User.DoesNotExist:
            data['preferred_connecta_name'] = 'Usuário não encontrado'
        
        # Verificar elegibilidade (≥2 votos)
        from django.conf import settings
        min_votes = getattr(settings, 'CONNECTA_MIN_VOTES', 2)
        data['eligible'] = data['votes'] >= min_votes
        
        return data
