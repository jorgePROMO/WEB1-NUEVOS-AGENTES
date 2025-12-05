import React, { useState, useEffect, useCallback } from 'react';
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
  UserCheck,
  ExternalLink,
  Eye,
  EyeOff,
} from 'lucide-react';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Traducciones de términos de entrenamiento (inglés → español de España)
const TRANSLATIONS = {
  // Tipos de entrenamiento
  'full_body': 'Cuerpo Completo',
  'upper_lower': 'Torso-Pierna',
  'push_pull_legs': 'Empuje-Tirón-Pierna',
  'bro_split': 'Rutina Weider',
  
  // Focos/énfasis
  'upper_body': 'Tren Superior',
  'lower_body': 'Tren Inferior',
  'push': 'Empuje',
  'pull': 'Tirón',
  'push_focus': 'Énfasis Empuje',
  'pull_focus': 'Énfasis Tirón',
  'chest': 'Pecho',
  'back': 'Espalda',
  'shoulders': 'Hombros',
  'triceps': 'Tríceps',
  'biceps': 'Bíceps',
  'quads': 'Cuádriceps',
  'hamstrings': 'Isquiotibiales',
  'glutes': 'Glúteos',
  'legs': 'Piernas',
  'arms': 'Brazos',
  'core': 'Core',
  'calves': 'Gemelos',
  
  // Grupos musculares
  'front_delts': 'Deltoides Anterior',
  'side_delts': 'Deltoides Lateral',
  'rear_delts': 'Deltoides Posterior',
  
  // Nombres de sesiones comunes (patrones)
  'Push Emphasis': 'Énfasis Empuje',
  'Pull Emphasis': 'Énfasis Tirón',
  'Push Dominante': 'Énfasis Empuje',
  'Pull Dominante': 'Énfasis Tirón',
  'Upper 1': 'Tren Superior 1',
  'Upper 2': 'Tren Superior 2',
  'Lower 1': 'Tren Inferior 1',
  'Lower 2': 'Tren Inferior 2',
  'Quad Dominante': 'Énfasis Cuádriceps',
  'Cuádriceps Dominante': 'Énfasis Cuádriceps',
  'Isquios y Glúteos Dominante': 'Énfasis Isquios y Glúteos'
};

// Función para traducir texto
const translate = (text) => {
  if (!text) return text;
  
  // Si es un array, traducir cada elemento
  if (Array.isArray(text)) {
    return text.map(t => TRANSLATIONS[t] || t).join(', ');
  }
  
  // Si es un string, buscar traducciones parciales
  let translated = text;
  Object.keys(TRANSLATIONS).forEach(key => {
    const regex = new RegExp(key, 'gi');
    translated = translated.replace(regex, TRANSLATIONS[key]);
  });
  
  return translated;
};

