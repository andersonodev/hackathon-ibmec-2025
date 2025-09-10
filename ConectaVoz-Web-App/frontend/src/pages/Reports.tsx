import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, MessageSquare, Calendar, Download, Filter } from 'lucide-react';
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';
import styles from './Reports.module.css';

interface MoodData {
  date: string;
  mood_1: number; // Muito Triste
  mood_2: number; // Triste
  mood_3: number; // Neutro
  mood_4: number; // Feliz
  mood_5: number; // Muito Feliz
  total_checkins: number;
}

interface ReportStats {
  total_reports: number;
  pending_reports: number;
  resolved_reports: number;
  average_resolution_time: number;
  reports_by_category: { [key: string]: number };
}

interface DashboardMetrics {
  total_users: number;
  active_users_today: number;
  total_checkins_today: number;
  total_posts_today: number;
  conectas_available: number;
  conectas_busy: number;
}

const Reports: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'dashboard' | 'mood' | 'reports' | 'engagement'>('dashboard');
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [moodData, setMoodData] = useState<MoodData[]>([]);
  const [reportStats, setReportStats] = useState<ReportStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('7'); // últimos 7 dias
  const [department, setDepartment] = useState('all');

  useEffect(() => {
    loadData();
  }, [dateRange, department]);

  const loadData = async () => {
    try {
      const [metricsResponse, moodResponse, reportsResponse] = await Promise.all([
        apiService.getDashboardStats(),
        apiService.getMoodAnalytics(`${dateRange}d`),
        apiService.getVoiceReportsAnalytics(`${dateRange}d`)
      ]);

      setMetrics(metricsResponse);
      setMoodData(moodResponse.mood_data || []);
      setReportStats(reportsResponse);
    } catch (error) {
      console.error('Erro ao carregar dados dos relatórios:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMoodEmoji = (mood: number) => {
    const emojis = ['😢', '😕', '😐', '😊', '😁'];
    return emojis[mood - 1] || '😐';
  };

  const getMoodLabel = (mood: number) => {
    const labels = ['Muito Triste', 'Triste', 'Neutro', 'Feliz', 'Muito Feliz'];
    return labels[mood - 1] || 'Neutro';
  };

  const calculateMoodAverage = (data: MoodData[]) => {
    if (data.length === 0) return 0;
    
    let totalScore = 0;
    let totalCount = 0;
    
    data.forEach(day => {
      totalScore += (day.mood_1 * 1) + (day.mood_2 * 2) + (day.mood_3 * 3) + (day.mood_4 * 4) + (day.mood_5 * 5);
      totalCount += day.total_checkins;
    });
    
    return totalCount > 0 ? totalScore / totalCount : 0;
  };

  const exportData = async (type: string) => {
    try {
      await apiService.exportReportsData('csv', type);
    } catch (error) {
      console.error('Erro ao exportar dados:', error);
      alert('Erro ao exportar dados. Tente novamente.');
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Carregando relatórios...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>
          <BarChart3 className={styles.headerIcon} />
          Relatórios e Análises
        </h1>
        <p>Visualize métricas, dashboards e análises do clima organizacional</p>
      </div>

      {/* Filtros globais */}
      <div className={styles.filters}>
        <div className={styles.filterGroup}>
          <label>Período:</label>
          <select value={dateRange} onChange={(e) => setDateRange(e.target.value)}>
            <option value="7">Últimos 7 dias</option>
            <option value="30">Últimos 30 dias</option>
            <option value="90">Últimos 3 meses</option>
            <option value="365">Último ano</option>
          </select>
        </div>
        <div className={styles.filterGroup}>
          <label>Departamento:</label>
          <select value={department} onChange={(e) => setDepartment(e.target.value)}>
            <option value="all">Todos os departamentos</option>
            <option value="tecnologia">Tecnologia</option>
            <option value="vendas">Vendas</option>
            <option value="marketing">Marketing</option>
            <option value="rh">Recursos Humanos</option>
            <option value="financeiro">Financeiro</option>
          </select>
        </div>
      </div>

      {/* Tabs */}
      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${activeTab === 'dashboard' ? styles.active : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <BarChart3 size={18} />
          Dashboard
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'mood' ? styles.active : ''}`}
          onClick={() => setActiveTab('mood')}
        >
          <TrendingUp size={18} />
          Clima Organizacional
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'reports' ? styles.active : ''}`}
          onClick={() => setActiveTab('reports')}
        >
          <MessageSquare size={18} />
          Relatórios de Voz
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'engagement' ? styles.active : ''}`}
          onClick={() => setActiveTab('engagement')}
        >
          <Users size={18} />
          Engajamento
        </button>
      </div>

      {/* Dashboard */}
      {activeTab === 'dashboard' && metrics && (
        <div className={styles.tabContent}>
          <div className={styles.metricsGrid}>
            <div className={styles.metricCard}>
              <div className={styles.metricIcon}>
                <Users size={24} />
              </div>
              <div className={styles.metricValue}>{metrics.total_users}</div>
              <div className={styles.metricLabel}>Usuários Totais</div>
            </div>
            
            <div className={styles.metricCard}>
              <div className={styles.metricIcon} style={{ backgroundColor: '#22c55e' }}>
                <Users size={24} />
              </div>
              <div className={styles.metricValue}>{metrics.active_users_today}</div>
              <div className={styles.metricLabel}>Usuários Ativos Hoje</div>
            </div>
            
            <div className={styles.metricCard}>
              <div className={styles.metricIcon} style={{ backgroundColor: '#f59e0b' }}>
                <Calendar size={24} />
              </div>
              <div className={styles.metricValue}>{metrics.total_checkins_today}</div>
              <div className={styles.metricLabel}>Check-ins Hoje</div>
            </div>
            
            <div className={styles.metricCard}>
              <div className={styles.metricIcon} style={{ backgroundColor: '#8b5cf6' }}>
                <MessageSquare size={24} />
              </div>
              <div className={styles.metricValue}>{metrics.total_posts_today}</div>
              <div className={styles.metricLabel}>Posts no Mural Hoje</div>
            </div>
          </div>

          <div className={styles.connectasStatus}>
            <h3>Status dos Conectas</h3>
            <div className={styles.connectasGrid}>
              <div className={styles.conectaStatusCard}>
                <div className={styles.statusIndicator} style={{ backgroundColor: '#22c55e' }}></div>
                <div className={styles.statusInfo}>
                  <div className={styles.statusValue}>{metrics.conectas_available}</div>
                  <div className={styles.statusLabel}>Conectas Disponíveis</div>
                </div>
              </div>
              <div className={styles.conectaStatusCard}>
                <div className={styles.statusIndicator} style={{ backgroundColor: '#ef4444' }}></div>
                <div className={styles.statusInfo}>
                  <div className={styles.statusValue}>{metrics.conectas_busy}</div>
                  <div className={styles.statusLabel}>Conectas Ocupados</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Clima Organizacional */}
      {activeTab === 'mood' && (
        <div className={styles.tabContent}>
          <div className={styles.moodSection}>
            <div className={styles.sectionHeader}>
              <h3>Análise do Clima Organizacional</h3>
              <button onClick={() => exportData('mood')} className={styles.exportButton}>
                <Download size={16} />
                Exportar Dados
              </button>
            </div>

            <div className={styles.moodOverview}>
              <div className={styles.moodMetric}>
                <div className={styles.moodValue}>
                  {calculateMoodAverage(moodData).toFixed(1)}
                </div>
                <div className={styles.moodLabel}>Clima Médio</div>
                <div className={styles.moodEmoji}>
                  {getMoodEmoji(Math.round(calculateMoodAverage(moodData)))}
                </div>
              </div>

              <div className={styles.moodTrend}>
                <h4>Evolução do Clima (últimos {dateRange} dias)</h4>
                <div className={styles.moodChart}>
                  {moodData.map((day, index) => {
                    const average = day.total_checkins > 0 
                      ? ((day.mood_1 * 1) + (day.mood_2 * 2) + (day.mood_3 * 3) + (day.mood_4 * 4) + (day.mood_5 * 5)) / day.total_checkins
                      : 0;
                    
                    return (
                      <div key={index} className={styles.moodDay}>
                        <div className={styles.moodBar}>
                          <div 
                            className={styles.moodFill}
                            style={{ 
                              height: `${(average / 5) * 100}%`,
                              backgroundColor: average >= 4 ? '#22c55e' : average >= 3 ? '#f59e0b' : '#ef4444'
                            }}
                          ></div>
                        </div>
                        <div className={styles.moodDate}>
                          {new Date(day.date).toLocaleDateString('pt-BR', { 
                            day: '2-digit', 
                            month: '2-digit' 
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            <div className={styles.moodBreakdown}>
              <h4>Distribuição de Humor</h4>
              <div className={styles.moodBars}>
                {[1, 2, 3, 4, 5].map(mood => {
                  const total = moodData.reduce((sum, day) => {
                    const moodValue = day[`mood_${mood}` as keyof MoodData];
                    return sum + (typeof moodValue === 'number' ? moodValue : 0);
                  }, 0);
                  const overallTotal = moodData.reduce((sum, day) => sum + day.total_checkins, 0);
                  const percentage = overallTotal > 0 ? (total / overallTotal) * 100 : 0;
                  
                  return (
                    <div key={mood} className={styles.moodBarContainer}>
                      <div className={styles.moodBarLabel}>
                        <span className={styles.moodBarEmoji}>{getMoodEmoji(mood)}</span>
                        <span className={styles.moodBarText}>{getMoodLabel(mood)}</span>
                        <span className={styles.moodBarPercentage}>{percentage.toFixed(1)}%</span>
                      </div>
                      <div className={styles.moodBarTrack}>
                        <div 
                          className={styles.moodBarProgress}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Relatórios de Voz */}
      {activeTab === 'reports' && reportStats && (
        <div className={styles.tabContent}>
          <div className={styles.reportsSection}>
            <div className={styles.sectionHeader}>
              <h3>Análise de Relatórios de Voz</h3>
              <button onClick={() => exportData('reports')} className={styles.exportButton}>
                <Download size={16} />
                Exportar Dados
              </button>
            </div>

            <div className={styles.reportsGrid}>
              <div className={styles.reportCard}>
                <div className={styles.reportValue}>{reportStats.total_reports}</div>
                <div className={styles.reportLabel}>Total de Relatórios</div>
              </div>
              <div className={styles.reportCard}>
                <div className={styles.reportValue} style={{ color: '#f59e0b' }}>
                  {reportStats.pending_reports}
                </div>
                <div className={styles.reportLabel}>Pendentes</div>
              </div>
              <div className={styles.reportCard}>
                <div className={styles.reportValue} style={{ color: '#22c55e' }}>
                  {reportStats.resolved_reports}
                </div>
                <div className={styles.reportLabel}>Resolvidos</div>
              </div>
              <div className={styles.reportCard}>
                <div className={styles.reportValue}>
                  {reportStats.average_resolution_time.toFixed(1)}h
                </div>
                <div className={styles.reportLabel}>Tempo Médio de Resolução</div>
              </div>
            </div>

            <div className={styles.categoriesSection}>
              <h4>Relatórios por Categoria</h4>
              <div className={styles.categoriesList}>
                {Object.entries(reportStats.reports_by_category).map(([category, count]) => (
                  <div key={category} className={styles.categoryItem}>
                    <div className={styles.categoryName}>{category}</div>
                    <div className={styles.categoryCount}>{count}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Engajamento */}
      {activeTab === 'engagement' && (
        <div className={styles.tabContent}>
          <div className={styles.engagementSection}>
            <h3>Análise de Engajamento</h3>
            <div className={styles.comingSoon}>
              <Users size={48} />
              <h4>Métricas de Engajamento</h4>
              <p>Análises detalhadas de engajamento em desenvolvimento</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reports;
