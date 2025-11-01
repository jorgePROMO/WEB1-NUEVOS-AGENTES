import React from 'react';
import { Target, Brain, Dumbbell } from 'lucide-react';

const AboutSection = () => {
  return (
    <section id="about" className="py-16 sm:py-24 bg-white">
      <div className="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Image Side */}
          <div className="relative px-4 sm:px-0">
            <div className="aspect-square rounded-3xl overflow-hidden shadow-2xl">
              <img
                src="https://customer-assets.emergentagent.com/job_landing-details/artifacts/xzer6hch_WhatsApp%20Image%202025-10-25%20at%2021.18.29.jpeg"
                alt="Jorge Calcerrada - Entrenador Personal"
                className="w-full h-full object-cover"
              />
            </div>
            {/* Decorative Element */}
            <div className="absolute -bottom-6 -right-6 w-48 h-48 bg-orange-200 rounded-full opacity-40 blur-3xl"></div>
            <div className="absolute -top-6 -left-6 w-48 h-48 bg-blue-200 rounded-full opacity-40 blur-3xl"></div>
          </div>

          {/* Content Side */}
          <div className="px-4 sm:px-0">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-6 sm:mb-8">
              Sobre <span className="text-blue-500">mí</span>
            </h2>

            <div className="space-y-6 text-gray-700 text-lg leading-relaxed">
              <p>
                Durante años creí que para transformar un cuerpo hacía falta sacrificio, fuerza de voluntad y toneladas de motivación. Hoy sé que no es así.
              </p>

              <p className="text-xl font-bold text-gray-900">
                La verdadera transformación no empieza en el gimnasio ni en la cocina, empieza en la cabeza.
              </p>

              <p>
                Y no va de hacerlo perfecto, va de hacerlo bien y con constancia.
              </p>

              <p className="text-xl font-bold text-blue-500 mt-6">
                Soy Jorge Calcerrada, entrenador personal.
              </p>

              <p>
                He pasado por todas las etapas: el chaval que entrenaba sin rumbo, el profesional obsesionado con la perfección, y el mentor que entendió que el verdadero cambio sucede cuando aprendes a construir hábitos reales —no cuando sigues un plan imposible durante tres semanas.
              </p>

              <p>
                Llevo más de una década ayudando a personas a recuperar el control de su cuerpo, su energía y su mentalidad. No enseño dietas. No vendo entrenamientos genéricos.
              </p>

              <p className="text-2xl font-bold text-orange-500 my-8">
                Construyo sistemas que transforman personas.
              </p>

              <div className="bg-gradient-to-r from-blue-50 to-orange-50 rounded-2xl p-8 my-8">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Mi trabajo combina tres pilares:</h3>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold">1</span>
                    <div>
                      <p className="font-semibold text-gray-900">Entrenamiento inteligente:</p>
                      <p className="text-gray-700">basado en ciencia, orientado a resultados reales y sostenibles, no en modas ni trucos rápidos.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-8 h-8 bg-orange-500 text-white rounded-full flex items-center justify-center font-bold">2</span>
                    <div>
                      <p className="font-semibold text-gray-900">Nutrición estratégica:</p>
                      <p className="text-gray-700">porque comer no es un castigo, es una herramienta. Cada plan tiene un propósito y una lógica detrás.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold">3</span>
                    <div>
                      <p className="font-semibold text-gray-900">Mentalidad de proceso:</p>
                      <p className="text-gray-700">sin esto, lo demás no sirve. Si no entiendes el por qué de lo que haces, tarde o temprano abandonarás.</p>
                    </div>
                  </div>
                </div>
              </div>

              <p>
                He diseñado programas tanto para personas que buscan un cambio físico real (donde trabajo mano a mano con cada cliente) como para quienes necesitan una guía profesional validada por mí y mi equipo (con seguimiento, estructura y claridad total).
              </p>

              <p className="font-semibold text-gray-900">
                Ambos parten de una misma base: la constancia supera al talento, y el compromiso gana siempre al entusiasmo pasajero.
              </p>

              <div className="bg-gray-900 text-white rounded-2xl p-8 my-8">
                <p className="text-sm font-semibold text-orange-400 mb-2">Mi lema lo resume todo:</p>
                <p className="text-xl italic leading-relaxed">
                  "Cada comida, cada entrenamiento, cada decisión cuenta.
                  <br />
                  Esto no va de perfección, va de constancia.
                  <br />
                  No va de sacrificio, va de compromiso contigo mismo."
                </p>
              </div>

              <p>
                No pretendo ser el típico entrenador que promete resultados en 21 días.
              </p>

              <p className="font-semibold text-gray-900">
                Mi objetivo es que aprendas a hacerlo bien de una vez por todas, con un método que entiendas, que disfrutes y que puedas mantener.
              </p>

              <p>
                Trabajo con profesionales que quieren recuperar su forma física sin perder el foco en su vida, y con personas que están cansadas de empezar siempre desde cero.
              </p>

              <p className="text-xl font-bold text-blue-500">
                Porque lo que te falta no es disciplina. Es estrategia, claridad y acompañamiento real.
              </p>

              <p className="text-gray-900 font-semibold mt-8">
                Si has llegado hasta aquí, es por una razón.
              </p>

              <p className="text-2xl font-bold text-orange-500">
                No busques un nuevo plan: busca una nueva forma de pensar.
              </p>

              <p className="text-gray-900 font-semibold">
                Y si estás listo para hacerlo bien esta vez, te acompaño en el proceso.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AboutSection;