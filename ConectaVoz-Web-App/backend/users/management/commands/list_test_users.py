from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from elections.models import ConnectaProfile, ConnectaAssignment

User = get_user_model()

class Command(BaseCommand):
    help = 'Lista todos os usuários de teste criados'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📋 Lista de Usuários de Teste'))
        self.stdout.write('=' * 60)
        
        # Admin e Diretoria
        self.stdout.write(self.style.WARNING('\n🔐 ADMINISTRADORES E DIRETORIA:'))
        admin_users = User.objects.filter(role__in=['admin', 'diretoria']).order_by('role', 'first_name')
        
        for user in admin_users:
            password = 'admin123' if user.role == 'admin' else 'diretora123'
            self.stdout.write(f'  👤 {user.get_full_name()} ({user.role.title()})')
            self.stdout.write(f'     📧 {user.email} | 🔑 {password}')
            self.stdout.write(f'     🏢 {user.department}')
            self.stdout.write('')
        
        # Conectas
        self.stdout.write(self.style.WARNING('🎯 CONECTAS (Colaboradores com função de escuta):'))
        conectas = User.objects.filter(is_connecta=True).order_by('first_name')
        
        for user in conectas:
            self.stdout.write(f'  👤 {user.get_full_name()} (Conecta)')
            self.stdout.write(f'     📧 {user.email} | 🔑 conecta123')
            self.stdout.write(f'     🏢 {user.department} - {user.team}')
            
            # Mostrar quem está atribuído a este Conecta
            assignments = ConnectaAssignment.objects.filter(connecta=user)
            if assignments.exists():
                self.stdout.write(f'     👥 Atribuições: {", ".join([a.employee.get_full_name() for a in assignments])}')
            self.stdout.write('')
        
        # Colaboradores regulares
        self.stdout.write(self.style.WARNING('👥 COLABORADORES REGULARES:'))
        colaboradores = User.objects.filter(role='colaborador', is_connecta=False).order_by('first_name')
        
        for user in colaboradores:
            self.stdout.write(f'  👤 {user.get_full_name()}')
            self.stdout.write(f'     📧 {user.email} | 🔑 colaborador123')
            self.stdout.write(f'     🏢 {user.department} - {user.team}')
            
            # Mostrar o Conecta atribuído
            try:
                assignment = ConnectaAssignment.objects.get(employee=user)
                self.stdout.write(f'     🎯 Conecta: {assignment.connecta.get_full_name()}')
            except ConnectaAssignment.DoesNotExist:
                self.stdout.write(f'     🎯 Conecta: Não atribuído')
            self.stdout.write('')
        
        # Estatísticas
        total_users = User.objects.count()
        total_conectas = User.objects.filter(is_connecta=True).count()
        total_assignments = ConnectaAssignment.objects.count()
        
        self.stdout.write(self.style.SUCCESS('\n📊 ESTATÍSTICAS:'))
        self.stdout.write(f'  • Total de usuários: {total_users}')
        self.stdout.write(f'  • Total de Conectas: {total_conectas}')
        self.stdout.write(f'  • Total de atribuições: {total_assignments}')
        
        self.stdout.write(self.style.SUCCESS('\n💡 COMO TESTAR:'))
        self.stdout.write('  1. Faça login com qualquer usuário')
        self.stdout.write('  2. Admin/Diretoria: Acesso completo ao sistema')
        self.stdout.write('  3. Conectas: Podem ver relatos dos colaboradores atribuídos')
        self.stdout.write('  4. Colaboradores: Podem escolher Conectas e fazer relatos')
        self.stdout.write('')
