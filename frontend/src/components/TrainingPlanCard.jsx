import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from './ui/dialog';
import {
  Edit,
  Mail,
  FileDown,
  Loader2,
  Save,
  X,
  ChevronDown,
  ChevronUp,
  Calendar,
  Target,
  Clock,
  Dumbbell,
  Trash2,
  AlertTriangle,
} from 'lucide-react';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TrainingPlanCard = ({ userId, token, onPlanUpdated }) => {
  const [latestPlan, setLatestPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editedPlan, setEditedPlan] = useState(null);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [expandedSessions, setExpandedSessions] = useState({});
  const [isExpanded, setIsExpanded] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Fetch latest plan
  useEffect(() => {
    if (userId) {
      fetchLatestPlan();
    }
  }, [userId]);

  const fetchLatestPlan = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${API}/admin/users/${userId}/training-plans/latest`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setLatestPlan(response.data);
    } catch (error) {
      if (error.response?.status !== 404) {
        console.error('Error fetching latest plan:', error);
      }
      setLatestPlan(null);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    setEditedPlan(JSON.parse(JSON.stringify(latestPlan))); // Deep clone
    setShowEditModal(true);
    // Initialize all sessions as collapsed
    const sessionsState = {};
    latestPlan.plan.sessions.forEach((_, idx) => {
      sessionsState[idx] = false;
    });
    setExpandedSessions(sessionsState);
  };

  const toggleSession = (idx) => {
    setExpandedSessions(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await axios.put(
        `${API}/admin/users/${userId}/training-plans/edit`,
        { plan: editedPlan.plan },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      // Update local state with edited plan
      setLatestPlan(editedPlan);
      setShowEditModal(false);
      
      // Show success message
      alert('✅ Plan guardado correctamente');
      
      if (onPlanUpdated) onPlanUpdated();
    } catch (error) {
      console.error('Error saving plan:', error);
      alert('❌ Error guardando el plan. Por favor intenta de nuevo.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    try {
      setDeleting(true);
      await axios.delete(
        `${API}/admin/users/${userId}/training-plans/latest`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      setLatestPlan(null);
      setShowDeleteConfirm(false);
      alert('✅ Plan eliminado correctamente');
      
      if (onPlanUpdated) onPlanUpdated();
    } catch (error) {
      console.error('Error deleting plan:', error);
      alert('❌ Error eliminando el plan. Por favor intenta de nuevo.');
    } finally {
      setDeleting(false);
    }
  };

  const handleSendEmail = async () => {
    alert('Funcionalidad de envío de email próximamente');
  };

  const handleExportPDF = async () => {
    alert('Funcionalidad de exportación a PDF próximamente');
  };

  const updatePlanField = (field, value) => {
    setEditedPlan(prev => ({
      ...prev,
      plan: {
        ...prev.plan,
        [field]: value
      }
    }));
  };

  const updateExerciseField = (sessionIdx, blockIdx, exerciseIdx, field, value) => {
    setEditedPlan(prev => {
      const newPlan = JSON.parse(JSON.stringify(prev));
      newPlan.plan.sessions[sessionIdx].blocks[blockIdx].exercises[exerciseIdx][field] = value;
      return newPlan;
    });
  };

  if (loading) {
    return (
      <Card className="border-2 border-blue-200">
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          <span className="ml-2 text-gray-600">Cargando plan...</span>
        </CardContent>
      </Card>
    );
  }

  if (!latestPlan) {
    return (
      <Card className="border-2 border-gray-200">
        <CardContent className="py-8 text-center">
          <Dumbbell className="h-12 w-12 mx-auto text-gray-400 mb-2" />
          <p className="text-gray-600">No hay plan de entrenamiento generado</p>
          <p className="text-sm text-gray-500 mt-1">
            Genera un plan usando los cuestionarios EDN360 disponibles
          </p>
        </CardContent>
      </Card>
    );
  }

  const { plan, created_at, status } = latestPlan;

  return (
    <>
      <Card className="border-2 border-blue-300 bg-gradient-to-br from-blue-50 to-cyan-50">
        <CardHeader className="border-b border-blue-200 bg-white">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Dumbbell className="h-5 w-5 text-blue-600" />
                <CardTitle className="text-xl text-blue-900">
                  Plan EDN360 (último generado)
                </CardTitle>
                <Badge variant={status === 'sent' ? 'success' : 'secondary'}>
                  {status === 'sent' ? 'Enviado' : 'Borrador'}
                </Badge>
              </div>
              <p className="text-sm text-gray-600">
                Generado el {new Date(created_at).toLocaleDateString('es-ES', {
                  day: 'numeric',
                  month: 'long',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            </div>
          </div>
        </CardHeader>

        <CardContent className="pt-4">
          {/* Plan Header */}
          <div className="bg-white rounded-lg p-4 mb-4 border border-blue-200">
            <h3 className="text-lg font-bold text-gray-900 mb-2">{plan.title}</h3>
            <p className="text-sm text-gray-700 mb-3">{plan.summary}</p>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="flex items-center gap-2 text-sm">
                <Target className="h-4 w-4 text-blue-600" />
                <span className="text-gray-700">{plan.goal}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Calendar className="h-4 w-4 text-blue-600" />
                <span className="text-gray-700">{plan.days_per_week} días/semana</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Clock className="h-4 w-4 text-blue-600" />
                <span className="text-gray-700">{plan.session_duration_min} min/sesión</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Dumbbell className="h-4 w-4 text-blue-600" />
                <span className="text-gray-700">{plan.sessions?.length || 0} sesiones</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-2">
            <Button
              onClick={handleEdit}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              <Edit className="h-4 w-4 mr-2" />
              Ver / Editar Plan
            </Button>
            <Button
              onClick={handleSendEmail}
              variant="outline"
              className="border-blue-300 text-blue-700 hover:bg-blue-50"
            >
              <Mail className="h-4 w-4 mr-2" />
              Enviar por Email
            </Button>
            <Button
              onClick={handleExportPDF}
              variant="outline"
              className="border-blue-300 text-blue-700 hover:bg-blue-50"
            >
              <FileDown className="h-4 w-4 mr-2" />
              Exportar PDF
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Edit Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl text-blue-900 flex items-center gap-2">
              <Edit className="h-6 w-6" />
              Editar Plan de Entrenamiento
            </DialogTitle>
            <DialogDescription>
              Modifica cualquier aspecto del plan. Los cambios se guardarán automáticamente.
            </DialogDescription>
          </DialogHeader>

          {editedPlan && (
            <div className="space-y-6 py-4">
              {/* Header Section */}
              <div className="space-y-4 bg-gray-50 p-4 rounded-lg">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Título del Plan
                  </label>
                  <Input
                    value={editedPlan.plan.title}
                    onChange={(e) => updatePlanField('title', e.target.value)}
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Resumen
                  </label>
                  <Textarea
                    value={editedPlan.plan.summary}
                    onChange={(e) => updatePlanField('summary', e.target.value)}
                    className="w-full"
                    rows={2}
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Objetivo
                  </label>
                  <Input
                    value={editedPlan.plan.goal}
                    onChange={(e) => updatePlanField('goal', e.target.value)}
                    className="w-full"
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">
                      Días/Semana
                    </label>
                    <Input
                      type="number"
                      value={editedPlan.plan.days_per_week}
                      onChange={(e) => updatePlanField('days_per_week', parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">
                      Duración (min)
                    </label>
                    <Input
                      type="number"
                      value={editedPlan.plan.session_duration_min}
                      onChange={(e) => updatePlanField('session_duration_min', parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">
                      Semanas
                    </label>
                    <Input
                      type="number"
                      value={editedPlan.plan.weeks}
                      onChange={(e) => updatePlanField('weeks', parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>
                </div>
              </div>

              {/* Sessions */}
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-gray-900">Sesiones de Entrenamiento</h3>
                
                {editedPlan.plan.sessions.map((session, sessionIdx) => (
                  <Card key={sessionIdx} className="border-2 border-blue-200">
                    <CardHeader
                      className="cursor-pointer hover:bg-blue-50 transition-colors"
                      onClick={() => toggleSession(sessionIdx)}
                    >
                      <div className="flex justify-between items-center">
                        <CardTitle className="text-lg text-blue-900">
                          {session.id} - {session.name}
                        </CardTitle>
                        {expandedSessions[sessionIdx] ? (
                          <ChevronUp className="h-5 w-5 text-blue-600" />
                        ) : (
                          <ChevronDown className="h-5 w-5 text-blue-600" />
                        )}
                      </div>
                    </CardHeader>

                    {expandedSessions[sessionIdx] && (
                      <CardContent className="pt-4 space-y-4">
                        {/* Session Blocks */}
                        {session.blocks.map((block, blockIdx) => (
                          <div key={blockIdx} className="bg-gray-50 p-4 rounded-lg space-y-3">
                            <h4 className="font-semibold text-gray-800">
                              Bloque {block.id} - {block.primary_muscles.join(', ')}
                            </h4>

                            {/* Exercises */}
                            <div className="space-y-3">
                              {block.exercises.map((exercise, exerciseIdx) => (
                                <div key={exerciseIdx} className="bg-white p-3 rounded border border-gray-200">
                                  <div className="grid grid-cols-12 gap-2 items-start">
                                    <div className="col-span-1 flex items-center justify-center">
                                      <span className="text-sm font-bold text-gray-500">
                                        {exercise.order}
                                      </span>
                                    </div>
                                    <div className="col-span-5">
                                      <Input
                                        value={exercise.name}
                                        onChange={(e) => updateExerciseField(sessionIdx, blockIdx, exerciseIdx, 'name', e.target.value)}
                                        className="text-sm"
                                        placeholder="Nombre del ejercicio"
                                      />
                                    </div>
                                    <div className="col-span-2">
                                      <Input
                                        value={exercise.series}
                                        onChange={(e) => updateExerciseField(sessionIdx, blockIdx, exerciseIdx, 'series', e.target.value)}
                                        className="text-sm"
                                        placeholder="Series"
                                      />
                                    </div>
                                    <div className="col-span-2">
                                      <Input
                                        value={exercise.reps}
                                        onChange={(e) => updateExerciseField(sessionIdx, blockIdx, exerciseIdx, 'reps', e.target.value)}
                                        className="text-sm"
                                        placeholder="Reps"
                                      />
                                    </div>
                                    <div className="col-span-2">
                                      <Input
                                        value={exercise.rpe}
                                        onChange={(e) => updateExerciseField(sessionIdx, blockIdx, exerciseIdx, 'rpe', e.target.value)}
                                        className="text-sm"
                                        placeholder="RPE"
                                      />
                                    </div>
                                  </div>
                                  <div className="mt-2">
                                    <Textarea
                                      value={exercise.notes}
                                      onChange={(e) => updateExerciseField(sessionIdx, blockIdx, exerciseIdx, 'notes', e.target.value)}
                                      className="text-sm"
                                      placeholder="Notas del ejercicio"
                                      rows={1}
                                    />
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </CardContent>
                    )}
                  </Card>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end gap-2 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => setShowEditModal(false)}
                  disabled={saving}
                >
                  <X className="h-4 w-4 mr-2" />
                  Cancelar
                </Button>
                <Button
                  onClick={handleSave}
                  disabled={saving}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {saving ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Guardando...
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Guardar Cambios
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default TrainingPlanCard;
