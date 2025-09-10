from rest_framework import serializers
from .models import MuralPost, MuralComment, MuralReaction

class MuralPostSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para posts do mural
    """
    class Meta:
        model = MuralPost
        fields = [
            'id', 'text', 'team', 'anonymous', 'emoji',
            'status', 'created_at', 'reactions'
        ]
        read_only_fields = ['created_at']

class MuralCommentSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para comentários do mural
    """
    class Meta:
        model = MuralComment
        fields = ['id', 'post', 'content', 'status', 'created_at']
        read_only_fields = ['created_at']

class MuralReactionSerializer(serializers.ModelSerializer):
    """
    Serializer para reações do mural
    """
    class Meta:
        model = MuralReaction
        fields = ['id', 'post', 'user', 'reaction_type', 'created_at']
        read_only_fields = ['user', 'created_at']
