import React from 'react';
import { Button } from './ui/button';
import { ArrowRight } from 'lucide-react';

const FinalCTA = () => {
  return (
    <section className="py-24 bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
          backgroundSize: '40px 40px'
        }}></div>
      </div>

      <div className="relative z-10 max-w-5xl mx-auto px-6 sm:px-8 lg:px-12 text-center">
        {/* Main Headline */}
        <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight mb-8">
          No busques el plan perfecto,
          <span className="block mt-3 bg-gradient-to-r from-blue-400 to-orange-400 bg-clip-text text-transparent">
            empieza con el que puedas mantener.
          </span>
        </h2>

        <p className="text-xl sm:text-2xl text-gray-300 max-w-3xl mx-auto mb-12 leading-relaxed">
          Deja de probar dietas y planes que no funcionan. Empieza a construir hábitos reales y sostenibles.
        </p>

        {/* CTA Button */}
        <Button
          size="lg"
          className="bg-gradient-to-r from-orange-400 to-orange-500 hover:from-orange-500 hover:to-orange-600 text-white px-16 py-7 text-xl font-bold rounded-full shadow-2xl hover:shadow-orange-500/50 transform hover:scale-105 transition-all duration-300"
          onClick={() => window.location.href = '/trabaja-conmigo'}
        >
          TRABAJA CON JORGE
          <ArrowRight className="ml-3 h-6 w-6" />
        </Button>

        {/* Additional Info */}
        <div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-8 text-gray-400">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
            <span>Sin permanencia</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
            <span>Plazas limitadas</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
            <span>Método profesional</span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FinalCTA;