import React from 'react';
import { Button } from './ui/button';
import { ArrowRight } from 'lucide-react';

const HeroSection = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-blue-50 via-white to-orange-50">
      {/* Background Abstract Image */}
      <div className="absolute inset-0 opacity-10">
        <img
          src="https://images.unsplash.com/photo-1633158834806-766387547d2c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHwxfHxtaW5kc2V0JTIwdHJhbnNmb3JtYXRpb258ZW58MHx8fHwxNzYxNDE2MjYwfDA&ixlib=rb-4.1.0&q=85"
          alt="Transformation"
          className="w-full h-full object-cover"
        />
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-20 text-center">
        <div className="animate-fade-in-up">
          {/* Main Headline */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 leading-tight mb-6">
            Esto no va de perfección,
            <span className="block mt-2 bg-gradient-to-r from-blue-400 to-orange-400 bg-clip-text text-transparent">
              va de constancia.
            </span>
          </h1>

          {/* Sub-headline */}
          <p className="text-xl sm:text-2xl text-gray-700 max-w-3xl mx-auto mb-8 leading-relaxed">
            Cada comida, cada entrenamiento, cada decisión cuenta.
          </p>

          <p className="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto mb-12">
            Método profesional de entrenamiento, nutrición y mentalidad creado por <span className="font-semibold text-blue-500">Jorge Calcerrada</span>.
          </p>

          {/* Primary CTA */}
          <Button
            size="lg"
            className="bg-gradient-to-r from-blue-400 to-blue-500 hover:from-blue-500 hover:to-blue-600 text-white px-12 py-6 text-lg font-semibold rounded-full shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
            onClick={() => window.open('https://forms.gle/TcZKhsrEVUoxJJLx9', '_blank')}
          >
            OBTÉN TU DIAGNÓSTICO GRATUITO
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-10 left-1/2 transform -translate-x-1/2 animate-bounce">
          <div className="w-6 h-10 border-2 border-gray-400 rounded-full flex items-start justify-center p-2">
            <div className="w-1 h-3 bg-gray-400 rounded-full"></div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;