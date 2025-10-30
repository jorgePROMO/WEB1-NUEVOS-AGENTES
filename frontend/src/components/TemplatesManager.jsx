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
  X,
  Edit,
  Tag
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const TemplatesManager = ({ token, onSelectTemplate }) => {
  const [templates, setTemplates] = useState([]);
  const [allTags, setAllTags] = useState([]);
  const [selectedType, setSelectedType] = useState('all');
  const [selectedTagFilter, setSelectedTagFilter] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showTagManager, setShowTagManager] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [newTemplate, setNewTemplate] = useState({
    type: 'whatsapp',
    name: '',
    subject: '',
    content: '',
    tags: []
  });
  const [tagInput, setTagInput] = useState('');
  const [newGlobalTag, setNewGlobalTag] = useState('');

  useEffect(() => {
    loadTemplates();
    loadAllTags();
  }, [selectedType]);

  const loadAllTags = async () => {
    try {
      const response = await axios.get(`${API}/admin/templates/tags/all`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setAllTags(response.data.tags || []);
    } catch (error) {
      console.error('Error loading tags:', error);
    }
  };

  const loadTemplates = async () => {
    try {
      const params = selectedType !== 'all' ? `?type=${selectedType}` : '';
      const response = await axios.get(`${API}/admin/templates${params}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
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
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      loadTemplates();
    } catch (error) {
      alert('Error al eliminar template');
    }
  };

  const createTemplate = async () => {
    if (!newTemplate.name || !newTemplate.content) {
      alert('Por favor completa nombre y contenido');
      return;
    }

    try {
      await axios.post(`${API}/admin/templates`, newTemplate, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      setShowCreateModal(false);
      setNewTemplate({
        type: 'whatsapp',
        name: '',
        subject: '',
        content: '',
        tags: []
      });
      setTagInput('');
      loadTemplates();
      alert('Template creado correctamente');
    } catch (error) {
      alert('Error al crear template');
    }
  };

  const openEditModal = (template) => {
    setEditingTemplate(template);
    setNewTemplate({
      type: template.type,
      name: template.name,
      subject: template.subject || '',
      content: template.content,
      category: template.category,
      tags: template.tags || []
    });
    setShowEditModal(true);
  };

  const updateTemplate = async () => {
    if (!newTemplate.name || !newTemplate.content) {
      alert('Por favor completa nombre y contenido');
      return;
    }

    try {
      await axios.patch(`${API}/admin/templates/${editingTemplate.id}`, {
        name: newTemplate.name,
        subject: newTemplate.subject,
        content: newTemplate.content,
        category: newTemplate.category,
        tags: newTemplate.tags
      }, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      setShowEditModal(false);
      setEditingTemplate(null);
      setNewTemplate({
        type: 'whatsapp',
        name: '',
        subject: '',
        content: '',
        tags: []
      });
      setTagInput('');
      loadTemplates();
      alert('Template actualizado correctamente');
    } catch (error) {
      alert('Error al actualizar template');
    }
  };

  const addTag = () => {
    if (tagInput.trim() && !newTemplate.tags.includes(tagInput.trim())) {
      setNewTemplate({
        ...newTemplate,
        tags: [...newTemplate.tags, tagInput.trim()]
      });
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove) => {
    setNewTemplate({
      ...newTemplate,
      tags: newTemplate.tags.filter(t => t !== tagToRemove)
    });
  };

  const createGlobalTag = async () => {
    if (!newGlobalTag.trim()) return;
    
    try {
      await axios.post(`${API}/admin/templates/tags`, { tag: newGlobalTag.trim() }, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      alert('✅ Tag creado correctamente');
      setNewGlobalTag('');
      loadAllTags();
    } catch (error) {
      alert('❌ ' + (error.response?.data?.detail || 'Error al crear tag'));
    }
  };

  const deleteGlobalTag = async (tagName) => {
    if (!window.confirm(`¿Eliminar el tag "${tagName}"?`)) return;
    
    try {
      await axios.delete(`${API}/admin/templates/tags/${encodeURIComponent(tagName)}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      alert('✅ Tag eliminado correctamente');
      loadAllTags();
    } catch (error) {
      alert('❌ ' + (error.response?.data?.detail || 'Error al eliminar tag'));
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
      <div className="flex gap-2 flex-wrap items-center">
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
        
        <div className="flex-1"></div>
        
        {/* Tag Filter Dropdown */}
        <div className="flex gap-2 items-center">
          <Tag className="h-4 w-4 text-gray-500" />
          <select
            value={selectedTagFilter}
            onChange={(e) => setSelectedTagFilter(e.target.value)}
            className="border rounded-md px-3 py-2 w-64"
          >
            <option value="">Todas las etiquetas</option>
            {allTags.map(tag => (
              <option key={tag} value={tag}>{tag}</option>
            ))}
          </select>
          <Button
            size="sm"
            variant="outline"
            onClick={() => setShowTagManager(true)}
            title="Gestionar etiquetas"
          >
            <Tag className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Templates Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates
          .filter(template => {
            // Filter by selected tag
            if (selectedTagFilter) {
              return template.tags && template.tags.includes(selectedTagFilter);
            }
            return true;
          })
          .map(template => (
          <Card key={template.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
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
                {template.tags && template.tags.length > 0 && (
                  <div>
                    <Label className="text-xs text-gray-600 flex items-center gap-1">
                      <Tag className="h-3 w-3" />
                      Etiquetas
                    </Label>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {template.tags.map(tag => (
                        <Badge key={tag} className="text-xs bg-blue-100 text-blue-700">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                <div className="flex gap-2 pt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1 bg-blue-50 hover:bg-blue-100 text-blue-700"
                    onClick={() => openEditModal(template)}
                  >
                    <Edit className="h-3 w-3 mr-1" />
                    Editar
                  </Button>
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

      {/* Create Template Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-4 flex items-center justify-between">
              <h3 className="text-xl font-bold">Crear Nuevo Template</h3>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setShowCreateModal(false)}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <Label>Tipo *</Label>
                <select
                  value={newTemplate.type}
                  onChange={(e) => setNewTemplate({...newTemplate, type: e.target.value})}
                  className="w-full border rounded-md px-3 py-2"
                >
                  <option value="whatsapp">WhatsApp</option>
                  <option value="alert">Alerta</option>
                  <option value="email">Email</option>
                </select>
              </div>

              <div>
                <Label>Nombre del Template *</Label>
                <Input
                  value={newTemplate.name}
                  onChange={(e) => setNewTemplate({...newTemplate, name: e.target.value})}
                  placeholder="Ej: Bienvenida Nuevo Cliente"
                />
              </div>

              {newTemplate.type !== 'whatsapp' && (
                <div>
                  <Label>Asunto</Label>
                  <Input
                    value={newTemplate.subject}
                    onChange={(e) => setNewTemplate({...newTemplate, subject: e.target.value})}
                    placeholder="Asunto del mensaje"
                  />
                </div>
              )}

              <div>
                <Label>Contenido del Mensaje *</Label>
                <Textarea
                  value={newTemplate.content}
                  onChange={(e) => setNewTemplate({...newTemplate, content: e.target.value})}
                  placeholder="Escribe tu mensaje aquí. Usa {nombre}, {fecha}, {hora} para variables"
                  rows={8}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Variables disponibles: {'{nombre}'}, {'{fecha}'}, {'{hora}'}
                </p>
              </div>

              <div>
                <Label className="flex items-center gap-2">
                  <Tag className="h-4 w-4" />
                  Etiquetas
                </Label>
                <div className="flex gap-2 mt-2">
                  <select
                    value={tagInput}
                    onChange={(e) => {
                      const selectedTag = e.target.value;
                      if (selectedTag && !newTemplate.tags.includes(selectedTag)) {
                        setNewTemplate({
                          ...newTemplate,
                          tags: [...newTemplate.tags, selectedTag]
                        });
                      }
                    }}
                    className="flex-1 border rounded-md px-3 py-2"
                  >
                    <option value="">Selecciona una etiqueta...</option>
                    {allTags
                      .filter(tag => !newTemplate.tags.includes(tag))
                      .map(tag => (
                        <option key={tag} value={tag}>{tag}</option>
                      ))}
                  </select>
                </div>
                {newTemplate.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {newTemplate.tags.map(tag => (
                      <Badge key={tag} className="bg-blue-100 text-blue-700 flex items-center gap-1">
                        {tag}
                        <X 
                          className="h-3 w-3 cursor-pointer hover:text-blue-900" 
                          onClick={() => removeTag(tag)}
                        />
                      </Badge>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  onClick={createTemplate}
                  disabled={!newTemplate.name || !newTemplate.content}
                  className="flex-1 bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Crear Template
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1"
                >
                  Cancelar
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Template Modal */}
      {showEditModal && editingTemplate && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-4 flex items-center justify-between">
              <h3 className="text-xl font-bold">Editar Template</h3>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => {
                  setShowEditModal(false);
                  setEditingTemplate(null);
                }}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <Label>Tipo *</Label>
                <select
                  value={newTemplate.type}
                  onChange={(e) => setNewTemplate({...newTemplate, type: e.target.value})}
                  className="w-full border rounded-md px-3 py-2"
                  disabled
                >
                  <option value="whatsapp">WhatsApp</option>
                  <option value="alert">Alerta</option>
                  <option value="email">Email</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">El tipo no se puede cambiar después de crear el template</p>
              </div>

              <div>
                <Label>Nombre del Template *</Label>
                <Input
                  value={newTemplate.name}
                  onChange={(e) => setNewTemplate({...newTemplate, name: e.target.value})}
                  placeholder="Ej: Bienvenida Nuevo Cliente"
                />
              </div>

              {newTemplate.type !== 'whatsapp' && (
                <div>
                  <Label>Asunto</Label>
                  <Input
                    value={newTemplate.subject}
                    onChange={(e) => setNewTemplate({...newTemplate, subject: e.target.value})}
                    placeholder="Asunto del mensaje"
                  />
                </div>
              )}

              <div>
                <Label>Contenido del Mensaje *</Label>
                <Textarea
                  value={newTemplate.content}
                  onChange={(e) => setNewTemplate({...newTemplate, content: e.target.value})}
                  placeholder="Escribe tu mensaje aquí. Usa {nombre}, {fecha}, {hora} para variables"
                  rows={8}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Variables disponibles: {'{nombre}'}, {'{fecha}'}, {'{hora}'}
                </p>
              </div>

              <div>
                <Label className="flex items-center gap-2">
                  <Tag className="h-4 w-4" />
                  Etiquetas
                </Label>
                <div className="flex gap-2 mt-2">
                  <select
                    value=""
                    onChange={(e) => {
                      const selectedTag = e.target.value;
                      if (selectedTag && !newTemplate.tags.includes(selectedTag)) {
                        setNewTemplate({
                          ...newTemplate,
                          tags: [...newTemplate.tags, selectedTag]
                        });
                      }
                    }}
                    className="flex-1 border rounded-md px-3 py-2"
                  >
                    <option value="">Selecciona una etiqueta...</option>
                    {allTags
                      .filter(tag => !newTemplate.tags.includes(tag))
                      .map(tag => (
                        <option key={tag} value={tag}>{tag}</option>
                      ))}
                  </select>
                </div>
                {newTemplate.tags && newTemplate.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {newTemplate.tags.map(tag => (
                      <Badge key={tag} className="bg-blue-100 text-blue-700 flex items-center gap-1">
                        {tag}
                        <X 
                          className="h-3 w-3 cursor-pointer hover:text-blue-900" 
                          onClick={() => removeTag(tag)}
                        />
                      </Badge>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  onClick={updateTemplate}
                  disabled={!newTemplate.name || !newTemplate.content}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                >
                  <Edit className="h-4 w-4 mr-2" />
                  Actualizar Template
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingTemplate(null);
                  }}
                  className="flex-1"
                >
                  Cancelar
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tag Manager Modal */}
      {showTagManager && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg w-full max-w-2xl">
            <div className="p-6 border-b flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold">Gestionar Etiquetas</h3>
                <p className="text-sm text-gray-600 mt-1">Añadir o eliminar etiquetas globales</p>
              </div>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setShowTagManager(false)}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>

            <div className="p-6 space-y-4">
              {/* Create New Tag */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <Label className="font-semibold mb-2 block">Crear Nueva Etiqueta</Label>
                <div className="flex gap-2">
                  <Input
                    value={newGlobalTag}
                    onChange={(e) => setNewGlobalTag(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && createGlobalTag()}
                    placeholder="Nombre de la etiqueta..."
                  />
                  <Button onClick={createGlobalTag}>
                    <Plus className="h-4 w-4 mr-2" />
                    Crear
                  </Button>
                </div>
              </div>

              {/* List of Tags */}
              <div>
                <Label className="font-semibold mb-3 block">Etiquetas Existentes ({allTags.length})</Label>
                <div className="grid grid-cols-2 gap-2 max-h-96 overflow-y-auto">
                  {allTags.map(tag => (
                    <div key={tag} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border">
                      <Badge className="bg-blue-100 text-blue-700">{tag}</Badge>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={() => deleteGlobalTag(tag)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TemplatesManager;
