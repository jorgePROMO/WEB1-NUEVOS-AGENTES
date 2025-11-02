import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { 
  Search, 
  Filter, 
  Eye, 
  Plus,
  Edit,
  Trash2,
  X,
  Calendar,
  Mail,
  Phone,
  Target,
  DollarSign,
  Clock,
  FileText,
  Save,
  UserPlus,
  Users
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const ProspectsCRM = ({ token }) => {
  const [prospects, setProspects] = useState([]);
  const [stages, setStages] = useState([]);
  const [selectedProspect, setSelectedProspect] = useState(null);
  const [showDetail, setShowDetail] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStage, setFilterStage] = useState('');
  const [showStageManager, setShowStageManager] = useState(false);
  const [showConvertModal, setShowConvertModal] = useState(false);
  const [prospectToConvert, setProspectToConvert] = useState(null);
  const [newNote, setNewNote] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadProspects();
    loadStages();
  }, []);

  const loadProspects = async (stage = null) => {
    try {
      const params = stage ? `?stage=${stage}` : '';
      const response = await axios.get(`${API}/admin/prospects${params}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setProspects(response.data.prospects || []);
    } catch (error) {
      console.error('Error loading prospects:', error);
      setProspects([]); // Set empty array on error
    }
  };

  const loadStages = async () => {
    try {
      const response = await axios.get(`${API}/admin/prospect-stages`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setStages(response.data.stages);
    } catch (error) {
      console.error('Error loading stages:', error);
    }
  };

  const loadProspectDetail = async (prospectId) => {
    try {
      const response = await axios.get(`${API}/admin/prospects/${prospectId}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setSelectedProspect(response.data);
      setShowDetail(true);
    } catch (error) {
      console.error('Error loading prospect detail:', error);
    }
  };

  const updateStage = async (prospectId, stageId) => {
    try {
      await axios.patch(`${API}/admin/prospects/${prospectId}/stage`, 
        { stage_id: stageId },
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      loadProspects(filterStage);
      if (selectedProspect && selectedProspect.id === prospectId) {
        loadProspectDetail(prospectId);
      }
    } catch (error) {
      alert('Error al actualizar etapa');
    }
  };

  const addNote = async () => {
    if (!newNote.trim() || !selectedProspect) return;
    
    try {
      await axios.post(`${API}/admin/prospects/${selectedProspect.id}/notes`,
        { prospect_id: selectedProspect.id, note: newNote },
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      setNewNote('');
      loadProspectDetail(selectedProspect.id);
    } catch (error) {
      alert('Error al agregar nota');
    }
  };


  const sendReportEmail = async (prospectId) => {
    if (!window.confirm('¿Enviar el informe por correo electrónico al prospecto?')) {
      return;
    }
    
    setLoading(true);
    try {
      await axios.post(`${API}/admin/prospects/${prospectId}/send-report-email`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      alert('✅ Informe enviado por email correctamente');
      loadProspectDetail(prospectId);
    } catch (error) {
      alert(`Error al enviar el informe: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const sendReportWhatsApp = async (prospectId) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/admin/prospects/${prospectId}/whatsapp-link`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      // Open WhatsApp Web in a new tab
      window.open(response.data.whatsapp_link, '_blank');
      
      alert('✅ WhatsApp abierto. Revisa el mensaje y dale enviar.');
      loadProspectDetail(prospectId);
    } catch (error) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };


  const deleteProspect = async (prospectId) => {
    if (!window.confirm('¿Estás seguro de eliminar este prospecto? Esta acción no se puede deshacer.')) {
      return;
    }
    
    try {
      await axios.delete(`${API}/admin/prospects/${prospectId}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      loadProspects(filterStage);
      if (showDetail && selectedProspect?.id === prospectId) {
        setShowDetail(false);
        setSelectedProspect(null);
      }
      alert('Prospecto eliminado correctamente');
    } catch (error) {
      alert('Error al eliminar prospecto');
    }
  };

  const openConvertModal = (prospect) => {
    setProspectToConvert(prospect);
    setShowConvertModal(true);
  };

  const convertProspect = async (targetCRM) => {
    if (!prospectToConvert) return;
    
    try {
      await axios.post(`${API}/admin/prospects/${prospectToConvert.id}/convert`,
        { target_crm: targetCRM },
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      setShowConvertModal(false);
      setProspectToConvert(null);
      loadProspects(filterStage);
      alert(`Prospecto convertido a ${targetCRM === 'team' ? 'Cliente Equipo' : 'Cliente Externo'} exitosamente`);
    } catch (error) {
      alert('Error al convertir prospecto');
    }
  };

  const filteredProspects = (prospects || []).filter(p => {
    const matchesSearch = p.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         p.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStage = !filterStage || p.stage_name === filterStage;
    return matchesSearch && matchesStage;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">CRM de Prospectos</h2>
          <p className="text-gray-600">Gestión de diagnósticos iniciales</p>
        </div>
        <Button
          onClick={() => setShowStageManager(true)}
          variant="outline"
        >
          <Edit className="h-4 w-4 mr-2" />
          Gestionar Etapas
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid md:grid-cols-2 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Buscar por nombre o email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="relative">
              <Filter className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <select
                value={filterStage}
                onChange={(e) => {
                  setFilterStage(e.target.value);
                  loadProspects(e.target.value || null);
                }}
                className="w-full border rounded-md px-10 py-2"
              >
                <option value="">Todas las etapas</option>
                {stages.map(stage => (
                  <option key={stage.id} value={stage.name}>{stage.name}</option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold">{prospects.length}</p>
              <p className="text-sm text-gray-600">Total Prospectos</p>
            </div>
          </CardContent>
        </Card>
        {stages.slice(0, 3).map(stage => {
          const count = prospects.filter(p => p.stage_name === stage.name).length;
          return (
            <Card key={stage.id}>
              <CardContent className="pt-6">
                <div className="text-center">
                  <p className="text-2xl font-bold">{count}</p>
                  <p className="text-sm text-gray-600">{stage.name}</p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Prospects Table */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Prospectos ({filteredProspects.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3">Nombre</th>
                  <th className="text-left p-3">Email</th>
                  <th className="text-left p-3">Fecha</th>
                  <th className="text-left p-3">Presupuesto</th>
                  <th className="text-left p-3">Etapa</th>
                  <th className="text-left p-3">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredProspects.map(prospect => (
                  <tr key={prospect.id} className="border-b hover:bg-gray-50">
                    <td className="p-3 font-medium">{prospect.nombre}</td>
                    <td className="p-3 text-sm">{prospect.email}</td>
                    <td className="p-3 text-sm">
                      {new Date(prospect.submitted_at).toLocaleDateString('es-ES')}
                    </td>
                    <td className="p-3 text-sm">{prospect.presupuesto}</td>
                    <td className="p-3">
                      <select
                        value={prospect.stage_id || ''}
                        onChange={(e) => updateStage(prospect.id, e.target.value)}
                        className="border-2 rounded-md px-3 py-1 text-sm font-medium"
                        style={{
                          borderColor: stages.find(s => s.id === prospect.stage_id)?.color || '#3B82F6',
                          backgroundColor: `${stages.find(s => s.id === prospect.stage_id)?.color}20` || '#EFF6FF',
                          color: stages.find(s => s.id === prospect.stage_id)?.color || '#3B82F6'
                        }}
                      >
                        <option value="">Sin etapa</option>
                        {stages.map(stage => (
                          <option key={stage.id} value={stage.id}>{stage.name}</option>
                        ))}
                      </select>
                    </td>
                    <td className="p-3">
                      <div className="flex gap-2">
                        {/* WhatsApp Button */}
                        <Button
                          size="sm"
                          variant="outline"
                          className="bg-green-50 hover:bg-green-100 text-green-600 border-green-300"
                          onClick={() => window.open(`https://wa.me/${prospect.whatsapp.replace(/[^0-9]/g, '')}`, '_blank')}
                          title="Contactar por WhatsApp"
                        >
                          <Phone className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => loadProspectDetail(prospect.id)}
                          title="Ver detalle"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-300"
                          onClick={() => openConvertModal(prospect)}
                          title="Convertir a cliente"
                        >
                          <UserPlus className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="bg-red-50 hover:bg-red-100 text-red-700 border-red-300"
                          onClick={() => deleteProspect(prospect.id)}
                          title="Eliminar"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredProspects.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No hay prospectos para mostrar
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Detail Modal */}
      {showDetail && selectedProspect && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-4 flex items-center justify-between">
              <h3 className="text-xl font-bold">Detalle del Prospecto</h3>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setShowDetail(false)}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>

            <div className="p-6 space-y-6">
              {/* Personal Info */}
              <div className="grid md:grid-cols-2 gap-4">
                <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                  <Mail className="h-5 w-5 text-blue-600" />
                  <div>
                    <p className="text-sm text-gray-600">Email</p>
                    <p className="font-medium">{selectedProspect.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                  <Phone className="h-5 w-5 text-green-600" />
                  <div>
                    <p className="text-sm text-gray-600">WhatsApp</p>
                    <p className="font-medium">{selectedProspect.whatsapp}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg">
                  <Calendar className="h-5 w-5 text-purple-600" />
                  <div>
                    <p className="text-sm text-gray-600">Fecha de envío</p>
                    <p className="font-medium">
                      {new Date(selectedProspect.submitted_at).toLocaleDateString('es-ES')}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-orange-50 rounded-lg">
                  <DollarSign className="h-5 w-5 text-orange-600" />
                  <div>
                    <p className="text-sm text-gray-600">Presupuesto</p>
                    <p className="font-medium">{selectedProspect.presupuesto}</p>
                  </div>
                </div>
              </div>

              {/* GPT Report Section */}
              <Card className="border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-blue-600" />
                    Informe Personalizado GPT
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Report Status */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {selectedProspect.report_generated ? (
                        <>
                          <Badge className="bg-green-600">✅ Informe Generado</Badge>
                          {selectedProspect.report_sent_at && (
                            <Badge className="bg-blue-600">
                              Enviado vía {selectedProspect.report_sent_via === 'email' ? '📧 Email' : '💬 WhatsApp'}
                            </Badge>
                          )}
                        </>
                      ) : (
                        <Badge className="bg-gray-400">⏳ Generando...</Badge>
                      )}
                    </div>
                  </div>

                  {/* Sent Date */}
                  {selectedProspect.report_sent_at && (
                    <div className="text-sm text-gray-600">
                      <span className="font-semibold">Último envío:</span>{' '}
                      {new Date(selectedProspect.report_sent_at).toLocaleDateString('es-ES', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  )}

                  {/* Send Buttons */}
                  {selectedProspect.report_generated && selectedProspect.report_content && (
                    <div className="flex gap-3 pt-2">
                      <Button
                        onClick={() => sendReportEmail(selectedProspect.id)}
                        disabled={loading}
                        className="flex-1 bg-blue-600 hover:bg-blue-700"
                      >
                        <Mail className="h-4 w-4 mr-2" />
                        Enviar por Email
                      </Button>
                      {selectedProspect.whatsapp && (
                        <Button
                          onClick={() => sendReportWhatsApp(selectedProspect.id)}
                          disabled={loading}
                          className="flex-1 bg-green-600 hover:bg-green-700"
                        >
                          <Phone className="h-4 w-4 mr-2" />
                          Enviar por WhatsApp
                        </Button>
                      )}
                    </div>
                  )}

                  {/* Info Note */}
                  {selectedProspect.report_generated && (
                    <p className="text-xs text-gray-500 italic">
                      💡 El informe se generó automáticamente al completar el cuestionario
                    </p>
                  )}
                </CardContent>
              </Card>

              {/* Full Details */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Información Completa</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label className="font-semibold">Objetivo Principal</Label>
                    <p className="mt-1">{selectedProspect.objetivo}</p>
                  </div>
                  <div>
                    <Label className="font-semibold">Intentos Previos</Label>
                    <p className="mt-1">{selectedProspect.intentos_previos}</p>
                  </div>
                  <div>
                    <Label className="font-semibold">Alimentación</Label>
                    <p className="mt-1">{selectedProspect.alimentacion}</p>
                  </div>
                  <div>
                    <Label className="font-semibold">¿Por qué ahora?</Label>
                    <p className="mt-1">{selectedProspect.por_que_ahora}</p>
                  </div>
                  {selectedProspect.comentarios_adicionales && (
                    <div>
                      <Label className="font-semibold">Comentarios Adicionales</Label>
                      <p className="mt-1">{selectedProspect.comentarios_adicionales}</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Notes Section */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Notas de Seguimiento</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Add Note */}
                  <div className="space-y-2">
                    <Textarea
                      placeholder="Agregar nota de seguimiento..."
                      value={newNote}
                      onChange={(e) => setNewNote(e.target.value)}
                      rows={3}
                    />
                    <Button onClick={addNote} disabled={!newNote.trim()}>
                      <Save className="h-4 w-4 mr-2" />
                      Guardar Nota
                    </Button>
                  </div>

                  {/* Notes List */}
                  <div className="space-y-3">
                    {selectedProspect.notes && selectedProspect.notes.length > 0 ? (
                      selectedProspect.notes.map(note => (
                        <div key={note.id} className="p-3 bg-gray-50 rounded-lg">
                          <p className="text-sm">{note.note}</p>
                          <p className="text-xs text-gray-500 mt-2">
                            {new Date(note.created_at).toLocaleString('es-ES')}
                          </p>
                        </div>
                      ))
                    ) : (
                      <p className="text-gray-500 text-center py-4">No hay notas aún</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      )}

      {/* Stage Manager Modal */}
      {showStageManager && (
        <StageManager
          stages={stages}
          onClose={() => setShowStageManager(false)}
          onUpdate={() => {
            loadStages();
            loadProspects(filterStage);
          }}
          token={token}
        />
      )}

      {/* Convert Prospect Modal */}
      {showConvertModal && prospectToConvert && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg w-full max-w-md">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold">Convertir Prospecto a Cliente</h3>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => {
                    setShowConvertModal(false);
                    setProspectToConvert(null);
                  }}
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>

              <div className="mb-6">
                <p className="text-gray-600 mb-2">
                  <strong>Prospecto:</strong> {prospectToConvert.nombre}
                </p>
                <p className="text-gray-600 mb-4">
                  <strong>Email:</strong> {prospectToConvert.email}
                </p>
                <p className="text-sm text-gray-500 mb-4">
                  Selecciona a qué CRM quieres mover este prospecto:
                </p>
              </div>

              <div className="space-y-3">
                <Button
                  className="w-full h-20 flex flex-col items-center justify-center bg-blue-500 hover:bg-blue-600 text-white"
                  onClick={() => convertProspect('team')}
                >
                  <Users className="h-8 w-8 mb-2" />
                  <span className="font-semibold">Cliente Equipo</span>
                  <span className="text-xs opacity-90">Trabaja con el equipo (web)</span>
                </Button>

                <Button
                  className="w-full h-20 flex flex-col items-center justify-center bg-orange-500 hover:bg-orange-600 text-white"
                  onClick={() => convertProspect('external')}
                >
                  <Target className="h-8 w-8 mb-2" />
                  <span className="font-semibold">Cliente Externo</span>
                  <span className="text-xs opacity-90">Trabajo directo (Harbiz)</span>
                </Button>

                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => {
                    setShowConvertModal(false);
                    setProspectToConvert(null);
                  }}
                >
                  Cancelar
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Stage Manager Component
const StageManager = ({ stages, onClose, onUpdate, token }) => {
  const [editingStage, setEditingStage] = useState(null);
  const [newStage, setNewStage] = useState({ name: '', color: '#3B82F6', order: stages.length + 1 });

  const createStage = async () => {
    if (!newStage.name.trim()) return;
    
    try {
      await axios.post(`${API}/admin/prospect-stages`, newStage, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setNewStage({ name: '', color: '#3B82F6', order: stages.length + 2 });
      onUpdate();
    } catch (error) {
      alert('Error al crear etapa');
    }
  };

  const updateStage = async (stageId, data) => {
    try {
      await axios.patch(`${API}/admin/prospect-stages/${stageId}`, data, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setEditingStage(null);
      onUpdate();
    } catch (error) {
      alert('Error al actualizar etapa');
    }
  };

  const deleteStage = async (stageId) => {
    if (!window.confirm('¿Eliminar esta etapa? Solo se puede eliminar si no hay prospectos usándola.')) return;
    
    try {
      await axios.delete(`${API}/admin/prospect-stages/${stageId}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      onUpdate();
    } catch (error) {
      alert(error.response?.data?.detail || 'Error al eliminar etapa');
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b p-4 flex items-center justify-between">
          <h3 className="text-xl font-bold">Gestionar Etapas</h3>
          <Button size="sm" variant="ghost" onClick={onClose}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        <div className="p-6 space-y-6">
          {/* Create New Stage */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Crear Nueva Etapa</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <Label>Nombre</Label>
                <Input
                  value={newStage.name}
                  onChange={(e) => setNewStage({ ...newStage, name: e.target.value })}
                  placeholder="Ej: En negociación"
                />
              </div>
              <div>
                <Label>Color</Label>
                <Input
                  type="color"
                  value={newStage.color}
                  onChange={(e) => setNewStage({ ...newStage, color: e.target.value })}
                />
              </div>
              <Button onClick={createStage}>
                <Plus className="h-4 w-4 mr-2" />
                Crear Etapa
              </Button>
            </CardContent>
          </Card>

          {/* Existing Stages */}
          <div className="space-y-3">
            <h4 className="font-semibold">Etapas Actuales</h4>
            {stages.map(stage => (
              <Card key={stage.id}>
                <CardContent className="pt-4">
                  {editingStage?.id === stage.id ? (
                    <div className="space-y-3">
                      <Input
                        value={editingStage.name}
                        onChange={(e) => setEditingStage({ ...editingStage, name: e.target.value })}
                      />
                      <Input
                        type="color"
                        value={editingStage.color}
                        onChange={(e) => setEditingStage({ ...editingStage, color: e.target.value })}
                      />
                      <div className="flex gap-2">
                        <Button size="sm" onClick={() => updateStage(stage.id, editingStage)}>
                          Guardar
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => setEditingStage(null)}>
                          Cancelar
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div
                          className="w-4 h-4 rounded"
                          style={{ backgroundColor: stage.color }}
                        />
                        <span className="font-medium">{stage.name}</span>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setEditingStage(stage)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => deleteStage(stage.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProspectsCRM;
