import React from 'react';
import { Card, CardContent } from './ui/card';
import { Quote } from 'lucide-react';

const TestimonialsSection = () => {
  const testimonials = [
    {
      text: 'Por fin entiendo lo que hago y no dependo de la motivación.',
      author: 'María L.',
      role: 'Cliente desde hace 6 meses'
    },
    {
      text: 'He vuelto a disfrutar de entrenar sin obsesionarme con la comida.',
      author: 'Carlos R.',
      role: 'Cliente desde hace 4 meses'
    },
    {
      text: 'No es una dieta más, es un cambio de mentalidad que funciona.',
      author: 'Ana P.',
      role: 'Cliente desde hace 8 meses'
    }
  ];

  return (
    <section id="testimonials" className="py-24 bg-gradient-to-br from-blue-50 via-orange-50 to-white">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Testimonios reales
          </h2>
          <p className="text-xl text-gray-700 max-w-3xl mx-auto">
            Lo que dicen quienes ya están trabajando con el método.
          </p>
        </div>

        {/* Testimonials Grid */}
        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <Card key={index} className="border-none shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
              <CardContent className="p-8">
                <div className="flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 text-blue-500 mb-6">
                  <Quote className="h-6 w-6" />
                </div>
                <p className="text-lg text-gray-700 mb-6 leading-relaxed italic">
                  "{testimonial.text}"
                </p>
                <div className="border-t border-gray-200 pt-4">
                  <p className="font-semibold text-gray-900">{testimonial.author}</p>
                  <p className="text-sm text-gray-600 mt-1">{testimonial.role}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Visual Image */}
        <div className="mt-16 max-w-4xl mx-auto">
          <div className="relative rounded-3xl overflow-hidden shadow-2xl">
            <img
              src="https://images.pexels.com/photos/13636369/pexels-photo-13636369.jpeg"
              alt="Achievement and Success"
              className="w-full h-96 object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end">
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