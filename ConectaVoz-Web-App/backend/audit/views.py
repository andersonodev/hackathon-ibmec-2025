from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AuditLog, DataRetentionLog, SystemEvent
from users.permissions import RoleBasedPermission

class AuditLogListView(generics.ListAPIView):
    """
    Listar logs de auditoria (apenas auditor/admin)
    """
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get_queryset(self):
        if not (self.request.user.is_auditor or self.request.user.is_admin_role):
            return AuditLog.objects.none()
        
        queryset = AuditLog.objects.all()
        
        # Filtros
        actor = self.request.query_params.get('actor')
        category = self.request.query_params.get('category')
        action = self.request.query_params.get('action')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if actor:
            queryset = queryset.filter(actor_id=actor)
        if category:
            queryset = queryset.filter(category=category)
        if action:
            queryset = queryset.filter(action__icontains=action)
        if start_date:
            queryset = queryset.filter(at__gte=start_date)
        if end_date:
            queryset = queryset.filter(at__lte=end_date)
        
        return queryset.order_by('-at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Paginar
        page = self.paginate_queryset(queryset)
        
        data = []
        logs = page if page is not None else queryset[:100]
        
        for log in logs:
            data.append({
                'id': log.id,
                'at': log.at,
                'actor': log.actor.get_full_name() if log.actor else 'Sistema',
                'action': log.action,
                'category': log.get_category_display(),
                'object_type': log.object_type,
                'object_id': log.object_id,
                'meta': log.meta,
                'ip_address': log.ip_address
            })
        
        if page is not None:
            return self.get_paginated_response(data)
        
        return Response({'results': data})


class DataRetentionLogListView(generics.ListAPIView):
    """
    Listar logs de retenção de dados
    """
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get_queryset(self):
        if not (self.request.user.is_auditor or self.request.user.is_admin_role):
            return DataRetentionLog.objects.none()
        
        return DataRetentionLog.objects.all().order_by('-executed_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        data = []
        for log in queryset[:50]:
            data.append({
                'id': log.id,
                'executed_at': log.executed_at,
                'retention_type': log.get_retention_type_display(),
                'policy_name': log.policy_name,
                'records_affected': log.records_affected,
                'date_threshold': log.date_threshold,
                'executed_by': log.executed_by.get_full_name() if log.executed_by else 'Sistema'
            })
        
        return Response({'results': data})


class SystemEventListView(generics.ListAPIView):
    """
    Listar eventos do sistema
    """
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get_queryset(self):
        if not (self.request.user.is_auditor or self.request.user.is_admin_role):
            return SystemEvent.objects.none()
        
        queryset = SystemEvent.objects.all()
        
        # Filtros
        event_type = self.request.query_params.get('event_type')
        severity = self.request.query_params.get('severity')
        resolved = self.request.query_params.get('resolved')
        
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        if severity:
            queryset = queryset.filter(severity=severity)
        if resolved is not None:
            queryset = queryset.filter(resolved=resolved.lower() == 'true')
        
        return queryset.order_by('-timestamp')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        data = []
        for event in queryset[:50]:
            data.append({
                'id': event.id,
                'timestamp': event.timestamp,
                'event_type': event.get_event_type_display(),
                'severity': event.get_severity_display(),
                'title': event.title,
                'description': event.description,
                'resolved': event.resolved,
                'resolved_at': event.resolved_at
            })
        
        return Response({'results': data})
