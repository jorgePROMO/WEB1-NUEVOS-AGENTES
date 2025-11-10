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
    if (result.prioridad === 'alta') {
      return {
        icon: <CheckCircle className="w-16 h-16 text-green-500" />,
        title: '🔥 ¡Perfil Prioritario!',
        subtitle: 'Eres candidato ideal para el programa',
        message: `Gracias por completar tu solicitud, ${result.nombre.split(' ')[0]}. Tu perfil ha sido calificado con una puntuación de **${result.score} puntos**, lo que te coloca en la **categoría prioritaria**.`,
        nextSteps: [
          'Recibirás un mensaje privado en las próximas **24-48 horas**',
          'Te enviaré los siguientes pasos para agendar una breve llamada de valoración',
          'Esta llamada dura aproximadamente 15 minutos y es el último paso antes de comenzar'
        ],
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200'
      };
    } else if (result.prioridad === 'media') {
      return {
        icon: <Clock className="w-16 h-16 text-yellow-500" />,
        title: '⚡ En Lista de Espera',
        subtitle: 'Tu solicitud está siendo revisada',
        message: `Gracias por completar tu solicitud, ${result.nombre.split(' ')[0]}. Tu perfil ha sido calificado con **${result.score} puntos**.`,
        nextSteps: [
          'Revisaré tu candidatura durante la próxima semana',
          'Si tu perfil encaja, recibirás un mensaje con los siguientes pasos',
          'Mientras tanto, te mantendré en la lista prioritaria de espera',
          'Recibirás contenido exclusivo por email para quienes están en la lista'
        ],
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200'
      };
    } else {
      return {
        icon: <AlertCircle className="w-16 h-16 text-blue-500" />,
        title: '💙 Gracias por tu Interés',
        subtitle: 'Explora otras opciones',
        message: `Gracias por tu interés, ${result.nombre.split(' ')[0]}. Después de revisar tu candidatura, creo que podrías beneficiarte más de trabajar con mi equipo.`,
        nextSteps: [
          'El programa personal tiene requisitos muy específicos de compromiso y disponibilidad',
          'Sin embargo, mi equipo ofrece opciones más flexibles que pueden adaptarse mejor a tu situación actual',
          'Te recomiendo explorar la opción de **Trabaja con mi Equipo**'
        ],
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
        showTeamButton: true
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
            <p className="text-lg text-gray-800 mb-6">
              {info.message}
            </p>
            
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              📸 Próximos pasos:
            </h3>
            <ul className="space-y-3">
              {info.nextSteps.map((step, index) => (
                <li key={index} className="text-gray-700">
                  {step}
                </li>
              ))}
            </ul>
          </div>
        </div>
        
        {/* Additional Info Card */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h3 className="text-lg font-bold text-gray-900 mb-3">
            📋 Mientras tanto...
          </h3>
          <p className="text-gray-700 mb-4">
            Te recomiendo mantenerte activo/a en tus entrenamientos y revisar los 
            correos que te irán llegando con contenido exclusivo para quienes están 
            en la lista prioritaria.
          </p>
          <p className="text-gray-700">
            Recuerda revisar tu carpeta de spam por si el email cae ahí.
          </p>
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
