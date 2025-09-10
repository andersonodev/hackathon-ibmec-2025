"""
Views gerais da API
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Endpoint raiz da API com informações básicas
    """
    return Response({
        'message': 'Bem-vindo à API Conecta Voz',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/v1/auth/',
            'mood': '/api/v1/mood/',
            'voice': '/api/v1/voice/',
            'mural': '/api/v1/mural/',
            'connectas': '/api/v1/connectas/',
            'reports': '/api/v1/reports/',
            'council': '/api/v1/council/',
            'escalation': '/api/v1/escalation/',
            'docs': '/api/docs/',
        },
        'debug': settings.DEBUG,
    })
