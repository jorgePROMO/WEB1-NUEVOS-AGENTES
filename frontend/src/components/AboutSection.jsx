import React from 'react';
import { Target, Brain, Dumbbell } from 'lucide-react';

const AboutSection = () => {
  return (
    <section id="about" className="py-24 bg-white">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Image Side */}
          <div className="relative">
            <div className="aspect-square rounded-3xl overflow-hidden shadow-2xl">
              <img
                src="https://images.unsplash.com/photo-1758930908722-6f8f561d7473?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHwyfHxtaW5kc2V0JTIwdHJhbnNmb3JtYXRpb258ZW58MHx8fHwxNzYxNDE2MjYwfDA&ixlib=rb-4.1.0&q=85"
                alt="Growth and Transformation"
                className="w-full h-full object-cover"
              />
            </div>
            {/* Decorative Element */}
            <div className="absolute -bottom-6 -right-6 w-48 h-48 bg-orange-200 rounded-full opacity-40 blur-3xl"></div>
            <div className="absolute -top-6 -left-6 w-48 h-48 bg-blue-200 rounded-full opacity-40 blur-3xl"></div>
          </div>

          {/* Content Side */}
          <div>
            <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-8">
              Sobre mí
            </h2>

            <div className="space-y-6 text-gray-700 text-lg leading-relaxed">
              <p>
                Soy Jorge Calcerrada, entrenador personal y creador de un sistema integrado de entrenamiento, nutrición y mentalidad.
              </p>

              <p className="text-2xl font-bold text-blue-500 my-8">
                Construyo sistemas que transforman personas.
              </p>

              <p>
                Durante años he trabajado con personas que lo habían intentado todo: dietas restrictivas, rutinas imposibles, promesas vacías. Y fracasaban una y otra vez. No porque no tuvieran fuerza de voluntad, sino porque seguían planes que no encajaban con su realidad.
              </p>

              <p>
                Entendí algo fundamental: la transformación real no empieza en el gimnasio ni en la cocina.
              </p>

              <p className="text-2xl font-bold text-orange-400 my-8">
                No busques un nuevo plan, busca una nueva forma de pensar.
              </p>

              <p>
                Mi método combina entrenamiento inteligente, nutrición estratégica y una mentalidad orientada al proceso. No prometo resultados mágicos en 30 días. Construyo hábitos reales, sostenibles y adaptados a tu vida.
              </p>

              <p>
                Porque esto no va de motivación. Va de claridad, estructura y constancia.
              </p>
            </div>

            {/* Key Points */}
            <div className="grid sm:grid-cols-3 gap-6 mt-12">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 text-blue-500 mb-4">
                  <Dumbbell className="h-8 w-8" />
                </div>
                <h3 className="font-semibold text-gray-900">Entrenamiento</h3>
                <p className="text-sm text-gray-600 mt-2">Adaptado a tu nivel</p>
              </div>
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-orange-100 text-orange-500 mb-4">
                  <Target className="h-8 w-8" />
                </div>
                <h3 className="font-semibold text-gray-900">Nutrición</h3>
                <p className="text-sm text-gray-600 mt-2">Estratégica y flexible</p>
              </div>
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 text-blue-500 mb-4">
                  <Brain className="h-8 w-8" />
                </div>
                <h3 className="font-semibold text-gray-900">Mentalidad</h3>
                <p className="text-sm text-gray-600 mt-2">Orientada al proceso</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AboutSection;