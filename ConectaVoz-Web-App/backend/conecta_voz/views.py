from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

def home(request):
    """
    Página inicial - redireciona para login ou dashboard
    """
    if request.user.is_authenticated:
        return render(request, 'dashboard/home.html')
    else:
        return render(request, 'auth/login.html')

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

@login_required
def checkin_view(request):
    """
    Página de check-in diário
    """
    return render(request, 'checkin/daily.html')

@login_required
def voice_view(request):
    """
    Página para falar com conecta
    """
    return render(request, 'voice/chat.html')

@login_required
def mural_view(request):
    """
    Página do mural da equipe
    """
    return render(request, 'mural/feed.html')

@login_required
def conecta_view(request):
    """
    Página para escolher conecta
    """
    return render(request, 'connectas/choose.html')
