// pages/PlaceholderPage.tsx
import React from 'react';
import styles from './PlaceholderPage.module.css';

interface PlaceholderPageProps {
  title: string;
  description: string;
  icon: string;
}

const PlaceholderPage: React.FC<PlaceholderPageProps> = ({
  title,
  description,
  icon,
}) => {
  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <div className={styles.icon}>{icon}</div>
        <h1 className={styles.title}>{title}</h1>
        <p className={styles.description}>{description}</p>
        <div className={styles.notice}>
          <p>Esta funcionalidade está em desenvolvimento.</p>
          <p>Em breve você poderá acessar todas as features da plataforma!</p>
        </div>
      </div>
    </div>
  );
};

export default PlaceholderPage;
