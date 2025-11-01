import React from 'react';
import { Check, X } from 'lucide-react';
import { Card } from './ui/card';

const ComparisonTable = () => {
  const features = [
    { name: 'Atención directa de Jorge', team: false, direct: true },
    { name: 'Supervisión del equipo', team: true, direct: false },
    { name: 'Trabajo 1 a 1 con Jorge', team: false, direct: true },
    { name: 'Entrenamiento adaptado', team: true, direct: true },
    { name: 'Nutrición estilo menú', team: true, direct: false },
    { name: 'Nutrición basada en equivalencias', team: false, direct: true },
    { name: 'Revisión mensual', team: true, direct: true },
    { name: 'Soporte ilimitado', team: false, direct: true },
    { name: 'Precio', team: '49,90€/mes', direct: '500€/trimestre' },
    { name: 'Plazas limitadas', team: false, direct: true }
  ];

  return (
    <section id="comparison" className="py-16 sm:py-24 bg-gradient-to-br from-gray-50 to-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-8 lg:px-12">
        {/* Header */}
        <div className="text-center mb-12 sm:mb-16 px-2">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4 sm:mb-6">
            Comparación de servicios
          </h2>
          <p className="text-base sm:text-lg md:text-xl text-gray-700 max-w-3xl mx-auto px-4">
            Elige el camino que mejor se adapte a tus necesidades y objetivos.
          </p>
        </div>

        {/* Mobile View - Cards */}
        <div className="md:hidden space-y-6 px-2">
          {features.map((feature, index) => (
            <Card key={index} className="p-4 shadow-lg">
              <div className="font-semibold text-gray-900 mb-3 text-center border-b pb-2">
                {feature.name}
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="text-xs font-semibold text-blue-500 mb-2">EQUIPO</div>
                  {typeof feature.team === 'boolean' ? (
                    feature.team ? (
                      <Check className="h-6 w-6 text-blue-500 mx-auto" />
                    ) : (
                      <X className="h-6 w-6 text-gray-300 mx-auto" />
                    )
                  ) : (
                    <span className="text-blue-600 font-semibold text-sm">{feature.team}</span>
                  )}
                </div>
                <div className="text-center">
                  <div className="text-xs font-semibold text-orange-500 mb-2">JORGE</div>
                  {typeof feature.direct === 'boolean' ? (
                    feature.direct ? (
                      <Check className="h-6 w-6 text-orange-500 mx-auto" />
                    ) : (
                      <X className="h-6 w-6 text-gray-300 mx-auto" />
                    )
                  ) : (
                    <span className="text-orange-600 font-semibold text-sm">{feature.direct}</span>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Desktop View - Table */}
        <Card className="hidden md:block overflow-hidden shadow-2xl">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="px-6 py-6 text-left">
                    <span className="text-lg font-semibold text-gray-900">Características</span>
                  </th>
                  <th className="px-6 py-6 text-center bg-blue-50">
                    <span className="text-xl font-bold text-blue-500">Equipo</span>
                  </th>
                  <th className="px-6 py-6 text-center bg-gradient-to-br from-orange-50 to-orange-100">
                    <span className="text-xl font-bold text-orange-500">Jorge</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {features.map((feature, index) => (
                  <tr
                    key={index}
                    className={`border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                      index % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                    }`}
                  >
                    <td className="px-6 py-5 text-gray-700 font-medium">
                      {feature.name}
                    </td>
                    <td className="px-6 py-5 text-center">
                      {typeof feature.team === 'boolean' ? (
                        feature.team ? (
                          <Check className="h-6 w-6 text-blue-500 mx-auto" />
                        ) : (
                          <X className="h-6 w-6 text-gray-300 mx-auto" />
                        )
                      ) : (
                        <span className="text-blue-600 font-semibold">{feature.team}</span>
                      )}
                    </td>
                    <td className="px-6 py-5 text-center">
                      {typeof feature.direct === 'boolean' ? (
                        feature.direct ? (
                          <Check className="h-6 w-6 text-orange-500 mx-auto" />
                        ) : (
                          <X className="h-6 w-6 text-gray-300 mx-auto" />
                        )
                      ) : (
                        <span className="text-orange-600 font-semibold">{feature.direct}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Bottom Note */}
        <div className="mt-8 sm:mt-12 text-center px-4">
          <p className="text-sm sm:text-base text-gray-600 italic">
            Ambas opciones incluyen estructura, claridad y apoyo profesional. La diferencia está en el nivel de personalización y contacto directo.
          </p>
        </div>
      </div>
    </section>
  );
};

export default ComparisonTable;