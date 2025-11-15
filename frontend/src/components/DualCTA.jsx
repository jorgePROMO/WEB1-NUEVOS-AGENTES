import React from 'react';
import { Button } from './ui/button';
import { useNavigate } from 'react-router-dom';
import { Users, User } from 'lucide-react';

const DualCTA = ({ 
  title = "¿Listo para transformar tu vida?",
  subtitle = "Elige la opción que mejor se adapte a ti",
  variant = "default" // default, compact, inline
}) => {
  const navigate = useNavigate();

  if (variant === "inline") {
    return (
      <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
        <Button
          onClick={() => navigate('/trabaja-conmigo')}
          className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white px-8 py-6 rounded-full font-bold shadow-lg transform hover:scale-105 transition-all duration-300 w-full sm:w-auto"
        >
          <User className="mr-2" size={20} />
          TRABAJA CONMIGO
        </Button>
        <Button
          onClick={() => navigate('/register')}
          className="bg-gradient-to-r from-blue-500 to-green-500 hover:from-blue-600 hover:to-green-600 text-white px-8 py-6 rounded-full font-bold shadow-lg transform hover:scale-105 transition-all duration-300 w-full sm:w-auto"
        >
          <Users className="mr-2" size={20} />
          TRABAJA CON MI EQUIPO
        </Button>
      </div>
    );
  }

  if (variant === "compact") {
    return (
      <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-2xl p-8 my-8">
        <h3 className="text-2xl font-bold text-center mb-6 text-gray-900">
          {title}
        </h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
            <div className="text-center mb-4">
              <div className="inline-block bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-full p-3 mb-3">
                <User size={32} />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-2">Trabaja Conmigo</h4>
              <p className="text-gray-600 text-sm mb-4">
                Acompañamiento 1 a 1 personalizado. Plazas limitadas.
              </p>
            </div>
            <Button
              onClick={() => navigate('/trabaja-conmigo')}
              className="w-full bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white font-bold py-3"
            >
              SOLICITAR PLAZA
            </Button>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
            <div className="text-center mb-4">
              <div className="inline-block bg-gradient-to-r from-blue-500 to-green-500 text-white rounded-full p-3 mb-3">
                <Users size={32} />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-2">Trabaja con Mi Equipo</h4>
              <p className="text-gray-600 text-sm mb-4">
                Acceso completo al sistema E.D.N.360™. Disponible ahora.
              </p>
            </div>
            <Button
              onClick={() => navigate('/register')}
              className="w-full bg-gradient-to-r from-blue-500 to-green-500 hover:from-blue-600 hover:to-green-600 text-white font-bold py-3"
            >
              EMPEZAR AHORA
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Default variant - full section
  return (
    <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white mb-4">
            {title}
          </h2>
          <p className="text-xl text-gray-300">
            {subtitle}
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Trabaja Conmigo */}
          <div className="bg-gradient-to-br from-orange-500 to-red-600 rounded-3xl p-8 shadow-2xl transform hover:scale-105 transition-all duration-300">
            <div className="text-center mb-6">
              <div className="inline-block bg-white/20 rounded-full p-4 mb-4">
                <User size={48} className="text-white" />
              </div>
              <h3 className="text-3xl font-black text-white mb-3">
                Trabaja Conmigo
              </h3>
              <div className="bg-white/20 rounded-xl p-4 mb-4">
                <p className="text-white font-semibold text-lg">
                  Acompañamiento 1 a 1 Personalizado
                </p>
              </div>
            </div>

            <ul className="space-y-3 mb-8 text-white">
              <li className="flex items-start gap-2">
                <span className="text-2xl">✓</span>
                <span>Atención directa y personalizada</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-2xl">✓</span>
                <span>Seguimiento exhaustivo semanal</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-2xl">✓</span>
                <span>Ajustes inmediatos según tu progreso</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-2xl">✓</span>
                <span>Acceso directo a mí por WhatsApp</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-2xl">⚠️</span>
                <span className="font-bold">Plazas muy limitadas</span>
              </li>
            </ul>

            <Button
              onClick={() => navigate('/trabaja-conmigo')}
              className="w-full bg-white text-orange-600 hover:bg-gray-100 text-xl py-6 rounded-full font-black shadow-xl"
            >
              SOLICITAR PLAZA →
            </Button>
          </div>

          {/* Trabaja con Mi Equipo */}
          <div className="bg-gradient-to-br from-blue-500 to-green-600 rounded-3xl p-8 shadow-2xl transform hover:scale-105 transition-all duration-300">
            <div className="text-center mb-6">
              <div className="inline-block bg-white/20 rounded-full p-4 mb-4">
                <Users size={48} className="text-white" />
              </div>
              <h3 className="text-3xl font-black text-white mb-3">
                Trabaja con Mi Equipo
              </h3>
              <div className="bg-white/20 rounded-xl p-4 mb-4">
                <p className="text-white font-semibold text-lg">
                  Sistema E.D.N.360™ Completo
                </p>
              </div>
            </div>

            <ul className="space-y-3 mb-8 text-white">
              <li className="flex items-start gap-2">
                <span className="text-2xl">✓</span>
                <span>Acceso completo al sistema E.D.N.360™</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-2xl">✓</span>
                <span>Seguimiento profesional de mi equipo</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-2xl">✓</span>
                <span>Planes personalizados de entreno y nutrición</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-2xl">✓</span>
                <span>Revisiones mensuales y ajustes</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-2xl">✓</span>
                <span className="font-bold">Disponible ahora</span>
              </li>
            </ul>

            <Button
              onClick={() => navigate('/register')}
              className="w-full bg-white text-blue-600 hover:bg-gray-100 text-xl py-6 rounded-full font-black shadow-xl"
            >
              EMPEZAR AHORA →
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default DualCTA;
