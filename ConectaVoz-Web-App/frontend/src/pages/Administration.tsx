import React, { useState, useEffect } from 'react';
import { Settings, Users, UserPlus, Shield, Edit, Trash2, Search, Filter } from 'lucide-react';
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';
import styles from './Administration.module.css';

interface User {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  role: 'colaborador' | 'diretoria' | 'admin';
  is_active: boolean;
  department: string;
  date_joined: string;
  last_login: string | null;
}

interface Conecta {
  id: number;
  user: User;
  specialties: string[];
  bio: string;
  available_slots: number;
  current_connections: number;
  is_available: boolean;
  created_at: string;
}

const Administration: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'users' | 'conectas' | 'settings'>('users');
  const [users, setUsers] = useState<User[]>([]);
  const [conectas, setConectas] = useState<Conecta[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('all');
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [showUserForm, setShowUserForm] = useState(false);

  // Formulário de usuário
  const [userForm, setUserForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    role: 'colaborador' as 'colaborador' | 'diretoria' | 'admin',
    department: '',
    password: ''
  });

  // Formulário de Conecta
  const [conectaForm, setConectaForm] = useState({
    user_id: '',
    specialties: [''],
    bio: '',
    available_slots: 5
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [usersResponse, conectasResponse] = await Promise.all([
        apiService.get('/admin/users/'),
        apiService.get('/admin/conectas/')
      ]);

      setUsers(usersResponse.data.results || usersResponse.data);
      setConectas(conectasResponse.data.results || conectasResponse.data);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await apiService.post('/admin/users/', userForm);
      setUsers(prev => [...prev, response.data]);
      setUserForm({
        first_name: '',
        last_name: '',
        email: '',
        role: 'colaborador',
        department: '',
        password: ''
      });
      setShowUserForm(false);
      alert('Usuário criado com sucesso!');
    } catch (error: any) {
      console.error('Erro ao criar usuário:', error);
      alert(error.response?.data?.detail || 'Erro ao criar usuário.');
    }
  };

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;

    try {
      const updateData = {
        first_name: userForm.first_name,
        last_name: userForm.last_name,
        email: userForm.email,
        role: userForm.role,
        department: userForm.department
      };

      const response = await apiService.put(`/admin/users/${editingUser.id}/`, updateData);
      setUsers(prev => prev.map(u => u.id === editingUser.id ? response.data : u));
      setEditingUser(null);
      setUserForm({
        first_name: '',
        last_name: '',
        email: '',
        role: 'colaborador',
        department: '',
        password: ''
      });
      alert('Usuário atualizado com sucesso!');
    } catch (error: any) {
      console.error('Erro ao atualizar usuário:', error);
      alert(error.response?.data?.detail || 'Erro ao atualizar usuário.');
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!window.confirm('Tem certeza que deseja excluir este usuário?')) return;

    try {
      await apiService.delete(`/admin/users/${userId}/`);
      setUsers(prev => prev.filter(u => u.id !== userId));
      alert('Usuário excluído com sucesso!');
    } catch (error: any) {
      console.error('Erro ao excluir usuário:', error);
      alert(error.response?.data?.detail || 'Erro ao excluir usuário.');
    }
  };

  const handleToggleUserStatus = async (userId: number, isActive: boolean) => {
    try {
      const response = await apiService.patch(`/admin/users/${userId}/`, {
        is_active: !isActive
      });
      setUsers(prev => prev.map(u => u.id === userId ? response.data : u));
    } catch (error) {
      console.error('Erro ao alterar status do usuário:', error);
    }
  };

  const handleCreateConecta = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const conectaData = {
        ...conectaForm,
        specialties: conectaForm.specialties.filter(s => s.trim() !== '')
      };

      const response = await apiService.post('/admin/conectas/', conectaData);
      setConectas(prev => [...prev, response.data]);
      setConectaForm({
        user_id: '',
        specialties: [''],
        bio: '',
        available_slots: 5
      });
      alert('Conecta criado com sucesso!');
    } catch (error: any) {
      console.error('Erro ao criar Conecta:', error);
      alert(error.response?.data?.detail || 'Erro ao criar Conecta.');
    }
  };

  const startEditUser = (userToEdit: User) => {
    setEditingUser(userToEdit);
    setUserForm({
      first_name: userToEdit.first_name,
      last_name: userToEdit.last_name,
      email: userToEdit.email,
      role: userToEdit.role as 'colaborador' | 'diretoria' | 'admin',
      department: userToEdit.department,
      password: ''
    });
    setShowUserForm(true);
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = 
      user.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.department.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesRole = roleFilter === 'all' || user.role === roleFilter;
    
    return matchesSearch && matchesRole;
  });

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'admin': return 'Administrador';
      case 'diretoria': return 'Diretoria';
      case 'colaborador': return 'Colaborador';
      default: return role;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin': return '#dc3545';
      case 'diretoria': return '#fd7e14';
      case 'colaborador': return '#28a745';
      default: return '#6c757d';
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Carregando dados administrativos...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>
          <Settings className={styles.headerIcon} />
          Administração
        </h1>
        <p>Gerencie usuários, Conectas e configurações da plataforma</p>
      </div>

      {/* Tabs */}
      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${activeTab === 'users' ? styles.active : ''}`}
          onClick={() => setActiveTab('users')}
        >
          <Users size={18} />
          Usuários
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'conectas' ? styles.active : ''}`}
          onClick={() => setActiveTab('conectas')}
        >
          <Shield size={18} />
          Conectas
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'settings' ? styles.active : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          <Settings size={18} />
          Configurações
        </button>
      </div>

      {/* Conteúdo das tabs */}
      {activeTab === 'users' && (
        <div className={styles.tabContent}>
          {/* Controles de usuários */}
          <div className={styles.controls}>
            <div className={styles.searchAndFilter}>
              <div className={styles.searchBox}>
                <Search size={18} />
                <input
                  type="text"
                  placeholder="Buscar usuários..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <div className={styles.filterBox}>
                <Filter size={18} />
                <select
                  value={roleFilter}
                  onChange={(e) => setRoleFilter(e.target.value)}
                >
                  <option value="all">Todas as funções</option>
                  <option value="colaborador">Colaboradores</option>
                  <option value="diretoria">Diretoria</option>
                  <option value="admin">Administradores</option>
                </select>
              </div>
            </div>
            <button
              onClick={() => {
                setShowUserForm(!showUserForm);
                setEditingUser(null);
                setUserForm({
                  first_name: '',
                  last_name: '',
                  email: '',
                  role: 'colaborador',
                  department: '',
                  password: ''
                });
              }}
              className={styles.createButton}
            >
              <UserPlus size={18} />
              Novo Usuário
            </button>
          </div>

          {/* Formulário de usuário */}
          {showUserForm && (
            <div className={styles.userForm}>
              <h3>{editingUser ? 'Editar Usuário' : 'Novo Usuário'}</h3>
              <form onSubmit={editingUser ? handleUpdateUser : handleCreateUser}>
                <div className={styles.formGrid}>
                  <div className={styles.formGroup}>
                    <label>Nome</label>
                    <input
                      type="text"
                      value={userForm.first_name}
                      onChange={(e) => setUserForm(prev => ({ ...prev, first_name: e.target.value }))}
                      required
                    />
                  </div>
                  <div className={styles.formGroup}>
                    <label>Sobrenome</label>
                    <input
                      type="text"
                      value={userForm.last_name}
                      onChange={(e) => setUserForm(prev => ({ ...prev, last_name: e.target.value }))}
                      required
                    />
                  </div>
                  <div className={styles.formGroup}>
                    <label>E-mail</label>
                    <input
                      type="email"
                      value={userForm.email}
                      onChange={(e) => setUserForm(prev => ({ ...prev, email: e.target.value }))}
                      required
                    />
                  </div>
                  <div className={styles.formGroup}>
                    <label>Função</label>
                    <select
                      value={userForm.role}
                      onChange={(e) => setUserForm(prev => ({ ...prev, role: e.target.value as any }))}
                      required
                    >
                      <option value="colaborador">Colaborador</option>
                      <option value="diretoria">Diretoria</option>
                      <option value="admin">Administrador</option>
                    </select>
                  </div>
                  <div className={styles.formGroup}>
                    <label>Departamento</label>
                    <input
                      type="text"
                      value={userForm.department}
                      onChange={(e) => setUserForm(prev => ({ ...prev, department: e.target.value }))}
                      required
                    />
                  </div>
                  {!editingUser && (
                    <div className={styles.formGroup}>
                      <label>Senha</label>
                      <input
                        type="password"
                        value={userForm.password}
                        onChange={(e) => setUserForm(prev => ({ ...prev, password: e.target.value }))}
                        required
                      />
                    </div>
                  )}
                </div>
                <div className={styles.formActions}>
                  <button type="submit" className={styles.saveButton}>
                    {editingUser ? 'Atualizar' : 'Criar'} Usuário
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowUserForm(false);
                      setEditingUser(null);
                    }}
                    className={styles.cancelButton}
                  >
                    Cancelar
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Lista de usuários */}
          <div className={styles.usersList}>
            <div className={styles.usersHeader}>
              <h3>Usuários ({filteredUsers.length})</h3>
            </div>
            <div className={styles.usersTable}>
              {filteredUsers.map(user => (
                <div key={user.id} className={styles.userRow}>
                  <div className={styles.userInfo}>
                    <div className={styles.userAvatar}>
                      {user.first_name.charAt(0).toUpperCase()}
                    </div>
                    <div className={styles.userDetails}>
                      <div className={styles.userName}>
                        {user.first_name} {user.last_name}
                      </div>
                      <div className={styles.userEmail}>{user.email}</div>
                      <div className={styles.userMeta}>
                        <span className={styles.userDepartment}>{user.department}</span>
                        <span 
                          className={styles.userRole}
                          style={{ backgroundColor: getRoleColor(user.role) }}
                        >
                          {getRoleLabel(user.role)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className={styles.userActions}>
                    <div className={styles.userStatus}>
                      <label className={styles.switch}>
                        <input
                          type="checkbox"
                          checked={user.is_active}
                          onChange={() => handleToggleUserStatus(user.id, user.is_active)}
                        />
                        <span className={styles.slider}></span>
                      </label>
                      <span className={styles.statusLabel}>
                        {user.is_active ? 'Ativo' : 'Inativo'}
                      </span>
                    </div>
                    <button
                      onClick={() => startEditUser(user)}
                      className={styles.editButton}
                    >
                      <Edit size={16} />
                    </button>
                    <button
                      onClick={() => handleDeleteUser(user.id)}
                      className={styles.deleteButton}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'conectas' && (
        <div className={styles.tabContent}>
          <div className={styles.conectasSection}>
            <h3>Gerenciar Conectas</h3>
            <p>Visualize e gerencie os Conectas da plataforma</p>
            
            {/* Aqui seria a lista de Conectas e formulário para criar novos */}
            <div className={styles.comingSoon}>
              <Shield size={48} />
              <h4>Gestão de Conectas</h4>
              <p>Interface de gerenciamento de Conectas em desenvolvimento</p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'settings' && (
        <div className={styles.tabContent}>
          <div className={styles.settingsSection}>
            <h3>Configurações da Plataforma</h3>
            <p>Configure parâmetros gerais da plataforma</p>
            
            <div className={styles.comingSoon}>
              <Settings size={48} />
              <h4>Configurações</h4>
              <p>Painel de configurações em desenvolvimento</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Administration;
