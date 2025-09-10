import React, { useState, useEffect } from 'react';
import { MessageSquare, Heart, Users, Plus, Eye, EyeOff } from 'lucide-react';
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';
import styles from './Mural.module.css';

interface Post {
  id: number;
  text: string; // Campo correto do backend
  team: string;
  anonymous: boolean;
  emoji: number;
  status: string;
  created_at: string;
  reactions: { [key: string]: number };
}

interface Comment {
  id: number;
  content: string;
  author: string | null;
  is_anonymous: boolean;
  created_at: string;
  post: number;
}

const Mural: React.FC = () => {
  const { user } = useAuth();
  const [posts, setPosts] = useState<Post[]>([]);
  const [newPost, setNewPost] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [expandedPosts, setExpandedPosts] = useState<Set<number>>(new Set());
  const [comments, setComments] = useState<{ [key: number]: Comment[] }>({});
  const [newComment, setNewComment] = useState<{ [key: number]: string }>({});

  useEffect(() => {
    loadPosts();
  }, []);

  const loadPosts = async () => {
    try {
      const response = await apiService.get('/mural/posts/');
      // O Django REST Framework retorna dados paginados
      setPosts(response.data.results || response.data);
    } catch (error) {
      console.error('Erro ao carregar posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitPost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPost.trim() || submitting) return;

    setSubmitting(true);
    try {
      const postData = {
        content: newPost.trim(),
        is_anonymous: isAnonymous
      };

      const response = await apiService.post('/mural/posts/', postData);
      
      // Adiciona o novo post ao topo da lista
      setPosts(prevPosts => [response.data, ...prevPosts]);
      setNewPost('');
      setIsAnonymous(false);
    } catch (error) {
      console.error('Erro ao criar post:', error);
      alert('Erro ao publicar post. Tente novamente.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleLike = async (postId: number) => {
    try {
      const response = await apiService.post(`/mural/posts/${postId}/like/`);
      
      setPosts(prevPosts =>
        prevPosts.map(post =>
          post.id === postId
            ? {
                ...post,
                is_liked: response.data.liked,
                likes_count: response.data.likes_count
              }
            : post
        )
      );
    } catch (error) {
      console.error('Erro ao curtir post:', error);
    }
  };

  const loadComments = async (postId: number) => {
    try {
      const response = await apiService.get(`/mural/posts/${postId}/comments/`);
      setComments(prev => ({
        ...prev,
        [postId]: response.data
      }));
    } catch (error) {
      console.error('Erro ao carregar comentários:', error);
    }
  };

  const toggleComments = async (postId: number) => {
    const isExpanded = expandedPosts.has(postId);
    
    if (isExpanded) {
      setExpandedPosts(prev => {
        const newSet = new Set(prev);
        newSet.delete(postId);
        return newSet;
      });
    } else {
      setExpandedPosts(prev => new Set(prev).add(postId));
      if (!comments[postId]) {
        await loadComments(postId);
      }
    }
  };

  const handleSubmitComment = async (postId: number, e: React.FormEvent) => {
    e.preventDefault();
    const commentText = newComment[postId];
    if (!commentText?.trim()) return;

    try {
      const commentData = {
        content: commentText.trim(),
        is_anonymous: false // Por simplicidade, comentários sempre identificados
      };

      const response = await apiService.post(`/mural/posts/${postId}/comments/`, commentData);
      
      setComments(prev => ({
        ...prev,
        [postId]: [...(prev[postId] || []), response.data]
      }));

      setPosts(prevPosts =>
        prevPosts.map(post =>
          post.id === postId
            ? { ...post } // Remover increment de comments_count temporariamente
            : post
        )
      );

      setNewComment(prev => ({ ...prev, [postId]: '' }));
    } catch (error) {
      console.error('Erro ao comentar:', error);
      alert('Erro ao publicar comentário. Tente novamente.');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

    if (diffInHours < 1) {
      return 'Agora há pouco';
    } else if (diffInHours < 24) {
      return `${diffInHours}h atrás`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      if (diffInDays === 1) {
        return 'Ontem';
      } else if (diffInDays < 7) {
        return `${diffInDays} dias atrás`;
      } else {
        return date.toLocaleDateString('pt-BR');
      }
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Carregando posts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>
          <Users className={styles.headerIcon} />
          Mural da Equipe
        </h1>
        <p>Compartilhe ideias, celebre conquistas e conecte-se com sua equipe</p>
      </div>

      {/* Formulário para novo post */}
      <div className={styles.newPostCard}>
        <h2>Compartilhar algo</h2>
        <form onSubmit={handleSubmitPost}>
          <textarea
            value={newPost}
            onChange={(e) => setNewPost(e.target.value)}
            placeholder="O que você gostaria de compartilhar com a equipe?"
            className={styles.textarea}
            rows={4}
            maxLength={500}
            disabled={submitting}
          />
          
          <div className={styles.postOptions}>
            <label className={styles.anonymousOption}>
              <input
                type="checkbox"
                checked={isAnonymous}
                onChange={(e) => setIsAnonymous(e.target.checked)}
                disabled={submitting}
              />
              {isAnonymous ? <EyeOff size={16} /> : <Eye size={16} />}
              Publicar anonimamente
            </label>
            
            <div className={styles.charCount}>
              {newPost.length}/500
            </div>
          </div>

          <button
            type="submit"
            className={styles.submitButton}
            disabled={!newPost.trim() || submitting}
          >
            <Plus size={20} />
            {submitting ? 'Publicando...' : 'Publicar'}
          </button>
        </form>
      </div>

      {/* Lista de posts */}
      <div className={styles.postsContainer}>
        {posts.length === 0 ? (
          <div className={styles.emptyState}>
            <Users size={48} />
            <h3>Nenhum post ainda</h3>
            <p>Seja o primeiro a compartilhar algo com a equipe!</p>
          </div>
        ) : (
          posts.map((post) => (
            <div key={post.id} className={styles.postCard}>
              <div className={styles.postHeader}>
                <div className={styles.authorInfo}>
                  <div className={styles.avatar}>
                    {post.anonymous ? '👤' : '👤'} {/* Sempre anônimo por enquanto */}
                  </div>
                  <div>
                    <div className={styles.authorName}>
                      {post.anonymous ? 'Anônimo' : 'Usuário'}
                    </div>
                    <div className={styles.postTime}>
                      {formatDate(post.created_at)}
                    </div>
                  </div>
                </div>
                {/* Remover verificação de moderação temporariamente */}
              </div>

              <div className={styles.postContent}>
                {post.text}
              </div>

              <div className={styles.postActions}>
                <button
                  onClick={() => handleLike(post.id)}
                  className={styles.actionButton}
                >
                  <Heart size={18} fill="none" />
                  {Object.values(post.reactions).reduce((sum, count) => sum + count, 0)}
                </button>

                <button
                  onClick={() => toggleComments(post.id)}
                  className={styles.actionButton}
                >
                  <MessageSquare size={18} />
                  0 {/* Comentários serão implementados depois */}
                </button>
              </div>

              {/* Seção de comentários */}
              {expandedPosts.has(post.id) && (
                <div className={styles.commentsSection}>
                  <div className={styles.commentsList}>
                    {comments[post.id]?.map((comment) => (
                      <div key={comment.id} className={styles.comment}>
                        <div className={styles.commentAvatar}>
                          {comment.is_anonymous ? '👤' : (comment.author?.charAt(0).toUpperCase() || '?')}
                        </div>
                        <div className={styles.commentContent}>
                          <div className={styles.commentHeader}>
                            <span className={styles.commentAuthor}>
                              {comment.is_anonymous ? 'Anônimo' : comment.author || 'Usuário'}
                            </span>
                            <span className={styles.commentTime}>
                              {formatDate(comment.created_at)}
                            </span>
                          </div>
                          <div className={styles.commentText}>
                            {comment.content}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <form
                    onSubmit={(e) => handleSubmitComment(post.id, e)}
                    className={styles.commentForm}
                  >
                    <input
                      type="text"
                      value={newComment[post.id] || ''}
                      onChange={(e) => setNewComment(prev => ({
                        ...prev,
                        [post.id]: e.target.value
                      }))}
                      placeholder="Escreva um comentário..."
                      className={styles.commentInput}
                      maxLength={200}
                    />
                    <button
                      type="submit"
                      className={styles.commentSubmit}
                      disabled={!newComment[post.id]?.trim()}
                    >
                      Comentar
                    </button>
                  </form>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Mural;
