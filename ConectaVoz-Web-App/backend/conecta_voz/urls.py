"""
URL Configuration for Conecta Voz project
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .api_views import api_root

# API endpoints
api_patterns = [
    path('', api_root, name='api-root'),
    path('auth/', include('users.urls')),
    path('mood/', include('mood.urls')),
    path('voice/', include('voice.urls')),
    path('mural/', include('mural.urls')),
    path('connectas/', include('connectas.urls')),
    path('reports/', include('reports.urls')),
    path('council/', include('council.urls')),
    path('escalation/', include('escalation.urls')),
]

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    path('api/v1/', include(api_patterns)),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
