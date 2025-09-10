// components/ApiHealthCheck.tsx
import React, { useState, useEffect } from 'react';
import { testBackendConnection } from '../utils/testConnection';
import styles from './ApiHealthCheck.module.css';

const ApiHealthCheck: React.FC = () => {
  const [status, setStatus] = useState<{
    backend: boolean | null;
    lastCheck: Date | null;
  }>({
    backend: null,
    lastCheck: null,
  });

  useEffect(() => {
    const checkHealth = async () => {
      const backendStatus = await testBackendConnection();
      setStatus({
        backend: backendStatus,
        lastCheck: new Date(),
      });
    };

    checkHealth();
  }, []);

  const formatTime = (date: Date | null) => {
    if (!date) return 'Nunca';
    return date.toLocaleTimeString('pt-BR');
  };

  return (
    <div className={styles.healthCheck}>
      <h3>Status da Conexão</h3>
      
      <div className={styles.statusGrid}>
        <div className={styles.statusItem}>
          <div className={styles.statusLabel}>Backend (Django)</div>
          <div className={`${styles.statusIndicator} ${
            status.backend === null ? styles.checking : 
            status.backend ? styles.healthy : styles.error
          }`}>
            {status.backend === null ? '⏳ Verificando...' : 
             status.backend ? '✅ Online' : '❌ Offline'}
          </div>
        </div>

        <div className={styles.statusItem}>
          <div className={styles.statusLabel}>Frontend (React)</div>
          <div className={`${styles.statusIndicator} ${styles.healthy}`}>
            ✅ Online
          </div>
        </div>

        <div className={styles.statusItem}>
          <div className={styles.statusLabel}>Última verificação</div>
          <div className={styles.timestamp}>
            {formatTime(status.lastCheck)}
          </div>
        </div>
      </div>

      <div className={styles.info}>
        <p><strong>Backend:</strong> http://localhost:8000</p>
        <p><strong>Frontend:</strong> http://localhost:3000</p>
      </div>
    </div>
  );
};

export default ApiHealthCheck;
