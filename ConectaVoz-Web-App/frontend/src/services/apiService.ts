import { User, LoginCredentials, RegisterData, ApiResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Token ${token}` })
    };
  }

  private getAuthHeadersForFormData() {
    const token = localStorage.getItem('token');
    return {
      ...(token && { 'Authorization': `Token ${token}` })
    };
  }

  async get(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
      ...options
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return {
      data: await response.json(),
      status: response.status
    };
  }

  async post(endpoint: string, data?: any, options: RequestInit = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: data ? JSON.stringify(data) : undefined,
      ...options
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(`HTTP error! status: ${response.status}`);
      (error as any).response = { data: errorData, status: response.status };
      throw error;
    }

    return {
      data: await response.json(),
      status: response.status
    };
  }

  async put(endpoint: string, data?: any, options: RequestInit = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: data ? JSON.stringify(data) : undefined,
      ...options
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(`HTTP error! status: ${response.status}`);
      (error as any).response = { data: errorData, status: response.status };
      throw error;
    }

    return {
      data: await response.json(),
      status: response.status
    };
  }

  async patch(endpoint: string, data?: any, options: RequestInit = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PATCH',
      headers: this.getAuthHeaders(),
      body: data ? JSON.stringify(data) : undefined,
      ...options
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(`HTTP error! status: ${response.status}`);
      (error as any).response = { data: errorData, status: response.status };
      throw error;
    }

    return {
      data: await response.json(),
      status: response.status
    };
  }

  async delete(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
      ...options
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(`HTTP error! status: ${response.status}`);
      (error as any).response = { data: errorData, status: response.status };
      throw error;
    }

    // Para DELETE, pode não ter body de resposta
    let data;
    try {
      data = await response.json();
    } catch {
      data = null;
    }

    return {
      data,
      status: response.status
    };
  }

  // =============================================================================
  // AUTENTICAÇÃO
  // =============================================================================

  async login(credentials: LoginCredentials): Promise<{ user: User; token: string }> {
    const response = await fetch(`${API_BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Erro ao fazer login');
    }

    const data = await response.json();
    
    // Salvar token no localStorage
    if (data.token) {
      localStorage.setItem('token', data.token);
    }

    return data;
  }

  async register(data: RegisterData): Promise<{ user: User; token: string }> {
    const response = await fetch(`${API_BASE_URL}/auth/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Erro ao registrar');
    }

    const responseData = await response.json();
    
    // Salvar token no localStorage
    if (responseData.token) {
      localStorage.setItem('token', responseData.token);
    }

    return responseData;
  }

  async logout() {
    try {
      await this.post('/auth/logout/');
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    } finally {
      localStorage.removeItem('token');
    }
  }

  isAuthenticated() {
    return !!localStorage.getItem('token');
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.get('/auth/user/');
    return response.data;
  }

  // =============================================================================
  // MOOD CHECKIN
  // =============================================================================

  async getMoodHistory() {
    const response = await this.get('/mood/checkins/');
    return response.data;
  }

  async submitMoodCheckin(moodLevel: number, comment?: string) {
    const response = await this.post('/mood/checkin/', { 
      mood_level: moodLevel, 
      comment: comment || ''
    });
    return response.data;
  }

  async getMoodStats() {
    const response = await this.get('/mood/stats/');
    return response.data;
  }

  // =============================================================================
  // CONECTAS
  // =============================================================================

  async getConnectas(): Promise<ApiResponse<User>> {
    const response = await this.get('/connectas/');
    return response.data;
  }

  async getAvailableConnectas() {
    const response = await this.get('/connectas/available/');
    return response.data;
  }

  async getMyConnecta(): Promise<User | null> {
    const response = await this.get('/connectas/my-connecta/');
    return response.data;
  }

  async chooseConnecta(connectaId: number): Promise<void> {
    const response = await this.post('/connectas/choose/', {
      connecta_id: connectaId
    });
    return response.data;
  }

  async requestConnection(connectaId: number) {
    const response = await this.post(`/connectas/${connectaId}/request/`);
    return response.data;
  }

  async getMyConnections() {
    const response = await this.get('/connectas/my-connections/');
    return response.data;
  }

  async acceptConnection(connectionId: number) {
    const response = await this.post(`/connectas/connections/${connectionId}/accept/`);
    return response.data;
  }

  async rejectConnection(connectionId: number) {
    const response = await this.post(`/connectas/connections/${connectionId}/reject/`);
    return response.data;
  }

  // =============================================================================
  // VOZ & RELATOS
  // =============================================================================

  async getVoiceReports() {
    const response = await this.get('/voice/reports/');
    return response.data;
  }

  async submitVoiceReport(data: {
    title: string;
    content: string;
    category: string;
    attachments?: File[];
  }) {
    const formData = new FormData();
    formData.append('title', data.title);
    formData.append('content', data.content);
    formData.append('category', data.category);
    
    if (data.attachments && data.attachments.length > 0) {
      data.attachments.forEach((file, index) => {
        formData.append(`attachment_${index}`, file);
      });
    }

    const response = await fetch(`${API_BASE_URL}/voice/reports/`, {
      method: 'POST',
      headers: this.getAuthHeadersForFormData(),
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async getVoiceReportCategories() {
    const response = await this.get('/voice/categories/');
    return response.data;
  }

  async updateVoiceReportStatus(reportId: number, status: string) {
    const response = await this.patch(`/voice/reports/${reportId}/`, { status });
    return response.data;
  }

  // =============================================================================
  // MURAL
  // =============================================================================

  async getMuralPosts() {
    const response = await this.get('/mural/posts/');
    return response.data;
  }

  async createMuralPost(content: string, isAnonymous: boolean) {
    const response = await this.post('/mural/posts/', { 
      content, 
      is_anonymous: isAnonymous 
    });
    return response.data;
  }

  async likeMuralPost(postId: number) {
    const response = await this.post(`/mural/posts/${postId}/like/`);
    return response.data;
  }

  async unlikeMuralPost(postId: number) {
    const response = await this.delete(`/mural/posts/${postId}/like/`);
    return response.data;
  }

  async commentOnMuralPost(postId: number, comment: string) {
    const response = await this.post(`/mural/posts/${postId}/comments/`, { 
      content: comment 
    });
    return response.data;
  }

  async getMuralComments(postId: number) {
    const response = await this.get(`/mural/posts/${postId}/comments/`);
    return response.data;
  }

  async deleteMuralPost(postId: number) {
    const response = await this.delete(`/mural/posts/${postId}/`);
    return response.data;
  }

  // =============================================================================
  // USUÁRIOS E ADMINISTRAÇÃO
  // =============================================================================

  async getUsers() {
    const response = await this.get('/users/');
    return response.data;
  }

  async createUser(userData: any) {
    const response = await this.post('/users/', userData);
    return response.data;
  }

  async updateUser(userId: number, userData: any) {
    const response = await this.put(`/users/${userId}/`, userData);
    return response.data;
  }

  async deleteUser(userId: number) {
    const response = await this.delete(`/users/${userId}/`);
    return response;
  }

  async getUserRoles() {
    const response = await this.get('/users/roles/');
    return response.data;
  }

  async bulkUpdateUsers(userIds: number[], updateData: any) {
    const response = await this.post('/users/bulk-update/', {
      user_ids: userIds,
      update_data: updateData
    });
    return response.data;
  }

  // =============================================================================
  // RELATÓRIOS E DASHBOARD
  // =============================================================================

  async getReportsData() {
    const response = await this.get('/reports/dashboard/');
    return response.data;
  }

  async getDashboardStats() {
    const response = await this.get('/reports/stats/');
    return response.data;
  }

  async getMoodAnalytics(period: string = '30d') {
    const response = await this.get(`/reports/mood-analytics/?period=${period}`);
    return response.data;
  }

  async getVoiceReportsAnalytics(period: string = '30d') {
    const response = await this.get(`/reports/voice-analytics/?period=${period}`);
    return response.data;
  }

  async getConnectasAnalytics() {
    const response = await this.get('/reports/connectas-analytics/');
    return response.data;
  }

  async exportReportsData(format: 'csv' | 'xlsx' = 'csv', reportType: string) {
    const response = await fetch(`${API_BASE_URL}/reports/export/?format=${format}&type=${reportType}`, {
      method: 'GET',
      headers: this.getAuthHeadersForFormData()
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `relatorio_${reportType}_${format}.${format}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  // =============================================================================
  // CONSELHO ÉTICO
  // =============================================================================

  async getCouncilCases() {
    const response = await this.get('/council/cases/');
    return response.data;
  }

  async createCouncilCase(caseData: any) {
    const response = await this.post('/council/cases/', caseData);
    return response.data;
  }

  async updateCouncilCase(caseId: number, caseData: any) {
    const response = await this.put(`/council/cases/${caseId}/`, caseData);
    return response.data;
  }

  async voteOnCouncilCase(caseId: number, vote: 'approve' | 'reject', comment?: string) {
    const response = await this.post(`/council/cases/${caseId}/vote/`, {
      vote,
      comment
    });
    return response.data;
  }

  // =============================================================================
  // AUDITORIA
  // =============================================================================

  async getAuditLogs(filters?: any) {
    const queryParams = filters ? `?${new URLSearchParams(filters).toString()}` : '';
    const response = await this.get(`/audit/logs/${queryParams}`);
    return response.data;
  }

  async getUserActivity(userId: number, period: string = '30d') {
    const response = await this.get(`/audit/user-activity/${userId}/?period=${period}`);
    return response.data;
  }

  // =============================================================================
  // ESCALAÇÃO
  // =============================================================================

  async getEscalations() {
    const response = await this.get('/escalation/cases/');
    return response.data;
  }

  async createEscalation(escalationData: any) {
    const response = await this.post('/escalation/cases/', escalationData);
    return response.data;
  }

  async updateEscalationStatus(escalationId: number, status: string, comment?: string) {
    const response = await this.patch(`/escalation/cases/${escalationId}/`, {
      status,
      resolution_comment: comment
    });
    return response.data;
  }

  // =============================================================================
  // UTILIDADES
  // =============================================================================

  async testConnection() {
    try {
      const response = await this.get('/health/');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  }

  async getSystemSettings() {
    const response = await this.get('/settings/');
    return response.data;
  }

  async updateSystemSettings(settings: any) {
    const response = await this.put('/settings/', settings);
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;
