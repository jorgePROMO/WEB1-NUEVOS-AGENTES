import React, { useState } from 'react';
import { Card } from './ui/card';
import { Quote } from 'lucide-react';

const TestimonialsSection = () => {
  const [activeTestimonial, setActiveTestimonial] = useState(null);

  const testimonials = [
    {
      id: 1,
      image: 'https://customer-assets.emergentagent.com/job_landing-details/artifacts/h4avh64l_1F77C5D3-14BD-4AE7-B175-B5E0833B9ACB.JPG',
      text: 'Al principio pensaba que necesitaba más motivación. Pero Jorge me enseñó que lo que me faltaba era un sistema claro. Ahora entreno sin excusas y los resultados hablan por sí solos.'
    },
    {
      id: 2,
      image: 'https://customer-assets.emergentagent.com/job_landing-details/artifacts/ho9gdudv_2ED9F02D-4760-49A8-93E0-8473E33B83E8.JPG',
      text: 'Llevaba años probando dietas y entrenamientos que nunca duraban. Con Jorge entendí que no se trata de ser perfecto, sino de ser constante. Esto ha cambiado mi vida completamente.'
    },
    {
      id: 3,
      image: 'https://customer-assets.emergentagent.com/job_landing-details/artifacts/qgquk8hs_9F9D9B96-4095-49C5-9777-C2C87251686C.JPG',
      text: 'No solo perdí peso, gané claridad mental. Jorge no te da un plan copiado, te construye un sistema que encaja con tu vida real. Por fin entiendo lo que hago y por qué lo hago.'
    },
    {
      id: 4,
      image: 'https://customer-assets.emergentagent.com/job_landing-details/artifacts/ijek8ayw_BA618A58-EEE2-423E-AC89-E6A650F785A8.JPG',
      text: 'Trabajo con profesionales que lo han intentado todo y siempre regresan a cero. Jorge me demostró que el problema no era yo, era el método. Ahora tengo resultados sostenibles y una mentalidad ganadora.'
    },
    {
      id: 5,
      image: 'https://customer-assets.emergentagent.com/job_landing-details/artifacts/vrh0y8xz_F037CF61-996D-4497-BE22-570B3DAB30FA.JPG',
      text: 'Pensé que entrenar era sufrir. Con Jorge descubrí que entrenar es construir. Me ayudó a entender mi cuerpo, mi nutrición y sobre todo, mi mente. Este es el mejor cambio que he hecho.'
    }
  ];

  return (
    <section id="testimonials" className="py-24 bg-gradient-to-br from-blue-50 via-orange-50 to-white">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 text-blue-500 mb-6">
            <Quote className="h-8 w-8" />
          </div>
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Testimonios reales
          </h2>
          <p className="text-xl text-gray-700 max-w-3xl mx-auto">
            Lo que dicen quienes ya están trabajando con el método.
          </p>
          <p className="text-gray-600 mt-4 italic">
            Pasa el cursor sobre las fotos para leer los testimonios
          </p>
        </div>

        {/* Testimonials Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {testimonials.map((testimonial) => (
            <Card 
              key={testimonial.id} 
              className="group relative overflow-hidden border-none shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 cursor-pointer"
              onMouseEnter={() => setActiveTestimonial(testimonial.id)}
              onMouseLeave={() => setActiveTestimonial(null)}
              onClick={() => setActiveTestimonial(activeTestimonial === testimonial.id ? null : testimonial.id)}
            >
              <div className="relative aspect-square">
                {/* Image */}
                <img
                  src={testimonial.image}
                  alt={`Cliente satisfecho ${testimonial.id}`}
                  className="w-full h-full object-cover"
                />
                
                {/* Overlay with Testimonial */}
                <div 
                  className={`absolute inset-0 bg-gradient-to-t from-blue-600/95 via-blue-500/90 to-transparent flex items-end p-6 transition-opacity duration-300 ${
                    activeTestimonial === testimonial.id ? 'opacity-100' : 'opacity-0'
                  }`}
                >
                  <div className="transform transition-transform duration-300">
                    <Quote className="h-8 w-8 text-white/80 mb-3" />
                    <p className="text-white text-base leading-relaxed italic">
                      "{testimonial.text}"
                    </p>
                  </div>
                </div>

                {/* Hover Indicator */}
                <div 
                  className={`absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-full p-2 transition-opacity duration-300 ${
                    activeTestimonial === testimonial.id ? 'opacity-0' : 'opacity-100'
                  }`}
                >
                  <Quote className="h-5 w-5 text-blue-500" />
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Visual Image */}
        <div className="mt-16 max-w-2xl mx-auto">
          <div className="relative rounded-3xl overflow-hidden shadow-2xl">
            <div className="aspect-[3/4]">
              <img
                src="https://customer-assets.emergentagent.com/job_landing-details/artifacts/tw2x0ku0_WhatsApp%20Image%202025-10-25%20at%2021.18.51.jpeg"
                alt="Jorge Calcerrada Training"
                className="w-full h-full object-cover object-center"
              />
            </div>
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent flex items-end">
              <div className="p-8">
                <p className="text-white text-2xl font-bold">
                  La transformación real se basa en claridad, no en motivación.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;