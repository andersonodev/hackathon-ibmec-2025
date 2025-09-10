#!/usr/bin/env python
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conecta_voz.settings')
django.setup()

from django.contrib.auth import get_user_model
from connectas.models import Connecta

User = get_user_model()

def create_conectas():
    """Criar apenas conectas para teste"""
    print("🚀 Criando conectas de teste...")
    
    # Criar usuários conectas se não existirem
    conectas_data = [
        {
            'username': 'maria_silva_conecta',
            'first_name': 'Maria',
            'last_name': 'Silva',
            'email': 'maria.silva@empresa.com',
            'specialties': ['Liderança', 'Gestão de Pessoas'],
            'bio': 'Especialista em liderança com 15 anos de experiência.',
            'rating': 4.8
        },
        {
            'username': 'joao_santos_conecta',
            'first_name': 'João',
            'last_name': 'Santos',
            'email': 'joao.santos@empresa.com',
            'specialties': ['Desenvolvimento Técnico', 'Carreira'],
            'bio': 'Mentor técnico com foco em desenvolvimento de carreira.',
            'rating': 4.5
        },
        {
            'username': 'ana_costa_conecta',
            'first_name': 'Ana',
            'last_name': 'Costa',
            'email': 'ana.costa@empresa.com',
            'specialties': ['Bem-estar', 'Work-life Balance'],
            'bio': 'Consultora de bem-estar e equilíbrio vida-trabalho.',
            'rating': 4.9
        }
    ]
    
    for data in conectas_data:
        # Verificar se o usuário já existe
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': data['email'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'role': 'colaborador',
                'is_connecta': True
            }
        )
        
        if created:
            print(f"✓ Usuário conecta {user.get_full_name()} criado")
        
        # Verificar se o conecta já existe
        connecta, created = Connecta.objects.get_or_create(
            user=user,
            defaults={
                'active': True,
                'capacity_max': 12,
                'assigned_count': 0
            }
        )
        
        if created:
            print(f"✓ Conecta {connecta.user.get_full_name()} criado")
        else:
            print(f"→ Conecta {connecta.user.get_full_name()} já existe")

def create_test_employee():
    """Criar um usuário colaborador para teste"""
    print("👤 Criando usuário colaborador para teste...")
    
    user, created = User.objects.get_or_create(
        username='teste_colaborador',
        defaults={
            'email': 'teste@empresa.com',
            'first_name': 'Teste',
            'last_name': 'Colaborador',
            'role': 'colaborador'
        }
    )
    
    if created:
        user.set_password('123456')
        user.save()
        print(f"✓ Usuário colaborador {user.get_full_name()} criado (senha: 123456)")
    else:
        print(f"→ Usuário colaborador {user.get_full_name()} já existe")

if __name__ == '__main__':
    try:
        create_test_employee()
        create_conectas()
        print("✅ Conectas de teste criados com sucesso!")
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)
