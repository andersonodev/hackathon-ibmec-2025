import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  SmilePlus,
  MessageSquareQuote,
  Newspaper,
  HeartHandshake,
  UserCheck,
  BarChart3,
  SlidersHorizontal,
  LogOut,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import ConnectionStatus from './ConnectionStatus';
import styles from './Sidebar.module.css';

type UserRole = 'colaborador' | 'diretoria' | 'admin';

interface SidebarProps {
  userRole: UserRole;
  onLogout?: () => void;
  onCollapseChange?: (collapsed: boolean) => void;
}

interface MenuItem {
  icon: React.ReactNode;
  label: string;
  path: string;
  visibleFor: UserRole[];
}

const Sidebar: React.FC<SidebarProps> = ({ userRole, onLogout, onCollapseChange }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const navigate = useNavigate();

  const menuItems: MenuItem[] = [
    {
      icon: <LayoutDashboard size={20} strokeWidth={1.5} />,
      label: 'Dashboard',
      path: '/dashboard',
      visibleFor: ['colaborador', 'diretoria', 'admin'],
    },
    {
      icon: <SmilePlus size={20} strokeWidth={1.5} />,
      label: 'Check-in de Humor',
      path: '/check-in',
      visibleFor: ['colaborador', 'diretoria', 'admin'],
    },
    {
      icon: <MessageSquareQuote size={20} strokeWidth={1.5} />,
      label: 'Voz & Relatos',
      path: '/voice',
      visibleFor: ['colaborador', 'diretoria', 'admin'],
    },
    {
      icon: <Newspaper size={20} strokeWidth={1.5} />,
      label: 'Mural da Equipe',
      path: '/mural',
      visibleFor: ['colaborador', 'diretoria', 'admin'],
    },
    {
      icon: <HeartHandshake size={20} strokeWidth={1.5} />,
      label: 'Conectas',
      path: '/conectas',
      visibleFor: ['colaborador', 'diretoria', 'admin'],
    },
    {
      icon: <UserCheck size={20} strokeWidth={1.5} />,
      label: 'Meu Conecta',
      path: '/my-connecta',
      visibleFor: ['colaborador', 'diretoria', 'admin'],
    },
    {
      icon: <BarChart3 size={20} strokeWidth={1.5} />,
      label: 'Relatórios',
      path: '/relatorios',
      visibleFor: ['diretoria', 'admin'],
    },
    {
      icon: <SlidersHorizontal size={20} strokeWidth={1.5} />,
      label: 'Administração',
      path: '/administracao',
      visibleFor: ['admin'],
    },
  ];

  const handleLogout = () => {
    if (onLogout) {
      onLogout();
    }
    // Adicionar lógica de logout aqui (ex: limpar localStorage, tokens, etc.)
    localStorage.removeItem('token');
    navigate('/login');
  };

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  const toggleCollapse = () => {
    const newCollapsedState = !isCollapsed;
    setIsCollapsed(newCollapsedState);
    onCollapseChange?.(newCollapsedState);
  };

  const filteredMenuItems = menuItems.filter((item) =>
    item.visibleFor.includes(userRole)
  );

  return (
    <aside className={`${styles.sidebar} ${isCollapsed ? styles.collapsed : ''}`}>
      {/* Header com Logo */}
      <div className={styles.header}>
        {!isCollapsed && (
          <img
            src="/conectavoz.svg"
            alt="Conecta Voz"
            className={styles.logo}
          />
        )}
        <button
          className={styles.toggleButton}
          onClick={toggleCollapse}
          aria-label={isCollapsed ? 'Expandir menu' : 'Recolher menu'}
        >
          {isCollapsed ? (
            <ChevronRight size={20} strokeWidth={1.5} />
          ) : (
            <ChevronLeft size={20} strokeWidth={1.5} />
          )}
        </button>
      </div>

      {/* Navegação Principal */}
      <nav className={styles.nav}>
        <ul className={styles.menuList}>
          {filteredMenuItems.map((item) => (
            <li key={item.path} className={styles.menuItem}>
              <button
                className={styles.menuButton}
                onClick={() => handleNavigation(item.path)}
                title={isCollapsed ? item.label : ''}
                aria-label={item.label}
              >
                <span className={styles.menuIcon}>{item.icon}</span>
                {!isCollapsed && (
                  <span className={styles.menuLabel}>{item.label}</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer com Logout */}
      <div className={styles.footer}>
        {!isCollapsed && <ConnectionStatus />}
        
        <button
          className={styles.logoutButton}
          onClick={handleLogout}
          title={isCollapsed ? 'Sair' : ''}
          aria-label="Sair do sistema"
        >
          <span className={styles.menuIcon}>
            <LogOut size={20} strokeWidth={1.5} />
          </span>
          {!isCollapsed && <span className={styles.menuLabel}>Sair</span>}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
