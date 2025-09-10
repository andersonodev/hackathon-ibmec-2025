from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import MuralPost, MuralComment, MuralReaction
from .serializers import MuralPostSerializer, MuralCommentSerializer

class MuralPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet simplificado para posts do mural
    """
    serializer_class = MuralPostSerializer
    permission_classes = []  # Sem permissões para debug
    
    def get_queryset(self):
        # Retornar todos os posts publicados
        return MuralPost.objects.filter(status='publicado').order_by('-created_at')


class MuralCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet simplificado para comentários do mural
    """
    serializer_class = MuralCommentSerializer
    permission_classes = []  # Sem permissões para debug
    
    def get_queryset(self):
        return MuralComment.objects.filter(status='publicado')


# Outras views temporariamente removidas para debug


class MuralFeedView(APIView):
    """
    Feed do mural da equipe
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        team = request.query_params.get('team', request.user.team)
        
        if not team:
            return Response(
                {'detail': 'Equipe não especificada.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar acesso à equipe
        if not request.user.is_admin_role and request.user.team != team:
            return Response(
                {'detail': 'Acesso negado à equipe especificada.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        posts = MuralPost.objects.filter(
            team=team,
            status='publicado'
        ).order_by('-created_at')[:20]
        
        posts_data = []
        for post in posts:
            posts_data.append({
                'id': post.id,
                'text': post.text,
                'emoji': post.emoji,
                'author': post.get_author_display(),
                'created_at': post.created_at,
                'reactions': post.reactions,
                'comments_count': post.comments.filter(status='publicado').count()
            })
        
        return Response({
            'team': team,
            'posts': posts_data
        })


class ReactToPostView(APIView):
    """
    Reagir a um post do mural
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        emoji = request.data.get('emoji')
        
        if not emoji:
            return Response(
                {'detail': 'Emoji é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            post = MuralPost.objects.get(pk=pk)
            
            # Verificar acesso
            if not request.user.is_admin_role and request.user.team != post.team:
                return Response(
                    {'detail': 'Acesso negado.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Adicionar reação
            post.add_reaction(emoji)
            
            return Response({
                'message': 'Reação adicionada com sucesso.',
                'reactions': post.reactions
            })
            
        except MuralPost.DoesNotExist:
            return Response(
                {'detail': 'Post não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )


class ModeratePostView(APIView):
    """
    Moderar post do mural (ocultar)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, pk):
        if not (request.user.is_connecta or request.user.is_admin_role):
            return Response(
                {'detail': 'Apenas Conectas e Admins podem moderar.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            post = MuralPost.objects.get(pk=pk)
            
            # Verificar acesso à equipe
            if not request.user.is_admin_role and request.user.team != post.team:
                return Response(
                    {'detail': 'Acesso negado.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            reason = request.data.get('reason', '')
            post.moderate(request.user, reason)
            
            # Auditoria
            from audit.models import AuditLog
            AuditLog.log_action(
                actor=request.user,
                action='mural_post_moderated',
                category='mural',
                object_type='MuralPost',
                object_id=post.id,
                meta={'reason': reason},
                request=request
            )
            
            return Response({
                'message': 'Post moderado com sucesso.'
            })
            
        except MuralPost.DoesNotExist:
            return Response(
                {'detail': 'Post não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
