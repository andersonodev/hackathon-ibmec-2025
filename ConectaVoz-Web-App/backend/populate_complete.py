#!/usr/bin/env python
import os
import sys
import django
from datetime import date, timedelta
import random

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conecta_voz.settings')
django.setup()

from django.contrib.auth import get_user_model
from connectas.models import Connecta, ConnectaPreference
from voice.models import VoicePost
from mural.models import MuralPost
from mood.models import MoodCheckin, PseudonymSalt

User = get_user_model()

def create_employees():
    """Criar colaboradores adicionais"""
    print("👥 Criando colaboradores...")
    
    employees_data = [
        {'username': 'carlos_pereira', 'first_name': 'Carlos', 'last_name': 'Pereira', 'email': 'carlos@empresa.com', 'team': 'Tech'},
        {'username': 'lucia_santos', 'first_name': 'Lúcia', 'last_name': 'Santos', 'email': 'lucia@empresa.com', 'team': 'Marketing'},
        {'username': 'pedro_silva', 'first_name': 'Pedro', 'last_name': 'Silva', 'email': 'pedro@empresa.com', 'team': 'RH'},
        {'username': 'ana_rodrigues', 'first_name': 'Ana', 'last_name': 'Rodrigues', 'email': 'ana.r@empresa.com', 'team': 'Vendas'},
        {'username': 'rafael_costa', 'first_name': 'Rafael', 'last_name': 'Costa', 'email': 'rafael@empresa.com', 'team': 'Tech'},
    ]
    
    for data in employees_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': data['email'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'role': 'colaborador',
                'team': data['team']
            }
        )
        
        if created:
            user.set_password('123456')
            user.save()
            print(f"✓ Colaborador {user.get_full_name()} criado")
        else:
            print(f"→ Colaborador {user.get_full_name()} já existe")

def create_voice_posts():
    """Criar posts de voz"""
    print("🗣️ Criando posts de voz...")
    
    employees = User.objects.filter(role='colaborador', is_connecta=False)
    
    posts_data = [
        {
            'text': 'O ambiente na nossa equipe está muito tenso ultimamente. Seria bom ter mais momentos de descontração.',
            'sentiment': 'alerta',
            'visibility': 'connecta_anon'
        },
        {
            'text': 'Estamos com muitas demandas e poucas pessoas. A equipe está sobrecarregada.',
            'sentiment': 'alerta',
            'visibility': 'connecta_ident'
        },
        {
            'text': 'Seria interessante ter mais transparência nas decisões que afetam nossa equipe.',
            'sentiment': 'positivo',
            'visibility': 'connecta_ident'
        }
    ]
    
    for i, post_data in enumerate(posts_data):
        employee = employees[i % len(employees)]
        
        if not VoicePost.objects.filter(text=post_data['text']).exists():
            post = VoicePost.objects.create(
                author=employee,
                pseudo_id=f"pseudo_{employee.id}",
                **post_data
            )
            print(f"✓ Post de voz '{post_data['text'][:30]}...' criado")

def create_mural_posts():
    """Criar posts do mural"""
    print("📝 Criando posts do mural...")
    
    users = User.objects.filter(role='colaborador')
    
    posts_data = [
        {
            'text': 'Parabéns para toda a equipe pelo sucesso do último projeto! 🎉',
            'team': 'Geral',
            'emoji': 5,
            'anonymous': False
        },
        {
            'text': 'Alguém sabe se vai ter happy hour essa sexta? Seria ótimo para relaxar.',
            'team': 'Tech',
            'emoji': 3,
            'anonymous': True
        },
        {
            'text': 'Adorei a nova política de home office. Muito mais flexibilidade!',
            'team': 'Geral',
            'emoji': 4,
            'anonymous': False
        },
        {
            'text': 'Seria legal ter um canal para compartilhar dicas técnicas entre as equipes.',
            'team': 'Tech',
            'emoji': 3,
            'anonymous': True
        }
    ]
    
    for i, post_data in enumerate(posts_data):
        user = users[i % len(users)]
        
        if not MuralPost.objects.filter(text=post_data['text']).exists():
            post = MuralPost.objects.create(
                created_by=user,
                **post_data
            )
            print(f"✓ Post '{post_data['text'][:30]}...' criado")

def create_mood_data():
    """Criar dados de humor"""
    print("😊 Criando dados de humor...")
    
    # Criar salt se não existir
    salt, created = PseudonymSalt.objects.get_or_create(
        defaults={'salt': 'conecta_voz_salt_2025'}
    )
    if created:
        print("✓ Salt para pseudônimos criado")
    
    employees = User.objects.filter(role='colaborador')
    
    # Criar check-ins para os últimos 7 dias
    for days_ago in range(7):
        check_date = date.today() - timedelta(days=days_ago)
        
        for employee in employees:
            # Criar apenas se não existir
            existing = MoodCheckin.objects.filter(
                pseudo_id=f"pseudo_{employee.id}",
                day=check_date
            ).exists()
            
            if not existing:
                mood_value = random.randint(1, 5)
                MoodCheckin.objects.create(
                    pseudo_id=f"pseudo_{employee.id}",
                    day=check_date,
                    score=mood_value,
                    comment=f"Comentário do dia {check_date}" if random.choice([True, False]) else ""
                )
        
        print(f"✓ Check-ins criados para {check_date}")

def create_connecta_preferences():
    """Criar preferências de conectas"""
    print("🤝 Criando preferências de conectas...")
    
    employees = User.objects.filter(role='colaborador', is_connecta=False)
    conectas = User.objects.filter(is_connecta=True)
    
    if not conectas.exists():
        print("⚠️ Nenhum conecta encontrado")
        return
    
    for employee in employees[:3]:  # Apenas alguns para teste
        if not ConnectaPreference.objects.filter(employee=employee).exists():
            chosen_connecta = random.choice(conectas)
            preference = ConnectaPreference.objects.create(
                employee=employee,
                preferred_connecta=chosen_connecta,
                vote_count=1,
                effective=False
            )
            print(f"✓ Preferência: {employee.get_full_name()} → {chosen_connecta.get_full_name()}")

if __name__ == '__main__':
    try:
        print("🚀 Populando banco de dados com dados completos...")
        print("=" * 50)
        
        create_employees()
        create_voice_posts()
        create_mural_posts()
        create_mood_data()
        create_connecta_preferences()
        
        print("=" * 50)
        print("✅ Banco de dados populado com sucesso!")
        
        # Estatísticas
        print("\n📊 Estatísticas:")
        print(f"- Usuários: {User.objects.count()}")
        print(f"- Conectas: {Connecta.objects.count()}")
        print(f"- Posts de Voz: {VoicePost.objects.count()}")
        print(f"- Posts do Mural: {MuralPost.objects.count()}")
        print(f"- Check-ins de Humor: {MoodCheckin.objects.count()}")
        print(f"- Preferências de Conectas: {ConnectaPreference.objects.count()}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
