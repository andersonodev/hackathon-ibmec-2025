from django.urls import path
from . import views

urlpatterns = [
    path('logs/', views.AuditLogListView.as_view(), name='audit-logs'),
    path('retention-logs/', views.DataRetentionLogListView.as_view(), name='retention-logs'),
    path('system-events/', views.SystemEventListView.as_view(), name='system-events'),
]
