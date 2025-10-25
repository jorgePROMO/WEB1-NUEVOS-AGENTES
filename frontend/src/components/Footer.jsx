import React from 'react';
import { Facebook, Instagram, Mail, Phone } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-gray-300 py-16">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        <div className="grid md:grid-cols-3 gap-12">
          {/* Brand */}
          <div>
            <h3 className="text-2xl font-bold text-white mb-4">Jorge Calcerrada</h3>
            <p className="text-gray-400 leading-relaxed">
              Método profesional de entrenamiento, nutrición y mentalidad. Construyendo sistemas que transforman personas.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Enlaces rápidos</h4>
            <ul className="space-y-3">
              <li>
                <a href="#about" className="hover:text-blue-400 transition-colors duration-300">
                  Sobre mí
                </a>
              </li>
              <li>
                <a href="#method" className="hover:text-blue-400 transition-colors duration-300">
                  Método
                </a>
              </li>
              <li>
                <a href="#services" className="hover:text-blue-400 transition-colors duration-300">
                  Servicios
                </a>
              </li>
              <li>
                <a href="#testimonials" className="hover:text-blue-400 transition-colors duration-300">
                  Testimonios
                </a>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Contacto</h4>
            <ul className="space-y-3">
              <li className="flex items-center gap-3">
                <Mail className="h-5 w-5 text-blue-400" />
                <span>info@jorgecalcerrada.com</span>
              </li>
              <li className="flex items-center gap-3">
                <Phone className="h-5 w-5 text-orange-400" />
                <span>+34 XXX XXX XXX</span>
              </li>
            </ul>
            {/* Social Media */}
            <div className="flex gap-4 mt-6">
              <a
                href="#"
                className="w-10 h-10 rounded-full bg-gray-800 hover:bg-blue-500 flex items-center justify-center transition-colors duration-300"
                aria-label="Facebook"
              >
                <Facebook className="h-5 w-5" />
              </a>
              <a
                href="#"
                className="w-10 h-10 rounded-full bg-gray-800 hover:bg-orange-500 flex items-center justify-center transition-colors duration-300"
                aria-label="Instagram"
              >
                <Instagram className="h-5 w-5" />
              </a>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 mt-12 pt-8 text-center">
          <p className="text-gray-500">
            &copy; {new Date().getFullYear()} Jorge Calcerrada. Todos los derechos reservados.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;