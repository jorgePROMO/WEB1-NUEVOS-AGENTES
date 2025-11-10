import React from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Check, Users, User, Star } from 'lucide-react';

const ServicesSection = () => {
  return (
    <section id="services" className="py-16 sm:py-24 bg-white">
      <div className="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12">
        {/* Header */}
        <div className="text-center mb-12 sm:mb-16 px-4">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4 sm:mb-6">
            Servicios disponibles
          </h2>
          <p className="text-base sm:text-lg md:text-xl text-gray-700 max-w-3xl mx-auto">
            Elige la opción que mejor se adapte a tus necesidades. Ambas opciones incluyen estructura, apoyo y claridad.
          </p>
        </div>

        {/* Services Grid */}
        <div className="grid md:grid-cols-2 gap-6 sm:gap-8 px-2 sm:px-0 max-w-6xl mx-auto">
          {/* Team Service */}
          <Card className="border-2 border-blue-200 hover:border-blue-400 transition-all duration-300 shadow-lg hover:shadow-2xl">
            <CardHeader className="bg-gradient-to-br from-blue-50 to-blue-100 pb-8">
              <div className="flex items-center justify-center mb-4">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-500 text-white">
                  <Users className="h-8 w-8" />
                </div>
              </div>
              <CardTitle className="text-3xl font-bold text-center text-gray-900">
                Trabaja con mi equipo
              </CardTitle>
              <div className="text-center mt-6">
                <div className="flex items-baseline justify-center gap-2">
                  <span className="text-5xl font-bold text-blue-500">49,90€</span>
                  <span className="text-xl text-gray-600">/mes</span>
                </div>
                <p className="text-sm text-gray-600 mt-2">Sin permanencia</p>
              </div>
            </CardHeader>
            <CardContent className="pt-8 pb-8">
              <ul className="space-y-4 mb-8">
                {[
                  'Plan de entrenamiento adaptado (nivel, espacio, equipamiento)',
                  'Nutrición estilo menú (estructurada, flexible, fácil de seguir)',
                  'Revisión mensual por chat',
                  'Chat privado con miembro del equipo (formado bajo mis estándares)',
                  'Seguimiento visual y recordatorios',
                  'Todos los planes validados personalmente por Jorge'
                ].map((feature, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <Check className="h-6 w-6 text-blue-500 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>
              <Button
                className="w-full bg-blue-500 hover:bg-blue-600 text-white py-6 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
                onClick={() => window.location.href = '/register'}
              >
                QUIERO ESTE PLAN
              </Button>
            </CardContent>
          </Card>

          {/* Direct Service - Premium */}
          <Card className="border-2 border-orange-300 hover:border-orange-500 transition-all duration-300 shadow-xl hover:shadow-2xl relative overflow-hidden">
            {/* Premium Badge */}
            <div className="absolute top-6 right-6 bg-gradient-to-r from-orange-400 to-orange-500 text-white px-4 py-2 rounded-full text-sm font-semibold flex items-center gap-2 shadow-lg">
              <Star className="h-4 w-4" />
              Exclusivo
            </div>
            
            <CardHeader className="bg-gradient-to-br from-orange-50 via-orange-100 to-orange-50 pb-8">
              <div className="flex items-center justify-center mb-4">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-orange-400 to-orange-500 text-white">
                  <User className="h-8 w-8" />
                </div>
              </div>
              <CardTitle className="text-3xl font-bold text-center text-gray-900">
                Trabaja conmigo
              </CardTitle>
              <div className="text-center mt-6">
                <div className="flex items-baseline justify-center gap-2">
                  <span className="text-5xl font-bold bg-gradient-to-r from-orange-400 to-orange-500 bg-clip-text text-transparent">500€</span>
                  <span className="text-xl text-gray-600">/trimestre</span>
                </div>
                <p className="text-sm font-semibold text-orange-600 mt-4 bg-orange-50 inline-block px-4 py-2 rounded-full">
                  Solo 10 clientes activos por ciclo
                </p>
              </div>
            </CardHeader>
            <CardContent className="pt-8 pb-8">
              <ul className="space-y-4 mb-8">
                {[
                  'Trabajo directo con Jorge',
                  'Entrenamiento 100% personalizado (objetivos, horarios, limitaciones)',
                  'Nutrición basada en tablas de equivalencias (educación + flexibilidad)',
                  'Revisión mensual directamente con Jorge',
                  'Ajustes ilimitados por WhatsApp',
                  'Contacto continuo y apoyo total',
                  'Acceso limitado: solo 10 clientes activos'
                ].map((feature, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <Check className="h-6 w-6 text-orange-500 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700 font-medium">{feature}</span>
                  </li>
                ))}
              </ul>
              <Button
                className="w-full bg-gradient-to-r from-orange-400 to-orange-500 hover:from-orange-500 hover:to-orange-600 text-white py-6 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
                onClick={() => window.open('https://calendar.app.google/m7bECfMJ52dp1UgK7', '_blank')}
              >
                Solicitar videollamada con Jorge
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
};

export default ServicesSection;