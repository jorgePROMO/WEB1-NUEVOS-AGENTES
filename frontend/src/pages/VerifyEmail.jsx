import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('verifying'); // verifying, success, error
  const [message, setMessage] = useState('Verificando tu email...');
  const [email, setEmail] = useState('');

  useEffect(() => {
    const verifyEmail = async () => {
      const token = searchParams.get('token');
      
      if (!token) {
        setStatus('error');
        setMessage('Token de verificación no proporcionado');
        return;
      }

      try {
        const response = await axios.get(`${BACKEND_URL}/api/auth/verify-email`, {
          params: { token }
        });

        if (response.data.success) {
          setStatus('success');
          setMessage(response.data.message);
          setEmail(response.data.email);
          
          // Redirect to login after 3 seconds
          setTimeout(() => {
            navigate('/login');
          }, 3000);
        }
      } catch (error) {
        setStatus('error');
        if (error.response?.data?.detail) {
          setMessage(error.response.data.detail);
        } else {
          setMessage('Error al verificar el email. Por favor intenta de nuevo.');
        }
      }
    };

    verifyEmail();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8">
        {/* Header */}
        <div className="text-center mb-6">
          {status === 'verifying' && (
            <div className="w-20 h-20 mx-auto mb-4">
              <div className="animate-spin rounded-full h-20 w-20 border-b-4 border-blue-600"></div>
            </div>
          )}
          
          {status === 'success' && (
            <div className="w-20 h-20 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
              <svg className="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          )}
          
          {status === 'error' && (
            <div className="w-20 h-20 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
              <svg className="w-12 h-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          )}

          <h1 className="text-2xl font-bold text-gray-800 mb-2">
            {status === 'verifying' && 'Verificando Email'}
            {status === 'success' && '¡Email Verificado!'}
            {status === 'error' && 'Error de Verificación'}
          </h1>
        </div>

        {/* Message */}
        <div className="text-center mb-6">
          <p className={`text-lg ${
            status === 'success' ? 'text-green-700' : 
            status === 'error' ? 'text-red-600' : 
            'text-gray-600'
          }`}>
            {message}
          </p>
          
          {email && status === 'success' && (
            <p className="text-sm text-gray-500 mt-2">
              {email}
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="space-y-3">
          {status === 'success' && (
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-3">
                Redirigiendo a la página de inicio de sesión en 3 segundos...
              </p>
              <button
                onClick={() => navigate('/login')}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition duration-200"
              >
                Ir a Iniciar Sesión
              </button>
            </div>
          )}
          
          {status === 'error' && (
            <div className="space-y-2">
              <button
                onClick={() => navigate('/register')}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition duration-200"
              >
                Volver a Registrarse
              </button>
              <button
                onClick={() => navigate('/login')}
                className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-4 rounded-lg transition duration-200"
              >
                Ir a Iniciar Sesión
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            ¿Necesitas ayuda? <a href="mailto:ecjtrainer@gmail.com" className="text-blue-600 hover:underline">Contacta con nosotros</a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default VerifyEmail;
