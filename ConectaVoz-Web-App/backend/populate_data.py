#!/usr/bin/env python
"""
Script para popular o banco de dados com dados de exemplo
"""
import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conecta_voz.settings')
django.setup()

from users.models import User
from mood.models import MoodCheckin, PseudonymSalt
from voice.models import VoicePost
from connectas.models import Connecta, ConnectaPreference
from council.models import CouncilCase
from mural.models import MuralPost
from reports.models import ClimaSnapshot

def create_sample_users():
    """Criar usuários de exemplo"""
    print("Criando usuários de exemplo...")
    
    # Criar colaboradores
    employees = []
    for i in range(1, 11):
        if not User.objects.filter(email=f'colaborador{i}@empresa.com').exists():
            user = User.objects.create_user(
                username=f'colaborador{i}',
                email=f'colaborador{i}@empresa.com',
                password='senha123',
                first_name=f'Colaborador',
                last_name=f'{i}',
                role='employee',
                team=f'Equipe {(i-1)//3 + 1}'
            )
            employees.append(user)
            print(f"✓ Colaborador {i} criado")
    
    # Criar conectas
    conectas = []
    for i in range(1, 4):
        if not User.objects.filter(email=f'conecta{i}@empresa.com').exists():
            user = User.objects.create_user(
                username=f'conecta{i}',
                email=f'conecta{i}@empresa.com',
                password='senha123',
                first_name=f'Conecta',
                last_name=f'{i}',
                role='connecta'
            )
            conectas.append(user)
            print(f"✓ Conecta {i} criado")
    
    # Criar membros do conselho
    for i in range(1, 3):
        if not User.objects.filter(email=f'conselho{i}@empresa.com').exists():
            user = User.objects.create_user(
                username=f'conselho{i}',
                email=f'conselho{i}@empresa.com',
                password='senha123',
                first_name=f'Conselheiro',
                last_name=f'{i}',
                role='council'
            )
            print(f"✓ Conselheiro {i} criado")
    
    # Criar auditor
    if not User.objects.filter(email='auditor@empresa.com').exists():
        user = User.objects.create_user(
            username='auditor',
            email='auditor@empresa.com',
            password='senha123',
            first_name='Auditor',
            last_name='Sistema',
            role='auditor'
        )
        print(f"✓ Auditor criado")
    
    return employees, conectas

def create_pseudonym_salt():
    """Criar salt para pseudônimos"""
    print("Criando salt para pseudônimos...")
    
    if not PseudonymSalt.objects.exists():
        PseudonymSalt.objects.create(
            label='2025-09',
            salt='exemplo_salt_setembro_2025'
        )
        print("✓ Salt criado")

def create_mood_checkins():
    """Criar check-ins de humor"""
    print("Criando check-ins de humor...")
    
    employees = User.objects.filter(role='employee')
    scores = [1, 2, 3, 4, 5]
    
    # Criar check-ins dos últimos 7 dias
    for day in range(7):
        date = timezone.now().date() - timedelta(days=day)
        
        for employee in employees[:8]:  # Só alguns funcionários para ter variação
            if not MoodCheckin.objects.filter(pseudo_id__startswith=str(employee.id)[:8], day=date).exists():
                pseudo_id = MoodCheckin.generate_pseudo_id(employee.id, date)
                MoodCheckin.objects.create(
                    day=date,
                    score=scores[day % len(scores)],
                    pseudo_id=pseudo_id,
                    comment=f"Comentário do dia {date.strftime('%d/%m')}" if day % 2 == 0 else ""
                )
        
        print(f"✓ Check-ins criados para {date}")

def create_conectas():
    """Criar registros de conectas"""
    print("Criando conectas...")
    
    conecta_users = User.objects.filter(role='connecta')
    
    for user in conecta_users:
        if not Connecta.objects.filter(user=user).exists():
            Connecta.objects.create(
                user=user,
                active=True,
                capacity_max=12,
                assigned_count=0
            )
            print(f"✓ Conecta criado para {user.get_full_name()}")

