import React from 'react';
import { Eye, Calendar, TrendingUp, CheckCircle } from 'lucide-react';
import { Card, CardContent } from './ui/card';

const MethodSection = () => {
  const steps = [
    {
      icon: Eye,
      title: 'Observación',
      description: '7 días analizando tus hábitos reales, sin restricciones ni juicios. Registro completo de rutinas, energía, hambre y emociones.',
      color: 'blue'
    },
    {
      icon: Calendar,
      title: 'Comprensión',
      description: 'Entendemos tu contexto real: horarios, preferencias, limitaciones. No imponemos, adaptamos.',
      color: 'orange'
    },
    {
      icon: TrendingUp,
      title: 'Construcción',
      description: 'Creamos un sistema progresivo: entrenamiento adaptado + nutrición lógica + educación continua.',
      color: 'blue'
    },
    {
      icon: CheckCircle,
      title: 'Ajuste',
      description: 'Modificaciones con sentido y propósito. Sin prohibiciones absurdas, sin dogmas, sin ansiedad.',
      color: 'orange'
    }
  ];

  return (
    <section id="method" className="py-24 bg-gradient-to-br from-gray-50 via-blue-50 to-orange-50">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Cómo funciona el método
          </h2>
          <p className="text-xl text-gray-700 max-w-3xl mx-auto leading-relaxed">
            Primero observo, después adapto. No impongo un plan. Construyo un sistema realista y sostenible basado en claridad, no solo motivación.
          </p>
        </div>

        {/* Method Image */}
        <div className="mb-16">
          <div className="relative rounded-3xl overflow-hidden shadow-2xl max-w-4xl mx-auto">
            <img
              src="https://images.unsplash.com/photo-1704969724398-ec70386c9b1b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHw0fHxtaW5kc2V0JTIwdHJhbnNmb3JtYXRpb258ZW58MHx8fHwxNzYxNDE2MjYwfDA&ixlib=rb-4.1.0&q=85"
              alt="Method Mindset"
              className="w-full h-80 object-cover"
            />
          </div>
        </div>

        {/* Steps */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => {
            const Icon = step.icon;
            const bgColor = step.color === 'blue' ? 'bg-blue-100' : 'bg-orange-100';
            const textColor = step.color === 'blue' ? 'text-blue-500' : 'text-orange-500';
            
            return (
              <Card key={index} className="border-none shadow-lg hover:shadow-xl transition-shadow duration-300">
                <CardContent className="p-8">
                  <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full ${bgColor} ${textColor} mb-6`}>
                    <Icon className="h-8 w-8" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-4">
                    {step.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {step.description}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Bottom Message */}
        <div className="mt-16 text-center">
          <div className="inline-block bg-white rounded-2xl shadow-lg px-8 py-6 max-w-2xl">
            <p className="text-xl font-semibold text-gray-900">
              El objetivo: crear una rutina realista y sostenible que funcione con claridad, no solo con motivación.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default MethodSection;