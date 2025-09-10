// utils/testConnection.ts
import { apiService } from '../services/apiService';

export const testBackendConnection = async () => {
  try {
    console.log('🔄 Testando conexão com o backend...');
    
    // Teste básico da API
    const response = await fetch('http://localhost:8000/api/v1/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      console.log('✅ Backend conectado com sucesso!');
      console.log('📡 Status:', response.status);
      return true;
    } else {
      console.log('❌ Erro na conexão:', response.status);
      return false;
    }
  } catch (error) {
    console.log('❌ Erro de rede:', error);
    return false;
  }
};

export const testAuthentication = async (credentials: { username: string; password: string }) => {
  try {
    console.log('🔐 Testando autenticação...');
    
    const result = await apiService.login(credentials);
    console.log('✅ Login realizado com sucesso!');
    console.log('👤 Usuário:', result.user.username);
    console.log('🔑 Token recebido');
    
    return result;
  } catch (error) {
    console.log('❌ Erro na autenticação:', error);
    throw error;
  }
};

// Função para testar todas as conexões
export const runConnectionTests = async () => {
  console.log('🚀 Iniciando testes de conectividade...');
  
  const backendOnline = await testBackendConnection();
  
  if (backendOnline) {
    console.log('🎯 Todos os testes de conectividade passaram!');
    console.log('📋 Próximos passos:');
    console.log('   1. Acesse http://localhost:3000');
    console.log('   2. Teste o login com as credenciais:');
    console.log('      - admin / admin123 (Admin)');
    console.log('      - diretora.ana / diretoria123 (Diretoria)');
    console.log('      - bruno.mendes / colab123 (Colaborador)');
  } else {
    console.log('⚠️ Backend não está respondendo. Verifique se está rodando na porta 8001');
  }
  
  return backendOnline;
};
