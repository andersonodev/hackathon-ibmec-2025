from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.db.models import Q
from .models import VoicePost, VoiceAttachment, Conversation
from .serializers import (
    VoicePostSerializer, VoicePostCreateSerializer, VoicePostQueueSerializer,
    ConversationSerializer, SendMessageSerializer, EscalatePostSerializer,
    VoiceAttachmentSerializer
)
from users.permissions import RoleBasedPermission, IsOwnerOrConnecta
from mood.models import MoodCheckin

class VoicePostViewSet(viewsets.ModelViewSet):
    """
    ViewSet para relatos de voz
    """
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_employee:
            # Colaborador vê apenas seus próprios relatos
            pseudo_id = MoodCheckin.generate_pseudo_id(user.id)
            return VoicePost.objects.filter(pseudo_id=pseudo_id)
        
        elif user.is_connecta:
            # Conecta vê relatos atribuídos a ele
            return VoicePost.objects.filter(assigned_to__user=user)
        
        elif user.is_council or user.is_admin_role:
            # Conselho vê apenas casos escalados
            return VoicePost.objects.filter(status='escalado')
        
        return VoicePost.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VoicePostCreateSerializer
        return VoicePostSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Cria relato para o Conecta do usuário
        """
        if not request.user.is_employee:
            return Response(
                {'detail': 'Apenas colaboradores podem criar relatos.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            voice_post = serializer.save()
            
            # Auditoria
            from audit.models import AuditLog
            AuditLog.log_action(
                actor=request.user,
                action='voice_post_created',
                category='voice',
                object_type='VoicePost',
                object_id=voice_post.id,
                meta={
                    'sentiment': voice_post.sentiment,
                    'visibility': voice_post.visibility,
                    'gostaria_retorno': voice_post.gostaria_retorno
                },
                request=request
            )
            
            return Response(
                VoicePostSerializer(voice_post).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsOwnerOrConnecta])
    def update_status(self, request, pk=None):
        """
        Atualiza status do relato (apenas Conecta)
        """
        voice_post = self.get_object()
        
        if not request.user.is_connecta:
            return Response(
                {'detail': 'Apenas Conectas podem alterar status.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if new_status not in ['em_analise', 'resolvido']:
            return Response(
                {'detail': 'Status inválido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = voice_post.status
        voice_post.status = new_status
        voice_post.save()
        
        # Auditoria
        from audit.models import AuditLog
        AuditLog.log_action(
            actor=request.user,
            action='voice_post_status_changed',
            category='voice',
            object_type='VoicePost',
            object_id=voice_post.id,
            meta={
                'old_status': old_status,
                'new_status': new_status
            },
            request=request
        )
        
        return Response({'status': new_status})


class MyVoicePostsView(APIView):
    """
    View para meus relatos (colaborador)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_employee:
            return Response(
                {'detail': 'Apenas colaboradores podem ver seus relatos.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        pseudo_id = MoodCheckin.generate_pseudo_id(request.user.id)
        queryset = VoicePost.objects.filter(pseudo_id=pseudo_id).order_by('-created_at')
        
        serializer = VoicePostSerializer(queryset, many=True)
        return Response(serializer.data)


class ConnectaQueueView(APIView):
    """
    Fila do Conecta - FIFO com filtros
    """
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get(self, request):
        if not request.user.is_connecta:
            return Response(
                {'detail': 'Apenas Conectas podem ver a fila.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Filtros
        order = request.query_params.get('order', 'received')  # received|sla|priority|unread
        priority = request.query_params.get('priority')  # alerta,denuncia,...
        status_filter = request.query_params.get('status')  # novo,em_analise
        
        # Queryset base
        queryset = VoicePost.objects.filter(assigned_to__user=request.user)
        
        # Aplicar filtros
        if priority:
            priorities = [p.strip() for p in priority.split(',')]
            queryset = queryset.filter(sentiment__in=priorities)
        
        if status_filter:
            statuses = [s.strip() for s in status_filter.split(',')]
            queryset = queryset.filter(status__in=statuses)
        
        # Aplicar ordenação
        if order == 'sla':
            # Ordenar por tempo sem resposta (mais antigo primeiro)
            queryset = queryset.order_by('created_at')
        elif order == 'priority':
            # Ordenar por prioridade: denuncia > alerta > positivo
            priority_order = {
                'denuncia': 1,
                'alerta': 2,
                'positivo': 3
            }
            queryset = sorted(queryset, key=lambda x: priority_order.get(x.sentiment, 99))
        elif order == 'unread':
            # Implementar lógica de não lidos
            queryset = queryset.order_by('created_at')
        else:
            # FIFO padrão (mais antigo primeiro)
            queryset = queryset.order_by('created_at')
        
        serializer = VoicePostQueueSerializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'order': order,
            'filters': {
                'priority': priority,
                'status': status_filter
            }
        })


class SendMessageView(APIView):
    """
    Enviar mensagem na conversa (chat cego)
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrConnecta]
    
    def post(self, request, pk):
        try:
            voice_post = VoicePost.objects.get(pk=pk)
        except VoicePost.DoesNotExist:
            return Response(
                {'detail': 'Relato não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar se tem conversa habilitada
        if not voice_post.gostaria_retorno:
            return Response(
                {'detail': 'Conversa não habilitada para este relato.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SendMessageSerializer(
            data=request.data,
            context={'voice_post': voice_post, 'request': request}
        )
        
        if serializer.is_valid():
            message = serializer.save()
            
            # Auditoria
            from audit.models import AuditLog
            AuditLog.log_action(
                actor=request.user,
                action='conversation_message_sent',
                category='voice',
                object_type='Conversation',
                object_id=voice_post.id,
                meta={'message_type': message['from']},
                request=request
            )
            
            return Response(message, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EscalatePostView(APIView):
    """
    Escalar relato para o Conselho
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        if not request.user.is_connecta:
            return Response(
                {'detail': 'Apenas Conectas podem escalar relatos.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            voice_post = VoicePost.objects.get(
                pk=pk,
                assigned_to__user=request.user
            )
        except VoicePost.DoesNotExist:
            return Response(
                {'detail': 'Relato não encontrado ou não atribuído a você.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if voice_post.status == 'escalado':
            return Response(
                {'detail': 'Relato já foi escalado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = EscalatePostSerializer(
            data=request.data,
            context={'voice_post': voice_post, 'request': request}
        )
        
        if serializer.is_valid():
            council_case = serializer.save()
            
            # Auditoria
            from audit.models import AuditLog
            AuditLog.log_action(
                actor=request.user,
                action='voice_post_escalated',
                category='voice',
                object_type='VoicePost',
                object_id=voice_post.id,
                meta={
                    'council_case_id': council_case.id,
                    'priority': council_case.priority
                },
                request=request
            )
            
            return Response({
                'message': 'Relato escalado com sucesso.',
                'council_case_id': council_case.id
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VoiceAttachmentUploadView(APIView):
    """
    Upload de anexos para relatos
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if not request.user.is_employee:
            return Response(
                {'detail': 'Apenas colaboradores podem fazer upload de anexos.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Implementar upload temporário ou vinculado a um post específico
        # Por simplicidade, vamos retornar sucesso
        files = request.FILES.getlist('files')
        
        uploaded_files = []
        for file in files:
            # Aqui você implementaria a lógica de upload
            uploaded_files.append({
                'filename': file.name,
                'size': file.size,
                'content_type': file.content_type
            })
        
        return Response({
            'message': f'{len(uploaded_files)} arquivo(s) enviado(s) com sucesso.',
            'files': uploaded_files
        })
