import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import DiagnosisQuestionnaire from './DiagnosisQuestionnaire';

const QuestionnaireModal = ({ isOpen, onClose }) => {
  // Bloquear scroll del body cuando el modal está abierto
  useEffect(() => {
    if (isOpen) {
      // Guardar la posición actual del scroll
      const scrollY = window.scrollY;
      document.body.style.position = 'fixed';
      document.body.style.top = `-${scrollY}px`;
      document.body.style.width = '100%';
      document.body.style.overflow = 'hidden';
      
      return () => {
        // Restaurar el scroll al cerrar
        document.body.style.position = '';
        document.body.style.top = '';
        document.body.style.width = '';
        document.body.style.overflow = '';
        window.scrollTo(0, scrollY);
      };
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/70 backdrop-blur-sm p-0 md:p-4"
      onClick={(e) => {
        // Cerrar si hace clic en el fondo (solo en desktop)
        if (e.target === e.currentTarget && window.innerWidth > 768) {
          onClose();
        }
      }}
    >
      <div className="relative bg-white rounded-none md:rounded-2xl shadow-2xl w-full h-full md:h-[90vh] md:max-w-4xl flex flex-col overflow-hidden z-[10000]">
        {/* Header - Fixed */}
        <div className="flex-shrink-0 flex items-center justify-between p-4 border-b bg-gradient-to-r from-blue-500 to-orange-500">
          <h2 className="text-lg md:text-xl font-bold text-white">Diagnóstico Inicial Gratuito</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-white/20 transition-colors"
            aria-label="Cerrar"
          >
            <X className="h-5 w-5 md:h-6 md:w-6 text-white" />
          </button>
        </div>

        {/* Questionnaire Content - Scrollable */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden">
          <DiagnosisQuestionnaire onClose={onClose} />
        </div>
      </div>
    </div>
  );
};

export default QuestionnaireModal;
