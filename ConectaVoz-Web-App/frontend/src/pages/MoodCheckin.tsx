// pages/MoodCheckin.tsx
import React, { useState, useEffect } from 'react';
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';
import styles from './MoodCheckin.module.css';

interface MoodOption {
  level: number;
  emoji: string;
  label: string;
  color: string;
}

const moodOptions: MoodOption[] = [
  { level: 1, emoji: '😔', label: 'Péssimo', color: '#ef4444' },
  { level: 2, emoji: '😕', label: 'Ruim', color: '#f97316' },
  { level: 3, emoji: '😐', label: 'Regular', color: '#eab308' },
  { level: 4, emoji: '😊', label: 'Bom', color: '#22c55e' },
  { level: 5, emoji: '😄', label: 'Excelente', color: '#10b981' },
];

const MoodCheckin: React.FC = () => {
  const [selectedMood, setSelectedMood] = useState<number | null>(null);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);
  const [hasCheckedToday, setHasCheckedToday] = useState(false);
  const [todayCheckin, setTodayCheckin] = useState<any>(null);
  
  const { user } = useAuth();

  useEffect(() => {
    checkTodayCheckin();
  }, []);

  const checkTodayCheckin = async () => {
    try {
      const response = await apiService.getMoodHistory();
      const today = new Date().toISOString().split('T')[0];
      
      if (response.results) {
        const todayEntry = response.results.find((entry: any) => 
          entry.created_at.split('T')[0] === today
        );
        
        if (todayEntry) {
          setHasCheckedToday(true);
          setTodayCheckin(todayEntry);
          setSelectedMood(todayEntry.mood_level);
          setComment(todayEntry.comment || '');
        }
      }
    } catch (error) {
      console.error('Erro ao verificar check-in de hoje:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (selectedMood === null) {
      setMessage({ text: 'Por favor, selecione como você está se sentindo.', type: 'error' });
      return;
    }

    if (hasCheckedToday) {
      setMessage({ text: 'Você já fez seu check-in hoje!', type: 'error' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      await apiService.submitMoodCheckin(selectedMood, comment);
      setMessage({ 
        text: 'Check-in realizado com sucesso! Obrigado por compartilhar como você está se sentindo.', 
        type: 'success' 
      });
      setHasCheckedToday(true);
      
      // Reset form
      setSelectedMood(null);
      setComment('');
    } catch (error: any) {
      if (error.message.includes('409')) {
        setMessage({ text: 'Você já fez seu check-in hoje!', type: 'error' });
        setHasCheckedToday(true);
      } else {
        setMessage({ text: 'Erro ao realizar check-in. Tente novamente.', type: 'error' });
      }
    } finally {
      setLoading(false);
    }
  };

  const selectedMoodData = moodOptions.find(mood => mood.level === selectedMood);

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Check-in de Humor</h1>
        <p>Como você está se sentindo hoje, {user?.first_name || user?.username}?</p>
      </header>

      {hasCheckedToday && todayCheckin ? (
        <div className={styles.alreadyChecked}>
          <div className={styles.todayCheckin}>
            <h2>✅ Check-in de hoje realizado!</h2>
            <div className={styles.checkinSummary}>
              <div className={styles.moodDisplay}>
                <span className={styles.bigEmoji}>
                  {moodOptions.find(m => m.level === todayCheckin.mood_level)?.emoji}
                </span>
                <span className={styles.moodLabel}>
                  {moodOptions.find(m => m.level === todayCheckin.mood_level)?.label}
                </span>
              </div>
              {todayCheckin.comment && (
                <div className={styles.comment}>
                  <strong>Seu comentário:</strong>
                  <p>"{todayCheckin.comment}"</p>
                </div>
              )}
            </div>
            <p className={styles.returnTomorrow}>
              Volte amanhã para fazer um novo check-in! 🌅
            </p>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.moodSelector}>
            <label className={styles.sectionLabel}>Selecione seu humor atual:</label>
            <div className={styles.moodOptions}>
              {moodOptions.map((mood) => (
                <button
                  key={mood.level}
                  type="button"
                  className={`${styles.moodOption} ${
                    selectedMood === mood.level ? styles.selected : ''
                  }`}
                  onClick={() => setSelectedMood(mood.level)}
                  style={{
                    borderColor: selectedMood === mood.level ? mood.color : '#e5e7eb',
                    backgroundColor: selectedMood === mood.level ? `${mood.color}20` : 'white',
                  }}
                >
                  <span className={styles.emoji}>{mood.emoji}</span>
                  <span className={styles.label}>{mood.label}</span>
                </button>
              ))}
            </div>
          </div>

          {selectedMood && (
            <div className={styles.selectedMoodDisplay}>
              <p>
                Você selecionou: <strong>{selectedMoodData?.emoji} {selectedMoodData?.label}</strong>
              </p>
            </div>
          )}

          <div className={styles.commentSection}>
            <label htmlFor="comment" className={styles.sectionLabel}>
              Comentário (opcional):
            </label>
            <textarea
              id="comment"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Quer compartilhar mais detalhes sobre como está se sentindo? (opcional)"
              className={styles.commentInput}
              rows={4}
              maxLength={500}
            />
            <div className={styles.charCount}>
              {comment.length}/500 caracteres
            </div>
          </div>

          {message && (
            <div className={`${styles.message} ${styles[message.type]}`}>
              {message.text}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || selectedMood === null}
            className={styles.submitButton}
          >
            {loading ? 'Enviando...' : 'Fazer Check-in'}
          </button>
        </form>
      )}

      <div className={styles.info}>
        <h3>💡 Por que o check-in de humor é importante?</h3>
        <ul>
          <li>Ajuda a empresa a entender o clima organizacional</li>
          <li>Permite identificar tendências e padrões</li>
          <li>Contribui para um ambiente de trabalho mais saudável</li>
          <li>Seus dados são sempre anônimos e agregados</li>
        </ul>
      </div>
    </div>
  );
};

export default MoodCheckin;
