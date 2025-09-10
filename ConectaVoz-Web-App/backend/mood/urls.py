from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'checkins', views.MoodCheckinViewSet, basename='mood-checkin')

urlpatterns = [
    path('', include(router.urls)),
    path('summary/', views.MoodSummaryView.as_view(), name='mood-summary'),
    path('my-history/', views.MyMoodHistoryView.as_view(), name='my-mood-history'),
    path('team-trends/', views.TeamTrendsView.as_view(), name='team-trends'),
]
