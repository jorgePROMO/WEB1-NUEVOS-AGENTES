import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, Clock, AlertCircle } from 'lucide-react';

const WaitlistConfirmacion = () => {
  const navigate = useNavigate();
  const [result, setResult] = useState(null);
  
  useEffect(() => {
    const savedResult = localStorage.getItem('waitlist_result');
    if (savedResult) {
      setResult(JSON.parse(savedResult));
    } else {
      // Si no hay resultado, redirigir al formulario
      navigate('/trabaja-conmigo');
    }
  }, [navigate]);
  
  if (!result) return null;
  
  const getPrioridadInfo = () => {
    // Texto común para todos
    const commonMessage = `Gracias por tomarte el tiempo de completar tu solicitud.

Durante los próximos días, estaré revisando cada candidatura personalmente para asegurarme de que las próximas plazas se asignan a las personas que realmente van a aprovechar el proceso.`;

    const commonSteps = [
      '🔸 El periodo de revisión dura aproximadamente una semana.',
      '🔸 Si tu perfil encaja con el programa, recibirás un mensaje privado con los siguientes pasos para agendar una breve llamada de valoración.',
      '🔸 Si aún no hay plazas disponibles, te mantendremos en la lista prioritaria de espera y serás de los primeros en enterarte cuando se abra la siguiente tanda.'
    ];

    if (result.prioridad === 'alta') {
      return {
        icon: <CheckCircle className="w-16 h-16 text-green-500" />,
        title: '¡Formulario enviado correctamente!',
        subtitle: `Perfil prioritario - ${result.score} puntos`,
        message: commonMessage,
        nextSteps: commonSteps,
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200'
      };
    } else if (result.prioridad === 'media') {
      return {
        icon: <CheckCircle className="w-16 h-16 text-yellow-500" />,
        title: '¡Formulario enviado correctamente!',
        subtitle: `En lista de espera - ${result.score} puntos`,
        message: commonMessage,
        nextSteps: commonSteps,
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200'
      };
    } else {
      return {
        icon: <CheckCircle className="w-16 h-16 text-blue-500" />,
        title: '¡Formulario enviado correctamente!',
        subtitle: `Solicitud recibida - ${result.score} puntos`,
        message: commonMessage,
        nextSteps: commonSteps,
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200'
      };
    }
  };
  
  const info = getPrioridadInfo();
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Success Icon */}
        <div className="text-center mb-8">
          {info.icon}
        </div>
        
        {/* Title */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            {info.title}
          </h1>
          <p className="text-xl text-gray-600">
            {info.subtitle}
          </p>
        </div>
        
        {/* Main Card */}
        <div className={`${info.bgColor} border-2 ${info.borderColor} rounded-xl p-8 mb-6`}>
          <div className="prose max-w-none">
            <p className="text-lg text-gray-800 mb-6 whitespace-pre-line">
              {info.message}
            </p>
            
            <div className="space-y-2 mb-6">
              {info.nextSteps.map((step, index) => (
                <p key={index} className="text-gray-700">
                  {step}
                </p>
              ))}
            </div>
            
            <p className="text-gray-700 mt-6">
              Mientras tanto, te recomiendo mantenerte activo/a en tus entrenamientos y revisar los 
              correos que te irán llegando con contenido exclusivo para quienes están en la lista prioritaria.
            </p>
          </div>
        </div>
        
        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => navigate('/')}
            className="px-8 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-cyan-700 transition-colors"
          >
            Volver al Inicio
          </button>
          
          {info.showTeamButton && (
            <button
              onClick={() => navigate('/register')}
              className="px-8 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg font-medium hover:from-green-700 hover:to-emerald-700 transition-colors"
            >
              Trabaja con mi Equipo
            </button>
          )}
        </div>
        
        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-gray-600">
            Nos vemos pronto.
          </p>
          <p className="text-xl font-bold text-gray-900 mt-2">
            — Jorge Calcerrada
          </p>
        </div>
      </div>
    </div>
  );
};

export default WaitlistConfirmacion;
