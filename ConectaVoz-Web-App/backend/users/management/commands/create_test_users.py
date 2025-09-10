from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from elections.models import ConnectaProfile, ConnectaAssignment

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria usuários de teste para o sistema Conecta Voz'

    def handle(self, *args, **options):
        self.stdout.write('Criando usuários de teste...')
        
        # Dados dos usuários pré-definidos
        users_data = [
            # Admin
            {
                'username': 'admin',
                'email': 'admin@conectavoz.com',
                'password': 'admin123',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'role': 'admin',
                'department': 'TI',
                'is_superuser': True,
                'is_staff': True
            },
            
            # Diretoria
            {
                'username': 'diretora',
                'email': 'diretora@conectavoz.com',
                'password': 'diretora123',
                'first_name': 'Marina',
                'last_name': 'Directora',
                'role': 'diretoria',
                'department': 'Executivo',
                'is_staff': True
            },
            
            # Conectas (Colaboradores designados)
            {
                'username': 'ana.silva',
                'email': 'ana.silva@conectavoz.com',
                'password': 'conecta123',
                'first_name': 'Ana',
                'last_name': 'Silva',
                'role': 'colaborador',
                'department': 'Recursos Humanos',
                'team': 'Bem-estar',
                'is_connecta': True
            },
            {
                'username': 'carlos.santos',
                'email': 'carlos.santos@conectavoz.com',
                'password': 'conecta123',
                'first_name': 'Carlos',
                'last_name': 'Santos',
                'role': 'colaborador',
                'department': 'Tecnologia',
                'team': 'Backend',
                'is_connecta': True
            },
            {
                'username': 'maria.oliveira',
                'email': 'maria.oliveira@conectavoz.com',
                'password': 'conecta123',
                'first_name': 'Maria',
                'last_name': 'Oliveira',
                'role': 'colaborador',
                'department': 'Produto',
                'team': 'Strategy',
                'is_connecta': True
            },
            
            # Colaboradores regulares
            {
                'username': 'joao.costa',
                'email': 'joao.costa@conectavoz.com',
                'password': 'colaborador123',
                'first_name': 'João',
                'last_name': 'Costa',
                'role': 'colaborador',
                'department': 'Design',
                'team': 'UX/UI'
            },
            {
                'username': 'fernanda.lima',
                'email': 'fernanda.lima@conectavoz.com',
                'password': 'colaborador123',
                'first_name': 'Fernanda',
                'last_name': 'Lima',
                'role': 'colaborador',
                'department': 'Marketing',
                'team': 'Digital'
            },
            {
                'username': 'roberto.mendes',
                'email': 'roberto.mendes@conectavoz.com',
                'password': 'colaborador123',
                'first_name': 'Roberto',
                'last_name': 'Mendes',
                'role': 'colaborador',
                'department': 'Vendas',
                'team': 'Enterprise'
            },
            {
                'username': 'luciana.soares',
                'email': 'luciana.soares@conectavoz.com',
                'password': 'colaborador123',
                'first_name': 'Luciana',
                'last_name': 'Soares',
                'role': 'colaborador',
                'department': 'Tecnologia',
                'team': 'Frontend'
            },
            {
                'username': 'pedro.alves',
                'email': 'pedro.alves@conectavoz.com',
                'password': 'colaborador123',
                'first_name': 'Pedro',
                'last_name': 'Alves',
                'role': 'colaborador',
                'department': 'Financeiro',
                'team': 'Controladoria'
            },
            {
                'username': 'juliana.barbosa',
                'email': 'juliana.barbosa@conectavoz.com',
                'password': 'colaborador123',
                'first_name': 'Juliana',
                'last_name': 'Barbosa',
                'role': 'colaborador',
                'department': 'Recursos Humanos',
                'team': 'Recrutamento'
            },
            {
                'username': 'marcos.ferreira',
                'email': 'marcos.ferreira@conectavoz.com',
                'password': 'colaborador123',
                'first_name': 'Marcos',
                'last_name': 'Ferreira',
                'role': 'colaborador',
                'department': 'Operações',
                'team': 'Logística'
            },
            {
                'username': 'aline.rodrigues',
                'email': 'aline.rodrigues@conectavoz.com',
                'password': 'colaborador123',
                'first_name': 'Aline',
                'last_name': 'Rodrigues',
                'role': 'colaborador',
                'department': 'Qualidade',
                'team': 'QA'
            }
        ]
        
        created_users = []
        
        for user_data in users_data:
            # Verifica se o usuário já existe
            if User.objects.filter(username=user_data['username']).exists():
                self.stdout.write(f'Usuário {user_data["username"]} já existe, pulando...')
                continue
            
            # Cria o usuário
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role'],
                department=user_data.get('department', ''),
                team=user_data.get('team', ''),
                is_connecta=user_data.get('is_connecta', False),
                is_superuser=user_data.get('is_superuser', False),
                is_staff=user_data.get('is_staff', False)
            )
            
            created_users.append(user)
            self.stdout.write(f'✅ Criado: {user.display_name} ({user.get_role_display()})')
        
        # Criar perfis para os Conectas
        self.stdout.write('\nCriando perfis de Conectas...')
        
        conectas_profiles = [
            {
                'username': 'ana.silva',
                'bio': 'Especialista em bem-estar corporativo com 8 anos de experiência em escuta ativa e mediação de conflitos. Foco em criar um ambiente de trabalho saudável e inclusivo.',
                'specialties': ['Bem-estar', 'Mediação', 'Desenvolvimento Pessoal', 'Inclusão'],
                'max_assignments': 15
            },
            {
                'username': 'carlos.santos',
                'bio': 'Líder técnico com foco em ambiente colaborativo e crescimento profissional da equipe. Experiência em mentoria e desenvolvimento de carreira em tecnologia.',
                'specialties': ['Liderança', 'Tech Career', 'Inovação', 'Mentoria Técnica'],
                'max_assignments': 12
            },
            {
                'username': 'maria.oliveira',
                'bio': 'Product Manager com experiência em coaching e desenvolvimento de equipes multidisciplinares. Especialista em estratégia e gestão de produtos.',
                'specialties': ['Coaching', 'Estratégia', 'Gestão de Equipes', 'Produto'],
                'max_assignments': 10
            }
        ]
        
        for profile_data in conectas_profiles:
            try:
                user = User.objects.get(username=profile_data['username'])
                profile, created = ConnectaProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'bio': profile_data['bio'],
                        'specialties': profile_data['specialties'],
                        'max_assignments': profile_data['max_assignments']
                    }
                )
                if created:
                    self.stdout.write(f'✅ Perfil criado para: {user.display_name}')
                else:
                    self.stdout.write(f'Perfil já existe para: {user.display_name}')
            except User.DoesNotExist:
                self.stdout.write(f'❌ Usuário {profile_data["username"]} não encontrado')
        
        # Criar algumas atribuições de exemplo
        self.stdout.write('\nCriando atribuições de exemplo...')
        
        assignments = [
            ('joao.costa', 'ana.silva'),
            ('fernanda.lima', 'carlos.santos'),
            ('roberto.mendes', 'maria.oliveira'),
            ('luciana.soares', 'carlos.santos'),
            ('pedro.alves', 'ana.silva'),
        ]
        
        for employee_username, connecta_username in assignments:
            try:
                employee = User.objects.get(username=employee_username)
                connecta = User.objects.get(username=connecta_username)
                
                assignment, created = ConnectaAssignment.objects.get_or_create(
                    employee=employee,
                    defaults={'connecta': connecta}
                )
                
                if created:
                    self.stdout.write(f'✅ {employee.display_name} → {connecta.display_name}')
                else:
                    self.stdout.write(f'Atribuição já existe: {employee.display_name} → {assignment.connecta.display_name}')
                    
            except User.DoesNotExist as e:
                self.stdout.write(f'❌ Erro: {e}')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Dados de teste criados com sucesso!'))
        self.stdout.write('\n📋 Resumo de usuários criados:')
        self.stdout.write('┌─────────────────────────────────────────────────────────┐')
        self.stdout.write('│ ADMIN & DIRETORIA (acesso total)                       │')
        self.stdout.write('├─────────────────────────────────────────────────────────┤')
        self.stdout.write('│ admin@conectavoz.com       | admin123                   │')
        self.stdout.write('│ diretora@conectavoz.com    | diretora123                │')
        self.stdout.write('├─────────────────────────────────────────────────────────┤')
        self.stdout.write('│ CONECTAS (colaboradores + função de escuta)            │')
        self.stdout.write('├─────────────────────────────────────────────────────────┤')
        self.stdout.write('│ ana.silva@conectavoz.com   | conecta123                 │')
        self.stdout.write('│ carlos.santos@conectavoz.com | conecta123               │')
        self.stdout.write('│ maria.oliveira@conectavoz.com | conecta123              │')
        self.stdout.write('├─────────────────────────────────────────────────────────┤')
        self.stdout.write('│ COLABORADORES (usuários regulares)                     │')
        self.stdout.write('├─────────────────────────────────────────────────────────┤')
        self.stdout.write('│ Todos os outros emails     | colaborador123             │')
        self.stdout.write('└─────────────────────────────────────────────────────────┘')
        
        self.stdout.write('\n💡 Para testar:')
        self.stdout.write('1. Faça login com qualquer usuário')
        self.stdout.write('2. Colaboradores podem escolher seus Conectas')
        self.stdout.write('3. Conectas podem ver e responder relatos')
        self.stdout.write('4. Admin/Diretoria têm acesso completo')
