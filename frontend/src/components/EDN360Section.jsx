import React from 'react';
import { Button } from './ui/button';
import { useNavigate } from 'react-router-dom';

const EDN360Section = () => {
  const navigate = useNavigate();

  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-green-50 via-white to-blue-50">
      <div className="max-w-6xl mx-auto">
        {/* Encabezado con Logo */}
        <div className="text-center mb-16">
          <div className="inline-block mb-8">
            <img 
              src="/logo-sin-fondo.png" 
              alt="Jorge Calcerrada" 
              className="h-24 w-auto mx-auto"
            />
          </div>
          <div className="inline-block bg-gradient-to-r from-green-500 to-blue-500 text-white px-8 py-4 rounded-2xl shadow-2xl mb-6">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-black">
              SISTEMA E.D.N.360™
            </h2>
          </div>
          <p className="text-xl sm:text-2xl text-gray-700 font-semibold mt-6 max-w-4xl mx-auto">
            El método definitivo para transformar tu cuerpo y tu vida de forma real y sostenible
          </p>
        </div>

        {/* Problema */}
        <div className="bg-white rounded-3xl shadow-xl p-8 sm:p-12 mb-12">
          <p className="text-lg sm:text-xl text-gray-700 leading-relaxed mb-6">
            Has probado entrenos, dietas y apps.
            <br />
            Nada funciona a largo plazo porque siempre falta una pieza.
          </p>
          <p className="text-lg sm:text-xl text-gray-900 font-bold leading-relaxed mb-6">
            El Sistema E.D.N.360™ une TODAS las piezas.
            <br />
            <span className="text-green-600">Entrenamiento</span>. <span className="text-blue-600">Nutrición</span>. <span className="text-purple-600">Neuroconducta</span>.
          </p>
          <p className="text-lg sm:text-xl text-gray-700 leading-relaxed">
            Integrados en un único sistema que te lleva paso a paso hacia tu mejor versión… y te enseña a mantenerla.
          </p>
        </div>

        {/* No es otro plan más */}
        <div className="text-center mb-16">
          <div className="inline-block bg-gradient-to-r from-orange-500 to-red-500 text-white px-6 py-3 rounded-xl mb-6">
            <p className="text-2xl sm:text-3xl font-bold">🔥 No es otro plan más. Es un sistema.</p>
          </div>
          <p className="text-lg text-gray-700 max-w-3xl mx-auto">
            Un método propio, basado en ciencia y diseñado para personas que quieren resultados reales sin vivir esclavos de la fuerza de voluntad.
          </p>
        </div>

        {/* Los 3 Pilares */}
        <div className="mb-16">
          <h3 className="text-3xl sm:text-4xl font-bold text-center mb-12 bg-gradient-to-r from-green-500 to-blue-500 bg-clip-text text-transparent">
            Qué significa E.D.N.360™
          </h3>
          
          <div className="grid md:grid-cols-3 gap-8">
            {/* E - Entrenamiento */}
            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-3xl p-8 text-white shadow-2xl transform hover:scale-105 transition-all duration-300">
              <div className="text-5xl font-black mb-4">E</div>
              <h4 className="text-2xl font-bold mb-4">Entrenamiento</h4>
              <p className="text-green-100 leading-relaxed mb-4">
                Programación inteligente, adaptada a tu nivel, horarios y estilo de vida.
              </p>
              <p className="text-white font-semibold">
                Progresión clara, ejercicios eficaces y mejoras medibles semana a semana.
              </p>
              <p className="text-green-100 mt-4 italic">
                Para que tu cuerpo mejore sin lesiones, sin caos y sin perder tiempo.
              </p>
            </div>

            {/* D - Dieta/Nutrición */}
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-3xl p-8 text-white shadow-2xl transform hover:scale-105 transition-all duration-300">
              <div className="text-5xl font-black mb-4">D</div>
              <h4 className="text-2xl font-bold mb-4">Dieta / Nutrición</h4>
              <p className="text-blue-100 leading-relaxed mb-4">
                Una estrategia nutricional que encaja en tu vida: flexible, estructurada y fácil de mantener.
              </p>
              <p className="text-white font-semibold">
                Nada de prohibiciones absurdas. Nada de ansiedad. Nada de "empieza el lunes".
              </p>
              <p className="text-blue-100 mt-4 italic">
                Comes bien, avanzas y entiendes lo que estás haciendo.
              </p>
            </div>

            {/* N - Neuroconducta */}
            <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-3xl p-8 text-white shadow-2xl transform hover:scale-105 transition-all duration-300">
              <div className="text-5xl font-black mb-4">N</div>
              <h4 className="text-2xl font-bold mb-4">Neuroconducta y Hábitos</h4>
              <p className="text-purple-100 leading-relaxed mb-4">
                La pieza que casi nadie trabaja.
                <br />
                Aquí es donde realmente cambias:
              </p>
              <ul className="text-white font-semibold space-y-2 mb-4">
                <li>• Adherencia real</li>
                <li>• Psicología del cambio</li>
                <li>• Gestión del hambre e impulsos</li>
                <li>• Rutinas y mentalidad</li>
              </ul>
              <p className="text-purple-100 italic">
                Si tu mente no cambia, tus resultados tampoco. Este pilar lo soluciona.
              </p>
            </div>
          </div>
        </div>

        {/* Por qué 360 */}
        <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-3xl p-8 sm:p-12 mb-16 text-white shadow-2xl">
          <h3 className="text-3xl sm:text-4xl font-bold mb-6">🔄 Por qué 360™</h3>
          <p className="text-lg sm:text-xl text-gray-300 leading-relaxed mb-4">
            Porque tu vida no es solo un entrenamiento o una dieta.
          </p>
          <p className="text-lg sm:text-xl text-white font-semibold leading-relaxed mb-4">
            Es trabajo, horarios, estrés, energía, familia, sueño, emociones.
          </p>
          <p className="text-xl sm:text-2xl text-green-400 font-bold">
            E.D.N.360™ cubre todos los ángulos. No deja nada al azar.
          </p>
        </div>

        {/* Qué hace único este sistema */}
        <div className="bg-white rounded-3xl shadow-xl p-8 sm:p-12 mb-16">
          <h3 className="text-3xl sm:text-4xl font-bold text-center mb-8 text-gray-900">
            🚀 Qué hace único este sistema
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-300">
                  <th className="text-left py-4 px-4 text-gray-700 font-bold">Elemento</th>
                  <th className="text-left py-4 px-4 text-gray-700 font-bold">Tu ventaja</th>
                </tr>
              </thead>
              <tbody className="text-gray-700">
                <tr className="border-b border-gray-200">
                  <td className="py-4 px-4 font-semibold">Método propio</td>
                  <td className="py-4 px-4">Más claridad, más autoridad, más resultados</td>
                </tr>
                <tr className="border-b border-gray-200">
                  <td className="py-4 px-4 font-semibold">Integración ciencia + conducta</td>
                  <td className="py-4 px-4">Evitas el efecto rebote</td>
                </tr>
                <tr className="border-b border-gray-200">
                  <td className="py-4 px-4 font-semibold">Seguimiento inteligente</td>
                  <td className="py-4 px-4">Progresas incluso en semanas complicadas</td>
                </tr>
                <tr className="border-b border-gray-200">
                  <td className="py-4 px-4 font-semibold">Adaptación constante</td>
                  <td className="py-4 px-4">Tu plan evoluciona contigo</td>
                </tr>
                <tr>
                  <td className="py-4 px-4 font-semibold">Visión completa</td>
                  <td className="py-4 px-4">Entreno + nutrición + hábitos = transformación real</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Resultados */}
        <div className="bg-gradient-to-br from-blue-50 to-green-50 rounded-3xl p-8 sm:p-12 mb-16">
          <h3 className="text-3xl sm:text-4xl font-bold text-center mb-8 text-gray-900">
            ⭐ Resultados que puedes esperar
          </h3>
          <ul className="space-y-4 text-lg text-gray-700 max-w-3xl mx-auto">
            <li className="flex items-start gap-3">
              <span className="text-green-500 font-bold text-2xl">✓</span>
              <span>Perder grasa sin recuperarla después</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-green-500 font-bold text-2xl">✓</span>
              <span>Mejorar fuerza, postura y energía</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-green-500 font-bold text-2xl">✓</span>
              <span>Comer sin ansiedad ni culpa</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-green-500 font-bold text-2xl">✓</span>
              <span>Ganar control sobre tu vida y tus hábitos</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-green-500 font-bold text-2xl">✓</span>
              <span>Mantener resultados a largo plazo</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-green-500 font-bold text-2xl">✓</span>
              <span className="font-bold">Y, sobre todo: dejar de empezar una y otra vez</span>
            </li>
          </ul>
        </div>

        {/* En una frase */}
        <div className="text-center mb-16">
          <div className="bg-gradient-to-r from-green-500 to-blue-500 rounded-3xl p-8 sm:p-12 text-white shadow-2xl">
            <h3 className="text-2xl sm:text-3xl font-bold mb-6">🏁 En una frase</h3>
            <p className="text-xl sm:text-2xl font-semibold leading-relaxed">
              El Sistema E.D.N.360™ es tu hoja de ruta completa para transformar tu cuerpo y tu estilo de vida con ciencia, estrategia y constancia.
            </p>
          </div>
        </div>

        {/* CTA Final */}
        <div className="text-center">
          <h3 className="text-2xl sm:text-3xl font-bold mb-6 text-gray-900">
            ¿Quieres aplicar este sistema en tu vida?
          </h3>
          <p className="text-lg text-gray-700 mb-8 max-w-2xl mx-auto">
            Empieza hoy con un acompañamiento profesional y un método que funciona incluso cuando tú crees que no puedes.
          </p>
          <Button
            onClick={() => navigate('/register')}
            className="bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white text-xl px-12 py-6 rounded-full font-bold shadow-2xl transform hover:scale-105 transition-all duration-300"
          >
            👉 REGÍSTRATE AHORA
          </Button>
        </div>
      </div>
    </section>
  );
};

export default EDN360Section;
