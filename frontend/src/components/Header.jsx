import React from 'react';
import { Button } from './ui/button';

const Header = () => {
  const [isScrolled, setIsScrolled] = React.useState(false);

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
    }
  };

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-white/95 backdrop-blur-md shadow-lg'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <div className="flex items-center">
            <a href="#" className="text-2xl font-bold">
              <span className={`transition-colors duration-300 ${
                isScrolled ? 'text-gray-900' : 'text-white'
              }`}>
                Jorge Calcerrada
              </span>
            </a>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-8">
            <button
              onClick={() => scrollToSection('about')}
              className={`font-medium transition-colors duration-300 hover:text-blue-500 ${
                isScrolled ? 'text-gray-700' : 'text-white'
              }`}
            >
              Sobre mí
            </button>
            <button
              onClick={() => scrollToSection('method')}
              className={`font-medium transition-colors duration-300 hover:text-blue-500 ${
                isScrolled ? 'text-gray-700' : 'text-white'
              }`}
            >
              Método
            </button>
            <button
              onClick={() => scrollToSection('services')}
              className={`font-medium transition-colors duration-300 hover:text-blue-500 ${
                isScrolled ? 'text-gray-700' : 'text-white'
              }`}
            >
              Servicios
            </button>
            <button
              onClick={() => scrollToSection('testimonials')}
              className={`font-medium transition-colors duration-300 hover:text-blue-500 ${
                isScrolled ? 'text-gray-700' : 'text-white'
              }`}
            >
              Testimonios
            </button>
          </nav>

          {/* Auth Buttons */}
          <div className="hidden lg:flex items-center gap-3">
            <Button
              variant="outline"
              className={`border-2 transition-all duration-300 ${
                isScrolled 
                  ? 'border-blue-500 text-blue-500 hover:bg-blue-50' 
                  : 'border-white text-white hover:bg-white/20'
              }`}
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
        </div>
      </div>
    </header>
  );
};

export default Header;