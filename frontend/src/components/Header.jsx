import React from 'react';
import { Button } from './ui/button';
import { Menu, X } from 'lucide-react';

const Header = () => {
  const [isScrolled, setIsScrolled] = React.useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

  React.useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
      setIsMobileMenuOpen(false);
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md shadow-lg transition-all duration-300">
      {/* Safe area padding for mobile notch/status bar */}
      <div className="h-safe-top bg-white/95"></div>
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        <div className="flex items-center justify-between h-20 md:h-20 pt-safe">
          {/* Logo */}
          <div className="flex items-center">
            <a href="#" className="text-2xl font-bold">
              <span className="text-gray-900 transition-colors duration-300">
                Jorge Calcerrada
              </span>
            </a>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-8">
            <button
              onClick={() => scrollToSection('about')}
              className="text-gray-700 font-medium transition-colors duration-300 hover:text-blue-500"
            >
              Sobre mí
            </button>
            <button
              onClick={() => scrollToSection('method')}
              className="text-gray-700 font-medium transition-colors duration-300 hover:text-blue-500"
            >
              Método
            </button>
            <button
              onClick={() => scrollToSection('services')}
              className="text-gray-700 font-medium transition-colors duration-300 hover:text-blue-500"
            >
              Servicios
            </button>
            <button
              onClick={() => scrollToSection('testimonials')}
              className="text-gray-700 font-medium transition-colors duration-300 hover:text-blue-500"
            >
              Testimonios
            </button>
          </nav>

          {/* Desktop Auth Buttons */}
          <div className="hidden md:flex items-center gap-3">
            <Button
              variant="outline"
              className="border-2 border-blue-500 text-blue-500 hover:bg-blue-50 transition-all duration-300"
              onClick={() => window.location.href = '/login'}
            >
              Iniciar sesión
            </Button>
            <Button
              className="bg-gradient-to-r from-blue-500 to-orange-500 hover:from-blue-600 hover:to-orange-600 text-white px-6 py-2 rounded-full shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
              onClick={() => window.location.href = '/login'}
            >
              Administrador
            </Button>
          </div>

          {/* Mobile menu button - con más padding */}
          <button
            className="md:hidden p-3 touch-manipulation"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Abrir menú"
          >
            {isMobileMenuOpen ? (
              <X className="h-7 w-7 text-gray-900" />
            ) : (
              <Menu className="h-7 w-7 text-gray-900" />
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden py-4 border-t">
            <nav className="flex flex-col gap-4">
              <button
                onClick={() => scrollToSection('about')}
                className="text-gray-700 font-medium text-left hover:text-blue-500 py-2"
              >
                Sobre mí
              </button>
              <button
                onClick={() => scrollToSection('method')}
                className="text-gray-700 font-medium text-left hover:text-blue-500 py-2"
              >
                Método
              </button>
              <button
                onClick={() => scrollToSection('services')}
                className="text-gray-700 font-medium text-left hover:text-blue-500 py-2"
              >
                Servicios
              </button>
              <button
                onClick={() => scrollToSection('testimonials')}
                className="text-gray-700 font-medium text-left hover:text-blue-500 py-2"
              >
                Testimonios
              </button>
              
              <div className="flex flex-col gap-3 mt-4 pt-4 border-t">
                <Button
                  variant="outline"
                  className="w-full border-2 border-blue-500 text-blue-500 hover:bg-blue-50"
                  onClick={() => window.location.href = '/login'}
                >
                  Iniciar sesión
                </Button>
                <Button
                  className="w-full bg-gradient-to-r from-blue-500 to-orange-500 hover:from-blue-600 hover:to-orange-600 text-white"
                  onClick={() => window.location.href = '/login'}
                >
                  Administrador
                </Button>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;