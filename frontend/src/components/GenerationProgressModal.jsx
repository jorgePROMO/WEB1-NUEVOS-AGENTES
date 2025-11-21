import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const GenerationProgressModal = ({ jobId, onComplete, onError, onClose }) => {
  const [jobStatus, setJobStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!jobId) return;

    // Polling interval: cada 3 segundos
    const pollInterval = setInterval(async () => {
      try {
        const response = await axios.get(`${API}/api/jobs/${jobId}`);
        const job = response.data;
        
        setJobStatus(job);

        // Si el job está completado
        if (job.status === 'completed') {
          clearInterval(pollInterval);
          setTimeout(() => {
            onComplete(job.result);
          }, 1000); // Dar 1 segundo para ver el 100%
        }

        // Si el job falló
        if (job.status === 'failed') {
          clearInterval(pollInterval);
          setError(job.error_message);
          onError(job.error_message);
        }
      } catch (err) {
        console.error('Error polling job status:', err);
        clearInterval(pollInterval);
        setError('Error al consultar el estado del job');
        onError('Error al consultar el estado del job');
      }
    }, 3000);

    // Cleanup
    return () => clearInterval(pollInterval);
  }, [jobId, onComplete, onError]);

  if (!jobStatus) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Iniciando generación...</p>
          </div>
        </div>
      </div>
    );
  }

  const { progress, status } = jobStatus;
  const percentage = progress?.percentage || 0;
  const message = progress?.message || 'Procesando...';
  const currentAgent = progress?.current_agent || '';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full">
        <h3 className="text-2xl font-bold mb-6 text-center text-gray-800">
          {status === 'completed' ? '✅ Generación Completada' : '🤖 Generando Plan E.D.N.360'}
        </h3>

        {error ? (
          <div className="mb-6">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800 font-semibold mb-2">❌ Error en la generación</p>
              <p className="text-red-600 text-sm">{error}</p>
            </div>
            <button
              onClick={onClose}
              className="mt-4 w-full bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            >
              Cerrar
            </button>
          </div>
        ) : (
          <>
            {/* Progress Bar */}
            <div className="mb-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>{message}</span>
                <span className="font-semibold">{percentage}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-blue-500 to-purple-500 h-4 rounded-full transition-all duration-500 ease-out flex items-center justify-end pr-2"
                  style={{ width: `${percentage}%` }}
                >
                  {percentage > 10 && (
                    <span className="text-white text-xs font-bold">{percentage}%</span>
                  )}
                </div>
              </div>
            </div>

            {/* Current Agent */}
            {currentAgent && status === 'running' && (
              <div className="mb-6 text-center">
                <div className="inline-flex items-center bg-blue-50 border border-blue-200 rounded-lg px-4 py-2">
                  <div className="animate-pulse mr-2 w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-blue-800 font-semibold">Agente {currentAgent}</span>
                </div>
              </div>
            )}

            {/* Steps Progress */}
            <div className="mb-6 text-center text-sm text-gray-500">
              <p>Paso {progress?.completed_steps || 0} de {progress?.total_steps || 18}</p>
            </div>

            {/* Loading Animation */}
            {status === 'running' && (
              <div className="flex justify-center mb-4">
                <div className="flex space-x-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-3 h-3 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            )}

            {/* Success Message */}
            {status === 'completed' && (
              <div className="text-center">
                <div className="text-6xl mb-4">✅</div>
                <p className="text-green-600 font-semibold">Plan generado exitosamente</p>
              </div>
            )}

            {/* Note */}
            {status === 'running' && (
              <p className="text-xs text-gray-400 text-center mt-4">
                Este proceso puede tardar 2-5 minutos. Por favor no cierres esta ventana.
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default GenerationProgressModal;
