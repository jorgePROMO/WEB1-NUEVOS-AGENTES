import React from 'react';
import { Card } from './ui/card';
import { TrendingUp } from 'lucide-react';

const TransformationsSection = () => {
  const transformations = [
    {
      id: 1,
      image: 'https://customer-assets.emergentagent.com/job_landing-details/artifacts/y1cg9c88_0AB507EA-06F5-4E8B-B4F1-9871EA2D9217.jpg',
      alt: 'Transformación cliente 1'
    },
    {
      id: 2,
      image: 'https://customer-assets.emergentagent.com/job_landing-details/artifacts/9bl17xn8_07f707b9-a1e0-4df1-abd4-09e2a86a6087.JPG',
      alt: 'Transformación cliente 2'
    },
    {
      id: 3,
      image: 'https://customer-assets.emergentagent.com/job_landing-details/artifacts/rbqmnztm_057534b3-7a4a-4574-aa9e-7264987c2614%20%281%29.jpg',
      alt: 'Transformación cliente 3'
    },
    {
      id: 4,
      image: 'https://customer-assets.emergentagent.com/job_landing-details/artifacts/woi2y0m3_68074EE0-23B4-404D-B8BA-D77729B31FAA.JPG',
      alt: 'Transformación cliente 4'
    },
    {
      id: 5,
      image: 'https://customer-assets.emergentagent.com/job_landing-details/artifacts/o56c6ttu_598884A3-F22A-408E-A7F5-4F4C7DA5335D%20%281%29.jpg',
      alt: 'Transformación cliente 5'
    },
    {
      id: 6,
      image: 'https://customer-assets.emergentagent.com/job_landing-details/artifacts/w2zzop6v_BA331569-0E2D-4931-9D33-BB55EF0E8C42%20%281%29.JPG',
      alt: 'Transformación cliente 6'
    },
    {
      id: 7,
      image: 'https://customer-assets.emergentagent.com/job_landing-details/artifacts/mdka6jdo_CA74D0C8-26FA-4DD5-8DA7-576AA966860C.jpg',
      alt: 'Transformación cliente 7'
    },
    {
      id: 8,
      image: 'https://customer-assets.emergentagent.com/job_landing-details/artifacts/mws7xh2i_CA946621-526C-418C-9CC6-70BCB536A868.JPG',
      alt: 'Transformación cliente 8'
    },
    {
      id: 9,
      image: 'https://customer-assets.emergentagent.com/job_landing-details/artifacts/u16uj9zf_cc82f864-6490-4122-8f5d-847caca41f64.JPG',
      alt: 'Transformación cliente 9'
    }
  ];

  return (
    <section id="transformations" className="py-24 bg-white">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-blue-400 to-orange-400 text-white mb-6">
            <TrendingUp className="h-8 w-8" />
          </div>
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Resultados reales
          </h2>
          <p className="text-xl text-gray-700 max-w-3xl mx-auto leading-relaxed">
            Estas son algunas de las transformaciones que mis clientes han logrado aplicando el método con constancia y compromiso.
          </p>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto mt-4">
            No promesas mágicas. Solo trabajo real, consistencia y resultados sostenibles.
          </p>
        </div>

        {/* Transformations Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {transformations.map((transformation) => (
            <Card key={transformation.id} className="overflow-hidden border-none shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
              <div className="relative aspect-square">
                <img
                  src={transformation.image}
                  alt={transformation.alt}
                  className="w-full h-full object-cover"
                />
                {/* Overlay on hover */}
                <div className="absolute inset-0 bg-gradient-to-t from-blue-500/90 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300 flex items-end">
                  <div className="p-6">
                    <p className="text-white font-semibold text-lg">
                      Transformación real
                    </p>
                    <p className="text-white/90 text-sm mt-1">
                      Constancia + método = resultados
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Bottom Message */}
        <div className="mt-16 max-w-4xl mx-auto">
          <div className="bg-gradient-to-r from-blue-50 to-orange-50 rounded-2xl p-8 text-center">
            <p className="text-xl font-bold text-gray-900 mb-3">
              Cada transformación es única, pero todas tienen algo en común:
            </p>
            <p className="text-lg text-gray-700">
              Un compromiso real con el proceso, claridad en el método y acompañamiento profesional.
            </p>
            <p className="text-2xl font-bold text-blue-500 mt-6">
              Tu turno puede ser el siguiente.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TransformationsSection;
