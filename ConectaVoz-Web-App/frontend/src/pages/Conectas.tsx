import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/apiService';
import { Users, Star, Clock, Search, Filter, X, User, CheckCircle } from 'lucide-react';
import styles from './Conectas.module.css';

interface ConnectaUser {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
}

interface Conecta {
  id: number;
  user: ConnectaUser;
  specialties: string[];
  bio: string;
  rating: number;
  total_reviews: number;
  response_time_hours: number;
  current_connections: number;
  available_slots: number;
  is_available: boolean;
}

interface ConnectionRequest {
  conecta_id: number;
  message: string;
}

const Conectas: React.FC = () => {
  const { user } = useAuth();
  const [conectas, setConnectas] = useState<Conecta[]>([]);
  const [filteredConnectas, setFilteredConnectas] = useState<Conecta[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSpecialty, setSelectedSpecialty] = useState('');
  const [showAvailableOnly, setShowAvailableOnly] = useState(false);
  const [selectedConnecta, setSelectedConnecta] = useState<Conecta | null>(null);
  const [requestMessage, setRequestMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [hasActiveConnection, setHasActiveConnection] = useState(false);

  // Lista de especialidades disponíveis
  const availableSpecialties = [
    'Recursos Humanos',
    'Tecnologia',
    'Marketing',
    'Vendas',
    'Finanças',
    'Operações',
    'Jurídico',
    'Administrativo'
  ];

  useEffect(() => {
    fetchConnectas();
    checkActiveConnection();
  }, []);

  useEffect(() => {
    filterConnectas();
  }, [conectas, searchTerm, selectedSpecialty, showAvailableOnly]);

  const fetchConnectas = async () => {
    try {
      setLoading(true);
      const response = await apiService.get('/conectas/');
      setConnectas(response.data || []);
    } catch (error) {
      console.error('Erro ao carregar conectas:', error);
      // Mock data para desenvolvimento
      const mockConnectas: Conecta[] = [
        {
          id: 1,
          user: {
            id: 1,
            first_name: 'Maria',
            last_name: 'Silva',
            email: 'maria.silva@empresa.com'
          },
          specialties: ['Recursos Humanos', 'Desenvolvimento Pessoal'],
          bio: 'Especialista em RH com mais de 10 anos de experiência em desenvolvimento de pessoas e cultura organizacional.',
          rating: 4.8,
          total_reviews: 45,
          response_time_hours: 2,
          current_connections: 8,
          available_slots: 15,
          is_available: true
        },
        {
          id: 2,
          user: {
            id: 2,
            first_name: 'João',
            last_name: 'Santos',
            email: 'joao.santos@empresa.com'
          },
          specialties: ['Tecnologia', 'Inovação'],
          bio: 'Desenvolvedor sênior e líder técnico, apaixonado por mentoria e crescimento profissional.',
          rating: 4.9,
          total_reviews: 32,
          response_time_hours: 1,
          current_connections: 12,
          available_slots: 20,
          is_available: true
        },
        {
          id: 3,
          user: {
            id: 3,
            first_name: 'Ana',
            last_name: 'Costa',
            email: 'ana.costa@empresa.com'
          },
          specialties: ['Marketing', 'Comunicação'],
          bio: 'Especialista em marketing digital e estratégias de comunicação corporativa.',
          rating: 4.7,
          total_reviews: 28,
          response_time_hours: 3,
          current_connections: 15,
          available_slots: 15,
          is_available: false
        }
      ];
      setConnectas(mockConnectas);
    } finally {
      setLoading(false);
    }
  };

  const checkActiveConnection = async () => {
    try {
      const response = await apiService.get('/my-connecta/');
      setHasActiveConnection(!!response.data);
    } catch (error) {
      // Se der erro, assume que não tem conexão ativa
      setHasActiveConnection(false);
    }
  };

  const filterConnectas = () => {
    let filtered = conectas;

    // Filtro por termo de busca
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(conecta => 
        conecta.user.first_name.toLowerCase().includes(term) ||
        conecta.user.last_name.toLowerCase().includes(term) ||
        conecta.specialties.some(specialty => 
          specialty.toLowerCase().includes(term)
        ) ||
        conecta.bio.toLowerCase().includes(term)
      );
    }

    // Filtro por especialidade
    if (selectedSpecialty) {
      filtered = filtered.filter(conecta =>
        conecta.specialties.includes(selectedSpecialty)
      );
    }

    // Filtro por disponibilidade
    if (showAvailableOnly) {
      filtered = filtered.filter(conecta => conecta.is_available);
    }

    setFilteredConnectas(filtered);
  };

  const handleConnectRequest = async () => {
    if (!selectedConnecta || !requestMessage.trim()) return;

    try {
      setSubmitting(true);
      const requestData: ConnectionRequest = {
        conecta_id: selectedConnecta.id,
        message: requestMessage.trim()
      };

      await apiService.post('/connection-requests/', requestData);
      
      alert('Solicitação de conexão enviada com sucesso!');
      setSelectedConnecta(null);
      setRequestMessage('');
      checkActiveConnection(); // Recheck connection status
    } catch (error) {
      console.error('Erro ao enviar solicitação:', error);
      alert('Erro ao enviar solicitação. Tente novamente.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatSpecialties = (specialties: string[]) => {
    return specialties.slice(0, 2).join(', ') + 
           (specialties.length > 2 ? ` +${specialties.length - 2}` : '');
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Carregando conectas...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>
          <Users className={styles.headerIcon} />
          Conectas
        </h1>
        <p>Encontre e conecte-se com profissionais que podem te ajudar</p>
      </div>

      {/* Aviso para usuários com conexão ativa */}
      {hasActiveConnection && (
        <div className={styles.activeConnectionNotice}>
          <CheckCircle size={20} />
          <div>
            <strong>Você já tem um Conecta ativo!</strong>
            <p>Vá para "Meu Conecta" para conversar e gerenciar sua conexão atual.</p>
          </div>
          <button 
            className={styles.goToMyConnectaButton}
            onClick={() => window.location.href = '/my-connecta'}
          >
            Ir para Meu Conecta
          </button>
        </div>
      )}

      {/* Filtros */}
      <div className={styles.filters}>
        <div className={styles.searchBox}>
          <Search size={20} className={styles.searchIcon} />
          <input
            type="text"
            placeholder="Buscar por nome, especialidade ou palavras-chave..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={styles.searchInput}
          />
        </div>

        <div className={styles.filterRow}>
          <div className={styles.filterGroup}>
            <Filter size={16} />
            <select
              value={selectedSpecialty}
              onChange={(e) => setSelectedSpecialty(e.target.value)}
              className={styles.filterSelect}
            >
              <option value="">Todas as especialidades</option>
              {availableSpecialties.map(specialty => (
                <option key={specialty} value={specialty}>
                  {specialty}
                </option>
              ))}
            </select>
          </div>

          <label className={styles.checkbox}>
            <input
              type="checkbox"
              checked={showAvailableOnly}
              onChange={(e) => setShowAvailableOnly(e.target.checked)}
            />
            <span>Apenas disponíveis</span>
          </label>
        </div>
      </div>

      {/* Grid de Conectas */}
      <div className={styles.conectasGrid}>
        {filteredConnectas.length === 0 ? (
          <div className={styles.emptyState}>
            <Users size={64} className={styles.emptyIcon} />
            <h2>Nenhum conecta encontrado</h2>
            <p>Tente ajustar os filtros para encontrar mais resultados.</p>
          </div>
        ) : (
          filteredConnectas.map(conecta => (
            <div key={conecta.id} className={styles.conectaCard}>
              <div className={styles.conectaHeader}>
                <div className={styles.conectaAvatar}>
                  <User size={32} />
                </div>
                <div className={styles.conectaInfo}>
                  <h3 className={styles.conectaName}>
                    {conecta.user.first_name} {conecta.user.last_name}
                  </h3>
                  <p className={styles.conectaSpecialties}>
                    {formatSpecialties(conecta.specialties)}
                  </p>
                </div>
                <span 
                  className={`${styles.availability} ${conecta.is_available ? styles.available : styles.unavailable}`}
                >
                  {conecta.is_available ? 'Disponível' : 'Indisponível'}
                </span>
              </div>

              <p className={styles.conectaBio}>
                {conecta.bio.length > 100 ? conecta.bio.substring(0, 100) + '...' : conecta.bio}
              </p>

              <div className={styles.conectaStats}>
                <div className={styles.stat}>
                  <Star size={16} />
                  <span>{conecta.rating.toFixed(1)} ({conecta.total_reviews})</span>
                </div>
                <div className={styles.stat}>
                  <Clock size={16} />
                  <span>Responde em {conecta.response_time_hours}h</span>
                </div>
                <div className={styles.stat}>
                  <Users size={16} />
                  <span>{conecta.current_connections}/{conecta.available_slots}</span>
                </div>
              </div>

              <div className={styles.conectaActions}>
                <button 
                  className={styles.viewButton}
                  onClick={() => setSelectedConnecta(conecta)}
                >
                  Ver Detalhes
                </button>
                {conecta.is_available && !hasActiveConnection && (
                  <button 
                    className={styles.connectButton}
                    onClick={() => setSelectedConnecta(conecta)}
                  >
                    Conectar
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal de Detalhes/Conexão */}
      {selectedConnecta && (
        <div className={styles.modal}>
          <div className={styles.modalContent}>
            <div className={styles.modalHeader}>
              <h2>
                {selectedConnecta.user.first_name} {selectedConnecta.user.last_name}
              </h2>
              <button 
                onClick={() => setSelectedConnecta(null)}
                className={styles.closeButton}
              >
                <X size={24} />
              </button>
            </div>

            <div className={styles.modalBody}>
              <div className={styles.conectaDetails}>
                <div className={styles.conectaAvatar}>
                  <User size={48} />
                </div>
                <div className={styles.conectaMainInfo}>
                  <p className={styles.conectaEmail}>{selectedConnecta.user.email}</p>
                  <div className={styles.specialties}>
                    {selectedConnecta.specialties.map((specialty, index) => (
                      <span key={index} className={styles.specialty}>
                        {specialty}
                      </span>
                    ))}
                  </div>
                  <span 
                    className={`${styles.availability} ${selectedConnecta.is_available ? styles.available : styles.unavailable}`}
                  >
                    {selectedConnecta.is_available ? 'Disponível' : 'Indisponível'}
                  </span>
                </div>
              </div>

              <div className={styles.conectaDescription}>
                <h3>Sobre</h3>
                <p>{selectedConnecta.bio}</p>
              </div>

              <div className={styles.conectaMetrics}>
                <div className={styles.metric}>
                  <Star size={20} />
                  <div>
                    <span className={styles.metricValue}>{selectedConnecta.rating.toFixed(1)}</span>
                    <span className={styles.metricLabel}>Avaliação ({selectedConnecta.total_reviews} reviews)</span>
                  </div>
                </div>
                <div className={styles.metric}>
                  <Clock size={20} />
                  <div>
                    <span className={styles.metricValue}>{selectedConnecta.response_time_hours}h</span>
                    <span className={styles.metricLabel}>Tempo de resposta</span>
                  </div>
                </div>
                <div className={styles.metric}>
                  <Users size={20} />
                  <div>
                    <span className={styles.metricValue}>{selectedConnecta.current_connections}/{selectedConnecta.available_slots}</span>
                    <span className={styles.metricLabel}>Conexões ativas</span>
                  </div>
                </div>
              </div>

              {selectedConnecta.is_available && !hasActiveConnection && (
                <div className={styles.connectionRequest}>
                  <h3>Solicitar Conexão</h3>
                  <textarea
                    value={requestMessage}
                    onChange={(e) => setRequestMessage(e.target.value)}
                    placeholder="Escreva uma mensagem explicando por que gostaria de se conectar com este profissional..."
                    className={styles.requestMessage}
                    rows={4}
                  />
                  <div className={styles.modalActions}>
                    <button 
                      onClick={() => setSelectedConnecta(null)}
                      className={styles.cancelButton}
                    >
                      Cancelar
                    </button>
                    <button 
                      onClick={handleConnectRequest}
                      disabled={!requestMessage.trim() || submitting}
                      className={styles.connectButton}
                    >
                      {submitting ? 'Enviando...' : 'Solicitar Conexão'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Conectas;
