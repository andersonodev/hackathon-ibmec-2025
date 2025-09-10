from rest_framework import serializers
from django.utils import timezone
from .models import VoicePost, VoiceAttachment, Conversation
from users.serializers import UserBasicSerializer
from mood.models import MoodCheckin

class VoiceAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer para anexos de relatos
    """
    class Meta:
        model = VoiceAttachment
        fields = ['id', 'filename', 'file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class VoicePostSerializer(serializers.ModelSerializer):
    """
    Serializer para relatos de voz
    """
    attachments = VoiceAttachmentSerializer(many=True, read_only=True)
    author_display = serializers.CharField(source='get_author_display', read_only=True)
    assigned_to_name = serializers.CharField(
        source='assigned_to.user.get_full_name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = VoicePost
        fields = [
            'id', 'created_at', 'visibility', 'sentiment', 'text', 'tags',
            'gostaria_retorno', 'status', 'author_display', 'assigned_to_name',
            'attachments'
        ]
        read_only_fields = ['id', 'created_at', 'status', 'author_display', 'assigned_to_name']
    
    def validate_visibility(self, value):
        if value not in ['connecta_ident', 'connecta_anon']:
            raise serializers.ValidationError("Visibilidade inválida.")
        return value
    
    def validate_sentiment(self, value):
        if value not in ['positivo', 'alerta', 'denuncia']:
            raise serializers.ValidationError("Sentimento inválido.")
        return value


class VoicePostCreateSerializer(serializers.Serializer):
    """
    Serializer para criação de relatos
    """
    visibility = serializers.ChoiceField(
        choices=['connecta_ident', 'connecta_anon'],
        default='connecta_ident'
    )
    sentiment = serializers.ChoiceField(
        choices=['positivo', 'alerta', 'denuncia']
    )
    text = serializers.CharField()
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    gostaria_retorno = serializers.BooleanField(default=False)
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True
    )
    
    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        
        # Gerar pseudônimo
        pseudo_id = MoodCheckin.generate_pseudo_id(user.id)
        
        # Encontrar Conecta do usuário
        from connectas.models import ConnectaPreference, Connecta
        try:
            pref = ConnectaPreference.objects.get(
                employee=user,
                effective=True
            )
            connecta = Connecta.objects.get(
                user=pref.preferred_connecta,
                active=True
            )
        except (ConnectaPreference.DoesNotExist, Connecta.DoesNotExist):
            raise serializers.ValidationError(
                "Você não possui um Conecta atribuído. Contacte o administrador."
            )
        
        # Criar relato
        attachments_data = validated_data.pop('attachments', [])
        
        voice_post = VoicePost.objects.create(
            pseudo_id=pseudo_id,
            author=user if validated_data['visibility'] == 'connecta_ident' else None,
            assigned_to=connecta,
            **validated_data
        )
        
        # Processar anexos
        for attachment_file in attachments_data:
            VoiceAttachment.objects.create(
                post=voice_post,
                file=attachment_file,
                filename=attachment_file.name
            )
        
        return voice_post


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer para conversas
    """
    class Meta:
        model = Conversation
        fields = ['id', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SendMessageSerializer(serializers.Serializer):
    """
    Serializer para envio de mensagens na conversa
    """
    text = serializers.CharField()
    
    def create(self, validated_data):
        voice_post = self.context['voice_post']
        user = self.context['request'].user
        
        # Criar conversa se não existir
        conversation, created = Conversation.objects.get_or_create(
            post=voice_post
        )
        
        # Determinar tipo do remetente
        if user == voice_post.author or (
            voice_post.pseudo_id == MoodCheckin.generate_pseudo_id(user.id)
        ):
            sender_type = 'autor'
        elif hasattr(user, 'connecta') and voice_post.assigned_to == user.connecta:
            sender_type = 'connecta'
        else:
            raise serializers.ValidationError("Usuário não autorizado a enviar mensagem.")
        
        # Adicionar mensagem
        message = conversation.add_message(
            sender_type=sender_type,
            text=validated_data['text'],
            sender_user=user
        )
        
        return message


class VoicePostQueueSerializer(serializers.ModelSerializer):
    """
    Serializer para fila do Conecta (FIFO + filtros)
    """
    author_display = serializers.CharField(source='get_author_display', read_only=True)
    has_conversation = serializers.SerializerMethodField()
    unread_messages = serializers.SerializerMethodField()
    days_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = VoicePost
        fields = [
            'id', 'created_at', 'sentiment', 'text', 'gostaria_retorno',
            'status', 'author_display', 'has_conversation', 'unread_messages',
            'days_since_created'
        ]
    
    def get_has_conversation(self, obj):
        return hasattr(obj, 'conversation')
    
    def get_unread_messages(self, obj):
        # Implementar lógica de mensagens não lidas
        # Por simplicidade, retornar 0
        return 0
    
    def get_days_since_created(self, obj):
        delta = timezone.now() - obj.created_at
        return delta.days


class EscalatePostSerializer(serializers.Serializer):
    """
    Serializer para escalonamento de relatos
    """
    reason = serializers.CharField(help_text="Motivo do escalonamento")
    priority = serializers.ChoiceField(
        choices=['baixa', 'media', 'alta', 'critica'],
        default='media'
    )
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def create(self, validated_data):
        voice_post = self.context['voice_post']
        escalated_by = self.context['request'].user
        
        # Criar caso no conselho
        from council.models import CouncilCase
        
        council_case = CouncilCase.objects.create(
            source_post=voice_post,
            escalated_by=escalated_by,
            priority=validated_data['priority'],
            notes=validated_data.get('notes', '')
        )
        
        # Adicionar ação inicial
        council_case.add_action(
            escalated_by,
            'case_created',
            validated_data['reason']
        )
        
        # Atualizar status do post
        voice_post.status = 'escalado'
        voice_post.save()
        
        return council_case
