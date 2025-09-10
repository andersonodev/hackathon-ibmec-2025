// components/ProtectedRoute.tsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { UserRole } from '../types';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: UserRole[];
  requireAuth?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRoles = [],
  requireAuth = true,
}) => {
  const { isAuthenticated, user } = useAuth();

  // Se não estiver autenticado e a autenticação for obrigatória
  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Se estiver autenticado mas não há usuário (estado inconsistente)
  if (requireAuth && isAuthenticated && !user) {
    return <Navigate to="/login" replace />;
  }

  // Se há papéis específicos requeridos
  if (requiredRoles.length > 0 && user) {
    if (!requiredRoles.includes(user.role)) {
      // Redirecionar para uma página de acesso negado ou dashboard
      return <Navigate to="/dashboard" replace />;
    }
  }

  return <>{children}</>;
};

export default ProtectedRoute;
