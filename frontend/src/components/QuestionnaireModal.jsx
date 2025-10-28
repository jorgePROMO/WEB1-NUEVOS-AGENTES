import React, { useState } from 'react';
import { X } from 'lucide-react';

const QuestionnaireModal = ({ isOpen, onClose, iframeUrl }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-5xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-blue-500 to-orange-500">
          <h2 className="text-xl font-bold text-white">Cuestionario de Diagnóstico</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-white/20 transition-colors"
          >
            <X className="h-6 w-6 text-white" />
          </button>
        </div>

        {/* Iframe Content */}
        <div className="flex-1 overflow-hidden">
          {iframeUrl ? (
            <iframe
              src={iframeUrl}
              className="w-full h-full border-0"
              title="Cuestionario de Diagnóstico"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-500">Cargando cuestionario...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuestionnaireModal;
