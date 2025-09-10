from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User
from .serializers import (
    UserSerializer, ProfileSerializer, ChangePasswordSerializer,
    UserRegistrationSerializer
)
from .permissions import RoleBasedPermission

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de usuários (apenas admin)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    
    def get_queryset(self):
        # Admin vê todos, outros veem apenas dados básicos do time
        if self.request.user.is_admin_role:
            return User.objects.all()
        elif self.request.user.team:
            return User.objects.filter(team=self.request.user.team).only(
                'id', 'first_name', 'last_name', 'username', 'role'
            )
        return User.objects.none()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Retorna dados do usuário logado
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ProfileView(APIView):
    """
    View para visualizar e editar perfil do usuário
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)
    
    def patch(self, request):
        serializer = ProfileSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    View para alterar senha
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Verificar senha atual
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': ['Senha atual incorreta.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar nova senha
            try:
                validate_password(serializer.validated_data['new_password'], user)
            except ValidationError as e:
                return Response(
                    {'new_password': e.messages},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Alterar senha
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Auditoria
            from audit.models import AuditLog
            AuditLog.log_action(
                actor=user,
                action='password_changed',
                category='auth',
                object_type='User',
                object_id=user.id,
                object_repr=str(user),
                request=request
            )
            
            return Response({'message': 'Senha alterada com sucesso.'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    View para logout (remove token)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Remover token se existir
            token = Token.objects.get(user=request.user)
            token.delete()
            
            # Auditoria
            from audit.models import AuditLog
            AuditLog.log_action(
                actor=request.user,
                action='logout',
                category='auth',
                object_type='User',
                object_id=request.user.id,
                object_repr=str(request.user),
                request=request
            )
            
            return Response({'message': 'Logout realizado com sucesso.'})
        except Token.DoesNotExist:
            return Response({'message': 'Logout realizado com sucesso.'})


class LoginView(APIView):
    """
    View customizada para login com auditoria
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)
                
                # Auditoria
                from audit.models import AuditLog
                AuditLog.log_action(
                    actor=user,
                    action='login',
                    category='auth',
                    object_type='User',
                    object_id=user.id,
                    object_repr=str(user),
                    request=request
                )
                
                return Response({
                    'token': token.key,
                    'user': UserSerializer(user).data
                })
            else:
                # Log de tentativa de login falhada
                from audit.models import AuditLog
                AuditLog.log_action(
                    actor=None,
                    action='login_failed',
                    category='auth',
                    object_type='User',
                    object_id=username,
                    meta={'username': username},
                    request=request
                )
                
                return Response(
                    {'error': 'Credenciais inválidas.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        return Response(
            {'error': 'Username e password são obrigatórios.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class RegisterView(APIView):
    """
    View para registro de novos usuários
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Cria token para o novo usuário
            token, created = Token.objects.get_or_create(user=user)
            
            # Log de auditoria
            from audit.models import AuditLog
            AuditLog.log_action(
                actor=user,
                action='register',
                category='auth',
                object_type='User',
                object_id=user.id,
                object_repr=str(user),
                request=request
            )
            
            return Response({
                'message': 'Usuário criado com sucesso!',
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': 'Dados inválidos.',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
