import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X, Send, Loader2, CheckCircle } from 'lucide-react';
import axios from 'axios';

const NutritionPlanChatDialog = ({ isOpen, onClose, planId, planContent, onPlanUpdated, token }) => {
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
          content: '¡Hola! Soy tu asistente de nutrición. Puedo ayudarte a modificar este plan. Por ejemplo:\n\n• "Cambia el pollo por pavo en la comida 2"\n• "Añade más proteína en el desayuno"\n• "Reduce las calorías del almuerzo"\n• "Sustituye el arroz por batata"\n• "Añade opciones vegetarianas"\n\n¿Qué te gustaría cambiar?',
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
      // Using axios instead of fetch to avoid React 19 Response.clone() bug
      const response = await axios.post(
        `${BACKEND_URL}/api/nutrition-plan/chat`,
        {
          plan_id: planId,
          user_message: userMessage
        },
        {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        }
      );

      const data = response.data;
      
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
      const errorMessage = error.response?.data?.detail || error.message || 'Error desconocido';
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
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-green-600 to-emerald-700 text-white rounded-t-lg">
          <div>
            <h3 className="text-lg font-bold">🥗 Chat con IA - Modificar Plan de Nutrición</h3>
            <p className="text-sm text-green-100">Pide cambios y la IA actualizará el plan</p>
          </div>
          <button 
            onClick={onClose}
            className="hover:bg-white hover:bg-opacity-20 rounded-lg p-2 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.role === 'user'
                    ? 'bg-green-600 text-white'
                    : message.isError
                    ? 'bg-red-50 text-red-900 border border-red-200'
                    : 'bg-white text-gray-900 border border-gray-200'
                }`}
              >
                <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                {message.plan_updated && (
                  <div className="mt-2 flex items-center gap-2 text-sm text-green-600">
                    <CheckCircle className="h-4 w-4" />
                    <span className="font-semibold">Plan actualizado correctamente</span>
                  </div>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-900 border border-gray-200 rounded-lg p-3">
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">Pensando...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t bg-white rounded-b-lg">
          <div className="flex gap-2">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Escribe qué quieres cambiar del plan..."
              className="flex-1 resize-none border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              rows="2"
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className={`px-6 rounded-lg font-medium transition-colors ${
                isLoading || !inputMessage.trim()
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-green-600 text-white hover:bg-green-700'
              }`}
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Send className="h-5 w-5" />
              )}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Pulsa Enter para enviar, Shift+Enter para nueva línea
          </p>
        </div>
      </div>
    </div>,
    document.body
  );
};

export default NutritionPlanChatDialog;
