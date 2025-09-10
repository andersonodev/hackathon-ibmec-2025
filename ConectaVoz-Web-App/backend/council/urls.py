from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cases', views.CouncilCaseViewSet, basename='council-case')
router.register(r'decisions', views.CouncilDecisionViewSet, basename='council-decision')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.CouncilDashboardView.as_view(), name='council-dashboard'),
    path('cases/<int:pk>/actions/', views.CaseActionsView.as_view(), name='case-actions'),
]
