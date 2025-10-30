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
      // Check BOTH hash AND query parameters for session_id (mobile compatibility)
      const hash = window.location.hash;
      const search = window.location.search;
      
      console.log('OAuthHandler: Hash:', hash);
      console.log('OAuthHandler: Search:', search);
      
      let sessionId = null;
      
      // Try to extract from hash first
      if (hash.includes('session_id=')) {
        sessionId = hash.split('session_id=')[1].split('&')[0];
        console.log('OAuthHandler: Found session_id in HASH:', sessionId);
      }
      
      // If not in hash, try query parameters (mobile fallback)
      if (!sessionId && search.includes('session_id=')) {
        const params = new URLSearchParams(search);
        sessionId = params.get('session_id');
        console.log('OAuthHandler: Found session_id in QUERY:', sessionId);
      }
      
      if (sessionId) {
        setIsProcessing(true);
        console.log('OAuthHandler: Processing session_id:', sessionId);
        
        const result = await googleAuth(sessionId);
        
        // Clean both hash and query from URL
        const cleanUrl = window.location.pathname;
        window.history.replaceState(null, '', cleanUrl);
        
        if (result.success) {
          console.log('OAuthHandler: Success, user:', result.user);
          // Redirect based on role
          if (result.user.role === 'admin') {
            navigate('/admin', { replace: true });
          } else {
            navigate('/dashboard', { replace: true });
          }
        } else {
          console.error('OAuthHandler: Failed', result.error);
          alert('Error en autenticación: ' + result.error);
          navigate('/login', { replace: true });
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