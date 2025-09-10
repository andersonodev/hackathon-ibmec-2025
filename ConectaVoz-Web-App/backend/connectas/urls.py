from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path('queue/', views.ConnectaQueueView.as_view(), name='connecta-queue'),
    path('preferences/', views.ConnectaPreferenceView.as_view(), name='connecta-preferences'),
    path('homologate/', views.HomologateConnectasView.as_view(), name='homologate-connectas'),
    path('my-scope/', views.MyScopeView.as_view(), name='my-scope'),
    path('available/', views.AvailableConnectasView.as_view(), name='available-connectas'),
    path('my-connections/', views.MyConnectionsView.as_view(), name='my-connections'),
]

# Router para endpoints de CRUD
router = DefaultRouter()
router.register(r'crud', views.ConnectaViewSet, basename='connecta')

urlpatterns += [
    path('', include(router.urls)),
]
