import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { 
  MessageSquare, 
  Bell, 
  Mail,
  Plus,
  Copy,
  Trash2,
  X
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const TemplatesManager = ({ token, onSelectTemplate }) => {
  const [templates, setTemplates] = useState([]);
  const [selectedType, setSelectedType] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTemplate, setNewTemplate] = useState({
    type: 'whatsapp',
    name: '',
    subject: '',
    content: '',
    category: 'general'
  });

  useEffect(() => {
    loadTemplates();
  }, [selectedType]);

  const loadTemplates = async () => {
    try {
      const params = selectedType !== 'all' ? `?type=${selectedType}` : '';
      const response = await axios.get(`${API}/admin/templates${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTemplates(response.data.templates || []);
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const deleteTemplate = async (templateId) => {
    if (!window.confirm('¿Eliminar este template?')) return;
    
    try {
      await axios.delete(`${API}/admin/templates/${templateId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      loadTemplates();
    } catch (error) {
      alert('Error al eliminar template');
    }
  };

  const copyToClipboard = (content) => {
    navigator.clipboard.writeText(content);
    alert('Copiado al portapapeles');
  };

  const getTypeIcon = (type) => {
    switch(type) {
      case 'whatsapp': return <MessageSquare className="h-4 w-4" />;
      case 'alert': return <Bell className="h-4 w-4" />;
      case 'email': return <Mail className="h-4 w-4" />;
      default: return null;
    }
  };

  const getTypeColor = (type) => {
    switch(type) {
      case 'whatsapp': return 'bg-green-100 text-green-800';
      case 'alert': return 'bg-purple-100 text-purple-800';
      case 'email': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Templates de Mensajes</h2>
          <p className="text-gray-600">Mensajes predefinidos para comunicación rápida</p>
        </div>
        <Button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Template
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        <Button
          variant={selectedType === 'all' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setSelectedType('all')}
        >
          Todos
        </Button>
        <Button
          variant={selectedType === 'whatsapp' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setSelectedType('whatsapp')}
          className={selectedType === 'whatsapp' ? 'bg-green-600' : ''}
        >
          <MessageSquare className="h-4 w-4 mr-2" />
          WhatsApp
        </Button>
        <Button
          variant={selectedType === 'alert' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setSelectedType('alert')}
          className={selectedType === 'alert' ? 'bg-purple-600' : ''}
        >
          <Bell className="h-4 w-4 mr-2" />
          Alertas
        </Button>
      </div>

      {/* Templates Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.map(template => (
          <Card key={template.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg">{template.name}</CardTitle>
                  <Badge className={`mt-2 ${getTypeColor(template.type)}`}>
                    <span className="flex items-center gap-1">
                      {getTypeIcon(template.type)}
                      {template.type}
                    </span>
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {template.subject && (
                  <div>
                    <Label className="text-xs text-gray-600">Asunto</Label>
                    <p className="text-sm font-medium">{template.subject}</p>
                  </div>
                )}
                <div>
                  <Label className="text-xs text-gray-600">Contenido</Label>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-2 rounded">
                    {template.content}
                  </p>
                </div>
                {template.variables && template.variables.length > 0 && (
                  <div>
                    <Label className="text-xs text-gray-600">Variables</Label>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {template.variables.map(v => (
                        <Badge key={v} variant="outline" className="text-xs">
                          {`{${v}}`}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                <div className="flex gap-2 pt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1"
                    onClick={() => copyToClipboard(template.content)}
                  >
                    <Copy className="h-3 w-3 mr-1" />
                    Copiar
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="border-red-200 text-red-600"
                    onClick={() => deleteTemplate(template.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {templates.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No hay templates para mostrar
        </div>
      )}
    </div>
  );
};

export default TemplatesManager;
