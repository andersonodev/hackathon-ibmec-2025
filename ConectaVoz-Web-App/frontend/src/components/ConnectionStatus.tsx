// components/ConnectionStatus.tsx
import React, { useState, useEffect } from 'react';
import { testBackendConnection } from '../utils/testConnection';
import styles from './ConnectionStatus.module.css';

const ConnectionStatus: React.FC = () => {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkConnection = async () => {
      setIsLoading(true);
      const connected = await testBackendConnection();
      setIsConnected(connected);
      setIsLoading(false);
    };

    checkConnection();
    
    // Verificar conexão a cada 30 segundos
    const interval = setInterval(checkConnection, 30000);
    
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className={styles.status}>
        <div className={styles.indicator}>
          <div className={styles.loading}></div>
        </div>
        <span>Verificando conexão...</span>
      </div>
    );
  }

  return (
    <div className={styles.status}>
      <div className={`${styles.indicator} ${isConnected ? styles.connected : styles.disconnected}`}>
        {isConnected ? '🟢' : '🔴'}
      </div>
      <span>
        {isConnected ? 'Backend conectado' : 'Backend desconectado'}
      </span>
    </div>
  );
};

export default ConnectionStatus;
