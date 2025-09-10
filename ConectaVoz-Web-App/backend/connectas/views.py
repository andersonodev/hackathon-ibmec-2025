from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Count
from django.conf import settings
from .models import Connecta, ConnectaPreference, ConnectaHomologation
from .serializers import (
    ConnectaSerializer, ConnectaPreferenceSerializer, ConnectaHomologationSerializer
)
from users.permissions import RoleBasedPermission, ConnectaChangePermission
from users.serializers import ConnectaUserSerializer
from users.models import User

class ConnectaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de Conectas (apenas admin)
    """
    queryset = Connecta.objects.all()
    serializer_class = ConnectaSerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get_queryset(self):
        if self.request.user.is_admin_role:
            return Connecta.objects.all()
        elif self.request.user.is_connecta:
            return Connecta.objects.filter(user=self.request.user)
        return Connecta.objects.filter(active=True)


class ConnectaQueueView(APIView):
    """
    Fila do Conecta - implementada em voice/views.py
    Esta view redireciona para manter compatibilidade
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Redirecionar para a implementação real em voice
        from voice.views import ConnectaQueueView as VoiceQueueView
        view = VoiceQueueView()
        view.setup(request)
        return view.get(request)


class ConnectaPreferenceView(APIView):
    """
    Gerenciar preferência de Conecta do colaborador
    """
    permission_classes = [permissions.IsAuthenticated, ConnectaChangePermission]
    
    def get(self, request):
        """
        Ver minha preferência atual de Conecta
        """
        try:
            preference = ConnectaPreference.objects.get(employee=request.user)
            serializer = ConnectaPreferenceSerializer(preference)
            return Response(serializer.data)
        except ConnectaPreference.DoesNotExist:
            return Response({
                'detail': 'Nenhuma preferência de Conecta definida.',
                'has_preference': False
            })
    
    def post(self, request):
        """
        Escolher ou trocar Conecta (respeitando janela de 15 dias)
        """
        preferred_connecta_id = request.data.get('preferred_connecta_id')
        
        if not preferred_connecta_id:
            return Response(
                {'detail': 'preferred_connecta_id é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar se o usuário escolhido existe e pode ser Conecta
        try:
            preferred_user = User.objects.get(id=preferred_connecta_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar capacidade do Conecta escolhido
        try:
            connecta = Connecta.objects.get(user=preferred_user)
            if not connecta.can_accept_assignment():
                return Response(
                    {'detail': 'Este Conecta atingiu sua capacidade máxima.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Connecta.DoesNotExist:
            # Criar Conecta se não existir
            connecta = Connecta.objects.create(user=preferred_user)
        
        # Verificar se pode trocar (janela de 15 dias)
        try:
            existing_pref = ConnectaPreference.objects.get(employee=request.user)
            if not existing_pref.can_change():
                next_change = existing_pref.next_change_at.strftime('%d/%m/%Y')
                return Response(
                    {'detail': f'Você só pode trocar de Conecta novamente em {next_change}.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Atualizar preferência existente
            existing_pref.preferred_connecta = preferred_user
            existing_pref.chosen_at = timezone.now()
            existing_pref.next_change_at = timezone.now() + timezone.timedelta(
                days=settings.CONNECTA_CHANGE_INTERVAL_DAYS
            )
            existing_pref.effective = False  # Precisa ser homologada novamente
            existing_pref.save()
            
            preference = existing_pref
            
        except ConnectaPreference.DoesNotExist:
            # Criar nova preferência
            preference = ConnectaPreference.objects.create(
                employee=request.user,
                preferred_connecta=preferred_user
            )
        
        # Auditoria
        from audit.models import AuditLog
        AuditLog.log_action(
            actor=request.user,
            action='connecta_preference_changed',
            category='connecta',
            object_type='ConnectaPreference',
            object_id=preference.id,
            meta={'preferred_connecta': preferred_user.get_full_name()},
            request=request
        )
        
        serializer = ConnectaPreferenceSerializer(preference)
        return Response({
            'message': 'Preferência de Conecta registrada com sucesso. Aguarde a homologação.',
            'preference': serializer.data
        })


class HomologateConnectasView(APIView):
    """
    Homologar Conectas (aplicar regra de corte ≥2 votos)
    """
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def post(self, request):
        if not request.user.is_admin_role:
            return Response(
                {'detail': 'Apenas administradores podem homologar Conectas.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Contar votos por Conecta
        vote_counts = ConnectaPreference.get_vote_counts()
        min_votes = settings.CONNECTA_MIN_VOTES
        
        approved_connectas = 0
        rejected_preferences = 0
        total_preferences = ConnectaPreference.objects.filter(effective=False).count()
        
        # Aplicar corte
        for vote_data in vote_counts:
            connecta_user_id = vote_data['preferred_connecta']
            votes = vote_data['votes']
            
            if votes >= min_votes:
                # Aprovar Conecta
                connecta, created = Connecta.objects.get_or_create(
                    user_id=connecta_user_id,
                    defaults={'active': True}
                )
                if not created:
                    connecta.active = True
                    connecta.save()
                
                # Marcar preferências como efetivas
                ConnectaPreference.objects.filter(
                    preferred_connecta_id=connecta_user_id,
                    effective=False
                ).update(effective=True, vote_count=votes)
                
                approved_connectas += 1
                
            else:
                # Rejeitar preferências com poucos votos
                rejected_prefs = ConnectaPreference.objects.filter(
                    preferred_connecta_id=connecta_user_id,
                    effective=False
                )
                rejected_preferences += rejected_prefs.count()
                rejected_prefs.delete()
        
        # Registrar homologação
        homologation = ConnectaHomologation.objects.create(
            homologated_by=request.user,
            total_preferences=total_preferences,
            approved_connectas=approved_connectas,
            rejected_preferences=rejected_preferences,
            notes=request.data.get('notes', '')
        )
        
        # Auditoria
        from audit.models import AuditLog
        AuditLog.log_action(
            actor=request.user,
            action='connectas_homologated',
            category='connecta',
            object_type='ConnectaHomologation',
            object_id=homologation.id,
            meta={
                'approved': approved_connectas,
                'rejected': rejected_preferences
            },
            request=request
        )
        
        return Response({
            'message': 'Homologação realizada com sucesso.',
            'results': {
                'total_preferences': total_preferences,
                'approved_connectas': approved_connectas,
                'rejected_preferences': rejected_preferences,
                'min_votes_required': min_votes
            }
        })


class MyScopeView(APIView):
    """
    Ver meu escopo como Conecta
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_connecta:
            return Response(
                {'detail': 'Apenas Conectas podem ver seu escopo.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Buscar colaboradores atribuídos
        assigned_employees = ConnectaPreference.objects.filter(
            preferred_connecta=request.user,
            effective=True
        ).select_related('employee')
        
        employees_data = []
        for pref in assigned_employees:
            employees_data.append({
                'id': pref.employee.id,
                'name': pref.employee.get_full_name(),
                'username': pref.employee.username,
                'department': pref.employee.department,
                'team': pref.employee.team,
                'chosen_at': pref.chosen_at
            })
        
        # Estatísticas
        from voice.models import VoicePost
        voice_stats = VoicePost.objects.filter(
            assigned_to__user=request.user
        ).values('status').annotate(count=Count('id'))
        
        return Response({
            'assigned_employees': employees_data,
            'total_assigned': len(employees_data),
            'voice_stats': list(voice_stats),
            'capacity': {
                'max': request.user.connecta.capacity_max if hasattr(request.user, 'connecta') else 12,
                'current': len(employees_data)
            }
        })


class AvailableConnectasView(APIView):
    """
    Listar Conectas disponíveis para escolha
    """
    permission_classes = []  # Removido temporariamente para teste
    
    def get(self, request):
        # Comentado temporariamente para teste
        # if not request.user.is_employee:
        #     return Response(
        #         {'detail': 'Apenas colaboradores podem ver Conectas disponíveis.'},
        #         status=status.HTTP_403_FORBIDDEN
        #     )
        
        # Conectas ativos com capacidade
        available_connectas = Connecta.objects.filter(
            active=True
        ).select_related('user')
        
        # Filtrar por equipe/departamento se aplicável (comentado para teste)
        # if hasattr(request.user, 'team') and request.user.team:
        #     available_connectas = available_connectas.filter(
        #         user__team=request.user.team
        #     )
        # elif hasattr(request.user, 'department') and request.user.department:
        #     available_connectas = available_connectas.filter(
        #         user__department=request.user.department
        #     )
        
        connectas_data = []
        for connecta in available_connectas:
            if connecta.is_available:
                # Estrutura compatível com o frontend
                conecta_data = {
                    'id': connecta.id,
                    'user': {
                        'id': connecta.user.id,
                        'first_name': connecta.user.first_name,
                        'last_name': connecta.user.last_name,
                        'email': connecta.user.email,
                    },
                    'specialties': getattr(connecta.user, 'specialties', ['Suporte Geral']),
                    'bio': getattr(connecta.user, 'bio', f'Conecta especializado em suporte e orientação para colaboradores.'),
                    'available_slots': connecta.capacity_max,
                    'current_connections': connecta.assigned_count,
                    'rating': 4.5,  # Valor padrão, pode ser calculado posteriormente
                    'response_time_hours': 24,  # Valor padrão
                    'is_available': connecta.is_available,
                    'created_at': connecta.created_at.isoformat(),
                }
                connectas_data.append(conecta_data)
        
        return Response(connectas_data)


class MyConnectionsView(APIView):
    """
    Minhas conexões de Conecta
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Retornar conexões do usuário
        connections = []
        
        # Se o usuário é um Conecta, retornar suas atribuições
        if hasattr(request.user, 'connecta_profile'):
            connecta = request.user.connecta_profile
            # Aqui você pode adicionar lógica para buscar as conexões ativas
            connections.append({
                'id': connecta.id,
                'type': 'connecta',
                'status': 'active' if connecta.active else 'inactive',
                'current_connections': connecta.assigned_count,
                'max_capacity': connecta.capacity_max,
            })
        
        return Response({'connections': connections})
