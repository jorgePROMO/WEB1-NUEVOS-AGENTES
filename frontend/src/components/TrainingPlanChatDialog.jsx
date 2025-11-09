import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X, Send, Loader2, CheckCircle } from 'lucide-react';

const TrainingPlanChatDialog = ({ isOpen, onClose, planId, planContent, onPlanUpdated }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add initial system message when dialog opens
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          role: 'assistant',
          content: '¡Hola! Soy tu asistente de entrenamiento. Puedo ayudarte a modificar este plan. Por ejemplo:\n\n• "Cambia el press banca por press inclinado"\n• "Añade 2 ejercicios más de espalda el lunes"\n• "Reduce el volumen del viernes"\n• "Quita los ejercicios de hombros"\n\n¿Qué te gustaría cambiar?',
          timestamp: new Date()
        }
      ]);
    }
  }, [isOpen]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    
    // Add user message
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    }]);

    setIsLoading(true);

    try {
      const response = await fetch(`${BACKEND_URL}/api/training-plan/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          plan_id: planId,
          user_message: userMessage
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Error desconocido' }));
        console.error('Backend error:', errorData);
        throw new Error(errorData.detail || 'Error al procesar mensaje');
      }

      const data = await response.json();
      
      // Add assistant message
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.assistant_message,
        timestamp: new Date(),
        plan_updated: !!data.updated_plan
      }]);

      // If plan was updated, notify parent
      if (data.updated_plan) {
        onPlanUpdated(data.updated_plan);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = error.message || 'Error desconocido';
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `❌ Error: ${errorMessage}\n\nPor favor, intenta de nuevo o contacta con soporte si el problema persiste.`,
        timestamp: new Date(),
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) return null;

  return createPortal(
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999] p-4"
      onClick={(e) => {
        // Close if clicking on backdrop
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-3xl h-[600px] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-t-lg">
          <div>
            <h3 className="text-lg font-bold">💬 Chat con IA - Modificar Plan</h3>
            <p className="text-sm text-blue-100">Pide cambios y la IA actualizará el plan</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-blue-500 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : message.isError
                    ? 'bg-red-100 text-red-800 border border-red-300'
                    : 'bg-white border border-gray-200 text-gray-800'
                }`}
              >
                <div className="whitespace-pre-wrap break-words">{message.content}</div>
                {message.plan_updated && (
                  <div className="mt-2 pt-2 border-t border-blue-200 flex items-center text-sm text-green-600 font-medium">
                    <CheckCircle className="w-4 h-4 mr-1" />
                    Plan actualizado
                  </div>
                )}
                <div className="text-xs mt-1 opacity-60">
                  {message.timestamp.toLocaleTimeString('es-ES', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-lg p-3 flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                <span className="text-sm text-gray-600">La IA está procesando...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t bg-white rounded-b-lg">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Escribe tu petición... (Ej: 'Añade 2 ejercicios más de pecho')"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className={`px-6 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2 ${
                isLoading || !inputMessage.trim()
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Enviando...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Enviar</span>
                </>
              )}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            💡 Tip: Sé específico sobre qué cambiar. La IA actualizará el plan automáticamente.
          </p>
        </div>
      </div>
    </div>,
    document.body
  );
};

export default TrainingPlanChatDialog;
