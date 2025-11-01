import React, { useState } from 'react';
import { Button } from './ui/button';
import { ArrowRight } from 'lucide-react';
import QuestionnaireModal from './QuestionnaireModal';

const HeroSection = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // URL del cuestionario - el usuario la proporcionará
  const questionnaireUrl = ""; // AQUÍ PONES LA URL QUE TE DÉ EL USUARIO

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-blue-50 via-white to-orange-50 pt-24 sm:pt-32 md:pt-20">
      {/* Background Image */}
      <div className="absolute inset-0">
        <img
          src="https://customer-assets.emergentagent.com/job_landing-details/artifacts/tw2x0ku0_WhatsApp%20Image%202025-10-25%20at%2021.18.51.jpeg"
          alt="Jorge Calcerrada Training"
          className="w-full h-full object-cover opacity-20"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50/90 via-white/90 to-orange-50/90"></div>
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
            onClick={() => setIsModalOpen(true)}
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

      {/* Questionnaire Modal */}
      <QuestionnaireModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)}
        iframeUrl={questionnaireUrl}
      />
    </section>
  );
};

export default HeroSection;