import React, { lazy, Suspense } from 'react';
import Header from '../components/Header';
import HeroSection from '../components/HeroSection';

// Lazy load components que no son críticos para la primera vista
const AboutSection = lazy(() => import('../components/AboutSection'));
const MethodSection = lazy(() => import('../components/MethodSection'));
const ServicesSection = lazy(() => import('../components/ServicesSection'));
const ComparisonTable = lazy(() => import('../components/ComparisonTable'));
const TransformationsSection = lazy(() => import('../components/TransformationsSection'));
const TestimonialsSection = lazy(() => import('../components/TestimonialsSection'));
const EDN360Section = lazy(() => import('../components/EDN360Section'));
const FinalCTA = lazy(() => import('../components/FinalCTA'));
const Footer = lazy(() => import('../components/Footer'));

// Fallback component simple
const SectionLoader = () => (
  <div className="w-full h-32 flex items-center justify-center">
    <div className="animate-pulse bg-gray-200 rounded w-full h-full"></div>
  </div>
);

const LandingPage = () => {
  return (
    <div>
      <Header />
      <HeroSection />
      <Suspense fallback={<SectionLoader />}>
        <AboutSection />
      </Suspense>
      <Suspense fallback={<SectionLoader />}>
        <MethodSection />
      </Suspense>
      <Suspense fallback={<SectionLoader />}>
        <ServicesSection />
      </Suspense>
      <Suspense fallback={<SectionLoader />}>
        <ComparisonTable />
      </Suspense>
      <Suspense fallback={<SectionLoader />}>
        <TransformationsSection />
      </Suspense>
      <Suspense fallback={<SectionLoader />}>
        <TestimonialsSection />
      </Suspense>
      <Suspense fallback={<SectionLoader />}>
        <FinalCTA />
      </Suspense>
      <Suspense fallback={<SectionLoader />}>
        <Footer />
      </Suspense>
    </div>
  );
};

export default LandingPage;
