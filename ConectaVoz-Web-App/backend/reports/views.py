from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.utils import timezone
from .models import ClimaSnapshot, TeamBulletin, ExportLog, DashboardWidget
from users.permissions import RoleBasedPermission
import csv
import io

class ClimaReportView(APIView):
    """
    Relatório de clima organizacional
    """
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get(self, request):
        if not (request.user.is_council or request.user.is_admin_role or request.user.is_connecta):
            return Response(
                {'detail': 'Acesso negado.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Filtros
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        department = request.query_params.get('department')
        team = request.query_params.get('team')
        
        # Buscar snapshots
        queryset = ClimaSnapshot.objects.all()
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if department:
            queryset = queryset.filter(department=department)
        if team:
            queryset = queryset.filter(team=team)
        
        # Últimos 30 dias se não especificado
        if not start_date and not end_date:
            thirty_days_ago = timezone.localdate() - timezone.timedelta(days=30)
            queryset = queryset.filter(date__gte=thirty_days_ago)
        
        snapshots = queryset.order_by('-date')[:30]
        
        data = []
        for snapshot in snapshots:
            data.append({
                'date': snapshot.date,
                'mood_index': snapshot.mood_index,
                'mood_collecting': snapshot.mood_collecting,
                'collecting_progress': snapshot.collecting_progress,
                'voice_total': snapshot.voice_total,
                'voice_positivo': snapshot.voice_positivo,
                'voice_alerta': snapshot.voice_alerta,
                'voice_denuncia': snapshot.voice_denuncia,
                'department': snapshot.department,
                'team': snapshot.team
            })
        
        return Response({
            'snapshots': data,
            'filters': {
                'start_date': start_date,
                'end_date': end_date,
                'department': department,
                'team': team
            }
        })


class ExportCSVView(APIView):
    """
    Exportar dados agregados em CSV
    """
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get(self, request):
        if not (request.user.is_council or request.user.is_admin_role):
            return Response(
                {'detail': 'Acesso negado.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Mesmo filtros do relatório de clima
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = ClimaSnapshot.objects.all()
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Gerar CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow([
            'Data', 'Departamento', 'Equipe', 'Índice de Humor', 
            'Em Coleta', 'Total Relatos', 'Positivos', 'Alertas', 'Denúncias'
        ])
        
        # Dados
        for snapshot in queryset.order_by('-date'):
            writer.writerow([
                snapshot.date,
                snapshot.department or 'Geral',
                snapshot.team or 'Geral',
                snapshot.mood_index if not snapshot.mood_collecting else 'Em coleta',
                'Sim' if snapshot.mood_collecting else 'Não',
                snapshot.voice_total,
                snapshot.voice_positivo,
                snapshot.voice_alerta,
                snapshot.voice_denuncia
            ])
        
        # Log da exportação
        ExportLog.objects.create(
            export_type='clima_csv',
            exported_by=request.user,
            records_count=queryset.count(),
            filters={
                'start_date': start_date,
                'end_date': end_date
            }
        )
        
        # Resposta HTTP
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="clima_report_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        return response


class TeamBulletinListCreateView(generics.ListCreateAPIView):
    """
    Listar e criar boletins da equipe
    """
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_connecta:
            # Conecta vê boletins da sua equipe
            return TeamBulletin.objects.filter(team=user.team)
        elif user.is_admin_role:
            # Admin vê todos
            return TeamBulletin.objects.all()
        else:
            # Outros veem boletins publicados da sua equipe
            return TeamBulletin.objects.filter(
                team=user.team,
                status='published'
            )


class TeamBulletinDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Detalhar, editar e deletar boletim
    """
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get_queryset(self):
        return TeamBulletin.objects.all()


class DashboardWidgetsView(APIView):
    """
    Widgets personalizados do dashboard
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        widgets = DashboardWidget.objects.filter(
            user=request.user,
            active=True
        ).order_by('position')
        
        widgets_data = []
        for widget in widgets:
            widgets_data.append({
                'id': widget.id,
                'widget_type': widget.widget_type,
                'title': widget.title,
                'position': widget.position,
                'config': widget.config
            })
        
        return Response({'widgets': widgets_data})


class ReportsStatsView(APIView):
    """
    Estatísticas gerais de relatórios
    """
    permission_classes = []  # Temporariamente sem autenticação para debug
    
    def get(self, request):
        # Retornar estatísticas básicas sem verificação de permissão
        stats = {
            'total_reports': 0,
            'monthly_reports': 0,
            'team_reports': 0,
            'pending_reports': 0
        }
        
        return Response(stats)


class MoodAnalyticsView(APIView):
    """
    Analytics de humor organizacional
    """
    permission_classes = []  # Sem autenticação para debug
    
    def get(self, request):
        period = request.query_params.get('period', '7d')
        
        # Retornar dados mock de analytics de humor
        analytics = {
            'period': period,
            'average_mood': 7.2,
            'mood_trend': 'positive',
            'total_responses': 150,
            'mood_distribution': {
                'excellent': 25,
                'good': 45,
                'neutral': 35,
                'poor': 20,
                'critical': 5
            },
            'weekly_trend': [6.8, 7.0, 7.1, 7.2, 7.3, 7.2, 7.2],
            'department_breakdown': [
                {'name': 'TI', 'average': 7.5, 'responses': 30},
                {'name': 'RH', 'average': 7.0, 'responses': 25},
                {'name': 'Vendas', 'average': 6.8, 'responses': 40},
                {'name': 'Marketing', 'average': 7.3, 'responses': 20}
            ]
        }
        
        return Response(analytics)


class VoiceAnalyticsView(APIView):
    """
    Analytics de manifestações da voz
    """
    permission_classes = []  # Sem autenticação para debug
    
    def get(self, request):
        period = request.query_params.get('period', '7d')
        
        # Retornar dados mock de analytics de voz
        analytics = {
            'period': period,
            'total_reports': 45,
            'resolved_reports': 32,
            'pending_reports': 13,
            'resolution_rate': 71.1,
            'category_breakdown': {
                'workplace_environment': 15,
                'leadership': 12,
                'career_development': 8,
                'compensation': 6,
                'workload': 4
            },
            'resolution_time_avg': 5.2,  # dias
            'satisfaction_score': 4.1,  # de 5
            'monthly_trend': [38, 42, 45, 41, 39, 45],
            'department_reports': [
                {'name': 'TI', 'reports': 12, 'resolved': 9},
                {'name': 'RH', 'reports': 8, 'resolved': 7},
                {'name': 'Vendas', 'reports': 15, 'resolved': 10},
                {'name': 'Marketing', 'reports': 10, 'resolved': 6}
            ]
        }
        
        return Response(analytics)
