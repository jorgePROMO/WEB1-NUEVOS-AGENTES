import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Register from './pages/Register';
import ResetPassword from './pages/ResetPassword';
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { user, loading, isAdmin } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && !isAdmin()) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

// Component to handle Google OAuth callback
const OAuthHandler = ({ children }) => {
  const { googleAuth } = useAuth();
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const handleOAuth = async () => {
      // Check if there's a session_id in the URL hash
      const hash = window.location.hash;
      console.log('OAuthHandler: Current hash:', hash);
      if (hash.includes('session_id=')) {
        setIsProcessing(true);
        const sessionId = hash.split('session_id=')[1].split('&')[0];
        console.log('OAuthHandler: Extracted session_id:', sessionId);
        
        if (sessionId) {
          const result = await googleAuth(sessionId);
          
          // Clean the hash from URL
          window.history.replaceState(null, '', window.location.pathname);
          
          if (result.success) {
            console.log('OAuthHandler: Success, redirecting to', result.user.role === 'admin' ? '/admin' : '/dashboard');
            // Redirect based on role
            if (result.user.role === 'admin') {
              navigate('/admin', { replace: true });
            } else {
              navigate('/dashboard', { replace: true });
            }
          } else {
            console.error('OAuthHandler: Failed', result.error);
            // Redirect to login with error
            navigate('/login', { replace: true, state: { error: 'Error en autenticación con Google' } });
          }
        }
        setIsProcessing(false);
      }
    };

    handleOAuth();
  }, [googleAuth, navigate]);

  if (isProcessing) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Autenticando con Google...</p>
        </div>
      </div>
    );
  }

  return children;
};

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route
        path="/dashboard"
        element={
          <OAuthHandler>
            <ProtectedRoute>
              <UserDashboard />
            </ProtectedRoute>
          </OAuthHandler>
        }
      />
      <Route
        path="/admin"
        element={
          <OAuthHandler>
            <ProtectedRoute adminOnly={true}>
              <AdminDashboard />
            </ProtectedRoute>
          </OAuthHandler>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;