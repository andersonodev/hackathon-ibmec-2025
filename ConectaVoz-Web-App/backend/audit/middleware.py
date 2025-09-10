from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from .models import AuditLog

class AuditMiddleware(MiddlewareMixin):
    """
    Middleware para auditoria automática de ações
    """
    
    # Ações que devem ser auditadas automaticamente
    AUDITABLE_ACTIONS = {
        'POST': 'create',
        'PUT': 'update',
        'PATCH': 'partial_update',
        'DELETE': 'delete',
    }
    
    # URLs que devem ser auditadas
    AUDITABLE_URLS = [
        'voice',
        'mood',
        'connecta',
        'council',
        'mural',
        'admin',
    ]
    
    def process_request(self, request):
        """
        Adiciona informações de auditoria ao request
        """
        request.audit_data = {
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
            'path': request.path,
            'method': request.method,
        }
        return None
    
    def process_response(self, request, response):
        """
        Registra ações auditáveis após a resposta
        """
        # Só audita se for uma ação modificadora e bem-sucedida
        if (request.method in self.AUDITABLE_ACTIONS and 
            200 <= response.status_code < 300 and
            hasattr(request, 'user') and 
            request.user and
            request.user.is_authenticated):
            
            try:
                # Verifica se a URL é auditável
                resolved = resolve(request.path_info)
                if any(url_part in request.path for url_part in self.AUDITABLE_URLS):
                    self.create_audit_log(request, resolved)
            except Exception:
                # Falha silenciosa para não afetar a resposta
                pass
        
        return response
    
    def create_audit_log(self, request, resolved):
        """
        Cria log de auditoria para a ação
        """
        action = self.AUDITABLE_ACTIONS.get(request.method, 'unknown')
        
        # Determinar categoria baseada na URL
        category = 'system'
        if 'voice' in request.path:
            category = 'voice'
        elif 'mood' in request.path:
            category = 'mood'
        elif 'connecta' in request.path:
            category = 'connecta'
        elif 'council' in request.path:
            category = 'council'
        elif 'mural' in request.path:
            category = 'mural'
        elif 'admin' in request.path:
            category = 'admin'
        
        # Extrair informações do objeto se possível
        object_type = resolved.url_name or 'unknown'
        object_id = resolved.kwargs.get('pk', 'unknown')
        
        AuditLog.log_action(
            actor=request.user,
            action=f"{action}_{object_type}",
            category=category,
            object_type=object_type,
            object_id=object_id,
            meta={
                'method': request.method,
                'path': request.path,
                'status_code': getattr(request, 'response_status_code', 'unknown')
            },
            request=request
        )
    
    @staticmethod
    def get_client_ip(request):
        """
        Obtém o IP real do cliente
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
