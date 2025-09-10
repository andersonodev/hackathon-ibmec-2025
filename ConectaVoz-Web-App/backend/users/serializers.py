from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from .models import User

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de novos usuários
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'username', 
            'password', 'confirm_password', 'department', 'photo'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'department': {'required': True},
        }
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs
    
    def create(self, validated_data):
        # Remove confirm_password antes de criar
        validated_data.pop('confirm_password', None)
        
        # Gera username baseado no email se não fornecido
        if not validated_data.get('username'):
            email = validated_data['email']
            username = email.split('@')[0]
            
            # Garante que o username é único
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            validated_data['username'] = username
        
        # Cria o usuário com role padrão 'colaborador'
        validated_data['role'] = 'colaborador'
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer completo para usuários (admin)
    """
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'department', 'team', 'is_active', 'date_joined',
            'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para perfil do usuário (dados editáveis)
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'department', 'team'
        ]
        read_only_fields = ['id', 'username', 'role']


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Serializer básico para listagem de usuários
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'role']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para mudança de senha
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("As senhas não coincidem.")
        
        # Validar nova senha
        try:
            validate_password(attrs['new_password'])
        except Exception as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        
        return attrs


class ConnectaUserSerializer(serializers.ModelSerializer):
    """
    Serializer para usuários elegíveis como Conecta
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    is_connecta = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'is_connecta']
    
    def get_is_connecta(self, obj):
        return hasattr(obj, 'connecta') and obj.connecta.active
