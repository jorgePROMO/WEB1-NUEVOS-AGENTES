import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const APP_VERSION = '3.0.0'; // Incrementar esto fuerza limpieza de caché

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Validate user session on mount
  useEffect(() => {
    const validateSession = async () => {
      // Check app version - if different, clear old data
      const storedVersion = localStorage.getItem('app_version');
      if (storedVersion !== APP_VERSION) {
        console.log('🔄 Nueva versión detectada, limpiando datos antiguos...');
        localStorage.clear();
        sessionStorage.clear();
        localStorage.setItem('app_version', APP_VERSION);
        setLoading(false);
        return;
      }
      
      const storedToken = localStorage.getItem('token');
      const storedUser = localStorage.getItem('user');
      
      if (storedToken && storedUser) {
        try {
          // Validate token against backend
          const response = await axios.get(`${API}/auth/me`, {
            headers: {
              'Authorization': `Bearer ${storedToken}`
            }
          });
          
          // Token is valid, update state
          setToken(storedToken);
          setUser(response.data);
          localStorage.setItem('user', JSON.stringify(response.data));
        } catch (error) {
          // Token is invalid or user deleted - clear localStorage
          console.warn('Session validation failed:', error.response?.data?.detail);
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setToken(null);
          setUser(null);
        }
      }
      setLoading(false);
    };
    
    validateSession();
  }, []);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, null, {
        params: { email, password }
      });
      setUser(response.data.user);
      setToken(response.data.token);
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error al iniciar sesión' 
      };
    }
  };

  const register = async (username, email, password, phone) => {
    try {
      const response = await axios.post(`${API}/auth/register`, {
        username,
        email,
        password,
        phone
      });
      setUser(response.data.user);
      setToken(response.data.token);
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error al registrarse' 
      };
    }
  };

  const logout = async () => {
    try {
      // Call backend logout to clear session
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
    } catch (error) {
      console.error('Logout error:', error);
    }
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  const isAdmin = () => {
    return user?.role === 'admin';
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAdmin
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};