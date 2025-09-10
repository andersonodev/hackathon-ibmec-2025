import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import MoodCheckin from './pages/MoodCheckin';
import VoiceReports from './pages/VoiceReports';
import Mural from './pages/Mural';
import Conectas from './pages/Conectas';
import MyConnecta from './pages/MyConnecta';
import Administration from './pages/Administration';
import Reports from './pages/Reports';
import PlaceholderPage from './pages/PlaceholderPage';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Rota pública */}
            <Route path="/login" element={<Login />} />
            
            {/* Rotas protegidas */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/check-in"
              element={
                <ProtectedRoute>
                  <Layout>
                    <MoodCheckin />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/voice"
              element={
                <ProtectedRoute>
                  <Layout>
                    <VoiceReports />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/mural"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Mural />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/conectas"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Conectas />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/my-connecta"
              element={
                <ProtectedRoute>
                  <Layout>
                    <MyConnecta />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/relatorios"
              element={
                <ProtectedRoute requiredRoles={['diretoria', 'admin']}>
                  <Layout>
                    <Reports />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/administracao"
              element={
                <ProtectedRoute requiredRoles={['admin']}>
                  <Layout>
                    <Administration />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            {/* Redirecionamento da raiz */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            {/* Fallback para rotas não encontradas */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
