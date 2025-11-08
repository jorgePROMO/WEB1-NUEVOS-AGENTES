import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { CheckCircle, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SubscriptionSuccess = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  const [status, setStatus] = useState('processing'); // processing, success, error
  const [message, setMessage] = useState('');
  const [pollingCount, setPollingCount] = useState(0);

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    
    if (!sessionId) {
      setStatus('error');
      setMessage('No se encontró ID de sesión. Por favor, contacta a soporte.');
      return;
    }

    // Poll payment status
    pollPaymentStatus(sessionId);
  }, [searchParams]);

  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 5;
    const pollInterval = 2000; // 2 seconds

    if (attempts >= maxAttempts) {
      setStatus('error');
      setMessage('No se pudo verificar el estado del pago. Por favor, verifica tu email o contacta a soporte.');
      return;
    }

    try {
      const response = await axios.get(`${API}/stripe/checkout-status/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.data.payment_status === 'paid') {
        setStatus('success');
        setMessage('¡Suscripción activada exitosamente! Ya puedes acceder a todos los servicios.');
        return;
      } else if (response.data.status === 'expired') {
        setStatus('error');
        setMessage('La sesión de pago expiró. Por favor, intenta de nuevo.');
        return;
      }

      // Continue polling
      setPollingCount(attempts + 1);
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
    } catch (error) {
      console.error('Error checking payment status:', error);
      setStatus('error');
      setMessage('Error al verificar el estado del pago. Por favor, intenta recargar la página.');
    }
  };

  const handleGoToDashboard = () => {
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <Card className="max-w-md w-full">
        <CardHeader>
          <CardTitle className="text-center">
            {status === 'processing' && 'Procesando Pago'}
            {status === 'success' && '¡Pago Exitoso!'}
            {status === 'error' && 'Error en el Pago'}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex flex-col items-center justify-center">
            {status === 'processing' && (
              <>
                <Loader2 className="h-16 w-16 text-blue-500 animate-spin mb-4" />
                <p className="text-center text-gray-600">
                  Verificando tu pago... ({pollingCount + 1}/5)
                </p>
              </>
            )}
            
            {status === 'success' && (
              <>
                <CheckCircle className="h-16 w-16 text-green-500 mb-4" />
                <p className="text-center text-gray-700 font-medium">
                  {message}
                </p>
                <Button
                  onClick={handleGoToDashboard}
                  className="mt-6 w-full bg-green-600 hover:bg-green-700"
                >
                  Ir a Mi Dashboard
                </Button>
              </>
            )}
            
            {status === 'error' && (
              <>
                <div className="h-16 w-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                  <span className="text-3xl">❌</span>
                </div>
                <p className="text-center text-gray-700">
                  {message}
                </p>
                <div className="flex gap-3 mt-6 w-full">
                  <Button
                    onClick={() => window.location.reload()}
                    variant="outline"
                    className="flex-1"
                  >
                    Reintentar
                  </Button>
                  <Button
                    onClick={handleGoToDashboard}
                    className="flex-1"
                  >
                    Ir al Dashboard
                  </Button>
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SubscriptionSuccess;
