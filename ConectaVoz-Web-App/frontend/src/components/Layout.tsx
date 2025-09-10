// components/Layout.tsx
import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from './Sidebar';
import styles from './Layout.module.css';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isAuthenticated, user, logout } = useAuth();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className={styles.layout}>
      <Sidebar 
        userRole={user.role} 
        onLogout={logout}
        onCollapseChange={setIsSidebarCollapsed}
      />
      <main className={`${styles.main} ${isSidebarCollapsed ? styles.collapsed : ''}`}>
        <div className={styles.content}>
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
