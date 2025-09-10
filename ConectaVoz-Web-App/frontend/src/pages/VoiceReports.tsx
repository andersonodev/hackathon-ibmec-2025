// pages/VoiceReports.tsx
import React, { useState, useEffect } from 'react';
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';
import { MessageSquareQuote, Send, Paperclip, User } from 'lucide-react';
import styles from './VoiceReports.module.css';

interface VoiceReport {
  id: number;
  title: string;
  content: string;
  category: string;
  status: string;
  created_at: string;
  connecta_name?: string;
}

const categories = [
  { value: 'feedback', label: 'Feedback' },
  { value: 'sugestao', label: 'Sugestão' },
  { value: 'reclamacao', label: 'Reclamação' },
  { value: 'denuncia', label: 'Denúncia' },
  { value: 'elogio', label: 'Elogio' },
  { value: 'outro', label: 'Outro' },
];

const VoiceReports: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'new' | 'history'>('new');
  const [myConnecta, setMyConnecta] = useState<any>(null);
  const [reports, setReports] = useState<VoiceReport[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: 'feedback',
    attachments: [] as File[],
  });
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);
  
  const { user } = useAuth();

  useEffect(() => {
    loadMyConnecta();
    if (activeTab === 'history') {
      loadReports();
    }
  }, [activeTab]);

  const loadMyConnecta = async () => {
    try {
      const connecta = await apiService.getMyConnecta();
      setMyConnecta(connecta);
    } catch (error) {
      console.error('Erro ao carregar Conecta:', error);
    }
  };

  const loadReports = async () => {
    try {
      setLoading(true);
      const response = await apiService.getVoiceReports();
      setReports(response.results || []);
    } catch (error) {
      console.error('Erro ao carregar relatórios:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim() || !formData.content.trim()) {
      setMessage({ text: 'Por favor, preencha o título e o conteúdo.', type: 'error' });
      return;
    }

    if (!myConnecta) {
      setMessage({ text: 'Você precisa escolher um Conecta antes de enviar um relato. Acesse a página "Conectas".', type: 'error' });
      return;
    }

    setSubmitting(true);
    setMessage(null);

    try {
      await apiService.submitVoiceReport({
        title: formData.title,
        content: formData.content,
        category: formData.category,
        attachments: formData.attachments
      });
      setMessage({ 
        text: 'Relato enviado com sucesso! Seu Conecta receberá a mensagem.', 
        type: 'success' 
      });
      
      // Reset form
      setFormData({
        title: '',
        content: '',
        category: 'feedback',
        attachments: [],
      });
    } catch (error: any) {
      setMessage({ text: 'Erro ao enviar relato. Tente novamente.', type: 'error' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusBadge = (status: string) => {
    const statusMap = {
      'pendente': { label: 'Pendente', color: '#eab308' },
      'em_analise': { label: 'Em Análise', color: '#3b82f6' },
      'resolvido': { label: 'Resolvido', color: '#10b981' },
      'escalado': { label: 'Escalado', color: '#f59e0b' },
    };
    
    const statusInfo = statusMap[status as keyof typeof statusMap] || { label: status, color: '#6b7280' };
    
    return (
      <span 
        className={styles.statusBadge}
        style={{ backgroundColor: `${statusInfo.color}20`, color: statusInfo.color }}
      >
        {statusInfo.label}
      </span>
    );
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>
          <MessageSquareQuote size={32} />
          Voz & Relatos
        </h1>
        <p>Compartilhe feedbacks, sugestões e relatos de forma privada com seu Conecta</p>
      </header>

      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${activeTab === 'new' ? styles.active : ''}`}
          onClick={() => setActiveTab('new')}
        >
          Novo Relato
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'history' ? styles.active : ''}`}
          onClick={() => setActiveTab('history')}
        >
          Meus Relatos
        </button>
      </div>

      {activeTab === 'new' && (
        <div className={styles.newReport}>
          {myConnecta ? (
            <div className={styles.connectaInfo}>
              <div className={styles.connectaCard}>
                <User size={20} />
                <div>
                  <strong>Enviando para:</strong> {myConnecta.first_name} {myConnecta.last_name}
                  <br />
                  <small>{myConnecta.department || 'Conecta'}</small>
                </div>
              </div>
            </div>
          ) : (
            <div className={styles.noConnecta}>
              <p>⚠️ Você ainda não escolheu um Conecta.</p>
              <p>Para enviar relatos, acesse a página "Conectas" e escolha seu ponto de contato.</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.field}>
              <label htmlFor="category">Categoria:</label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                className={styles.select}
              >
                {categories.map(cat => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            <div className={styles.field}>
              <label htmlFor="title">Título:</label>
              <input
                id="title"
                name="title"
                type="text"
                value={formData.title}
                onChange={handleInputChange}
                placeholder="Descreva brevemente o assunto"
                className={styles.input}
                maxLength={100}
                required
              />
              <div className={styles.charCount}>{formData.title.length}/100</div>
            </div>

            <div className={styles.field}>
              <label htmlFor="content">Conteúdo:</label>
              <textarea
                id="content"
                name="content"
                value={formData.content}
                onChange={handleInputChange}
                placeholder="Descreva sua situação, feedback ou sugestão de forma detalhada..."
                className={styles.textarea}
                rows={8}
                maxLength={2000}
                required
              />
              <div className={styles.charCount}>{formData.content.length}/2000</div>
            </div>

            <div className={styles.attachments}>
              <button type="button" className={styles.attachButton} disabled>
                <Paperclip size={16} />
                Anexar arquivo (em breve)
              </button>
            </div>

            {message && (
              <div className={`${styles.message} ${styles[message.type]}`}>
                {message.text}
              </div>
            )}

            <button
              type="submit"
              disabled={submitting || !myConnecta}
              className={styles.submitButton}
            >
              <Send size={16} />
              {submitting ? 'Enviando...' : 'Enviar Relato'}
            </button>
          </form>
        </div>
      )}

      {activeTab === 'history' && (
        <div className={styles.history}>
          {loading ? (
            <div className={styles.loading}>Carregando seus relatos...</div>
          ) : reports.length === 0 ? (
            <div className={styles.empty}>
              <MessageSquareQuote size={48} />
              <p>Você ainda não enviou nenhum relato.</p>
              <button
                onClick={() => setActiveTab('new')}
                className={styles.newReportButton}
              >
                Enviar primeiro relato
              </button>
            </div>
          ) : (
            <div className={styles.reportsList}>
              {reports.map(report => (
                <div key={report.id} className={styles.reportCard}>
                  <div className={styles.reportHeader}>
                    <h3>{report.title}</h3>
                    <div className={styles.reportMeta}>
                      {getStatusBadge(report.status)}
                      <span className={styles.category}>
                        {categories.find(c => c.value === report.category)?.label}
                      </span>
                    </div>
                  </div>
                  <p className={styles.reportContent}>
                    {report.content.length > 150 
                      ? `${report.content.substring(0, 150)}...` 
                      : report.content
                    }
                  </p>
                  <div className={styles.reportFooter}>
                    <span className={styles.date}>
                      {formatDate(report.created_at)}
                    </span>
                    {report.connecta_name && (
                      <span className={styles.connecta}>
                        Conecta: {report.connecta_name}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className={styles.info}>
        <h3>🔒 Privacidade e Segurança</h3>
        <ul>
          <li>Seus relatos são enviados apenas para o Conecta que você escolheu</li>
          <li>Apenas você e seu Conecta podem ver o conteúdo</li>
          <li>Relatos nunca são publicados no Mural da Equipe</li>
          <li>Seu Conecta pode te responder de forma privada</li>
        </ul>
      </div>
    </div>
  );
};

export default VoiceReports;
