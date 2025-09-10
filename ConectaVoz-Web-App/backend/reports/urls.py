from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.ReportsStatsView.as_view(), name='reports-stats'),
    path('mood-analytics/', views.MoodAnalyticsView.as_view(), name='mood-analytics'),
    path('voice-analytics/', views.VoiceAnalyticsView.as_view(), name='voice-analytics'),
    path('clima/', views.ClimaReportView.as_view(), name='clima-report'),
    path('export.csv', views.ExportCSVView.as_view(), name='export-csv'),
    path('bulletins/', views.TeamBulletinListCreateView.as_view(), name='team-bulletins'),
    path('bulletins/<int:pk>/', views.TeamBulletinDetailView.as_view(), name='team-bulletin-detail'),
    path('dashboard/widgets/', views.DashboardWidgetsView.as_view(), name='dashboard-widgets'),
]
