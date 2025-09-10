from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import CouncilCase, CouncilDecision
from users.permissions import RoleBasedPermission

class CouncilCaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet para casos do Conselho
    """
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get_queryset(self):
        if self.request.user.is_council or self.request.user.is_admin_role:
            return CouncilCase.objects.all()
        return CouncilCase.objects.none()


class CouncilDecisionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para decisões do Conselho
    """
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get_queryset(self):
        if self.request.user.is_council or self.request.user.is_admin_role:
            return CouncilDecision.objects.all()
        return CouncilDecision.objects.none()


class CouncilDashboardView(APIView):
    """
    Dashboard do Conselho
    """
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get(self, request):
        if not (request.user.is_council or request.user.is_admin_role):
            return Response(
                {'detail': 'Acesso negado.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Estatísticas básicas
        stats = {
            'total_cases': CouncilCase.objects.count(),
            'open_cases': CouncilCase.objects.filter(status='aberto').count(),
            'in_progress_cases': CouncilCase.objects.filter(status='andamento').count(),
            'closed_cases': CouncilCase.objects.filter(status='fechado').count(),
        }
        
        return Response(stats)


class CaseActionsView(APIView):
    """
    Ações de um caso específico
    """
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get(self, request, pk):
        try:
            case = CouncilCase.objects.get(pk=pk)
            actions = case.actions
            
            return Response({'actions': actions})
        except CouncilCase.DoesNotExist:
            return Response(
                {'detail': 'Caso não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