def create_voice_posts():
    """Criar posts de voz (relatos)"""
    print("Criando posts de voz...")
    
    employees = User.objects.filter(role='employee')
    conectas = list(Connecta.objects.all())
    
    posts_data = [
        {
            'text': 'Estou tendo dificuldades com meu gestor direto. Gostaria de conversar sobre isso.',
            'tags': ['gestao'],
            'visibility': 'connecta_ident',
            'gostaria_retorno': True
        },
        {
            'text': 'A equipe está sobrecarregada e precisamos de ajuda para redistribuir as tarefas.',
            'tags': ['carga_trabalho'],
            'visibility': 'connecta_anon',
            'gostaria_retorno': True
        },
        {
            'text': 'O ambiente da nossa sala está muito barulhento, afetando a concentração.',
            'tags': ['ambiente'],
            'visibility': 'connecta_ident',
            'gostaria_retorno': False
        }
    ]
    
    for i, post_data in enumerate(posts_data):
        user = employees[i % len(employees)]
        connecta = conectas[i % len(conectas)] if conectas else None
        
        if not VoicePost.objects.filter(text__contains=post_data['text'][:20]).exists():
            pseudo_id = f"voice_pseudo_{user.id}_{i}"
            post = VoicePost.objects.create(
                author=user,
                assigned_to=connecta,
                pseudo_id=pseudo_id,
                **post_data
            )
            print(f"✓ Post '{post_data['text'][:30]}...' criado")

def create_mural_posts():
    """Criar posts do mural"""
    print("Criando posts do mural...")
    
    users = User.objects.filter(role__in=['employee', 'admin'])
    
    mural_posts_data = [
        {
            'text': 'Nova política de home office: A partir do próximo mês, teremos maior flexibilidade para trabalho remoto.',
            'team': 'Geral',
            'emoji': 3,
            'anonymous': False
        },
        {
            'text': 'Evento de integração: Vamos organizar um happy hour na próxima sexta-feira às 18h.',
            'team': 'Equipe 1',
            'emoji': 5,
            'anonymous': False
        },
        {
            'text': 'Gostaria de sugerir melhorias no processo de feedback.',
            'team': 'RH',
            'emoji': 2,
            'anonymous': True
        }
    ]
    
    for i, post_data in enumerate(mural_posts_data):
        user = users[i % len(users)]
        
        # Verificar se já existe um post com o mesmo texto
        if not MuralPost.objects.filter(text=post_data['text']).exists():
            post = MuralPost.objects.create(
                created_by=user,
                **post_data
            )
            print(f"✓ Post mural '{post_data['text'][:30]}...' criado")

def create_clima_snapshot():
    """Criar snapshot do clima organizacional"""
    print("Criando snapshot do clima...")
    
    if not ClimaSnapshot.objects.filter(
        week_start=timezone.now().date() - timedelta(days=timezone.now().weekday())
    ).exists():
        ClimaSnapshot.objects.create(
            week_start=timezone.now().date() - timedelta(days=timezone.now().weekday()),
            total_employees=10,
            participation_rate=0.80,
            avg_mood_score=3.2,
            mood_distribution={
                'muito_ruim': 5,
                'ruim': 15,
                'neutro': 25,
                'bom': 35,
                'muito_bom': 20
            },
            trending_categories=['gestao', 'carga_trabalho'],
            insights=[
                'Aumento na satisfação geral da equipe',
                'Questões de gestão precisam de atenção'
            ]
        )
        print("✓ Snapshot do clima criado")

def main():
    """Função principal"""
    print("🚀 Iniciando população do banco de dados...")
    print("-" * 50)
    
    try:
        create_sample_users()
        create_pseudonym_salt()
        create_mood_checkins()
        create_conectas()
        create_voice_posts()
        create_mural_posts()
        create_clima_snapshot()
        
        print("-" * 50)
        print("✅ Banco de dados populado com sucesso!")
        print("\n📊 Resumo:")
        print(f"👥 Usuários: {User.objects.count()}")
        print(f"😊 Check-ins de humor: {MoodCheckin.objects.count()}")
        print(f"🎯 Conectas: {Connecta.objects.count()}")
        print(f"📝 Posts de voz: {VoicePost.objects.count()}")
        print(f"📢 Posts do mural: {MuralPost.objects.count()}")
        print(f"📈 Snapshots: {ClimaSnapshot.objects.count()}")
        
        print("\n🔐 Credenciais de acesso:")
        print("Admin: admin@conectavoz.com.br / admin123")
        print("Colaborador: colaborador1@empresa.com / senha123")
        print("Conecta: conecta1@empresa.com / senha123")
        print("Conselho: conselho1@empresa.com / senha123")
        print("Auditor: auditor@empresa.com / senha123")
        
    except Exception as e:
        print(f"❌ Erro ao popular banco: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
