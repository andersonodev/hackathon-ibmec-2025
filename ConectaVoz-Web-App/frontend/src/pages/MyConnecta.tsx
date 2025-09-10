import React, { useState, useEffect } from 'react';
import { Users, MessageCircle, Star, Clock, CheckCircle, User, Send, X } from 'lucide-react';
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';
import styles from './MyConnecta.module.css';

interface Conecta {
  id: number;
  user: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
  };
  specialties: string[];
  bio: string;
  available_slots: number;
  current_connections: number;
  rating: number;
  response_time_hours: number;
  is_available: boolean;
  created_at: string;
}

interface MyConnection {
  id: number;
  conecta: Conecta;
  status: 'active' | 'pending' | 'inactive';
  created_at: string;
  last_interaction: string | null;
}

interface ChatMessage {
  id: number;
  sender_id: number;
  sender_name: string;
  content: string;
  timestamp: string;
  is_from_me: boolean;
}

const MyConnecta: React.FC = () => {
  const { user } = useAuth();
  const [myConnection, setMyConnection] = useState<MyConnection | null>(null);
  const [loading, setLoading] = useState(true);
  const [showChat, setShowChat] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loadingMessages, setLoadingMessages] = useState(false);

  useEffect(() => {
    loadMyConnection();
  }, []);

  const loadMyConnection = async () => {
    try {
      setLoading(true);
      const myConnectionResponse = await apiService.getMyConnections();
      const connections: any = Array.isArray(myConnectionResponse.data) ? myConnectionResponse.data : [myConnectionResponse.data];
      const activeConnection = connections.find((conn: any) => conn.status === 'active' || conn.status === 'pending');
      setMyConnection(activeConnection || null);
    } catch (error) {
      console.error('Erro ao carregar conexão:', error);
      setMyConnection(null);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelConnection = async () => {
    if (!myConnection) return;
    
    try {
      await apiService.rejectConnection(myConnection.id);
      await loadMyConnection();
    } catch (error) {
      console.error('Erro ao cancelar conexão:', error);
    }
  };

  const handleStartChat = () => {
    setShowChat(true);
    loadChatMessages();
  };

  const handleViewProfile = () => {
    console.log('Ver perfil de:', myConnection?.conecta.user.first_name);
    // TODO: Implementar modal de perfil detalhado
  };

  const handleRateConnecta = () => {
    console.log('Avaliar Conecta:', myConnection?.conecta.user.first_name);
    // TODO: Implementar modal de avaliação
  };

  const handleScheduleMeeting = () => {
    console.log('Agendar reunião com:', myConnection?.conecta.user.first_name);
    // TODO: Implementar sistema de agendamento
  };

  const loadChatMessages = async () => {
    if (!myConnection) return;
    
    try {
      setLoadingMessages(true);
      // TODO: Implementar endpoint de mensagens
      // const response = await apiService.getChatMessages(myConnection.id);
      // setChatMessages(response.data);
      
      // Dados mockados para demonstração
      const mockMessages: ChatMessage[] = [
        {
          id: 1,
          sender_id: myConnection.conecta.user.id,
          sender_name: `${myConnection.conecta.user.first_name} ${myConnection.conecta.user.last_name}`,
          content: 'Olá! Como posso ajudá-lo hoje?',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          is_from_me: false
        },
        {
          id: 2,
          sender_id: user?.id || 0,
          sender_name: user?.first_name || 'Você',
          content: 'Oi! Gostaria de conversar sobre algumas questões do trabalho.',
          timestamp: new Date(Date.now() - 1800000).toISOString(),
          is_from_me: true
        }
      ];
      setChatMessages(mockMessages);
    } catch (error) {
      console.error('Erro ao carregar mensagens:', error);
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !myConnection) return;

    try {
      // TODO: Implementar envio de mensagem real
      // await apiService.sendChatMessage(myConnection.id, newMessage);
      
      // Adicionar mensagem localmente (simulação)
      const newMsg: ChatMessage = {
        id: chatMessages.length + 1,
        sender_id: user?.id || 0,
        sender_name: user?.first_name || 'Você',
        content: newMessage,
        timestamp: new Date().toISOString(),
        is_from_me: true
      };
      
      setChatMessages(prev => [...prev, newMsg]);
      setNewMessage('');
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('pt-BR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#22c55e';
      case 'pending': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Ativo';
      case 'pending': return 'Pendente';
      case 'inactive': return 'Inativo';
      default: return status;
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Carregando informações do seu Conecta...</p>
        </div>
      </div>
    );
  }

  if (!myConnection) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <h1>
            <Users className={styles.headerIcon} />
            Meu Conecta
          </h1>
          <p>Veja informações do seu Conecta atual e gerencie sua conexão</p>
        </div>

        <div className={styles.emptyState}>
          <Users size={64} className={styles.emptyIcon} />
          <h2>Você ainda não tem um Conecta</h2>
          <p>Vá para a página de Conectas para escolher seu ponto de contato.</p>
          <button 
            className={styles.goToConnectasButton}
            onClick={() => window.location.href = '/conectas'}
          >
            Escolher Conecta
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>
          <CheckCircle className={styles.headerIcon} />
          Meu Conecta
        </h1>
        <p>Converse e gerencie sua conexão com seu Conecta</p>
      </div>

      {/* Informações do Conecta */}
      <div className={styles.connectaInfo}>
        <div className={styles.connectaCard}>
          <div className={styles.connectaHeader}>
            <div className={styles.connectaAvatar}>
              <User size={32} />
            </div>
            <div className={styles.connectaDetails}>
              <h2 className={styles.connectaName}>
                {myConnection.conecta.user.first_name} {myConnection.conecta.user.last_name}
              </h2>
              <p className={styles.connectaEmail}>
                {myConnection.conecta.user.email}
              </p>
              <div className={styles.specialties}>
                {myConnection.conecta.specialties.map((specialty, index) => (
                  <span key={index} className={styles.specialty}>
                    {specialty}
                  </span>
                ))}
              </div>
            </div>
            <div className={styles.connectionStatus}>
              <span 
                className={styles.status}
                style={{ backgroundColor: getStatusColor(myConnection.status) }}
              >
                {getStatusText(myConnection.status)}
              </span>
            </div>
          </div>

          <div className={styles.connectaStats}>
            <div className={styles.stat}>
              <Star size={16} />
              <span>{myConnection.conecta.rating.toFixed(1)}</span>
            </div>
            <div className={styles.stat}>
              <Clock size={16} />
              <span>Responde em {myConnection.conecta.response_time_hours}h</span>
            </div>
            <div className={styles.stat}>
              <Users size={16} />
              <span>{myConnection.conecta.current_connections}/{myConnection.conecta.available_slots} conexões</span>
            </div>
          </div>

          <div className={styles.connectionMeta}>
            <span className={styles.connectionDate}>
              Conectado em {formatDate(myConnection.created_at)}
            </span>
            {myConnection.last_interaction && (
              <span className={styles.lastInteraction}>
                Última interação: {formatDate(myConnection.last_interaction)}
              </span>
            )}
          </div>
        </div>

        {/* Biografia do Conecta */}
        {myConnection.conecta.bio && (
          <div className={styles.conectaBio}>
            <h3>Sobre seu Conecta</h3>
            <p>{myConnection.conecta.bio}</p>
          </div>
        )}
      </div>

      {/* Ações Rápidas */}
      <div className={styles.quickActions}>
        <h3>Ações</h3>
        <div className={styles.actionButtons}>
          {myConnection.status === 'active' && (
            <>
              <button 
                className={styles.primaryActionButton}
                onClick={handleStartChat}
              >
                <MessageCircle size={20} />
                <span>Conversar</span>
              </button>
              <button 
                className={styles.actionButton}
                onClick={handleViewProfile}
              >
                <User size={20} />
                <span>Ver Perfil</span>
              </button>
              <button 
                className={styles.actionButton}
                onClick={handleRateConnecta}
              >
                <Star size={20} />
                <span>Avaliar</span>
              </button>
              <button 
                className={styles.actionButton}
                onClick={handleScheduleMeeting}
              >
                <Clock size={20} />
                <span>Agendar</span>
              </button>
            </>
          )}
          {myConnection.status === 'pending' && (
            <div className={styles.pendingNotice}>
              <Clock size={20} />
              <span>Aguardando confirmação do Conecta</span>
            </div>
          )}
          <button 
            onClick={handleCancelConnection}
            className={styles.cancelButton}
          >
            Encerrar Conexão
          </button>
        </div>
      </div>

      {/* Modal do Chat */}
      {showChat && (
        <div className={styles.chatModal}>
          <div className={styles.chatContainer}>
            <div className={styles.chatHeader}>
              <div className={styles.chatHeaderInfo}>
                <div className={styles.chatAvatar}>
                  <User size={24} />
                </div>
                <div>
                  <h3>{myConnection.conecta.user.first_name} {myConnection.conecta.user.last_name}</h3>
                  <span className={styles.chatStatus}>Online</span>
                </div>
              </div>
              <button 
                onClick={() => setShowChat(false)}
                className={styles.closeChatButton}
              >
                <X size={24} />
              </button>
            </div>

            <div className={styles.chatMessages}>
              {loadingMessages ? (
                <div className={styles.loadingMessages}>
                  <div className={styles.spinner}></div>
                  <p>Carregando mensagens...</p>
                </div>
              ) : (
                chatMessages.map((message) => (
                  <div 
                    key={message.id} 
                    className={`${styles.message} ${message.is_from_me ? styles.myMessage : styles.theirMessage}`}
                  >
                    <div className={styles.messageContent}>
                      <p>{message.content}</p>
                      <span className={styles.messageTime}>
                        {formatTime(message.timestamp)}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className={styles.chatInput}>
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Digite sua mensagem..."
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                className={styles.messageInput}
              />
              <button 
                onClick={handleSendMessage}
                disabled={!newMessage.trim()}
                className={styles.sendButton}
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyConnecta;
