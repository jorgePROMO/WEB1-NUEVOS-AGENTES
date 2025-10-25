import React, { useState, useEffect, useRef } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Send, User } from 'lucide-react';
import { mockMessages } from '../mock';

const ChatBox = ({ userId, isAdmin = false }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Load messages for this user
    const userMessages = mockMessages.filter(m => m.userId === userId);
    setMessages(userMessages);
  }, [userId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = () => {
    if (!newMessage.trim()) return;

    const message = {
      id: Date.now().toString(),
      userId: userId,
      senderId: isAdmin ? 'admin1' : userId,
      senderName: isAdmin ? 'Jorge Calcerrada' : 'Tú',
      message: newMessage,
      timestamp: new Date().toISOString(),
      isAdmin: isAdmin
    };

    setMessages([...messages, message]);
    setNewMessage('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ maxHeight: '500px' }}>
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-12">
            <p>No hay mensajes aún</p>
            <p className="text-sm mt-2">Inicia la conversación</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start gap-3 ${
                msg.isAdmin !== isAdmin ? 'flex-row' : 'flex-row-reverse'
              }`}
            >
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  msg.isAdmin ? 'bg-blue-500' : 'bg-gray-300'
                }`}
              >
                <User className="h-5 w-5 text-white" />
              </div>
              <div
                className={`flex-1 max-w-xs lg:max-w-md ${
                  msg.isAdmin !== isAdmin ? '' : 'flex flex-col items-end'
                }`}
              >
                <div
                  className={`rounded-2xl px-4 py-2 ${
                    msg.isAdmin !== isAdmin
                      ? 'bg-gray-100 text-gray-900'
                      : 'bg-blue-500 text-white'
                  }`}
                >
                  <p className="text-xs font-semibold mb-1 opacity-75">{msg.senderName}</p>
                  <p className="text-sm">{msg.message}</p>
                </div>
                <p className="text-xs text-gray-500 mt-1 px-2">
                  {new Date(msg.timestamp).toLocaleTimeString('es-ES', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <div className="flex gap-2">
          <Input
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Escribe tu mensaje..."
            className="flex-1"
          />
          <Button
            onClick={handleSend}
            className="bg-blue-500 hover:bg-blue-600 text-white"
            disabled={!newMessage.trim()}
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatBox;