from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'posts', views.VoicePostViewSet, basename='voice-post')

urlpatterns = [
    path('', include(router.urls)),
    path('my/', views.MyVoicePostsView.as_view(), name='my-voice-posts'),
    path('<int:pk>/message/', views.SendMessageView.as_view(), name='send-message'),
    path('<int:pk>/escalate/', views.EscalatePostView.as_view(), name='escalate-post'),
    path('attachments/', views.VoiceAttachmentUploadView.as_view(), name='upload-attachment'),
]
