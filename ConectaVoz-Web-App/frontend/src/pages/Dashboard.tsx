// pages/Dashboard.tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/apiService';
import ApiHealthCheck from '../components/ApiHealthCheck';
import styles from './Dashboard.module.css';

interface DashboardStats {
  mood_checkins_today: number;
  voice_reports_pending: number;
  mural_posts_today: number;
  my_connecta: any;
  recent_activity: any[];
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const data = await apiService.getDashboardStats();
      setStats(data);
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Dashboard</h1>
        <p>Bem-vindo, {user?.first_name || user?.username}!</p>
      </header>

      <ApiHealthCheck />

      {loading ? (
        <div className={styles.loading}>Carregando dados...</div>
      ) : (
        <div className={styles.grid}>
          <div className={styles.card}>
            <h3>Check-in de Humor</h3>
            <p>Registre como você está se sentindo hoje</p>
            <div className={styles.emoji}>😊</div>
            {stats && (
              <div className={styles.stat}>
                {stats.mood_checkins_today} check-ins hoje
              </div>
            )}
          </div>

          <div className={styles.card}>
            <h3>Voz & Relatos</h3>
            <p>Compartilhe feedbacks e sugestões</p>
            <div className={styles.emoji}>💬</div>
            {stats && (
              <div className={styles.stat}>
                {stats.voice_reports_pending} relatos pendentes
              </div>
            )}
          </div>

          <div className={styles.card}>
            <h3>Mural da Equipe</h3>
            <p>Veja as novidades e interaja com a equipe</p>
            <div className={styles.emoji}>📰</div>
            {stats && (
              <div className={styles.stat}>
                {stats.mural_posts_today} posts hoje
              </div>
            )}
          </div>

          <div className={styles.card}>
            <h3>Conectas</h3>
            <p>Conheça e escolha seu Conecta</p>
            <div className={styles.emoji}>🤝</div>
            {stats?.my_connecta ? (
              <div className={styles.stat}>
                Conecta: {stats.my_connecta.first_name}
              </div>
            ) : (
              <div className={styles.stat}>
                Nenhum Conecta escolhido
              </div>
            )}
          </div>

          {(user?.role === 'diretoria' || user?.role === 'admin') && (
            <div className={styles.card}>
              <h3>Relatórios</h3>
              <p>Visualize métricas e análises</p>
              <div className={styles.emoji}>📊</div>
            </div>
          )}

        {user?.role === 'admin' && (
          <div className={styles.card}>
            <h3>Administração</h3>
            <p>Gerencie usuários e configurações</p>
            <div className={styles.emoji}>⚙️</div>
          </div>
        )}
        </div>
      )}

      <div className={styles.userInfo}>
        <h2>Informações do Usuário</h2>
        <div className={styles.infoGrid}>
          <div><strong>Nome:</strong> {user?.first_name} {user?.last_name}</div>
          <div><strong>Email:</strong> {user?.email}</div>
          <div><strong>Papel:</strong> {user?.role}</div>
          <div><strong>Departamento:</strong> {user?.department || 'Não informado'}</div>
          <div><strong>É Conecta:</strong> {user?.is_connecta ? 'Sim' : 'Não'}</div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