const TrainingPlanCard = ({ userId, token, onPlanUpdated }) => {
  const [allPlans, setAllPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [editedPlan, setEditedPlan] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [expandedSessions, setExpandedSessions] = useState({});
  const [expandedPlans, setExpandedPlans] = useState({});
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [planToDelete, setPlanToDelete] = useState(null);
  const [sending, setSending] = useState(false);

  const fetchAllPlans = useCallback(async () => {
    try {
      setLoading(true);
      
      // Get ALL training plans from the list endpoint
      const response = await axios.get(
        `${API}/admin/users/${userId}/training-plans`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      // Los planes ya vienen ordenados por created_at DESC (más reciente primero)
      const plans = response.data || [];
      const plansArray = Array.isArray(plans) ? plans : [];
      
      setAllPlans(plansArray);
    } catch (error) {
      if (error.response?.status !== 404) {
        console.error('Error fetching plans:', error);
      }
      setAllPlans([]);
    } finally {
      setLoading(false);
    }
  }, [userId, token]);

  // Fetch latest plan
  useEffect(() => {
    if (userId) {
      fetchAllPlans();
    }
  }, [userId, fetchAllPlans]);

  const handleEdit = (planData) => {
    setEditedPlan(JSON.parse(JSON.stringify(planData))); // Deep clone
    setShowEditModal(true);
    // Initialize all sessions as collapsed
    const sessionsState = {};
    planData.plan.sessions.forEach((_, idx) => {
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
      
      // Refresh plans to get updated data
      await fetchAllPlans();
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
    if (!planToDelete) return;
    
    try {
      setDeleting(true);
      await axios.delete(
        `${API}/admin/training-plans/${planToDelete.id}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      await fetchAllPlans();
      setShowDeleteConfirm(false);
      setPlanToDelete(null);
      alert('✅ Plan eliminado correctamente');
      
      if (onPlanUpdated) {
        onPlanUpdated(null);
      }
    } catch (error) {
      console.error('Error deleting plan:', error);
      alert('❌ Error eliminando el plan. Inténtalo de nuevo.');
    } finally {
      setDeleting(false);
    }
  };

  const handleToggleStatus = async (planData) => {
    try {
      const currentStatus = planData.status || 'draft';
      const action = currentStatus === 'sent' ? 'desactivar' : 'activar';
      
      if (!window.confirm(`¿Seguro que quieres ${action} este plan?`)) {
        return;
      }
      
      const response = await axios.patch(
        `${API}/admin/training-plans/${planData.id}/toggle-status`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      await fetchAllPlans();
      alert(response.data.message || '✅ Estado actualizado correctamente');
      
      if (onPlanUpdated) {
        onPlanUpdated(null);
      }
    } catch (error) {
      console.error('Error toggling plan status:', error);
      alert('❌ Error cambiando el estado del plan. Inténtalo de nuevo.');
    }
  };

  const handleSendToUserPanel = async () => {
    try {
      setSending(true);
      await axios.post(
        `${API}/admin/users/${userId}/training-plans/send-to-user-panel`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      alert('✅ Plan enviado al panel del usuario y notificación por email enviada');
      
      // Refrescar el plan para actualizar el status
      await fetchAllPlans();
    } catch (error) {
      console.error('Error sending to user panel:', error);
      const errorMsg = error.response?.data?.detail?.message || error.message;
      alert(`❌ Error: ${errorMsg}`);
    } finally {
      setSending(false);
    }
  };

  const handleSendEmail = async () => {
    try {
      setSending(true);
      await axios.post(
        `${API}/admin/users/${userId}/training-plans/send-email`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      alert('✅ Plan enviado por email correctamente al cliente');
    } catch (error) {
      console.error('Error sending email:', error);
      const errorMsg = error.response?.data?.detail?.message || error.message;
      alert(`❌ Error enviando email: ${errorMsg}`);
    } finally {
      setSending(false);
    }
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
      const session = newPlan.plan.sessions[sessionIdx];
      
      // Support both new structure (bloques_estructurados) and old structure (blocks)
      if (session.bloques_estructurados) {
        session.bloques_estructurados[blockIdx].ejercicios[exerciseIdx][field] = value;
      } else if (session.blocks) {
        session.blocks[blockIdx].exercises[exerciseIdx][field] = value;
      }
      
      return newPlan;
    });
  };

  if (loading) {
    return (
      <Card className="border border-gray-200">
        <CardContent className="flex items-center justify-center py-4">
          <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
          <span className="ml-2 text-sm text-gray-600">Cargando plan...</span>
        </CardContent>
      </Card>
    );
  }

  if (allPlans.length === 0) {
    return (
      <Card className="border border-gray-200">
        <CardContent className="py-6 text-center">
          <Dumbbell className="h-10 w-10 mx-auto text-gray-400 mb-2" />
          <p className="text-sm text-gray-600">No hay planes de entrenamiento generados</p>
          <p className="text-xs text-gray-500 mt-1">
            Genera un plan usando los cuestionarios EDN360
          </p>
        </CardContent>
      </Card>
    );
  }

  // Renderizar TODOS los planes (más reciente arriba)
  return (
    <div className="space-y-4">
      {allPlans.map((planData, planIndex) => {
        // Validate planData structure
        if (!planData || !planData.plan) {
          console.warn('Invalid plan data at index', planIndex, planData);
          return null;
        }
        
        const { plan, created_at, status, id: planId } = planData;
        const isPlanExpanded = expandedPlans[planIndex] || false;
        
        // Validate plan object
        if (!plan || typeof plan !== 'object') {
          console.warn('Invalid plan object at index', planIndex, plan);
          return null;
        }

        return (
          <Card key={planIndex} className="border-2 border-blue-300 shadow-sm hover:shadow-md transition-shadow">
            {/* Compact Header - Always Visible */}
            <CardHeader 
              className="cursor-pointer hover:bg-blue-50 transition-colors pb-3"
              onClick={() => setExpandedPlans(prev => ({...prev, [planIndex]: !prev[planIndex]}))}
            >
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3 flex-1">
              <Dumbbell className="h-5 w-5 text-blue-600 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <CardTitle className="text-base font-semibold text-gray-900 truncate">
                    {plan.title}
                  </CardTitle>
                  <Badge 
                    variant={status === 'sent' ? 'success' : 'secondary'}
                    className="flex-shrink-0 text-xs"
                  >
                    {status === 'sent' ? 'Enviado' : 'Borrador'}
                  </Badge>
                </div>
                <div className="flex items-center gap-3 text-xs text-gray-600">
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {plan.days_per_week} días/sem
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {plan.session_duration_min} min
                  </span>
                  <span className="flex items-center gap-1">
                    <Dumbbell className="h-3 w-3" />
                    {plan.sessions?.length || 0} sesiones
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 ml-2">
              {isPlanExpanded ? (
                <ChevronUp className="h-5 w-5 text-gray-500" />
              ) : (
                <ChevronDown className="h-5 w-5 text-gray-500" />
              )}
            </div>
          </div>
        </CardHeader>

        {/* Expanded Content */}
        {isPlanExpanded && (
          <CardContent className="pt-0 space-y-4 border-t">
            {/* Plan Details */}
            <div className="bg-gray-50 rounded-lg p-3 space-y-3">
              <div>
                <p className="text-xs font-semibold text-gray-500 mb-1">Objetivo</p>
                <p className="text-sm text-gray-900">{plan.goal}</p>
              </div>
              <div>
                <p className="text-xs font-semibold text-gray-500 mb-1">Resumen del Programa</p>
                <p className="text-sm text-gray-700">{plan.summary}</p>
              </div>
              
              {/* Notas Generales del Plan */}
              {plan.general_notes && plan.general_notes.length > 0 && (
                <div className="border-t border-gray-200 pt-3">
                  <p className="text-xs font-semibold text-gray-500 mb-2">⚠️ Notas Generales Importantes</p>
                  <ul className="space-y-1">
                    {plan.general_notes.map((note, idx) => (
                      <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                        <span className="text-blue-600 mt-0.5">•</span>
                        <span>{note}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Programa Info */}
              <div className="border-t border-gray-200 pt-3 grid grid-cols-2 gap-3">
                <div>
                  <p className="text-xs font-semibold text-gray-500 mb-1">Tipo de Rutina</p>
                  <p className="text-sm text-gray-900">{translate(plan.training_type)}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-500 mb-1">Duración del Programa</p>
                  <p className="text-sm text-gray-900">{plan.weeks} semanas</p>
                </div>
              </div>
              
              <div>
                <p className="text-xs font-semibold text-gray-500 mb-1">Generado</p>
                <p className="text-sm text-gray-700">
                  {new Date(created_at).toLocaleDateString('es-ES', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-2">
              <Button
                onClick={(e) => {
                  e.stopPropagation();
                  handleEdit(planData);
                }}
                size="sm"
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                <Edit className="h-3 w-3 mr-1" />
                Ver/Editar
              </Button>
              <Button
                onClick={(e) => {
                  e.stopPropagation();
                  handleSendToUserPanel();
                }}
                size="sm"
                variant="outline"
                className="border-green-400 text-green-700 hover:bg-green-50"
                disabled={sending || status === 'sent'}
              >
                {sending ? (
                  <>
                    <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                    Enviando...
                  </>
                ) : (
                  <>
                    <UserCheck className="h-3 w-3 mr-1" />
                    {status === 'sent' ? 'Ya Enviado' : 'Enviar al Panel del Usuario'}
                  </>
                )}
              </Button>
              <Button
                onClick={(e) => {
                  e.stopPropagation();
                  handleSendEmail();
                }}
                size="sm"
                variant="outline"
                className="border-blue-400 text-blue-700 hover:bg-blue-50"
                disabled={sending}
              >
                <Mail className="h-3 w-3 mr-1" />
                Enviar por Email
              </Button>
              <Button
                onClick={(e) => {
                  e.stopPropagation();
                  handleToggleStatus(planData);
                }}
                size="sm"
                variant="outline"
                className={
                  status === 'sent'
                    ? 'border-orange-400 text-orange-700 hover:bg-orange-50'
                    : 'border-green-400 text-green-700 hover:bg-green-50'
                }
              >
                {status === 'sent' ? (
                  <>
                    <EyeOff className="h-3 w-3 mr-1" />
                    Desactivar
                  </>
                ) : (
                  <>
                    <Eye className="h-3 w-3 mr-1" />
                    Activar
                  </>
                )}
              </Button>
              <Button
                onClick={(e) => {
                  e.stopPropagation();
                  setPlanToDelete(planData);
                  setShowDeleteConfirm(true);
                }}
                size="sm"
                variant="outline"
                className="border-red-300 text-red-700 hover:bg-red-50"
              >
                <Trash2 className="h-3 w-3 mr-1" />
                Eliminar
              </Button>
            </div>
          </CardContent>
        )}
      </Card>
        );
      })}

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-700">
              <AlertTriangle className="h-5 w-5" />
              ¿Eliminar plan de entrenamiento?
            </DialogTitle>
            <DialogDescription>
              Esta acción no se puede deshacer. El plan será eliminado permanentemente de la base de datos.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-2 mt-4">
            <Button
              variant="outline"
              onClick={() => setShowDeleteConfirm(false)}
              disabled={deleting}
            >
              Cancelar
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleting}
              className="bg-red-600 hover:bg-red-700"
            >
              {deleting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Eliminando...
                </>
              ) : (
                <>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Sí, eliminar
                </>
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Edit Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-xl text-blue-900 flex items-center gap-2">
              <Edit className="h-5 w-5" />
              Editar Plan de Entrenamiento
            </DialogTitle>
            <DialogDescription>
              Modifica cualquier aspecto del plan y guarda los cambios.
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
                <h3 className="text-base font-bold text-gray-900">Sesiones de Entrenamiento</h3>
                
                {editedPlan.plan.sessions.map((session, sessionIdx) => (
                  <Card key={sessionIdx} className="border border-blue-200">
                    <CardHeader
                      className="cursor-pointer hover:bg-blue-50 transition-colors py-3"
                      onClick={() => toggleSession(sessionIdx)}
                    >
                      <div className="flex justify-between items-center">
                        <CardTitle className="text-sm font-semibold text-blue-900">
                          {session.id} - {translate(session.name)}
                        </CardTitle>
                        {expandedSessions[sessionIdx] ? (
                          <ChevronUp className="h-4 w-4 text-blue-600" />
                        ) : (
                          <ChevronDown className="h-4 w-4 text-blue-600" />
                        )}
                      </div>
                      
                      {/* Focus tags (español) */}
                      {session.focus && session.focus.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {session.focus.map((f, idx) => (
                            <Badge key={idx} variant="secondary" className="text-xs">
                              {translate(f)}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </CardHeader>

                    {expandedSessions[sessionIdx] && (
                      <CardContent className="pt-3 space-y-3">
                        {/* Session Blocks - New 4-block structure */}
                        {(session.bloques_estructurados || session.blocks).map((block, blockIdx) => {
                          // Handle new 4-block structure or old structure for backward compatibility
                          const blockName = block.nombre || `Bloque ${block.id} - ${translate(block.primary_muscles)}`;
                          const blockExercises = block.ejercicios || block.exercises;
                          
                          return (
                            <div key={blockIdx} className="bg-gray-50 p-3 rounded-lg space-y-2">
                              <h4 className="text-sm font-semibold text-gray-800">
                                {blockName}
                              </h4>

                              {/* Exercises */}
                              <div className="space-y-2">
                                {/* Table Headers */}
                                <div className="grid grid-cols-12 gap-2 items-center bg-gray-100 px-2 py-1 rounded">
                                  <div className="col-span-1 text-xs font-semibold text-gray-700 text-center">
                                    #
                                  </div>
                                  <div className="col-span-5 text-xs font-semibold text-gray-700">
                                    Ejercicio
                                  </div>
                                  <div className="col-span-2 text-xs font-semibold text-gray-700">
                                    Series
                                  </div>
                                  <div className="col-span-2 text-xs font-semibold text-gray-700">
                                    Reps
                                  </div>
                                  <div className="col-span-2 text-xs font-semibold text-gray-700">
                                    RPE
                                  </div>
                                </div>
                                
                                {blockExercises.map((exercise, exerciseIdx) => (
                                  <div key={exerciseIdx} className="bg-white p-2 rounded border border-gray-200">
                                    <div className="grid grid-cols-12 gap-2 items-start">
                                      <div className="col-span-1 flex items-center justify-center">
                                        <span className="text-xs font-bold text-gray-500">
                                          {exercise.order}
                                        </span>
                                      </div>
                                      <div className="col-span-5">
                                        <Input
                                          value={exercise.name}
                                          onChange={(e) => updateExerciseField(sessionIdx, blockIdx, exerciseIdx, 'name', e.target.value)}
                                          className="text-xs h-8"
                                          placeholder="Nombre del ejercicio"
                                        />
                                      </div>
                                      <div className="col-span-2">
                                        <Input
                                          value={exercise.series}
                                          onChange={(e) => updateExerciseField(sessionIdx, blockIdx, exerciseIdx, 'series', e.target.value)}
                                          className="text-xs h-8"
                                          placeholder="Series"
                                        />
                                      </div>
                                      <div className="col-span-2">
                                        <Input
                                          value={exercise.reps}
                                          onChange={(e) => updateExerciseField(sessionIdx, blockIdx, exerciseIdx, 'reps', e.target.value)}
                                          className="text-xs h-8"
                                          placeholder="Reps"
                                        />
                                      </div>
                                      <div className="col-span-2">
                                        <Input
                                          value={exercise.rpe}
                                          onChange={(e) => updateExerciseField(sessionIdx, blockIdx, exerciseIdx, 'rpe', e.target.value)}
                                          className="text-xs h-8"
                                          placeholder="RPE"
                                        />
                                      </div>
                                    </div>
                                    <div className="mt-2 space-y-1">
                                      <Textarea
                                        value={exercise.notes}
                                        onChange={(e) => updateExerciseField(sessionIdx, blockIdx, exerciseIdx, 'notes', e.target.value)}
                                        className="text-xs"
                                        placeholder="Notas del ejercicio"
                                        rows={1}
                                      />
                                      {/* Botón Ver Video */}
                                      {exercise.video_url && (
                                        <Button
                                          onClick={() => window.open(exercise.video_url, '_blank')}
                                          size="sm"
                                          variant="outline"
                                          className="w-full text-xs border-blue-300 text-blue-700 hover:bg-blue-50"
                                        >
                                          <ExternalLink className="h-3 w-3 mr-1" />
                                          Ver Video
                                        </Button>
                                      )}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          );
                        })}
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
    </div>
  );
};

export default TrainingPlanCard;
