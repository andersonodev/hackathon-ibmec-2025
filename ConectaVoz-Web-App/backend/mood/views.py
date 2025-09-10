from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Avg, Count
from django.conf import settings
from .models import MoodCheckin, PseudonymSalt
from .serializers import MoodCheckinSerializer, MoodSummarySerializer
from users.permissions import RoleBasedPermission, KAnonymityPermission

class MoodCheckinViewSet(viewsets.ModelViewSet):
    """
    ViewSet para check-ins de humor
    """
    serializer_class = MoodCheckinSerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get_queryset(self):
        # Usuários só veem seus próprios check-ins via pseudônimo
        if self.request.user.is_employee:
            pseudo_id = MoodCheckin.generate_pseudo_id(self.request.user.id)
            return MoodCheckin.objects.filter(pseudo_id=pseudo_id)
        
        # Admin/Conecta/Council veem agregados (respeitando k-anonimato)
        return MoodCheckin.objects.all()
    
    def create(self, request, *args, **kwargs):
        """
        Cria check-in diário com pseudônimo
        """
        day = timezone.localdate()
        pseudo_id = MoodCheckin.generate_pseudo_id(request.user.id, day)
        
        # Verificar se já existe check-in hoje
        if MoodCheckin.objects.filter(day=day, pseudo_id=pseudo_id).exists():
            return Response(
                {'detail': 'Já existe um check-in para hoje.'},
                status=status.HTTP_409_CONFLICT
            )
        
        # Criar check-in
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                day=day,
                pseudo_id=pseudo_id
            )
            
            # Auditoria
            from audit.models import AuditLog
            AuditLog.log_action(
                actor=request.user,
                action='mood_checkin_created',
                category='mood',
                object_type='MoodCheckin',
                object_id=serializer.instance.id,
                meta={'score': serializer.instance.score},
                request=request
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MoodSummaryView(APIView):
    """
    View para resumo de humor (respeitando k-anonimato)
    """
    permission_classes = [permissions.IsAuthenticated, KAnonymityPermission]
    
    def get(self, request):
        # Filtros
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        department = request.query_params.get('department')
        team = request.query_params.get('team')
        
        # Construir queryset
        queryset = MoodCheckin.objects.all()
        
        if start_date:
            queryset = queryset.filter(day__gte=start_date)
        if end_date:
            queryset = queryset.filter(day__lte=end_date)
        
        # Aplicar filtros de escopo se não for admin
        if not request.user.is_admin_role:
            if request.user.team:
                # Usuários normais só veem dados do seu time
                # Aqui precisaríamos de uma forma de relacionar pseudônimos com teams
                # Por simplicidade, vamos permitir visualização geral
                pass
        
        # Verificar k-anonimato
        k_check = KAnonymityPermission.check_k_anonymity(queryset)
        
        if k_check['collecting']:
            # Ainda coletando dados, não exibir números
            return Response({
                'collecting': True,
                'collecting_progress': k_check['collecting_progress'],
                'count': k_check['count'],
                'threshold': k_check['threshold']
            })
        
        # Calcular métricas
        stats = queryset.aggregate(
            avg_score=Avg('score'),
            total_checkins=Count('id')
        )
        
        # Distribuição por score
        distribution = []
        for score in range(1, 6):
            count = queryset.filter(score=score).count()
            distribution.append({
                'score': score,
                'count': count,
                'percentage': round((count / stats['total_checkins']) * 100, 1) if stats['total_checkins'] > 0 else 0
            })
        
        # Índice de clima (0-100)
        clima_index = None
        if stats['avg_score']:
            clima_index = round(((stats['avg_score'] - 1) / 4) * 100, 1)
        
        serializer = MoodSummarySerializer({
            'collecting': False,
            'collecting_progress': k_check['collecting_progress'],
            'count': stats['total_checkins'],
            'avg_score': stats['avg_score'],
            'clima_index': clima_index,
            'distribution': distribution
        })
        
        return Response(serializer.data)


class MyMoodHistoryView(APIView):
    """
    View para histórico pessoal de humor
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        pseudo_id = MoodCheckin.generate_pseudo_id(request.user.id)
        
        # Últimos 30 dias
        thirty_days_ago = timezone.localdate() - timezone.timedelta(days=30)
        queryset = MoodCheckin.objects.filter(
            pseudo_id=pseudo_id,
            day__gte=thirty_days_ago
        ).order_by('day')
        
        # Calcular médias
        weekly_avg = queryset.filter(
            day__gte=timezone.localdate() - timezone.timedelta(days=7)
        ).aggregate(avg=Avg('score'))['avg']
        
        monthly_avg = queryset.aggregate(avg=Avg('score'))['avg']
        
        # Histórico diário
        daily_history = []
        for checkin in queryset:
            daily_history.append({
                'day': checkin.day,
                'score': checkin.score,
                'comment': checkin.comment,
                'tags': checkin.tags
            })
        
        return Response({
            'weekly_avg': round(weekly_avg, 1) if weekly_avg else None,
            'monthly_avg': round(monthly_avg, 1) if monthly_avg else None,
            'daily_history': daily_history,
            'total_checkins': queryset.count()
        })


class TeamTrendsView(APIView):
    """
    View para tendências da equipe (apenas Conecta/Council/Admin)
    """
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get(self, request):
        if not (request.user.is_connecta or request.user.is_council or request.user.is_admin_role):
            return Response(
                {'detail': 'Sem permissão para visualizar tendências da equipe.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Últimos 30 dias
        thirty_days_ago = timezone.localdate() - timezone.timedelta(days=30)
        
        # Tendência diária (últimos 30 dias)
        daily_trends = []
        for i in range(30):
            day = timezone.localdate() - timezone.timedelta(days=i)
            day_data = MoodCheckin.objects.filter(day=day)
            
            # Verificar k-anonimato por dia
            k_check = KAnonymityPermission.check_k_anonymity(day_data)
            
            if k_check['collecting']:
                daily_trends.append({
                    'day': day,
                    'collecting': True,
                    'collecting_progress': k_check['collecting_progress'],
                    'avg_score': None,
                    'count': k_check['count']
                })
            else:
                avg_score = day_data.aggregate(avg=Avg('score'))['avg']
                daily_trends.append({
                    'day': day,
                    'collecting': False,
                    'avg_score': round(avg_score, 1) if avg_score else None,
                    'count': day_data.count()
                })
        
        return Response({
            'daily_trends': list(reversed(daily_trends)),
            'period': '30 days'
        })
