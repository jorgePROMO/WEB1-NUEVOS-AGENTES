import React from 'react';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import AboutSection from './components/AboutSection';
import MethodSection from './components/MethodSection';
import ServicesSection from './components/ServicesSection';
import ComparisonTable from './components/ComparisonTable';
import TestimonialsSection from './components/TestimonialsSection';
import FinalCTA from './components/FinalCTA';
import Footer from './components/Footer';
import './App.css';

function App() {
  return (
    <div className="App">
      <Header />
      <HeroSection />
      <AboutSection />
      <MethodSection />
      <ServicesSection />
      <ComparisonTable />
      <TestimonialsSection />
      <FinalCTA />
      <Footer />
    </div>
  );
}

export default App;