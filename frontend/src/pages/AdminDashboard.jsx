import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle,
  DialogDescription 
} from '../components/ui/dialog';
import TrainingPlanChatDialog from '../components/TrainingPlanChatDialog';
import NutritionPlanChatDialog from '../components/NutritionPlanChatDialog';
import axios from 'axios';
import { 
  Users, 
  LogOut,
  UserPlus,
  Send,
  Calendar,
  FileText,
  Upload,
  Bell,
  MessageSquare,
  Search,
  CheckCircle,
  XCircle,
  Edit,
  Mail,
  Download,
  Trash2,
  Target,
  Copy,
  X,
  CalendarPlus,
  ExternalLink,
  UtensilsCrossed,
  Loader2,
  Save,
  UserCheck,
  Dumbbell,
  CreditCard,
  DollarSign
} from 'lucide-react';
import ChatBox from '../components/ChatBox';
import { AdminCalendar } from '../components/Calendar';
import { EditUserModal, SendPasswordResetButton } from '../components/AdminComponents';
import ProspectsCRM from '../components/ProspectsCRM';
import TeamClientsCRM from '../components/TeamClientsCRM';
import ExternalClientsCRM from '../components/ExternalClientsCRM';
import TemplatesManager from '../components/TemplatesManager';
import ClientsAtRisk from '../components/ClientsAtRisk';
import GoogleCalendarManager from '../components/GoogleCalendarManager';
import GenerationProgressModal from '../components/GenerationProgressModal';
import TrainingPlanCard from '../components/TrainingPlanCard';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminDashboard = () => {
  const { user, logout, isAdmin, token } = useAuth();
  const navigate = useNavigate();
  const [clients, setClients] = useState([]);
  const [stats, setStats] = useState({ total: 0, active: 0, pending: 0 });
  const [selectedClient, setSelectedClient] = useState(null);
  const [selectedClientDetails, setSelectedClientDetails] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showChat, setShowChat] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingClientData, setLoadingClientData] = useState(false); // NEW: Prevent flickering during client data load
  const [showArchived, setShowArchived] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [userToEdit, setUserToEdit] = useState(null);
  const [activeView, setActiveView] = useState('clients'); // clients, prospects, team-clients, external-clients, calendar
  const [templates, setTemplates] = useState([]);
  const [allTags, setAllTags] = useState([]);
  const [selectedTagFilter, setSelectedTagFilter] = useState('');
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [showTemplateSelector, setShowTemplateSelector] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [templateMessage, setTemplateMessage] = useState('');

  // Nutrition states
  const [nutritionPlans, setNutritionPlans] = useState([]); // Array de planes
  const [questionnaireSubmissions, setQuestionnaireSubmissions] = useState([]); // Array de respuestas pendientes LEGACY
  const [edn360QuestionnaireSubmissions, setEdn360QuestionnaireSubmissions] = useState([]); // EDN360 questionnaires
  const [selectedPlan, setSelectedPlan] = useState(null); // Plan seleccionado actualmente
  const [selectedSubmission, setSelectedSubmission] = useState(null); // Submission seleccionada
  const [editingNutrition, setEditingNutrition] = useState(false);
  const [nutritionContent, setNutritionContent] = useState('');
  const [generatingPDF, setGeneratingPDF] = useState(false);
  const [sendingNutrition, setSendingNutrition] = useState(null);
  const [generatingPlan, setGeneratingPlan] = useState(false);
  const [showNutritionModal, setShowNutritionModal] = useState(false); // Control del modal
  const [modalPlan, setModalPlan] = useState(null); // Plan que se muestra en el modal
  const [showNutritionChat, setShowNutritionChat] = useState(false); // Control del chat de nutrición
  
  // Training states
  const [trainingPlans, setTrainingPlans] = useState([]); // Array de planes de entrenamiento
  const [selectedTrainingPlan, setSelectedTrainingPlan] = useState(null); // Plan seleccionado
  const [editingTraining, setEditingTraining] = useState(false);
  const [trainingContent, setTrainingContent] = useState('');
  const [generatingTrainingPDF, setGeneratingTrainingPDF] = useState(false);
  const [sendingTraining, setSendingTraining] = useState(null);
  const [generatingTrainingPlan, setGeneratingTrainingPlan] = useState(false);
  const [generatingFromFollowup, setGeneratingFromFollowup] = useState(false);
  const [showTrainingModal, setShowTrainingModal] = useState(false);
  const [modalTrainingPlan, setModalTrainingPlan] = useState(null);
  const [showTrainingChat, setShowTrainingChat] = useState(false);
  
  // Selector states - Training
  const [availableQuestionnaires, setAvailableQuestionnaires] = useState([]);
  const [availableTrainingPlans, setAvailableTrainingPlans] = useState([]);
  const [selectedQuestionnaireForTraining, setSelectedQuestionnaireForTraining] = useState(null);
  const [selectedPreviousTrainingPlan, setSelectedPreviousTrainingPlan] = useState(null);
  
  // Selector states - Nutrition
  const [selectedQuestionnaireForNutrition, setSelectedQuestionnaireForNutrition] = useState(null);
  const [selectedTrainingPlanForNutrition, setSelectedTrainingPlanForNutrition] = useState(null);
  const [selectedPreviousNutritionPlan, setSelectedPreviousNutritionPlan] = useState(null);
  
  // Async Generation Job states
  const [currentJobId, setCurrentJobId] = useState(null);
  const [showGenerationProgress, setShowGenerationProgress] = useState(false);
  
  // EDN360 Input Preview - FASE 2
  const [showEDN360InputModal, setShowEDN360InputModal] = useState(false);
  const [edn360InputData, setEDN360InputData] = useState(null);
  const [loadingEDN360Input, setLoadingEDN360Input] = useState(false);
  
  // EDN360 Workflow Test - FASE 3
  const [launchingWorkflow, setLaunchingWorkflow] = useState(false);
  const [workflowResult, setWorkflowResult] = useState(null);
  const [showWorkflowResultModal, setShowWorkflowResultModal] = useState(false);
  
  // EDN360 Training Plan Generation - NEW FLOW
  const [generatingEDN360Plan, setGeneratingEDN360Plan] = useState(false);
  const [generatedEDN360Plan, setGeneratedEDN360Plan] = useState(null);
  
  // Follow-up Report states
  const [selectedPreviousTrainingForReport, setSelectedPreviousTrainingForReport] = useState(null);
  const [selectedNewTrainingForReport, setSelectedNewTrainingForReport] = useState(null);
  const [selectedPreviousNutritionForReport, setSelectedPreviousNutritionForReport] = useState(null);
  const [selectedNewNutritionForReport, setSelectedNewNutritionForReport] = useState(null);
  const [selectedFollowUpQuestionnaireForReport, setSelectedFollowUpQuestionnaireForReport] = useState(null);
  const [availableNutritionPlans, setAvailableNutritionPlans] = useState([]);
  const [followUpReports, setFollowUpReports] = useState([]);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [showReportModal, setShowReportModal] = useState(false);
  
  // Follow-up states
  const [followUps, setFollowUps] = useState([]); // Array de seguimientos
  const [selectedFollowUp, setSelectedFollowUp] = useState(null); // Seguimiento seleccionado
  const [followUpAnalysis, setFollowUpAnalysis] = useState(''); // Análisis del seguimiento
  const [editingAnalysis, setEditingAnalysis] = useState(false);
  const [generatingAnalysis, setGeneratingAnalysis] = useState(false);
  
  // Pending Reviews states
  const [pendingReviews, setPendingReviews] = useState([]); // Array de clientes con seguimientos pendientes
  const [loadingPendingReviews, setLoadingPendingReviews] = useState(false);
  
  // History modal state
  const [selectedHistoryItem, setSelectedHistoryItem] = useState(null);

  // Financial states
  const [financialMetrics, setFinancialMetrics] = useState(null);
  const [allPayments, setAllPayments] = useState([]);
  const [loadingFinancials, setLoadingFinancials] = useState(false);


  // Waitlist states
  const [waitlistLeads, setWaitlistLeads] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [loadingWaitlist, setLoadingWaitlist] = useState(false);
  const [waitlistCount, setWaitlistCount] = useState(0);
  const [newLeadNote, setNewLeadNote] = useState('');

  // Manual Payments (Caja A/B)
  const [manualPayments, setManualPayments] = useState([]);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [editingManualPayment, setEditingManualPayment] = useState(null);
  const [newManualPayment, setNewManualPayment] = useState({
    concepto: '',
    amount: '',
    fecha: new Date().toISOString().split('T')[0],
    metodo_pago: 'Transferencia',
    notas: ''
  });



  // Form states
  const [formData, setFormData] = useState({
    title: '',
    url: ''
  });

  const [alertData, setAlertData] = useState({
    title: '',
    message: '',
    link: ''
  });

  const [pdfData, setPdfData] = useState({
    title: '',
    type: 'training'
  });

  useEffect(() => {
    if (!isAdmin()) {
      navigate('/dashboard');
      return;
    }
    loadClients();
    loadTemplates();
    loadAllTags();
  }, [isAdmin, navigate]);

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


  // ==================== TRAINING PLAN FUNCTIONS ====================
  
  const loadTrainingPlans = async (userId) => {
    try {
      const response = await axios.get(`${API}/admin/users/${userId}/training`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setTrainingPlans(response.data.plans || []);
    } catch (error) {
      if (error.response?.status !== 404) {
        console.error('Error loading training plans:', error);
      }
      setTrainingPlans([]);
    }
  };

  // ============================================
  // EDN360 INPUT PREVIEW - FASE 2
  // ============================================
  
  const handleViewEDN360Input = async (userId) => {
    setLoadingEDN360Input(true);
    setShowEDN360InputModal(true);
    setEDN360InputData(null);
    
    try {
      const response = await axios.get(
        `${API}/admin/users/${userId}/edn360-input-preview`,
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      
      setEDN360InputData(response.data);
      console.log('✅ EDN360Input cargado:', response.data);
    } catch (error) {
      console.error('❌ Error cargando EDN360Input:', error);
      
      if (error.response?.status === 404) {
        alert(
          error.response?.data?.detail?.message || 
          'Este usuario no tiene client_drawer o no ha completado cuestionarios.'
        );
      } else {
        alert('Error al cargar EDN360Input. Ver consola para detalles.');
      }
      
      setShowEDN360InputModal(false);
    } finally {
      setLoadingEDN360Input(false);
    }
  };

  const handleLaunchWorkflow = async (userId, userName) => {
    // Confirmación
    const confirmed = window.confirm(
      `¿Seguro que quieres lanzar el Workflow EDN360 para ${userName}?\n\n` +
      'Esto creará un snapshot técnico en la BD, pero NO enviará ningún plan al cliente.\n\n' +
      'NOTA: Esto es solo para testing interno (FASE 3).'
    );
    
    if (!confirmed) return;
    
    setLaunchingWorkflow(true);
    
    try {
      const response = await axios.post(
        `${API}/admin/users/${userId}/edn360-run-workflow`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      
      console.log('✅ Workflow EDN360 ejecutado:', response.data);
      
      setWorkflowResult(response.data.result);
      setShowWorkflowResultModal(true);
      
      // Mostrar alerta con resultado
      const result = response.data.result;
      if (result.status === 'success') {
        alert(
          `✅ Workflow EDN360 ejecutado exitosamente!\n\n` +
          `Snapshot ID: ${result.snapshot_id}\n` +
          `Status: ${result.status}\n` +
          `Workflow: ${result.workflow_name}`
        );
      } else {
        alert(
          `⚠️ Workflow EDN360 ejecutado pero falló\n\n` +
          `Snapshot ID: ${result.snapshot_id}\n` +
          `Status: ${result.status}\n` +
          `Error: ${result.error_message || 'Sin mensaje de error'}`
        );
      }
    } catch (error) {
      console.error('❌ Error lanzando Workflow EDN360:', error);
      
      let errorMessage = 'Error al lanzar Workflow EDN360.';
      
      if (error.response?.status === 404) {
        errorMessage = error.response?.data?.detail?.message || 'Usuario no encontrado.';
      } else if (error.response?.data?.detail?.message) {
        errorMessage = error.response.data.detail.message;
      }
      
      alert(`❌ ${errorMessage}\n\nVer consola para más detalles.`);
    } finally {
      setLaunchingWorkflow(false);
    }
  };

  const generateTrainingPlan = async (sourceType, sourceId) => {
    // Validate selectors
    if (!selectedQuestionnaireForTraining) {
      alert('❌ Por favor selecciona un cuestionario base');
      return;
    }
    
    // Auto-detect source type basándose en el cuestionario seleccionado
    let actualSourceType = sourceType;
    let actualSourceId = sourceId || selectedQuestionnaireForTraining;
    
    // Detectar tipo basándose en el cuestionario, NO en si hay plan previo
    if (!sourceType || sourceType === 'initial') {
      const selectedQ = availableQuestionnaires.find(q => q.id === actualSourceId);
      console.log('🔍 Cuestionario seleccionado:', selectedQ);
      if (selectedQ && selectedQ.type === 'followup') {
        actualSourceType = 'followup';
        console.log('✅ Detectado como followup');
      } else {
        actualSourceType = 'initial';
        console.log('✅ Detectado como initial');
      }
    }
    
    try {
      // Preparar payload para generación asíncrona
      const payload = {
        submission_id: actualSourceId,
        mode: 'training',
        previous_training_plan_id: selectedPreviousTrainingPlan || null
      };
      
      const response = await axios.post(
        `${API}/admin/users/${selectedClient.id}/plans/generate_async`,
        payload,
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      
      const { job_id } = response.data;
      setCurrentJobId(job_id);
      setShowGenerationProgress(true);
      
    } catch (error) {
      console.error('Error starting training plan generation:', error);
      alert('❌ Error al iniciar generación: ' + (error.response?.data?.detail || error.message));
    }
  };

  const generateNutritionPlan = async (submissionId, regenerate = false) => {
    // Validate selectors
    if (!selectedQuestionnaireForNutrition) {
      alert('❌ Por favor selecciona un cuestionario base');
      return;
    }
    
    try {
      // Preparar payload para generación asíncrona
      const payload = {
        submission_id: selectedQuestionnaireForNutrition,
        mode: 'nutrition',
        training_plan_id: selectedTrainingPlanForNutrition || null,
        previous_nutrition_plan_id: selectedPreviousNutritionPlan || null
      };
      
      const response = await axios.post(
        `${API}/admin/users/${selectedClient.id}/plans/generate_async`,
        payload,
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      
      const { job_id } = response.data;
      setCurrentJobId(job_id);
      setShowGenerationProgress(true);
      
    } catch (error) {
      console.error('Error starting nutrition plan generation:', error);
      alert('❌ Error al iniciar generación: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Callbacks para GenerationProgressModal
  const handleGenerationComplete = async (result) => {
    console.log('✅ Generación completada:', result);
    
    // Cerrar modal de progreso
    setShowGenerationProgress(false);
    setCurrentJobId(null);
    
    // Recargar datos según lo que se generó
    if (result.training_plan_id) {
      await loadTrainingPlans(selectedClient.id);
      await loadTrainingPlansForSelector(selectedClient.id);
    }
    
    if (result.nutrition_plan_id) {
      await loadNutritionPlan(selectedClient.id);
      await loadNutritionPlansForSelector(selectedClient.id);
    }
    
    // Mostrar mensaje de éxito
    const messages = [];
    if (result.training_plan_id) messages.push('Plan de Entrenamiento');
    if (result.nutrition_plan_id) messages.push('Plan de Nutrición');
    
    alert(`✅ ${messages.join(' y ')} generado exitosamente!`);
  };

  const handleGenerationError = (error) => {
    console.error('❌ Error en generación:', error);
    
    setShowGenerationProgress(false);
    setCurrentJobId(null);
    
    alert(`❌ Error al generar plan: ${error}`);
  };

  const handleGenerationClose = () => {
    setShowGenerationProgress(false);

  // Generar ambos planes (Training + Nutrition) en un solo job
  const generateFullPlan = async () => {
    // Validate selectors
    if (!selectedQuestionnaireForTraining) {
      alert('❌ Por favor selecciona un cuestionario base');
      return;
    }
    
    try {
      // Preparar payload para generación completa (training + nutrition)
      const payload = {
        submission_id: selectedQuestionnaireForTraining,
        mode: 'full',
        previous_training_plan_id: selectedPreviousTrainingPlan || null,
        previous_nutrition_plan_id: selectedPreviousNutritionPlan || null
      };
      
      const response = await axios.post(
        `${API}/admin/users/${selectedClient.id}/plans/generate_async`,
        payload,
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      
      const { job_id } = response.data;
      setCurrentJobId(job_id);
      setShowGenerationProgress(true);
      
    } catch (error) {
      console.error('Error starting full plan generation:', error);
      alert('❌ Error al iniciar generación completa: ' + (error.response?.data?.detail || error.message));
    }
  };

    setCurrentJobId(null);
  };


  const openTrainingPlanModal = (plan) => {
    setModalTrainingPlan(plan);
    setTrainingContent(plan.plan_text || plan.plan_final);
    setShowTrainingModal(true);
  };

  const saveTrainingChanges = async () => {
    if (!modalTrainingPlan) return;
    
    try {
      await axios.patch(
        `${API}/admin/users/${selectedClient.id}/training/${modalTrainingPlan.id}`,
        { plan_final: trainingContent },
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      
      alert('✅ Plan de entrenamiento actualizado correctamente');
      setEditingTraining(false);
      await loadTrainingPlans(selectedClient.id);
      
      const updatedPlan = { ...modalTrainingPlan, plan_final: trainingContent, edited: true };
      setModalTrainingPlan(updatedPlan);
    } catch (error) {
      console.error('Error saving training plan:', error);
      alert('❌ Error al guardar cambios');
    }
  };

  const generateTrainingPDF = async (planId) => {
    setGeneratingTrainingPDF(true);
    try {
      await axios.post(
        `${API}/admin/users/${selectedClient.id}/training-pdf`,
        null,
        {
          params: { plan_id: planId },
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      
      alert('✅ PDF generado correctamente');
      await loadTrainingPlans(selectedClient.id);
      await loadClientDetails(selectedClient.id); // Reload PDFs list
      
      if (modalTrainingPlan && modalTrainingPlan.id === planId) {
        const response = await axios.get(`${API}/admin/users/${selectedClient.id}/training`, {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        });
        const updatedPlan = response.data.plans.find(p => p.id === planId);
        if (updatedPlan) {
          setModalTrainingPlan(updatedPlan);
        }
      }
    } catch (error) {
      console.error('Error generating PDF:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Error desconocido';
      alert('❌ Error al generar PDF: ' + (typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg)));
    } finally {
      setGeneratingTrainingPDF(false);
    }
  };

  const sendTrainingEmail = async (planId) => {
    setSendingTraining('email');
    try {
      await axios.post(
        `${API}/admin/users/${selectedClient.id}/training/send-email`,
        null,
        {
          params: { plan_id: planId },
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      
      alert('✅ Plan enviado por email correctamente');
      await loadTrainingPlans(selectedClient.id);
    } catch (error) {
      console.error('Error sending email:', error);
      alert('❌ Error al enviar email: ' + (error.response?.data?.detail || error.message));
    } finally {
      setSendingTraining(null);
    }
  };

  // FUNCIÓN DESHABILITADA - WhatsApp solo para follow-up
  // const sendTrainingWhatsApp = async (planId) => {
  //   setSendingTraining('whatsapp');
  //   try {
  //     const response = await axios.get(
  //       `${API}/admin/users/${selectedClient.id}/training/whatsapp-link`,
  //       {
  //         params: { plan_id: planId },
  //         headers: { Authorization: `Bearer ${token}` },
  //         withCredentials: true
  //       }
  //     );
  //     
  //     window.open(response.data.whatsapp_link, '_blank');
  //     await loadTrainingPlans(selectedClient.id);
  //   } catch (error) {
  //     console.error('Error generating WhatsApp link:', error);
  //     alert('❌ Error al generar link: ' + (error.response?.data?.detail || error.message));
  //   } finally {
  //     setSendingTraining(null);
  //   }
  // };

  // Load questionnaires for selectors
  const loadQuestionnaires = async (userId) => {
    try {
      console.log('🔍 Loading questionnaires for user:', userId);
      
      // Cargar cuestionarios EDN360
      const edn360Response = await axios.get(`${API}/admin/users/${userId}/edn360-questionnaires`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      const edn360Questionnaires = edn360Response.data.questionnaires || [];
      console.log('📋 EDN360 questionnaires received:', edn360Questionnaires);
      
      // Formatear para el selector
      const formattedQuestionnaires = edn360Questionnaires.map((q, index) => {
        const isInitial = q.source === 'initial';
        const date = new Date(q.submitted_at).toLocaleDateString('es-ES', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric'
        });
        
        return {
          id: q.id,
          label: `${isInitial ? '📝 Inicial' : '🔄 Seguimiento'} - ${date}`,
          is_initial: isInitial,
          submitted_at: q.submitted_at
        };
      });
      
      console.log('📋 Formatted questionnaires:', formattedQuestionnaires);
      setAvailableQuestionnaires(formattedQuestionnaires);
      
      // Auto-seleccionar cuestionario inicial solo si no hay selección previa
      if (!selectedQuestionnaireForTraining && formattedQuestionnaires.length > 0) {
        const initial = formattedQuestionnaires.find(q => q.is_initial);
        if (initial) {
          console.log('✅ Auto-seleccionando cuestionario inicial:', initial.id);
          setSelectedQuestionnaireForTraining(initial.id);
        }
      }
    } catch (error) {
      console.error('❌ Error loading questionnaires:', error);
      console.error('❌ Error details:', error.response?.data);
      setAvailableQuestionnaires([]);
    }
  };

  // Load training plans for selectors
  const loadTrainingPlansForSelector = async (userId) => {
    try {
      const response = await axios.get(`${API}/admin/users/${userId}/training-plans`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      const plans = response.data.plans || [];
      setAvailableTrainingPlans(plans);
      
      // Set default to latest plan for nutrition only on first load
      if (plans.length > 0 && !selectedTrainingPlanForNutrition) {
        setSelectedTrainingPlanForNutrition(plans[0].id);
      }
    } catch (error) {
      console.error('Error loading training plans for selector:', error);
      setAvailableTrainingPlans([]);
    }
  };

  // Load nutrition plans for selectors
  const loadNutritionPlansForSelector = async (userId) => {
    try {
      const response = await axios.get(`${API}/admin/users/${userId}/nutrition-plans`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      const plans = response.data.plans || [];
      setAvailableNutritionPlans(plans);
    } catch (error) {
      console.error('Error loading nutrition plans for selector:', error);
      setAvailableNutritionPlans([]);
    }
  };

  // Generate EDN360 Training Plan - NEW FLOW
  const generateEDN360TrainingPlan = async (submissionId) => {
    if (!selectedClient) return;
    
    try {
      setGeneratingEDN360Plan(true);
      
      // Preparar el payload con cuestionario y plan previo (opcional)
      const payload = {
        user_id: selectedClient.id,
        questionnaire_submission_id: submissionId
      };
      
      // Agregar plan previo si está seleccionado
      if (selectedPreviousTrainingPlan && selectedPreviousTrainingPlan !== 'none') {
        payload.previous_training_plan_id = selectedPreviousTrainingPlan;
        console.log('📋 Usando plan previo:', selectedPreviousTrainingPlan);
      }
      
      console.log('🚀 Generando plan EDN360 con payload:', payload);
      
      const response = await axios.post(
        `${API}/training-plan`,
        payload,
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      
      // Guardar el plan generado
      setGeneratedEDN360Plan(response.data.client_training_program_enriched);
      
      alert('✅ Plan de entrenamiento generado exitosamente!');
      
    } catch (error) {
      console.error('Error generating EDN360 training plan:', error);
      const errorMsg = error.response?.data?.detail?.message || error.message;
      alert(`❌ Error generando plan: ${errorMsg}`);
    } finally {
      setGeneratingEDN360Plan(false);
    }
  };


  // Load follow-up reports
  const loadFollowUpReports = async (userId) => {
    try {
      const response = await axios.get(`${API}/admin/users/${userId}/follow-up-reports`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setFollowUpReports(response.data.reports || []);
    } catch (error) {
      console.error('Error loading follow-up reports:', error);
      setFollowUpReports([]);
    }
  };

  // Load follow-up questionnaires
  const loadFollowUpQuestionnaires = async (userId) => {
    try {
      const response = await axios.get(`${API}/admin/users/${userId}/follow-up-questionnaires`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setQuestionnaireSubmissions(response.data.questionnaires || []);
    } catch (error) {
      console.error('Error loading follow-up questionnaires:', error);
      setQuestionnaireSubmissions([]);
    }
  };

  // Delete questionnaire
  const deleteQuestionnaire = async (submissionId, type) => {
    if (!window.confirm('⚠️ ¿Estás seguro de eliminar este cuestionario? Esta acción no se puede deshacer.')) {
      return;
    }

    try {
      await axios.delete(`${API}/admin/questionnaires/${submissionId}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });

      alert('✅ Cuestionario eliminado exitosamente');
      
      // Recargar datos
      if (selectedClient) {
        await loadAllClientData(selectedClient.id);
      }
    } catch (error) {
      console.error('Error deleting questionnaire:', error);
      alert('❌ Error al eliminar: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Delete follow-up
  const deleteFollowUp = async (followupId) => {
    if (!window.confirm('⚠️ ¿Estás seguro de eliminar este seguimiento? Esta acción no se puede deshacer.')) {
      return;
    }

    try {
      await axios.delete(`${API}/admin/follow-ups/${followupId}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });

      alert('✅ Seguimiento eliminado exitosamente');
      
      // Recargar datos
      if (selectedClient) {
        await loadAllClientData(selectedClient.id);
      }
    } catch (error) {
      console.error('Error deleting follow-up:', error);
      alert('❌ Error al eliminar: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Generate follow-up report
  const generateFollowUpReport = async () => {
    if (!selectedPreviousTrainingForReport || !selectedNewTrainingForReport) {
      alert('❌ Debes seleccionar al menos los planes de entrenamiento (anterior y nuevo)');
      return;
    }

    if (!selectedFollowUpQuestionnaireForReport) {
      alert('❌ Debes seleccionar el cuestionario de seguimiento para análisis inteligente');
      return;
    }

    setGeneratingReport(true);
    try {
      const response = await axios.post(
        `${API}/admin/users/${selectedClient.id}/follow-up-report/generate`,
        {
          previous_training_id: selectedPreviousTrainingForReport,
          new_training_id: selectedNewTrainingForReport,
          previous_nutrition_id: selectedPreviousNutritionForReport || null,
          new_nutrition_id: selectedNewNutritionForReport || null,
          followup_questionnaire_id: selectedFollowUpQuestionnaireForReport
        },
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );

      alert('✅ Informe de seguimiento generado exitosamente!');
      await loadFollowUpReports(selectedClient.id);
    } catch (error) {
      console.error('Error generating follow-up report:', error);
      // Better error handling - show actual error message
      let errorMsg = 'Error desconocido';
      if (error.response?.data?.detail) {
        errorMsg = typeof error.response.data.detail === 'string' 
          ? error.response.data.detail 
          : JSON.stringify(error.response.data.detail);
      } else if (error.message) {
        errorMsg = error.message;
      }
      alert('❌ Error al generar informe: ' + errorMsg);
    } finally {
      setGeneratingReport(false);
    }
  };

  // Load all client data when client is selected
  const loadAllClientData = async (clientId) => {
    // Set loading state to prevent UI flickering
    setLoadingClientData(true);
    
    try {
      await loadClientDetails(clientId);
      await loadNutritionPlan(clientId);
      
      // Load training plans
      try {
        const trainingResponse = await axios.get(`${API}/admin/users/${clientId}/training`, {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        });
        setTrainingPlans(trainingResponse.data.plans || []);
      } catch (error) {
        if (error.response?.status !== 404) {
          console.error('Error loading training plans:', error);
        }
        setTrainingPlans([]);
      }
      
      // Load data for selectors
      await loadQuestionnaires(clientId);
      await loadTrainingPlansForSelector(clientId);
      await loadNutritionPlansForSelector(clientId);
      await loadFollowUpReports(clientId);
      await loadFollowUpQuestionnaires(clientId);
      
      // Now load follow-ups after other data is loaded
      try {
        const response = await axios.get(`${API}/admin/users/${clientId}/follow-ups`, {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        });
        setFollowUps(response.data.follow_ups || []);
      } catch (error) {
        console.error('Error loading follow-ups:', error);
        setFollowUps([]);
      }
      
      // Load EDN360 questionnaires ABSOLUTELY LAST to override any legacy data
      console.log('🔥 [FINAL STEP] Loading EDN360 questionnaires...');
      const edn360Data = await loadEDN360Questionnaires(clientId);
      console.log('🔥 [FINAL STEP] EDN360 questionnaires loaded:', edn360Data.length);
      
    } finally {
      // Clear loading state
      setLoadingClientData(false);
    }
  };

  useEffect(() => {
    if (selectedClient) {
      loadAllClientData(selectedClient.id);
    } else {
      // Clear loading state if no client selected
      setLoadingClientData(false);
    }
  }, [selectedClient?.id]); // Only re-run when the client ID changes, not the whole object

  // Delete follow-up report
  const deleteFollowUpReport = async (reportId) => {
    if (!window.confirm('¿Estás seguro de que quieres eliminar este informe?')) {
      return;
    }

    try {
      await axios.delete(
        `${API}/admin/users/${selectedClient.id}/follow-up-reports/${reportId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );

      alert('✅ Informe eliminado exitosamente');
      await loadFollowUpReports(selectedClient.id);
      setShowReportModal(false);
      setSelectedReport(null);
    } catch (error) {
      console.error('Error deleting report:', error);
      alert('❌ Error al eliminar informe: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Update follow-up report
  const updateFollowUpReport = async (reportId, reportText) => {
    try {
      await axios.patch(
        `${API}/admin/users/${selectedClient.id}/follow-up-reports/${reportId}`,
        { report_text: reportText },
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );

      alert('✅ Informe actualizado exitosamente');
      await loadFollowUpReports(selectedClient.id);
      
      // Actualizar el report seleccionado
      setSelectedReport({ ...selectedReport, report_text: reportText });
    } catch (error) {
      console.error('Error updating report:', error);
      alert('❌ Error al actualizar informe: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Manual Payments Functions (MUST be before useEffect)
  const loadManualPayments = async () => {
    try {
      const response = await axios.get(`${API}/admin/manual-payments`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setManualPayments(response.data.payments || []);
    } catch (error) {
      console.error('Error loading manual payments:', error);
    }
  };

  const createManualPayment = async () => {
    if (!newManualPayment.concepto || !newManualPayment.amount || !newManualPayment.metodo_pago) {
      alert('Completa concepto, monto y método de pago');
      return;
    }

    try {
      await axios.post(`${API}/admin/manual-payments`, newManualPayment, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNewManualPayment({
        concepto: '',
        amount: '',
        fecha: new Date().toISOString().split('T')[0],
        metodo_pago: 'Transferencia',
        notas: ''
      });
      setShowPaymentModal(false);
      loadManualPayments();
      alert('✅ Pago registrado correctamente');
    } catch (error) {
      alert('Error al registrar pago');
    }
  };

  const updateManualPayment = async () => {
    if (!editingManualPayment.concepto || !editingManualPayment.amount || !editingManualPayment.metodo_pago) {
      alert('Completa todos los campos');
      return;
    }

    try {
      await axios.put(
        `${API}/admin/manual-payments/${editingManualPayment._id}`,
        editingManualPayment,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setEditingManualPayment(null);
      loadManualPayments();
      alert('✅ Pago actualizado');
    } catch (error) {
      alert('Error al actualizar pago');
    }
  };

  const deleteManualPayment = async (paymentId) => {
    if (!window.confirm('¿Eliminar este pago?')) return;

    try {
      await axios.delete(`${API}/admin/manual-payments/${paymentId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      loadManualPayments();
      alert('✅ Pago eliminado');
    } catch (error) {
      alert('Error al eliminar pago');
    }
  };

  useEffect(() => {
    // Load pending reviews when navigating to that view
    if (activeView === 'pending-reviews') {
      const fetchPendingReviews = async () => {
        setLoadingPendingReviews(true);
        try {
          const response = await axios.get(`${API}/admin/pending-reviews`, {
            headers: { Authorization: `Bearer ${token}` },
            withCredentials: true
          });
          setPendingReviews(response.data.pending_reviews || []);
        } catch (error) {
          console.error('Error loading pending reviews:', error);
          setPendingReviews([]);
        } finally {
          setLoadingPendingReviews(false);
        }
      };
      fetchPendingReviews();
    }
  }, [activeView, token]);


  useEffect(() => {
    // Load financial data when navigating to finances view
    if (activeView === 'finances') {
      loadFinancialMetrics();
      loadAllPayments();
    }
  }, [activeView, token]);


  useEffect(() => {
    // Load waitlist data when navigating to waitlist view
    if (activeView === 'waitlist') {
      loadWaitlistLeads();
    }
    // Load manual payments when navigating to finances
    if (activeView === 'finances') {
      loadManualPayments();
    }
  }, [activeView, token]);



  const loadClients = async () => {
    try {
      // Use clients endpoint to show web-registered clients
      const response = await axios.get(`${API}/admin/clients`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        withCredentials: true
      });
      setClients(response.data.clients || []);
      // Use stats from backend
      setStats(response.data.stats || { total: 0, active: 0, pending: 0 });
      setLoading(false);
    } catch (error) {
      console.error('Error loading clients:', error);
      setLoading(false);
    }
  };

  const loadClientDetails = async (userId) => {
    try {
      const response = await axios.get(`${API}/admin/clients/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        withCredentials: true
      });
      setSelectedClientDetails(response.data);
      // Update selectedClient with complete data from backend
      setSelectedClient(response.data.user);
    } catch (error) {
      console.error('❌ Error loading client details:', error);
      console.error('Error details:', error.response?.data || error.message);
      setSelectedClientDetails({ user: selectedClient, forms: [], pdfs: [], alerts: [] });
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await axios.get(`${API}/admin/templates`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setTemplates(response.data.templates || []);
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  // Load nutrition plans (historial) y questionnaire submissions
  const loadNutritionPlan = async (userId) => {
    try {
      const response = await axios.get(`${API}/admin/users/${userId}/nutrition`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setNutritionPlans(response.data.plans || []);
      setQuestionnaireSubmissions(response.data.questionnaire_submissions || []);
      // REMOVED: setSelectedPlan(null) - esto causaba que el acordeón se cerrara inmediatamente
      // El acordeón ahora mantiene su estado al recargar datos
    } catch (error) {
      if (error.response?.status !== 404) {
        console.error('Error loading nutrition plan:', error);
      }
      setNutritionPlans([]);
      setQuestionnaireSubmissions([]);
      // REMOVED: setSelectedPlan(null) - dejar que el usuario controle el estado del acordeón
    }
  };


  // Load EDN360 questionnaires from client_drawers
  const loadEDN360Questionnaires = async (userId) => {
    try {
      console.log('🔄 [EDN360] Loading questionnaires for user:', userId);
      const response = await axios.get(`${API}/admin/users/${userId}/edn360-questionnaires`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      const edn360Questionnaires = response.data.questionnaires || [];
      console.log('📦 [EDN360] Response received:', edn360Questionnaires);
      
      // Usar el estado SEPARADO para EDN360
      setEdn360QuestionnaireSubmissions(edn360Questionnaires);
      console.log('✅ [EDN360] edn360QuestionnaireSubmissions updated, count:', edn360Questionnaires.length);
      
      return edn360Questionnaires;
    } catch (error) {
      console.error('❌ [EDN360] Error loading questionnaires:', error);
      setEdn360QuestionnaireSubmissions([]);
      return [];
    }
  };


  // Save nutrition plan changes
  const saveNutritionChanges = async () => {
    const planToUse = modalPlan || selectedPlan;
    if (!planToUse) return;

  // Load follow-up submissions
  const loadFollowUps = async (userId) => {
    try {
      const response = await axios.get(`${API}/admin/users/${userId}/follow-ups`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setFollowUps(response.data.follow_ups || []);
    } catch (error) {
      console.error('Error loading follow-ups:', error);
      setFollowUps([]);
    }
  };

  // ALL TRAINING FUNCTIONS MOVED UP - now defined before loadAllClientData


  // Activate follow-up for a client
  const activateFollowUpForClient = async (userId) => {
    try {
      await axios.post(`${API}/admin/users/${userId}/activate-followup`, {}, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      alert('✅ Cuestionario de seguimiento activado correctamente');
      
      // Reload pending reviews to update status
      setLoadingPendingReviews(true);
      try {
        const response = await axios.get(`${API}/admin/pending-reviews`, {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        });
        setPendingReviews(response.data.pending_reviews || []);
      } catch (error) {
        console.error('Error reloading pending reviews:', error);
      } finally {
        setLoadingPendingReviews(false);
      }
    } catch (error) {
      console.error('Error activating follow-up:', error);
      alert('❌ Error al activar cuestionario de seguimiento');
    }
  };

    
    try {
      await axios.patch(
        `${API}/admin/users/${selectedClient.id}/nutrition/${planToUse.id}`,
        { plan_content: nutritionContent },
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      alert('✅ Plan de nutrición actualizado');
      setEditingNutrition(false);
      // Actualizar modalPlan con el nuevo contenido
      if (modalPlan) {
        setModalPlan({...modalPlan, plan_verificado: nutritionContent});
      }
      loadNutritionPlan(selectedClient.id);
    } catch (error) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  // Generate PDF and upload to user documents
  const generateNutritionPDF = async () => {
    const planToUse = modalPlan || selectedPlan;
    if (!planToUse) {
      alert('No hay plan seleccionado');
      return;
    }
    
    if (!window.confirm('¿Generar PDF y subirlo a los documentos del usuario?')) {
      return;
    }

    setGeneratingPDF(true);
    try {
      const response = await axios.post(
        `${API}/admin/users/${selectedClient.id}/nutrition-pdf?plan_id=${planToUse.id}`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      alert('✅ PDF generado y subido a documentos del usuario');
      loadNutritionPlan(selectedClient.id);
      loadClientDetails(selectedClient.id);
    } catch (error) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setGeneratingPDF(false);
    }
  };


  // Generate plan with AI from questionnaire submission
  const generatePlanWithAI = async (submissionId, regenerate = false) => {
    if (!selectedClient) return;
    
    if (!regenerate && !confirm('¿Generar plan de nutrición con IA a partir de las respuestas del cuestionario?')) {
      return;
    }
    
    setGeneratingPlan(true);
    try {
      const response = await axios.post(
        `${API}/admin/users/${selectedClient.id}/nutrition/generate?submission_id=${submissionId}&regenerate=${regenerate}`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      
      alert('✅ Plan generado exitosamente con IA');
      // Recargar nutrition plans
      await loadNutritionPlan(selectedClient.id);
      // Seleccionar el nuevo plan
      setSelectedPlan(response.data.plan);
      setNutritionContent(response.data.plan.plan_verificado);
      // Cerrar vista de submission
      setSelectedSubmission(null);
    } catch (error) {
      alert(`Error generando plan: ${error.response?.data?.detail || error.message}`);
    } finally {
      setGeneratingPlan(false);
    }
  };

  // Create plan manually (without AI)
  const createManualPlan = async (submissionId) => {
    if (!selectedClient) return;
    
    // Marcar submission como procesada sin generar plan con IA
    // El admin escribirá el plan manualmente
    setSelectedSubmission(null);
    setEditingNutrition(true);
    setNutritionContent('# Plan de Nutrición Personalizado\n\n## Escribe aquí tu plan...\n\n');
  };



  // Abrir modal con plan seleccionado
  const openPlanModal = useCallback((plan) => {
    setModalPlan(plan); // Guardar plan en estado del modal
    setSelectedPlan(plan);
    setNutritionContent(plan.plan_text || plan.plan_verificado);  // Priorizar plan_text profesional
    setEditingNutrition(false);
    setShowNutritionModal(true);
  }, []);

  // Cerrar modal
  const closePlanModal = useCallback(() => {
    setShowNutritionModal(false);
    setEditingNutrition(false);
    setModalPlan(null);
    // No resetear selectedPlan aquí para mantener la referencia
  }, []);


  // Send nutrition plan by email
  const sendNutritionByEmail = async (userId) => {
    const planToUse = modalPlan || selectedPlan;
    if (!planToUse) {
      alert('No hay plan seleccionado');
      return;
    }
    
    if (!window.confirm('¿Enviar el plan de nutrición por email al cliente?')) {
      return;
    }

    setSendingNutrition('email');
    try {
      const response = await axios.post(
        `${API}/admin/users/${userId}/nutrition/send-email?plan_id=${planToUse.id}`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      alert('✅ Plan de nutrición enviado por email correctamente');
      // Recargar el plan para actualizar los estados
      await loadNutritionPlan(userId);
    } catch (error) {
      alert(`Error al enviar email: ${error.response?.data?.detail || error.message}`);
    } finally {
      setSendingNutrition(null);
    }
  };

  // Send nutrition plan by WhatsApp
  // FUNCIÓN DESHABILITADA - WhatsApp solo para follow-up
  // const sendNutritionByWhatsApp = async (userId) => {
  //   const planToUse = modalPlan || selectedPlan;
  //   if (!planToUse) {
  //     alert('No hay plan seleccionado');
  //     return;
  //   }
  //   
  //   setSendingNutrition('whatsapp');
  //   try {
  //     const response = await axios.get(
  //       `${API}/admin/users/${userId}/nutrition/whatsapp-link?plan_id=${planToUse.id}`,
  //       {
  //         headers: { Authorization: `Bearer ${token}` },
  //         withCredentials: true
  //       }
  //     );
  //     
  //     if (response.data.whatsapp_link) {
  //       window.open(response.data.whatsapp_link, '_blank');
  //       alert('✅ Link de WhatsApp generado. Se abrirá en una nueva ventana.');
  //       // Recargar el plan para actualizar los estados
  //       await loadNutritionPlan(userId);
  //     }
  //   } catch (error) {
  //     alert(`Error al generar link de WhatsApp: ${error.response?.data?.detail || error.message}`);
  //   } finally {
  //     setSendingNutrition(null);
  //   }
  // };

  const openTemplateModal = (template) => {
    if (!selectedClient) return;
    
    setSelectedTemplate(template);
    
    // Get client name from available fields
    const clientName = selectedClient.nombre || selectedClient.name || selectedClient.username || 'Cliente';
    
    // Replace variables in template
    let message = template.content;
    message = message.replace(/{nombre}/g, clientName);
    message = message.replace(/{hora}/g, 'HH:MM'); // Placeholder
    message = message.replace(/{fecha}/g, new Date().toLocaleDateString('es-ES'));
    
    setTemplateMessage(message);
    setShowTemplateModal(true);
  };

  const sendTemplateMessage = () => {
    // Copy to clipboard
    navigator.clipboard.writeText(templateMessage);
    alert('Mensaje copiado al portapapeles. Ahora puedes pegarlo en WhatsApp.');
    
    // Open WhatsApp if client has phone number
    if (selectedClient.whatsapp || selectedClient.email) {
      const phone = (selectedClient.whatsapp || '').replace(/[^0-9]/g, '');
      if (phone) {
        const whatsappUrl = `https://wa.me/${phone}?text=${encodeURIComponent(templateMessage)}`;
        window.open(whatsappUrl, '_blank');
      }
    }
    
    setShowTemplateModal(false);
  };

  const sendTemplateViaWhatsApp = () => {
    if (selectedClient.whatsapp || selectedClient.email) {
      const phone = (selectedClient.whatsapp || '').replace(/[^0-9]/g, '');
      if (phone) {
        const whatsappUrl = `https://wa.me/${phone}?text=${encodeURIComponent(templateMessage)}`;
        window.open(whatsappUrl, '_blank');
        setShowTemplateModal(false);
        alert('WhatsApp abierto con el mensaje');
      } else {
        alert('Este cliente no tiene número de WhatsApp configurado');
      }
    } else {
      alert('Este cliente no tiene número de WhatsApp configurado');
    }
  };

  const sendTemplateViaEmail = async () => {
    try {
      const emailPayload = {
        to_email: selectedClient.email,
        subject: selectedTemplate?.name || 'Mensaje de Jorge Calcerrada',
        message: templateMessage
      };

      await axios.post(`${API}/admin/send-email-template`, emailPayload, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });

      alert('✅ Email enviado correctamente a ' + selectedClient.email);
      setShowTemplateModal(false);
    } catch (error) {
      console.error('Error sending email:', error);
      alert('❌ Error al enviar email: ' + (error.response?.data?.detail || error.message));
    }
  };

  const sendTemplateAsAlert = async () => {
    try {
      const alertPayload = {
        user_id: selectedClient.id,
        title: selectedTemplate?.name || 'Mensaje',
        message: templateMessage,
        type: 'info',
        link: ''
      };

      await axios.post(`${API}/alerts/send`, alertPayload, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });

      alert('✅ Alerta enviada correctamente al cliente');
      setShowTemplateModal(false);
      if (selectedClient) {
        loadClientDetails(selectedClient.id);
      }
    } catch (error) {
      console.error('Error sending alert:', error);
      alert('❌ Error al enviar alerta: ' + (error.response?.data?.detail || error.message));
    }
  };

  const sendTemplateToChat = async () => {
    try {
      // Send message via internal chat
      const messagePayload = {
        user_id: selectedClient.id,
        message: templateMessage
      };

      await axios.post(`${API}/messages/send`, messagePayload, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });

      alert('✅ Mensaje enviado al chat interno');
      setShowTemplateModal(false);
    } catch (error) {
      console.error('Error sending chat message:', error);
      alert('❌ Error al enviar mensaje: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const filteredClients = clients.filter(client => {
    const matchesSearch = client.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      client.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      client.username?.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Show archived clients only when showArchived is true
    // Show non-archived clients (including those without archived field) when showArchived is false
    if (showArchived) {
      return matchesSearch && client.subscription?.archived === true;
    } else {
      return matchesSearch && client.subscription?.archived !== true;
    }
  });

  const handleSendForm = async () => {
    if (!selectedClient || !formData.title || !formData.url) {
      alert('Por favor completa todos los campos');
      return;
    }
    try {
      await axios.post(`${API}/forms/send`, {
        user_id: selectedClient.id,
        title: formData.title,
        url: formData.url
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      alert(`Formulario "${formData.title}" enviado a ${selectedClient.name}`);
      setFormData({ title: '', url: '' });
    } catch (error) {
      console.error('Error sending form:', error);
      alert('Error al enviar formulario');
    }
  };

  const handleSendAlert = async () => {
    if (!selectedClient || !alertData.title || !alertData.message) {
      alert('Por favor completa todos los campos');
      return;
    }
    try {
      await axios.post(`${API}/alerts/send`, {
        user_id: selectedClient.id,
        title: alertData.title,
        message: alertData.message,
        type: 'general',
        link: alertData.link
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      alert(`Alerta enviada a ${selectedClient.name}`);
      setAlertData({ title: '', message: '', link: '' });
    } catch (error) {
      console.error('Error sending alert:', error);
      alert('Error al enviar alerta');
    }
  };

  const handleUploadPDF = async () => {
    if (!selectedClient || !pdfData.title) {
      alert('Por favor completa todos los campos');
      return;
    }

    const fileInput = document.getElementById('pdf-file');
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
      alert('Por favor selecciona un archivo PDF');
      return;
    }

    const file = fileInput.files[0];
    
    // Verify it's a PDF
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Por favor selecciona un archivo PDF válido');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', selectedClient.id);
      formData.append('title', pdfData.title);
      formData.append('type', pdfData.type);

      await axios.post(`${API}/pdfs/upload`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      alert(`PDF "${pdfData.title}" subido correctamente para ${selectedClient.name}`);
      setPdfData({ title: '', type: 'training' });
      fileInput.value = ''; // Clear file input
      
      // Reload client details to show new PDF
      loadClientDetails(selectedClient.id);
    } catch (error) {
      console.error('Error uploading PDF:', error);
      alert('Error al subir el PDF: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleVerifyPayment = async (clientId) => {
    try {
      await axios.post(`${API}/admin/verify-payment/${clientId}`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      alert('Pago verificado - El cliente recibirá notificación');
      loadClients(); // Reload clients to update status
    } catch (error) {
      console.error('Error verifying payment:', error);
      alert('Error al verificar pago');
    }
  };

  const handleDownloadPDF = async (pdfId) => {
    try {
      const response = await axios.get(`${API}/pdfs/${pdfId}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        responseType: 'blob'
      });

      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Get filename from response headers or use default
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'document.pdf';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert('Error al descargar documento: ' + (error.response?.data?.detail || 'Error desconocido'));
    }
  };

  const handleDeletePDF = async (pdfId) => {
    if (!window.confirm('¿Estás seguro de eliminar este documento? Esta acción no se puede deshacer.')) {
      return;
    }

    try {
      await axios.delete(`${API}/pdfs/${pdfId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        withCredentials: true
      });

      alert('Documento eliminado correctamente');
      
      // Refresh client details
      if (selectedClient) {
        loadClientDetails(selectedClient.id);
      }
    } catch (error) {
      alert('Error al eliminar documento: ' + (error.response?.data?.detail || 'Error desconocido'));
    }
  };

  const handleDeleteClient = async (clientId, clientName) => {
    // Primera confirmación
    if (!window.confirm(`⚠️ ¿Eliminar PERMANENTEMENTE a ${clientName}?`)) {
      return;
    }
    
    // Segunda confirmación MÁS FUERTE
    const confirmText = prompt(
      `🚨 ADVERTENCIA FINAL\n\n` +
      `Estás a punto de ELIMINAR PERMANENTEMENTE:\n\n` +
      `👤 Usuario: ${clientName}\n` +
      `📊 Todos los planes de nutrición\n` +
      `📝 Todos los cuestionarios\n` +
      `📄 Todos los documentos y PDFs\n` +
      `💬 Todos los mensajes y alertas\n` +
      `📅 Todas las sesiones\n\n` +
      `⛔ ESTA ACCIÓN NO SE PUEDE DESHACER ⛔\n\n` +
      `Si estás seguro, escribe: ELIMINAR`
    );
    
    if (confirmText !== 'ELIMINAR') {
      alert('❌ Eliminación cancelada');
      return;
    }

    try {
      const response = await axios.delete(`${API}/admin/delete-client/${clientId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // Mostrar resumen de lo eliminado
      const deleted = response.data.deleted_data;
      alert(
        `✅ Cliente eliminado permanentemente\n\n` +
        `Datos eliminados:\n` +
        `- Planes de nutrición: ${deleted.nutrition_plans}\n` +
        `- Cuestionarios: ${deleted.questionnaire_submissions}\n` +
        `- Formularios: ${deleted.forms}\n` +
        `- PDFs: ${deleted.pdfs}\n` +
        `- Mensajes: ${deleted.messages}\n` +
        `- Alertas: ${deleted.alerts}\n` +
        `- Sesiones: ${deleted.sessions}`
      );
      
      setSelectedClient(null);
      loadClients();
    } catch (error) {
      console.error('Error eliminando cliente:', error);
      alert(`❌ Error al eliminar cliente: ${error.response?.data?.detail || error.message}`);
    }
  };

  // Archivar cliente
  const handleArchiveClient = async (clientId, clientName) => {
    if (!window.confirm(`¿Archivar a ${clientName}?\n\nEl cliente NO podrá acceder pero mantendrá todos sus datos.\nPodrás reactivarlo cuando quieras.`)) {
      return;
    }

    try {
      await axios.patch(`${API}/admin/archive-client/${clientId}`, {}, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      alert('✅ Cliente archivado correctamente');
      setSelectedClient(null);
      loadClients();
    } catch (error) {
      alert(`❌ Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  // Reactivar cliente archivado
  const handleUnarchiveClient = async (clientId, clientName) => {
    if (!window.confirm(`¿Reactivar a ${clientName}?\n\nEl cliente podrá acceder cuando realice el pago.`)) {
      return;
    }

    try {
      await axios.patch(`${API}/admin/unarchive-client/${clientId}`, {}, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      alert('✅ Cliente reactivado. Debe completar el pago para acceder.');
      loadClients();
    } catch (error) {
      alert(`❌ Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando...</p>
        </div>
      </div>
    );
  }


  // Financial Functions
  const loadFinancialMetrics = async () => {
    try {
      setLoadingFinancials(true);
      const response = await axios.get(`${API}/admin/financial-overview`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFinancialMetrics(response.data);
    } catch (error) {
      console.error('Error loading financial metrics:', error);
    } finally {
      setLoadingFinancials(false);
    }
  };

  const loadAllPayments = async () => {
    try {
      const response = await axios.get(`${API}/admin/all-payments`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAllPayments(response.data.payments || []);
    } catch (error) {
      console.error('Error loading payments:', error);
    }
  };


  const loadWaitlistLeads = async () => {
    setLoadingWaitlist(true);
    try {
      const response = await axios.get(`${API}/admin/waitlist/all`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setWaitlistLeads(response.data || []);
      setWaitlistCount(response.data?.length || 0);
    } catch (error) {
      console.error('Error loading waitlist leads:', error);
    } finally {
      setLoadingWaitlist(false);
    }
  };

  const updateLeadStatus = async (lead, newStatus) => {
    const leadId = lead._id || lead.id;
    try {
      await axios.put(
        `${API}/admin/waitlist/${leadId}/status`,
        { estado: newStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      loadWaitlistLeads(); // Reload list
      // Update selectedLead if it's open
      if (selectedLead && (selectedLead._id === leadId || selectedLead.id === leadId)) {
        const response = await axios.get(`${API}/admin/waitlist/${leadId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setSelectedLead(response.data);
      }
    } catch (error) {
      console.error('Error updating lead status:', error);
      alert('Error al actualizar estado');
    }
  };

  const addLeadNote = async (lead, nota) => {
    // Use _id if available (from detail view), otherwise use id (from list view)
    const leadId = lead._id || lead.id;
    
    try {
      await axios.post(
        `${API}/admin/waitlist/${leadId}/note`,
        { nota },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Reload detailed view
      const response = await axios.get(`${API}/admin/waitlist/${leadId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSelectedLead(response.data);
      setNewLeadNote(''); // Clear input after adding note
      alert('✅ Nota añadida correctamente');
    } catch (error) {
      console.error('Error adding note:', error);
      alert('Error al añadir nota: ' + (error.response?.data?.detail || error.message));
    }
  };

  const deleteLeadNote = async (lead, noteIndex) => {
    const leadId = lead._id || lead.id;
    
    if (!window.confirm('¿Eliminar esta nota?')) return;
    
    try {
      await axios.delete(
        `${API}/admin/waitlist/${leadId}/note/${noteIndex}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Reload detailed view
      const response = await axios.get(`${API}/admin/waitlist/${leadId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSelectedLead(response.data);
      alert('✅ Nota eliminada');
    } catch (error) {
      console.error('Error deleting note:', error);
      alert('Error al eliminar nota: ' + (error.response?.data?.detail || error.message));
    }
  };

  const deleteWaitlistLead = async (lead) => {
    const leadId = lead._id || lead.id;
    if (!window.confirm('¿Estás seguro de que deseas eliminar este lead?')) {
      return;
    }
    try {
      await axios.delete(`${API}/admin/waitlist/${leadId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSelectedLead(null);
      loadWaitlistLeads();
      setActiveView('waitlist');
    } catch (error) {
      console.error('Error deleting lead:', error);
      alert('Error al eliminar lead');
    }
  };



  const handleDeletePayment = async (transactionId) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar esta transacción?')) {
      return;
    }
    
    try {
      await axios.delete(`${API}/admin/payment/${transactionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('✅ Transacción eliminada exitosamente');
      
      // Recargar datos
      loadAllPayments();
      loadFinancialMetrics();
    } catch (error) {
      console.error('Error deleting payment:', error);
      alert('❌ Error al eliminar la transacción');
    }
  };

  const handleCleanupPendingPayments = async () => {
    const pendingCount = allPayments.filter(p => p.status === 'pending').length;
    
    if (!window.confirm(`¿Estás seguro de que deseas eliminar ${pendingCount} transacciones pendientes?`)) {
      return;
    }
    
    try {
      const response = await axios.delete(`${API}/admin/payments/cleanup`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert(`✅ ${response.data.deleted_count} transacciones eliminadas exitosamente`);
      
      // Recargar datos
      loadAllPayments();
      loadFinancialMetrics();
    } catch (error) {
      console.error('Error cleaning up payments:', error);
      alert('❌ Error al limpiar transacciones');
    }
  };


  const formatAmount = (amount, currency = 'EUR') => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: currency.toUpperCase()
    }).format(amount);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Panel de Administrador</h1>
            <p className="text-blue-100 mt-1">Gestión de clientes y contenido</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="font-semibold">{user?.name}</p>
              <p className="text-sm text-blue-100">Administrador</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleLogout}
              className="bg-white/10 border-white/20 text-white hover:bg-white/20"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Salir
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Clientes</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
                </div>
                <Users className="h-12 w-12 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Clientes Activos</p>
                  <p className="text-3xl font-bold text-green-600">{stats.active}</p>
                </div>
                <CheckCircle className="h-12 w-12 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Pagos Pendientes</p>
                  <p className="text-3xl font-bold text-orange-600">{stats.pending}</p>
                </div>
                <XCircle className="h-12 w-12 text-orange-500" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* CRM Navigation Cards */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow border-2 border-purple-200 hover:border-purple-400"
            onClick={() => setActiveView('pending-reviews')}
          >
            <CardContent className="pt-6 text-center">
              <div className="relative">
                <UtensilsCrossed className="h-12 w-12 text-purple-500 mx-auto mb-3" />
                {/* Add notification badge if there are pending reviews */}
                {pendingReviews.length > 0 && (
                  <div className="absolute -top-1 -right-1 bg-purple-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center font-bold">
                    {pendingReviews.length}
                  </div>
                )}
              </div>
              <h3 className="text-lg font-bold mb-2">📊 Revisiones Pendientes</h3>
              <p className="text-sm text-gray-600">Seguimientos mensuales</p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow border-2 border-purple-200 hover:border-purple-400"
            onClick={() => setActiveView('prospects')}
          >
            <CardContent className="pt-6 text-center">
              <Target className="h-12 w-12 text-purple-500 mx-auto mb-3" />
              <h3 className="text-lg font-bold mb-2">CRM Prospectos</h3>
              <p className="text-sm text-gray-600">Gestiona leads del cuestionario</p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow border-2 border-blue-200 hover:border-blue-400"
            onClick={() => setActiveView('team-clients')}
          >
            <CardContent className="pt-6 text-center">
              <Users className="h-12 w-12 text-blue-500 mx-auto mb-3" />
              <h3 className="text-lg font-bold mb-2">CRM Clientes Equipo</h3>
              <p className="text-sm text-gray-600">Clientes registrados en web</p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow border-2 border-orange-200 hover:border-orange-400"
            onClick={() => setActiveView('external-clients')}
          >
            <CardContent className="pt-6 text-center">
              <Target className="h-12 w-12 text-orange-500 mx-auto mb-3" />
              <h3 className="text-lg font-bold mb-2">CRM Clientes Externos</h3>
              <p className="text-sm text-gray-600">Clientes Harbiz (trabajo directo)</p>
            </CardContent>
          </Card>


          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow border-2 border-green-200 hover:border-green-400"
            onClick={() => setActiveView('finances')}
          >
            <CardContent className="pt-6 text-center">
              <CreditCard className="h-12 w-12 text-green-500 mx-auto mb-3" />
              <h3 className="text-lg font-bold mb-2">💰 Finanzas</h3>
              <p className="text-sm text-gray-600">Ingresos y suscripciones</p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow border-2 border-pink-200 hover:border-pink-400"
            onClick={() => setActiveView('waitlist')}
          >
            <CardContent className="pt-6 text-center">
              <div className="relative">
                <UserPlus className="h-12 w-12 text-pink-500 mx-auto mb-3" />
                {/* Add notification badge if there are waitlist leads */}
                {waitlistCount > 0 && (
                  <div className="absolute -top-1 -right-1 bg-pink-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center font-bold">
                    {waitlistCount}
                  </div>
                )}
              </div>
              <h3 className="text-lg font-bold mb-2">🎯 Waitlist</h3>
              <p className="text-sm text-gray-600">Lista de espera prioritaria</p>
            </CardContent>
          </Card>

        </div>

        {/* Conditional View Rendering */}
        {activeView === 'pending-reviews' && (
          <div>
            <Button 
              variant="outline" 
              className="mb-4"
              onClick={() => setActiveView('clients')}
            >
              ← Volver a Gestión de Clientes
            </Button>
            
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <UtensilsCrossed className="h-6 w-6" />
                  Revisiones Pendientes - Seguimientos Mensuales
                </CardTitle>
                <p className="text-sm text-gray-600 mt-2">
                  Clientes que han completado 30+ días desde su último plan de nutrición. 
                  Puedes activar el cuestionario de seguimiento manualmente o esperar que lo completen automáticamente.
                </p>
              </CardHeader>
              <CardContent>
                {loadingPendingReviews ? (
                  <div className="text-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2" />
                    <p className="text-gray-600">Cargando revisiones pendientes...</p>
                  </div>
                ) : pendingReviews.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <CheckCircle className="h-12 w-12 mx-auto mb-2 text-green-500" />
                    <p>No hay revisiones pendientes en este momento.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {pendingReviews.map((review) => (
                      <Card key={review.user_id} className="border-2">
                        <CardContent className="pt-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <h4 className="font-bold text-lg">{review.name}</h4>
                                {review.status === 'completed' && (
                                  <Badge className="bg-green-500">✅ Completado</Badge>
                                )}
                                {review.status === 'activated' && (
                                  <Badge className="bg-blue-500">⏳ Activado</Badge>
                                )}
                                {review.status === 'pending' && (
                                  <Badge className="bg-orange-500">⚠️ Pendiente</Badge>
                                )}
                              </div>
                              
                              <div className="text-sm text-gray-600 space-y-1">
                                <p>📧 Email: {review.email}</p>
                                {review.phone && <p>📱 Teléfono: {review.phone}</p>}
                                <p>📅 Último plan: {new Date(review.last_plan_date).toLocaleDateString('es-ES')}</p>
                                <p className="font-semibold text-purple-600">
                                  ⏱️ Hace {review.days_since_plan} días
                                </p>
                                {review.status_date && (
                                  <p className="text-xs text-gray-500">
                                    Última acción: {new Date(review.status_date).toLocaleDateString('es-ES')}
                                  </p>
                                )}
                              </div>
                            </div>
                            
                            <div className="flex flex-col gap-2 ml-4">
                              {review.status === 'completed' && review.last_followup_id && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => {
                                    // Navigate to client with follow-up
                                    const client = clients.find(c => c.id === review.user_id);
                                    if (client) {
                                      setSelectedClient(client);
                                      setActiveView('clients');
                                      // TODO: Auto-open followups tab
                                    }
                                  }}
                                >
                                  Ver Respuestas
                                </Button>
                              )}
                              
                              {review.status === 'pending' && !review.followup_activated && (
                                <Button
                                  size="sm"
                                  className="bg-purple-500 hover:bg-purple-600"
                                  onClick={() => activateFollowUpForClient(review.user_id)}
                                >
                                  🔔 Activar Cuestionario
                                </Button>
                              )}
                              
                              {review.status === 'activated' && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  disabled
                                >
                                  Esperando respuesta...
                                </Button>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {activeView === 'templates' && (
          <div>
            <Button 
              variant="outline" 
              className="mb-4"
              onClick={() => setActiveView('clients')}
            >
              ← Volver a Gestión de Clientes
            </Button>
            <TemplatesManager token={token} />
          </div>
        )}

        {activeView === 'prospects' && (
          <div>
            <Button 
              variant="outline" 
              className="mb-4"
              onClick={() => setActiveView('clients')}
            >
              ← Volver a Gestión de Clientes
            </Button>
            <ProspectsCRM token={token} />
          </div>
        )}

        {activeView === 'team-clients' && (
          <div>
            <Button 
              variant="outline" 
              className="mb-4"
              onClick={() => setActiveView('clients')}
            >
              ← Volver a Gestión de Clientes
            </Button>
            <TeamClientsCRM token={token} />
          </div>
        )}

        {activeView === 'external-clients' && (
          <div>
            <Button 
              variant="outline" 
              className="mb-4"
              onClick={() => setActiveView('clients')}
            >
              ← Volver a Gestión de Clientes
            </Button>
            <ExternalClientsCRM token={token} />
          </div>
        )}


        {activeView === 'waitlist' && (
          <div>
            <Button 
              variant="outline" 
              className="mb-4"
              onClick={() => setActiveView('clients')}
            >
              ← Volver a Gestión de Clientes
            </Button>
            
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <UserPlus className="h-6 w-6" />
                    Waitlist - Lista de Espera Prioritaria
                  </div>
                  <Badge className="bg-pink-100 text-pink-700 border-pink-300">
                    {waitlistCount} leads
                  </Badge>
                </CardTitle>
                <p className="text-sm text-gray-600 mt-2">
                  Leads capturados desde el formulario público de waitlist, ordenados por score y prioridad automática.
                </p>
              </CardHeader>
              <CardContent>
                {loadingWaitlist ? (
                  <div className="flex justify-center items-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin text-pink-500" />
                  </div>
                ) : waitlistLeads.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <UserPlus className="h-12 w-12 mx-auto mb-3 opacity-50" />
                    <p>No hay leads en la waitlist</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2 px-4">Nombre</th>
                          <th className="text-left py-2 px-4">Email</th>
                          <th className="text-left py-2 px-4">Score</th>
                          <th className="text-left py-2 px-4">Prioridad</th>
                          <th className="text-left py-2 px-4">Estado</th>
                          <th className="text-left py-2 px-4">Fecha</th>
                          <th className="text-left py-2 px-4">Acciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        {waitlistLeads.map((lead) => (
                          <tr key={lead.id} className="border-b hover:bg-gray-50">
                            <td className="py-3 px-4 font-medium">{lead.nombre_apellidos}</td>
                            <td className="py-3 px-4 text-sm text-gray-600">{lead.email}</td>
                            <td className="py-3 px-4">
                              <span className="font-bold text-lg">{lead.score_total}/100</span>
                            </td>
                            <td className="py-3 px-4">
                              <Badge className={
                                lead.prioridad === 'alta' ? 'bg-red-100 text-red-700 border-red-300' :
                                lead.prioridad === 'media' ? 'bg-yellow-100 text-yellow-700 border-yellow-300' :
                                'bg-gray-100 text-gray-700 border-gray-300'
                              }>
                                {lead.prioridad}
                              </Badge>
                            </td>
                            <td className="py-3 px-4">
                              <Badge className={
                                lead.estado === 'pendiente' ? 'bg-blue-100 text-blue-700 border-blue-300' :
                                lead.estado === 'contactado' ? 'bg-purple-100 text-purple-700 border-purple-300' :
                                lead.estado === 'aceptado' ? 'bg-green-100 text-green-700 border-green-300' :
                                'bg-gray-100 text-gray-700 border-gray-300'
                              }>
                                {lead.estado}
                              </Badge>
                            </td>
                            <td className="py-3 px-4 text-sm text-gray-600">
                              {new Date(lead.submitted_at).toLocaleDateString('es-ES')}
                            </td>
                            <td className="py-3 px-4">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={async () => {
                                  const response = await axios.get(`${API}/admin/waitlist/${lead.id}`, {
                                    headers: { Authorization: `Bearer ${token}` }
                                  });
                                  setSelectedLead(response.data);
                                }}
                              >
                                Ver detalles →
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Lead Detail Modal */}
            {selectedLead && (
              <Dialog open={!!selectedLead} onOpenChange={() => setSelectedLead(null)}>
                <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span>{selectedLead.nombre_apellidos}</span>
                        <Badge className={
                          selectedLead.prioridad === 'alta' ? 'bg-red-100 text-red-700 border-red-300' :
                          selectedLead.prioridad === 'media' ? 'bg-yellow-100 text-yellow-700 border-yellow-300' :
                          'bg-gray-100 text-gray-700 border-gray-300'
                        }>
                          {selectedLead.prioridad} - {selectedLead.score_total}/100
                        </Badge>
                      </div>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => deleteWaitlistLead(selectedLead)}
                      >
                        <Trash2 className="h-4 w-4 mr-1" />
                        Eliminar
                      </Button>
                    </DialogTitle>
                  </DialogHeader>

                  <div className="space-y-6">
                    {/* Contact Info */}
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <Label className="text-sm font-semibold text-gray-700">Email</Label>
                        <div className="flex items-center gap-2">
                          <p className="text-gray-900">{selectedLead.email}</p>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => window.location.href = `mailto:${selectedLead.email}`}
                            className="ml-auto"
                          >
                            <Mail className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <div>
                        <Label className="text-sm font-semibold text-gray-700">Teléfono</Label>
                        <div className="flex items-center gap-2">
                          <p className="text-gray-900">{selectedLead.telefono}</p>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              const phone = selectedLead.telefono.replace(/[^0-9]/g, '');
                              const message = `Hola ${selectedLead.nombre_apellidos.split(' ')[0]}, soy Jorge Calcerrada. He revisado tu solicitud para trabajar conmigo...`;
                              window.open(`https://wa.me/${phone}?text=${encodeURIComponent(message)}`, '_blank');
                            }}
                            className="ml-auto bg-green-50 hover:bg-green-100 text-green-600 border-green-200"
                          >
                            <MessageSquare className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <div>
                        <Label className="text-sm font-semibold text-gray-700">Edad</Label>
                        <p className="text-gray-900">{selectedLead.edad}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-semibold text-gray-700">Ciudad/País</Label>
                        <p className="text-gray-900">{selectedLead.ciudad_pais}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-semibold text-gray-700">Cómo conoció a Jorge</Label>
                        <p className="text-gray-900">{selectedLead.como_conociste}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-semibold text-gray-700">Fecha de envío</Label>
                        <p className="text-gray-900">{new Date(selectedLead.submitted_at).toLocaleString('es-ES')}</p>
                      </div>
                    </div>

                    {/* Scoring Breakdown */}
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-semibold mb-3">Desglose de Scoring</h4>
                      <div className="grid md:grid-cols-2 gap-3 text-sm">
                        <div className="flex justify-between">
                          <span>💰 Capacidad económica:</span>
                          <span className="font-bold">{selectedLead.score_capacidad_economica}/25</span>
                        </div>
                        <div className="flex justify-between">
                          <span>🎯 Objetivos y motivación:</span>
                          <span className="font-bold">{selectedLead.score_objetivos_motivacion}/25</span>
                        </div>
                        <div className="flex justify-between">
                          <span>💪 Experiencia y hábitos:</span>
                          <span className="font-bold">{selectedLead.score_experiencia_habitos}/15</span>
                        </div>
                        <div className="flex justify-between">
                          <span>⏰ Disponibilidad y compromiso:</span>
                          <span className="font-bold">{selectedLead.score_disponibilidad_compromiso}/20</span>
                        </div>
                        <div className="flex justify-between">
                          <span>🤝 Personalidad y afinidad:</span>
                          <span className="font-bold">{selectedLead.score_personalidad_afinidad}/10</span>
                        </div>
                        <div className="flex justify-between">
                          <span>📞 Disponibilidad entrevista:</span>
                          <span className="font-bold">{selectedLead.score_disponibilidad_entrevista}/5</span>
                        </div>
                      </div>
                    </div>

                    {/* Tags */}
                    <div>
                      <h4 className="font-semibold mb-2">Tags Automáticos</h4>
                      <div className="flex flex-wrap gap-2">
                        <Badge className="bg-blue-100 text-blue-700">Cap. Econ: {selectedLead.capacidad_economica}</Badge>
                        <Badge className="bg-green-100 text-green-700">Objetivo: {selectedLead.objetivo}</Badge>
                        <Badge className="bg-purple-100 text-purple-700">Motivación: {selectedLead.motivacion}</Badge>
                        <Badge className="bg-orange-100 text-orange-700">Experiencia: {selectedLead.nivel_experiencia}</Badge>
                        <Badge className="bg-pink-100 text-pink-700">Compromiso: {selectedLead.nivel_compromiso}</Badge>
                        <Badge className="bg-red-100 text-red-700">Urgencia: {selectedLead.urgencia}</Badge>
                        <Badge className="bg-indigo-100 text-indigo-700">Afinidad: {selectedLead.afinidad_estilo}</Badge>
                      </div>
                    </div>

                    {/* All Responses */}
                    <div>
                      <h4 className="font-semibold mb-3">Respuestas Completas</h4>
                      <div className="space-y-3 max-h-96 overflow-y-auto bg-gray-50 p-4 rounded-lg">
                        {Object.entries(selectedLead.responses || {}).map(([key, value]) => (
                          <div key={key} className="border-b pb-2">
                            <Label className="text-sm font-semibold text-gray-700">
                              {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </Label>
                            <p className="text-gray-900 text-sm mt-1">{value || 'N/A'}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Status Update */}
                    <div>
                      <Label className="font-semibold mb-2">Cambiar Estado</Label>
                      <div className="flex gap-2 mt-2">
                        <Button
                          size="sm"
                          variant={selectedLead.estado === 'pendiente' ? 'default' : 'outline'}
                          onClick={() => updateLeadStatus(selectedLead, 'pendiente')}
                        >
                          Pendiente
                        </Button>
                        <Button
                          size="sm"
                          variant={selectedLead.estado === 'contactado' ? 'default' : 'outline'}
                          onClick={() => updateLeadStatus(selectedLead, 'contactado')}
                        >
                          Contactado
                        </Button>
                        <Button
                          size="sm"
                          variant={selectedLead.estado === 'aceptado' ? 'default' : 'outline'}
                          onClick={() => updateLeadStatus(selectedLead, 'aceptado')}
                        >
                          Aceptado
                        </Button>
                        <Button
                          size="sm"
                          variant={selectedLead.estado === 'rechazado' ? 'default' : 'outline'}
                          onClick={() => updateLeadStatus(selectedLead, 'rechazado')}
                        >
                          Rechazado
                        </Button>
                      </div>
                    </div>

                    {/* Notes */}
                    <div>
                      <Label className="font-semibold mb-2">Notas del Admin</Label>
                      <div className="space-y-2 mb-3">
                        {(selectedLead.notas_admin || []).map((note, idx) => (
                          <div key={idx} className="bg-yellow-50 p-3 rounded border border-yellow-200 relative group">
                            <Button
                              size="sm"
                              variant="ghost"
                              className="absolute top-2 right-2 h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-100 hover:text-red-600"
                              onClick={() => deleteLeadNote(selectedLead, idx)}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                            <p className="text-sm text-gray-900 pr-8">{note.texto}</p>
                            <p className="text-xs text-gray-500 mt-1">
                              {new Date(note.fecha).toLocaleString('es-ES')}
                            </p>
                          </div>
                        ))}
                      </div>
                      <div className="flex gap-2">
                        <Input
                          placeholder="Añadir nota..."
                          value={newLeadNote}
                          onChange={(e) => setNewLeadNote(e.target.value)}
                          onKeyPress={(e) => {
                            if (e.key === 'Enter' && newLeadNote.trim()) {
                              addLeadNote(selectedLead, newLeadNote.trim());
                            }
                          }}
                        />
                        <Button
                          size="sm"
                          onClick={() => {
                            if (newLeadNote.trim()) {
                              addLeadNote(selectedLead, newLeadNote.trim());
                            }
                          }}
                          disabled={!newLeadNote.trim()}
                        >
                          <Send className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            )}
          </div>
        )}


        {(activeView === 'clients' || activeView === 'calendar' || activeView === 'finances') && (
          <Tabs value={activeView} onValueChange={setActiveView} className="space-y-6">
            <TabsList className="grid w-full max-w-5xl mx-auto grid-cols-4">
              <TabsTrigger value="clients">
                <Users className="h-4 w-4 mr-2" />
                <span className="hidden sm:inline">Gestión de Clientes</span>
                <span className="sm:hidden">Clientes</span>
              </TabsTrigger>
              <TabsTrigger value="templates">
                <MessageSquare className="h-4 w-4 mr-2" />
                Templates
              </TabsTrigger>
              <TabsTrigger value="calendar">
                <Calendar className="h-4 w-4 mr-2" />
                Calendario
              </TabsTrigger>
              <TabsTrigger value="finances">
                <CreditCard className="h-4 w-4 mr-2" />
                <span className="hidden sm:inline">Finanzas</span>
                <span className="sm:hidden">€</span>
              </TabsTrigger>
            </TabsList>

          {/* Clients Management Tab - RESTORED FULL FUNCTIONALITY */}
          <TabsContent value="clients">
            <div className="grid lg:grid-cols-3 gap-6">
              {/* Client List */}
              <Card className="lg:col-span-1">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Users className="h-5 w-5" />
                      Clientes Activos
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setShowArchived(!showArchived)}
                      className={showArchived ? "bg-orange-50 border-orange-300 text-orange-600" : ""}
                    >
                      {showArchived ? "Ver activos" : "Ver archivados"}
                    </Button>
                  </CardTitle>
                  <div className="relative mt-4">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Buscar cliente..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 max-h-[600px] overflow-y-auto">
                    {filteredClients.map((client) => (
                      <div
                        key={client.id}
                        onClick={() => setSelectedClient(client)}
                        className={`p-4 rounded-lg border cursor-pointer transition-all ${
                          selectedClient?.id === client.id
                            ? 'bg-blue-50 border-blue-300'
                            : 'hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex-1">
                            <p className="font-semibold text-gray-900">
                              {client.nombre || client.name || client.username || 'Sin nombre'}
                            </p>
                            {client.username && (
                              <p className="text-xs text-gray-500">@{client.username}</p>
                            )}
                          </div>
                          <Badge
                            className={
                              client.client_status === 'active'
                                ? 'bg-green-100 text-green-700'
                                : client.client_status === 'pending'
                                ? 'bg-orange-100 text-orange-700'
                                : 'bg-gray-100 text-gray-700'
                            }
                          >
                            {client.client_status === 'active' ? 'Activo' : client.client_status === 'pending' ? 'Pendiente' : 'Inactivo'}
                          </Badge>
                        </div>
                        
                        {/* Contact Info */}
                        <div className="space-y-1 mt-2">
                          <div className="flex items-center gap-2 text-xs text-gray-600">
                            <Mail className="h-3 w-3" />
                            <span className="truncate">{client.email}</span>
                          </div>
                          {client.whatsapp && (
                            <div className="flex items-center gap-2 text-xs text-gray-600">
                              <MessageSquare className="h-3 w-3" />
                              <span>{client.whatsapp}</span>
                            </div>
                          )}
                        </div>

                        {/* Registration Date */}
                        {client.created_at && (
                          <p className="text-xs text-gray-400 mt-2">
                            Desde: {new Date(client.created_at).toLocaleDateString('es-ES')}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Client Management */}
              <Card className="lg:col-span-2">
                {loadingClientData ? (
                  <CardContent className="pt-20 pb-20 text-center">
                    <div className="flex flex-col items-center justify-center gap-4">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                      <p className="text-gray-600">Cargando datos del cliente...</p>
                    </div>
                  </CardContent>
                ) : selectedClient ? (
                  <>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span>Gestión de {selectedClient.name}</span>
                          {selectedClient.status === 'archived' && (
                            <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-bold rounded-full">
                              📦 ARCHIVADO
                            </span>
                          )}
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setUserToEdit(selectedClient);
                              setShowEditModal(true);
                            }}
                          >
                            <Edit className="h-4 w-4 mr-2" />
                            Editar
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setShowChat(true)}
                          >
                            <MessageSquare className="h-4 w-4 mr-2" />
                            Chat
                          </Button>
                          
                          {/* BOTONES DE PRUEBA OCULTOS TEMPORALMENTE
                          <Button
                            size="sm"
                            variant="outline"
                            className="bg-purple-50 border-purple-300 text-purple-700 hover:bg-purple-100"
                            onClick={() => setShowTemplateSelector(true)}
                          >
                            <FileText className="h-4 w-4 mr-2" />
                            Templates
                          </Button>
                          
                          <Button
                            size="sm"
                            variant="outline"
                            className="bg-indigo-50 border-indigo-300 text-indigo-700 hover:bg-indigo-100"
                            onClick={() => handleViewEDN360Input(selectedClient.id)}
                          >
                            <FileText className="h-4 w-4 mr-2" />
                            Ver EDN360 Input
                          </Button>
                          
                          <Button
                            size="sm"
                            variant="outline"
                            className="bg-orange-50 border-orange-300 text-orange-700 hover:bg-orange-100"
                            onClick={() => handleLaunchWorkflow(selectedClient.id, selectedClient.name)}
                            disabled={launchingWorkflow}
                          >
                            {launchingWorkflow ? (
                              <>
                                <div className="h-4 w-4 mr-2 border-2 border-orange-600 border-t-transparent rounded-full animate-spin" />
                                Lanzando...
                              </>
                            ) : (
                              <>
                                <FileText className="h-4 w-4 mr-2" />
                                Lanzar EDN360 Workflow (TEST)
                              </>
                            )}
                          </Button>
                          FIN BOTONES DE PRUEBA */}
                          
                          {selectedClient.subscription?.payment_status === 'pending' && (
                            <Button
                              size="sm"
                              onClick={() => handleVerifyPayment(selectedClient.id)}
                              className="bg-green-500 hover:bg-green-600"
                            >
                              <CheckCircle className="h-4 w-4 mr-2" />
                              Verificar pago
                            </Button>
                          )}
                          
                          {/* Botones Archivar/Reactivar */}
                          {selectedClient.status === 'archived' ? (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleUnarchiveClient(selectedClient.id, selectedClient.name)}
                              className="border-green-300 text-green-600 hover:bg-green-50"
                            >
                              <CheckCircle className="h-4 w-4 mr-2" />
                              Reactivar
                            </Button>
                          ) : (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleArchiveClient(selectedClient.id, selectedClient.name)}
                              className="border-yellow-300 text-yellow-600 hover:bg-yellow-50"
                            >
                              📦 Archivar
                            </Button>
                          )}
                          
                          {/* Botón Eliminar */}
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDeleteClient(selectedClient.id, selectedClient.name)}
                            className="border-red-300 text-red-600 hover:bg-red-50"
                          >
                            🗑️ Eliminar
                          </Button>
                        </div>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Tabs defaultValue="data" className="space-y-4">
                        <div className="overflow-x-auto">
                          <TabsList className="flex w-full min-w-max gap-1">
                            <TabsTrigger value="data" className="whitespace-nowrap px-3">Datos</TabsTrigger>
                            <TabsTrigger value="forms" className="whitespace-nowrap px-3">Formularios</TabsTrigger>
                            <TabsTrigger value="pdfs" className="whitespace-nowrap px-3">PDFs</TabsTrigger>
                            <TabsTrigger value="nutrition" className="whitespace-nowrap px-3">🥗 Nutrición</TabsTrigger>
                            <TabsTrigger value="training" className="whitespace-nowrap px-3">🏋️ Entrenamiento</TabsTrigger>
                            <TabsTrigger value="followup" className="whitespace-nowrap px-3">📊 Seguimiento</TabsTrigger>
                            <TabsTrigger value="history" className="whitespace-nowrap px-3">📋 Historial</TabsTrigger>
                            <TabsTrigger value="alerts" className="whitespace-nowrap px-3">Alertas</TabsTrigger>
                            <TabsTrigger value="sessions" className="whitespace-nowrap px-3">Sesiones</TabsTrigger>
                          </TabsList>
                        </div>

                        {/* Data Tab */}
                        <TabsContent value="data" className="space-y-4">
                          <Card className="bg-gradient-to-br from-blue-50 to-white">
                            <CardHeader>
                              <CardTitle>Información del Cliente</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                              <div className="grid md:grid-cols-2 gap-4">
                                <div>
                                  <label className="text-sm font-semibold text-gray-700">ID</label>
                                  <p className="text-gray-900 bg-white p-2 rounded border">{selectedClient.id}</p>
                                </div>
                                <div>
                                  <label className="text-sm font-semibold text-gray-700">Nombre de usuario</label>
                                  <p className="text-gray-900 bg-white p-2 rounded border">{selectedClient.username}</p>
                                </div>
                                <div>
                                  <label className="text-sm font-semibold text-gray-700">Nombre completo</label>
                                  <p className="text-gray-900 bg-white p-2 rounded border">{selectedClient.name}</p>
                                </div>
                                <div>
                                  <label className="text-sm font-semibold text-gray-700">Email</label>
                                  <p className="text-gray-900 bg-white p-2 rounded border">{selectedClient.email}</p>
                                </div>
                                <div>
                                  <label className="text-sm font-semibold text-gray-700">Rol</label>
                                  <Badge className="bg-blue-100 text-blue-700">{selectedClient.role}</Badge>
                                </div>
                                <div>
                                  <label className="text-sm font-semibold text-gray-700">Fecha de registro</label>
                                  <p className="text-gray-900 bg-white p-2 rounded border">
                                    {new Date(selectedClient.created_at).toLocaleString('es-ES')}
                                  </p>
                                </div>
                              </div>

                              {/* Estado del Cliente */}
                              <div className="border-t pt-4 mt-4">
                                <h4 className="font-semibold text-lg mb-3">Estado del Cliente</h4>
                                <div className="flex gap-2 flex-wrap">
                                  <Button
                                    size="sm"
                                    onClick={async () => {
                                      try {
                                        await axios.patch(
                                          `${API}/admin/team-clients/${selectedClient.id}/status`,
                                          { status: 'active' },
                                          {
                                            headers: { Authorization: `Bearer ${token}` },
                                            withCredentials: true
                                          }
                                        );
                                        setSelectedClient({...selectedClient, client_status: 'active'});
                                        alert('✅ Cliente activado correctamente');
                                        loadClients();
                                      } catch (error) {
                                        alert(`❌ Error: ${error.response?.data?.detail || error.message}`);
                                      }
                                    }}
                                    disabled={selectedClient.client_status === 'active'}
                                    className="bg-green-600 hover:bg-green-700 disabled:opacity-50"
                                  >
                                    <UserCheck className="h-4 w-4 mr-2" />
                                    Activar Cliente
                                  </Button>
                                  
                                  <Button
                                    size="sm"
                                    onClick={async () => {
                                      try {
                                        await axios.patch(
                                          `${API}/admin/team-clients/${selectedClient.id}/status`,
                                          { status: 'inactive' },
                                          {
                                            headers: { Authorization: `Bearer ${token}` },
                                            withCredentials: true
                                          }
                                        );
                                        setSelectedClient({...selectedClient, client_status: 'inactive'});
                                        alert('✅ Cliente desactivado correctamente');
                                        loadClients();
                                      } catch (error) {
                                        alert(`❌ Error: ${error.response?.data?.detail || error.message}`);
                                      }
                                    }}
                                    disabled={selectedClient.client_status === 'inactive'}
                                    variant="outline"
                                    className="border-orange-300 text-orange-600 hover:bg-orange-50 disabled:opacity-50"
                                  >
                                    <XCircle className="h-4 w-4 mr-2" />
                                    Desactivar Cliente
                                  </Button>
                                  
                                  <Badge className={`ml-2 ${
                                    selectedClient.client_status === 'active' ? 'bg-green-100 text-green-700' :
                                    selectedClient.client_status === 'inactive' ? 'bg-orange-100 text-orange-700' :
                                    'bg-yellow-100 text-yellow-700'
                                  }`}>
                                    Estado actual: {selectedClient.client_status === 'active' ? 'Activo' : 
                                                    selectedClient.client_status === 'inactive' ? 'Inactivo' : 'Pendiente'}
                                  </Badge>
                                </div>
                              </div>

                              <div className="border-t pt-4 mt-4">
                                <h4 className="font-semibold text-lg mb-3">Suscripción</h4>
                                <div className="grid md:grid-cols-2 gap-4">
                                  <div>
                                    <label className="text-sm font-semibold text-gray-700">Plan</label>
                                    <p className="text-gray-900 bg-white p-2 rounded border">{selectedClient.subscription?.plan === 'team' ? 'Equipo' : 'Directo'}</p>
                                  </div>
                                  <div>
                                    <label className="text-sm font-semibold text-gray-700">Estado de Pago</label>
                                    <Badge className={
                                      selectedClient.subscription?.payment_status === 'verified'
                                        ? 'bg-green-100 text-green-700'
                                        : 'bg-orange-100 text-orange-700'
                                    }>
                                      {selectedClient.subscription?.payment_status === 'verified' ? 'Verificado' : 'Pendiente'}
                                    </Badge>
                                  </div>
                                  <div>
                                    <label className="text-sm font-semibold text-gray-700">Fecha de inicio</label>
                                    <p className="text-gray-900 bg-white p-2 rounded border">
                                      {new Date(selectedClient.subscription?.start_date).toLocaleDateString('es-ES')}
                                    </p>
                                  </div>
                                  <div>
                                    <label className="text-sm font-semibold text-gray-700">Archivado</label>
                                    <Badge className={
                                      selectedClient.subscription?.archived
                                        ? 'bg-orange-100 text-orange-700'
                                        : 'bg-green-100 text-green-700'
                                    }>
                                      {selectedClient.subscription?.archived ? 'Sí' : 'No'}
                                    </Badge>
                                  </div>
                                  {selectedClient.subscription?.archived && selectedClient.subscription?.archived_reason && (
                                    <div className="md:col-span-2">
                                      <label className="text-sm font-semibold text-gray-700">Razón de archivado</label>
                                      <p className="text-gray-900 bg-white p-2 rounded border">{selectedClient.subscription.archived_reason}</p>
                                    </div>
                                  )}
                                </div>
                              </div>

                              <div className="border-t pt-4 mt-4">
                                <h4 className="font-semibold text-lg mb-3">Acciones de Seguridad</h4>
                                <SendPasswordResetButton 
                                  userId={selectedClient.id} 
                                  userName={selectedClient.name} 
                                />
                              </div>

                              <div className="border-t pt-4 mt-4">
                                <h4 className="font-semibold text-lg mb-3">Estadísticas</h4>
                                <div className="grid md:grid-cols-3 gap-4">
                                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                                    <p className="text-2xl font-bold text-blue-600">{selectedClientDetails?.forms?.length || 0}</p>
                                    <p className="text-sm text-gray-600">Formularios</p>
                                  </div>
                                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                                    <p className="text-2xl font-bold text-orange-600">{selectedClientDetails?.pdfs?.length || 0}</p>
                                    <p className="text-sm text-gray-600">Documentos</p>
                                  </div>
                                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                                    <p className="text-2xl font-bold text-purple-600">{selectedClientDetails?.alerts?.length || 0}</p>
                                    <p className="text-sm text-gray-600">Alertas</p>
                                  </div>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </TabsContent>

                        {/* Forms Tab */}
                        <TabsContent value="forms" className="space-y-4">
                          {/* Cuestionario de Seguimiento Mensual */}
                          <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg border-2 border-purple-300">
                            <h3 className="font-semibold mb-3 flex items-center gap-2">
                              📊 Cuestionario de Seguimiento Mensual
                            </h3>
                            <p className="text-sm text-gray-700 mb-3">
                              Envía el cuestionario de seguimiento al cliente. Podrás analizar sus respuestas y generar un nuevo plan.
                            </p>
                            
                            {/* Control Manual del Botón */}
                            <div className="mb-4 p-3 bg-white rounded-lg border border-purple-200">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-semibold">Control del botón en panel del cliente:</span>
                                <Badge className={selectedClient.followup_activated ? 'bg-green-500' : 'bg-gray-400'}>
                                  {selectedClient.followup_activated ? '🟢 Activado' : '⚫ Desactivado'}
                                </Badge>
                              </div>
                              <div className="flex gap-2">
                                <Button
                                  size="sm"
                                  onClick={async () => {
                                    try {
                                      await axios.post(
                                        `${API}/admin/users/${selectedClient.id}/activate-followup`,
                                        {},
                                        {
                                          headers: { Authorization: `Bearer ${token}` },
                                          withCredentials: true
                                        }
                                      );
                                      setSelectedClient({...selectedClient, followup_activated: true});
                                      alert('✅ Botón de seguimiento ACTIVADO en el panel del cliente');
                                      loadClients();
                                    } catch (error) {
                                      alert(`❌ Error: ${error.response?.data?.detail || error.message}`);
                                    }
                                  }}
                                  disabled={selectedClient.followup_activated}
                                  className="flex-1 bg-green-600 hover:bg-green-700 disabled:opacity-50"
                                >
                                  <CheckCircle className="h-4 w-4 mr-2" />
                                  Activar Botón
                                </Button>
                                <Button
                                  size="sm"
                                  onClick={async () => {
                                    try {
                                      await axios.post(
                                        `${API}/admin/users/${selectedClient.id}/deactivate-followup`,
                                        {},
                                        {
                                          headers: { Authorization: `Bearer ${token}` },
                                          withCredentials: true
                                        }
                                      );
                                      setSelectedClient({...selectedClient, followup_activated: false});
                                      alert('✅ Botón de seguimiento DESACTIVADO en el panel del cliente');
                                      loadClients();
                                    } catch (error) {
                                      alert(`❌ Error: ${error.response?.data?.detail || error.message}`);
                                    }
                                  }}
                                  disabled={!selectedClient.followup_activated}
                                  variant="outline"
                                  className="flex-1 border-red-300 text-red-600 hover:bg-red-50 disabled:opacity-50"
                                >
                                  <XCircle className="h-4 w-4 mr-2" />
                                  Desactivar Botón
                                </Button>
                              </div>
                              <p className="text-xs text-gray-600 mt-2">
                                {selectedClient.followup_activated 
                                  ? '✓ El cliente puede ver y completar el cuestionario en su panel'
                                  : '✗ El cliente NO verá el botón (solo se mostrará si tiene plan >= 30 días)'}
                              </p>
                            </div>
                            
                            <div className="grid grid-cols-2 gap-2">
                              <Button
                                onClick={() => {
                                  const message = `Hola ${selectedClient.name}! 👋\n\nEs momento de hacer tu seguimiento mensual. Por favor completa este cuestionario para evaluar tu progreso:\n\n${window.location.origin}/dashboard\n\n¡Gracias! 💪`;
                                  const whatsappUrl = `https://wa.me/${selectedClient.phone?.replace(/\D/g, '')}?text=${encodeURIComponent(message)}`;
                                  window.open(whatsappUrl, '_blank');
                                }}
                                className="bg-green-600 hover:bg-green-700"
                              >
                                <MessageSquare className="h-4 w-4 mr-2" />
                                WhatsApp
                              </Button>
                              <Button
                                onClick={() => {
                                  navigator.clipboard.writeText(`${window.location.origin}/dashboard`);
                                  alert('✅ Link copiado al portapapeles');
                                }}
                                variant="outline"
                                className="border-purple-300"
                              >
                                <Copy className="h-4 w-4 mr-2" />
                                Copiar Link
                              </Button>
                            </div>
                          </div>

                          <div className="bg-blue-50 p-4 rounded-lg">
                            <h3 className="font-semibold mb-3 flex items-center gap-2">
                              <Send className="h-5 w-5" />
                              Enviar otro formulario
                            </h3>
                            <div className="space-y-3">
                              <div>
                                <Label htmlFor="form-title">Título del formulario</Label>
                                <Input
                                  id="form-title"
                                  placeholder="Ej: Cuestionario personalizado"
                                  value={formData.title}
                                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                />
                              </div>
                              <div>
                                <Label htmlFor="form-url">URL del formulario</Label>
                                <Input
                                  id="form-url"
                                  placeholder="https://forms.gle/..."
                                  value={formData.url}
                                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                                />
                              </div>
                              <Button onClick={handleSendForm} className="w-full">
                                <Send className="h-4 w-4 mr-2" />
                                Enviar formulario
                              </Button>
                            </div>
                          </div>

                          <div>
                            <h4 className="font-semibold mb-3">Formularios enviados</h4>
                            {selectedClientDetails?.forms?.length > 0 ? (
                              <div className="space-y-2">
                                {selectedClientDetails.forms.map((form) => (
                                  <div key={form.id} className="p-3 bg-gray-50 rounded-lg flex items-center justify-between">
                                    <div>
                                      <p className="font-medium">{form.title}</p>
                                      <p className="text-sm text-gray-600">Enviado: {new Date(form.sent_date).toLocaleDateString('es-ES')}</p>
                                    </div>
                                    <Badge className={form.completed ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'}>
                                      {form.completed ? 'Completado' : 'Pendiente'}
                                    </Badge>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <p className="text-gray-500 text-center py-4">No hay formularios enviados</p>
                            )}
                          </div>
                        </TabsContent>

                        {/* PDFs Tab */}
                        <TabsContent value="pdfs" className="space-y-4">
                          <div className="bg-orange-50 p-4 rounded-lg">
                            <h3 className="font-semibold mb-3 flex items-center gap-2">
                              <Upload className="h-5 w-5" />
                              Subir nuevo documento
                            </h3>
                            <div className="space-y-3">
                              <div>
                                <Label htmlFor="pdf-title">Título del documento</Label>
                                <Input
                                  id="pdf-title"
                                  placeholder="Ej: Plan de Entrenamiento - Semana 1-4"
                                  value={pdfData.title}
                                  onChange={(e) => setPdfData({ ...pdfData, title: e.target.value })}
                                />
                              </div>
                              <div>
                                <Label htmlFor="pdf-type">Tipo</Label>
                                <select
                                  id="pdf-type"
                                  className="w-full px-3 py-2 border rounded-md"
                                  value={pdfData.type}
                                  onChange={(e) => setPdfData({ ...pdfData, type: e.target.value })}
                                >
                                  <option value="training">Entrenamiento</option>
                                  <option value="nutrition">Nutrición</option>
                                </select>
                              </div>
                              <div>
                                <Label htmlFor="pdf-file">Archivo PDF</Label>
                                <Input id="pdf-file" type="file" accept=".pdf" />
                              </div>
                              <Button onClick={handleUploadPDF} className="w-full">
                                <Upload className="h-4 w-4 mr-2" />
                                Subir documento
                              </Button>
                            </div>
                          </div>

                          <div>
                            <h4 className="font-semibold mb-3 flex items-center gap-2">
                              <FileText className="h-5 w-5 text-blue-500" />
                              Documentos Enviados (por ti)
                            </h4>
                            {selectedClientDetails?.pdfs?.filter(pdf => pdf.uploaded_by === 'admin').length > 0 ? (
                              <div className="grid md:grid-cols-2 gap-3">
                                {selectedClientDetails.pdfs.filter(pdf => pdf.uploaded_by === 'admin').map((pdf) => (
                                  <div key={pdf.id} className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                                    <div className="flex items-start justify-between mb-2">
                                      <p className="font-medium text-sm">{pdf.title}</p>
                                      <Badge className={pdf.type === 'training' ? 'bg-blue-100 text-blue-700' : 'bg-orange-100 text-orange-700'}>
                                        {pdf.type === 'training' ? 'Entrenamiento' : 'Nutrición'}
                                      </Badge>
                                    </div>
                                    <p className="text-xs text-gray-600 mb-2">
                                      Subido: {pdf.upload_date ? new Date(pdf.upload_date).toLocaleDateString('es-ES') : 'Fecha no disponible'}
                                    </p>
                                    <div className="flex gap-2">
                                      <Button
                                        size="sm"
                                        variant="outline"
                                        className="flex-1"
                                        onClick={() => handleDownloadPDF(pdf.id)}
                                      >
                                        <Download className="h-4 w-4 mr-2" />
                                        Descargar
                                      </Button>
                                      <Button
                                        size="sm"
                                        variant="outline"
                                        className="border-red-200 text-red-600 hover:bg-red-50"
                                        onClick={() => handleDeletePDF(pdf.id)}
                                      >
                                        <Trash2 className="h-4 w-4" />
                                      </Button>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <p className="text-gray-500 text-center py-4 bg-gray-50 rounded-lg">No has enviado documentos aún</p>
                            )}
                          </div>

                          <div>
                            <h4 className="font-semibold mb-3 flex items-center gap-2">
                              <FileText className="h-5 w-5 text-green-500" />
                              Documentos Recibidos (del cliente)
                            </h4>
                            {selectedClientDetails?.pdfs?.filter(pdf => pdf.uploaded_by === 'user').length > 0 ? (
                              <div className="grid md:grid-cols-2 gap-3">
                                {selectedClientDetails.pdfs.filter(pdf => pdf.uploaded_by === 'user').map((pdf) => (
                                  <div key={pdf.id} className="p-3 bg-green-50 border border-green-200 rounded-lg">
                                    <div className="flex items-start justify-between mb-2">
                                      <p className="font-medium text-sm">{pdf.title}</p>
                                      <Badge className="bg-green-100 text-green-700">
                                        {pdf.type || 'General'}
                                      </Badge>
                                    </div>
                                    <p className="text-xs text-gray-600 mb-2">
                                      Recibido: {pdf.upload_date ? new Date(pdf.upload_date).toLocaleDateString('es-ES') : 'Fecha no disponible'}
                                    </p>
                                    <div className="flex gap-2">
                                      <Button
                                        size="sm"
                                        variant="outline"
                                        className="flex-1"
                                        onClick={() => handleDownloadPDF(pdf.id)}
                                      >
                                        <Download className="h-4 w-4 mr-2" />
                                        Descargar
                                      </Button>
                                      <Button
                                        size="sm"
                                        variant="outline"
                                        className="border-red-200 text-red-600 hover:bg-red-50"
                                        onClick={() => handleDeletePDF(pdf.id)}
                                      >
                                        <Trash2 className="h-4 w-4" />
                                      </Button>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <p className="text-gray-500 text-center py-4 bg-gray-50 rounded-lg">El cliente no ha enviado documentos aún</p>
                            )}
                          </div>
                        </TabsContent>

                        {/* Alerts Tab */}
                        <TabsContent value="alerts" className="space-y-4">
                          <div className="bg-purple-50 p-4 rounded-lg">
                            <h3 className="font-semibold mb-3 flex items-center gap-2">
                              <Bell className="h-5 w-5" />
                              Enviar nueva alerta
                            </h3>
                            <div className="space-y-3">
                              <div>
                                <Label htmlFor="alert-title">Título</Label>
                                <Input
                                  id="alert-title"
                                  placeholder="Ej: Cuestionario de seguimiento"
                                  value={alertData.title}
                                  onChange={(e) => setAlertData({ ...alertData, title: e.target.value })}
                                />
                              </div>
                              <div>
                                <Label htmlFor="alert-message">Mensaje</Label>
                                <Textarea
                                  id="alert-message"
                                  placeholder="Describe la alerta..."
                                  value={alertData.message}
                                  onChange={(e) => setAlertData({ ...alertData, message: e.target.value })}
                                  rows={3}
                                />
                              </div>
                              <div>
                                <Label htmlFor="alert-link">Enlace (opcional)</Label>
                                <Input
                                  id="alert-link"
                                  placeholder="https://..."
                                  value={alertData.link}
                                  onChange={(e) => setAlertData({ ...alertData, link: e.target.value })}
                                />
                              </div>
                              <Button onClick={handleSendAlert} className="w-full">
                                <Bell className="h-4 w-4 mr-2" />
                                Enviar alerta
                              </Button>
                            </div>
                          </div>

                          <div>
                            <h4 className="font-semibold mb-3">Alertas enviadas</h4>
                            {selectedClientDetails?.alerts?.length > 0 ? (
                              <div className="space-y-2">
                                {selectedClientDetails.alerts.map((alert) => (
                                  <div key={alert.id} className="p-3 bg-gray-50 rounded-lg">
                                    <p className="font-medium">{alert.title}</p>
                                    <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                                    <p className="text-xs text-gray-500 mt-2">Enviado: {new Date(alert.date).toLocaleDateString('es-ES')}</p>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <p className="text-gray-500 text-center py-4">No hay alertas enviadas</p>
                            )}
                          </div>
                        </TabsContent>

                        {/* Alerts Tab - placeholder */}
                        <TabsContent value="alerts">
                          <div className="bg-gray-50 p-8 rounded-lg text-center">
                            <Bell className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                            <h3 className="font-semibold text-lg mb-2">Sistema de Alertas</h3>
                            <p className="text-gray-600">
                              Aquí se mostrarán las alertas del cliente.
                            </p>
                          </div>
                        </TabsContent>

                        {/* Nutrition Tab */}
                        <TabsContent value="nutrition">
                          {/* Questionnaire Submissions Pendientes */}
                          {questionnaireSubmissions.length > 0 && questionnaireSubmissions.some(sub => !sub.plan_generated) && (
                            <div className="mb-6">
                              <div className="bg-gradient-to-r from-orange-50 to-amber-50 border-2 border-orange-300 rounded-lg p-4">
                                <h3 className="text-xl font-bold text-orange-800 mb-3 flex items-center gap-2">
                                  📝 Cuestionarios Pendientes de Procesar
                                  <span className="bg-orange-500 text-white text-xs px-2 py-1 rounded-full">
                                    {questionnaireSubmissions.filter(sub => !sub.plan_generated).length}
                                  </span>
                                </h3>
                                
                                <div className="space-y-3">
                                  {questionnaireSubmissions.filter(sub => !sub.plan_generated).map((submission) => (
                                    <Card key={submission.id} className="border-orange-200 bg-white">
                                      <CardHeader>
                                        <div className="flex justify-between items-center">
                                          <div>
                                            <CardTitle className="text-lg text-gray-800">
                                              📋 Respuestas del Cuestionario
                                            </CardTitle>
                                            <p className="text-sm text-gray-500">
                                              Enviado el {new Date(submission.submitted_at).toLocaleDateString('es-ES', {
                                                day: 'numeric',
                                                month: 'long',
                                                year: 'numeric',
                                                hour: '2-digit',
                                                minute: '2-digit'
                                              })}
                                            </p>
                                          </div>
                                          
                                          <div className="flex gap-2">
                                            <Button
                                              onClick={() => setSelectedSubmission(selectedSubmission?.id === submission.id ? null : submission)}
                                              variant={selectedSubmission?.id === submission.id ? "default" : "outline"}
                                              className="flex items-center gap-2"
                                            >
                                              {selectedSubmission?.id === submission.id ? 'Ocultar' : 'Ver Respuestas'}
                                            </Button>
                                          </div>
                                        </div>
                                      </CardHeader>
                                      
                                      {/* Respuestas del cuestionario */}
                                      {selectedSubmission?.id === submission.id && (
                                        <CardContent className="border-t pt-4">
                                          <div className="bg-gray-50 p-4 rounded-lg mb-4 max-h-96 overflow-y-auto">
                                            <h4 className="font-bold text-gray-800 mb-3">📊 Respuestas Completas:</h4>
                                            <div className="space-y-3">
                                              {Object.entries(submission.responses).map(([key, value]) => {
                                                if (!value || key === 'submit') return null;
                                                
                                                // Formatear el nombre del campo
                                                const fieldName = key
                                                  .replace(/_/g, ' ')
                                                  .replace(/\b\w/g, l => l.toUpperCase());
                                                
                                                return (
                                                  <div key={key} className="border-b border-gray-200 pb-2">
                                                    <p className="text-sm font-semibold text-gray-700">{fieldName}:</p>
                                                    <p className="text-sm text-gray-600">{String(value)}</p>
                                                  </div>
                                                );
                                              })}
                                            </div>
                                          </div>
                                          
                                          {/* Opciones: Generar con IA o Manual */}
                                          <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border border-blue-200">
                                            <h4 className="font-bold text-gray-800 mb-3">¿Cómo quieres crear el plan?</h4>
                                            <div className="flex gap-3">
                                              <Button
                                                onClick={() => generatePlanWithAI(submission.id)}
                                                disabled={generatingPlan}
                                                className="flex-1 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white"
                                              >
                                                {generatingPlan ? (
                                                  <>
                                                    <span className="animate-spin mr-2">⏳</span>
                                                    Generando con IA...
                                                  </>
                                                ) : (
                                                  <>
                                                    🤖 Generar con IA
                                                  </>
                                                )}
                                              </Button>
                                              
                                              <Button
                                                onClick={() => createManualPlan(submission.id)}
                                                variant="outline"
                                                className="flex-1 border-purple-300 hover:bg-purple-50"
                                              >
                                                ✍️ Escribir Manualmente
                                              </Button>
                                            </div>
                                            <p className="text-xs text-gray-500 mt-2 text-center">
                                              La IA tardará ~30-60 segundos. El manual te permite escribir libremente.
                                            </p>
                                          </div>
                                        </CardContent>
                                      )}
                                    </Card>
                                  ))}
                                </div>
                              </div>
                            </div>
                          )}
                          
                          {/* Configuration Selectors */}
                          {availableQuestionnaires.length > 0 && (
                            <Card className="mb-6 border-2 border-green-200 bg-gradient-to-br from-green-50 to-emerald-50">
                              <CardHeader>
                                <CardTitle className="text-lg text-green-900">⚙️ Configuración de Generación</CardTitle>
                                <p className="text-sm text-gray-600">Selecciona los datos que quieres usar para generar el plan</p>
                              </CardHeader>
                              <CardContent className="space-y-4">
                                {/* Questionnaire Selector */}
                                <div>
                                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                                    📋 Cuestionario Base
                                  </label>
                                  <select
                                    value={selectedQuestionnaireForNutrition || ''}
                                    onChange={(e) => setSelectedQuestionnaireForNutrition(e.target.value)}
                                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                                  >
                                    <option value="">Selecciona un cuestionario...</option>
                                    {availableQuestionnaires.map((q) => (
                                      <option key={q.id} value={q.id}>
                                        {q.label}
                                      </option>
                                    ))}
                                  </select>
                                  <p className="text-xs text-gray-500 mt-1">
                                    Datos del cliente (alergias, comidas diarias, horarios, etc.)
                                  </p>
                                </div>

                                {/* Training Plan Selector */}
                                <div>
                                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                                    💪 Plan de Entrenamiento de Referencia
                                  </label>
                                  <select
                                    value={selectedTrainingPlanForNutrition || ''}
                                    onChange={(e) => setSelectedTrainingPlanForNutrition(e.target.value || null)}
                                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                                  >
                                    <option value="">Último generado (recomendado)</option>
                                    {availableTrainingPlans.map((plan) => (
                                      <option key={plan.id} value={plan.id}>
                                        {plan.label}
                                      </option>
                                    ))}
                                  </select>
                                  <p className="text-xs text-gray-500 mt-1">
                                    La nutrición se sincronizará con este entrenamiento (días A/M/B, pre/post entreno)
                                  </p>
                                </div>

                                {/* Previous Nutrition Plan Selector */}
                                <div>
                                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                                    🔄 Plan Nutricional Previo (Opcional)
                                  </label>
                                  <select
                                    value={selectedPreviousNutritionPlan || ''}
                                    onChange={(e) => setSelectedPreviousNutritionPlan(e.target.value || null)}
                                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                                  >
                                    <option value="">Sin plan previo</option>
                                    {nutritionPlans.map((plan) => (
                                      <option key={plan.id} value={plan.id}>
                                        {new Date(plan.generated_at).toLocaleDateString('es-ES')} - Mes {plan.month}/{plan.year}
                                      </option>
                                    ))}
                                  </select>
                                  <p className="text-xs text-gray-500 mt-1">
                                    Para progresión/adaptación desde un plan anterior
                                  </p>
                                </div>
                              </CardContent>
                            </Card>
                          )}
                          
                          {/* ⚠️ GENERACIÓN DE PLANES TEMPORALMENTE DESHABILITADA */}
                          {questionnaireSubmissions.length > 0 && (
                            <div className="mb-6">
                              <div className="bg-gradient-to-r from-yellow-50 to-amber-50 border-2 border-yellow-400 rounded-lg p-4">
                                <h3 className="text-xl font-bold text-yellow-800 mb-3 flex items-center gap-2">
                                  ⚠️ Sistema en Migración
                                  <span className="bg-yellow-500 text-white text-xs px-2 py-1 rounded-full">
                                    Actualización
                                  </span>
                                </h3>
                                
                                <div className="space-y-3">
                                  {questionnaireSubmissions.map((submission) => (
                                    <Card key={submission.id} className="border-yellow-200 bg-white">
                                      <CardHeader>
                                        <div className="flex justify-between items-center">
                                          <div className="flex-1">
                                            <CardTitle className="text-lg text-gray-800">
                                              📋 Cuestionario Disponible
                                            </CardTitle>
                                            <p className="text-sm text-gray-500 mb-2">
                                              Enviado el {new Date(submission.submitted_at).toLocaleDateString('es-ES', {
                                                day: 'numeric',
                                                month: 'long',
                                                year: 'numeric'
                                              })}
                                            </p>
                                            <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                                              <p className="text-sm text-yellow-800 font-medium">
                                                ⚠️ La generación automática de planes está temporalmente deshabilitada mientras migramos al nuevo sistema EDN360 con arquitectura mejorada.
                                              </p>
                                              <p className="text-xs text-yellow-700 mt-1">
                                                Los cuestionarios se guardan correctamente y estarán disponibles cuando el nuevo sistema esté listo.
                                              </p>
                                            </div>
                                          </div>
                                        </div>
                                      </CardHeader>
                                    </Card>
                                  ))}
                                </div>
                              </div>
                            </div>
                          )}

                          {/* Planes de Nutrición Existentes */}
                          {nutritionPlans.length > 0 ? (
                            <div className="space-y-4">
                              <div className="flex justify-between items-center mb-4">
                                <h3 className="text-xl font-bold text-gray-800">📋 Planes de Nutrición Mensuales</h3>
                                <span className="text-sm text-gray-500">{nutritionPlans.length} plan(es) total</span>
                              </div>

                              {/* Lista de planes como cards simples */}
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {nutritionPlans.map((plan, index) => {
                                  const monthNames = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                                                     "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
                                  
                                  return (
                                    <Card 
                                      key={plan.id} 
                                      className="border-2 border-gray-200 hover:border-blue-400 transition-all cursor-pointer hover:shadow-lg"
                                      onClick={() => openPlanModal(plan)}
                                    >
                                      <CardHeader>
                                        <div className="flex items-center justify-between">
                                          <div className="flex items-center gap-3">
                                            <div className="w-12 h-12 rounded-full flex items-center justify-center bg-blue-500 text-white font-bold text-lg">
                                              {index + 1}
                                            </div>
                                            <div>
                                              <CardTitle className="text-lg">
                                                🥗 {monthNames[plan.month]} {plan.year}
                                              </CardTitle>
                                              <p className="text-sm text-gray-500">
                                                {new Date(plan.generated_at).toLocaleDateString('es-ES')}
                                              </p>
                                            </div>
                                          </div>
                                        </div>
                                      </CardHeader>
                                      <CardContent>
                                        {/* Status badges */}
                                        <div className="flex flex-wrap gap-2">
                                          {plan.pdf_id && (
                                            <Badge variant="secondary" className="bg-orange-100 text-orange-800">
                                              📄 PDF
                                            </Badge>
                                          )}
                                          {plan.sent_email && (
                                            <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                                              ✉️ Email
                                            </Badge>
                                          )}
                                          {plan.sent_whatsapp && (
                                            <Badge variant="secondary" className="bg-green-100 text-green-800">
                                              💬 WhatsApp
                                            </Badge>
                                          )}
                                          {plan.edited && (
                                            <Badge variant="secondary" className="bg-purple-100 text-purple-800">
                                              ✏️ Editado
                                            </Badge>
                                          )}
                                        </div>
                                        <div className="flex gap-2 mt-4">
                                          <Button 
                                            variant="outline" 
                                            className="flex-1"
                                            onClick={(e) => {
                                              e.stopPropagation();
                                              openPlanModal(plan);
                                            }}
                                          >
                                            Ver Detalles →
                                          </Button>
                                          <Button 
                                            variant="outline" 
                                            className="border-red-300 text-red-600 hover:bg-red-50"
                                            onClick={async (e) => {
                                              e.stopPropagation();
                                              if (window.confirm('⚠️ ¿Eliminar completamente este plan de nutrición?\n\nEsta acción NO se puede deshacer.\n\n¿Continuar?')) {
                                                try {
                                                  await axios.delete(
                                                    `${API}/admin/users/${selectedClient.id}/nutrition/${plan.id}`,
                                                    {
                                                      headers: { Authorization: `Bearer ${token}` },
                                                      withCredentials: true
                                                    }
                                                  );
                                                  alert('✅ Plan eliminado completamente');
                                                  await loadNutritionPlan(selectedClient.id);
                                                  await loadClientDetails(selectedClient.id);
                                                } catch (error) {
                                                  console.error('Error eliminando plan:', error);
                                                  alert('❌ Error al eliminar: ' + (error.response?.data?.detail || error.message));
                                                }
                                              }
                                            }}
                                          >
                                            <Trash2 className="h-4 w-4" />
                                          </Button>
                                        </div>
                                      </CardContent>
                                    </Card>
                                  );
                                })}
                              </div>
                            </div>
                          ) : (
                            <>
                              {questionnaireSubmissions.length === 0 ? (
                                <div className="bg-gray-50 p-8 rounded-lg text-center">
                                  <UtensilsCrossed className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                                  <h3 className="font-semibold text-lg mb-2 text-gray-700">
                                    Sin Cuestionario
                                  </h3>
                                  <p className="text-gray-500">
                                    Este usuario aún no ha completado el cuestionario de nutrición.
                                  </p>
                                </div>
                              ) : (
                                <div className="bg-green-50 p-8 rounded-lg text-center border-2 border-green-300">
                                  <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
                                  <h3 className="font-semibold text-lg mb-2 text-green-800">
                                    ✅ Cuestionario Completado
                                  </h3>
                                  <p className="text-gray-700">
                                    Este usuario ha enviado sus respuestas. Revisa arriba para generar su plan.
                                  </p>
                                </div>
                              )}
                            </>
                          )}
                        </TabsContent>


                        {/* Training Tab */}
                        <TabsContent value="training">
                          {/* Configuration Selectors */}
                          {availableQuestionnaires.length > 0 && (
                            <Card className="mb-6 border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-cyan-50">
                              <CardHeader>
                                <CardTitle className="text-lg text-blue-900">⚙️ Configuración de Generación</CardTitle>
                                <p className="text-sm text-gray-600">
                                  El sistema incluye automáticamente todos los cuestionarios en orden cronológico
                                </p>
                              </CardHeader>
                              <CardContent className="space-y-4">
                                {/* Cuestionarios que se incluirán - INFORMATIVO */}
                                <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-lg p-4">
                                  <label className="block text-sm font-bold text-green-900 mb-3 flex items-center gap-2">
                                    <span className="text-lg">📋</span>
                                    Cuestionarios que se incluirán:
                                  </label>
                                  <div className="space-y-2">
                                    {availableQuestionnaires.map((q, index) => (
                                      <div key={q.id} className="flex items-start gap-3 bg-white bg-opacity-60 rounded px-3 py-2">
                                        <span className="text-green-600 font-bold text-lg flex-shrink-0">✓</span>
                                        <div className="flex-1">
                                          <span className="text-sm font-medium text-gray-800 block">
                                            {index + 1}. {q.label}
                                          </span>
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                  <div className="mt-3 bg-blue-100 border-l-4 border-blue-500 p-3 rounded">
                                    <p className="text-xs text-blue-800 flex items-start gap-2">
                                      <span className="flex-shrink-0">ℹ️</span>
                                      <span>
                                        <strong>Todos los cuestionarios se envían al workflow</strong> para que los agentes analicen 
                                        el progreso completo (evolución de peso, objetivos, lesiones, preferencias, etc.)
                                      </span>
                                    </p>
                                  </div>
                                </div>

                                {/* Previous Plan Selector */}
                                <div>
                                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                                    📊 Plan de Referencia (para progresión)
                                  </label>
                                  <select
                                    value={selectedPreviousTrainingPlan || ''}
                                    onChange={(e) => setSelectedPreviousTrainingPlan(e.target.value || null)}
                                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                  >
                                    <option value="">Ninguno (primer plan del cliente)</option>
                                    {availableTrainingPlans.map((plan) => (
                                      <option key={plan.id} value={plan.id}>
                                        {plan.label}
                                      </option>
                                    ))}
                                  </select>
                                  <p className="text-xs text-gray-500 mt-1">
                                    Selecciona el plan anterior para aplicar progresión de cargas, volumen y ejercicios
                                  </p>
                                </div>
                              </CardContent>
                            </Card>
                          )}
                          
                          {/* ✅ BOTÓN GENERAR PLAN EDN360 */}
                          {availableQuestionnaires.length > 0 && (
                            <div className="mb-6">
                              <Button
                                onClick={() => {
                                  if (!selectedQuestionnaireForTraining) {
                                    alert('⚠️ Por favor selecciona un cuestionario base');
                                    return;
                                  }
                                  generateEDN360TrainingPlan(selectedQuestionnaireForTraining);
                                }}
                                disabled={generatingEDN360Plan || !selectedQuestionnaireForTraining}
                                className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white shadow-md disabled:opacity-50 py-6 text-lg"
                              >
                                {generatingEDN360Plan ? (
                                  <>
                                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                                    Generando plan EDN360...
                                  </>
                                ) : (
                                  <>
                                    <Dumbbell className="h-5 w-5 mr-2" />
                                    Generar Plan EDN360
                                  </>
                                )}
                              </Button>
                              {!selectedQuestionnaireForTraining && (
                                <p className="text-sm text-amber-600 mt-2 text-center">
                                  ⚠️ Selecciona un cuestionario base arriba para generar el plan
                                </p>
                              )}
                            </div>
                          )}
                          
                          {/* ✅ PLAN EDN360 PERSISTENTE - CARD EDITABLE */}
                          <div className="mb-6">
                            <TrainingPlanCard 
                              userId={selectedClient.id}
                              token={token}
                              onPlanUpdated={() => {
                                // Refrescar datos si es necesario
                                console.log('Plan actualizado');
                              }}
                            />
                          </div>
                          
                          {/* ✅ PLAN EDN360 GENERADO - VISTA DE RENDERIZADO */}
                          {generatedEDN360Plan && (
                            <div className="mb-6">
                              <Card className="border-2 border-green-400 bg-gradient-to-br from-green-50 to-emerald-50">
                                <CardHeader className="border-b border-green-200 bg-white">
                                  <div className="flex justify-between items-center">
                                    <div>
                                      <CardTitle className="text-2xl text-green-900 flex items-center gap-2">
                                        🎉 {generatedEDN360Plan.title || 'Plan de Entrenamiento'}
                                      </CardTitle>
                                      <p className="text-sm text-gray-600 mt-2">{generatedEDN360Plan.summary}</p>
                                    </div>
                                    <Button
                                      variant="outline"
                                      onClick={() => setGeneratedEDN360Plan(null)}
                                      className="border-gray-300 hover:bg-gray-100"
                                    >
                                      <X className="h-4 w-4" />
                                    </Button>
                                  </div>
                                </CardHeader>
                                <CardContent className="pt-4">
                                  {/* Plan Metadata */}
                                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                                    <div className="bg-white p-3 rounded-lg border border-green-200">
                                      <p className="text-xs text-gray-500">Objetivo</p>
                                      <p className="font-semibold text-gray-900">{generatedEDN360Plan.goal}</p>
                                    </div>
                                    <div className="bg-white p-3 rounded-lg border border-green-200">
                                      <p className="text-xs text-gray-500">Días/Semana</p>
                                      <p className="font-semibold text-gray-900">{generatedEDN360Plan.days_per_week} días</p>
                                    </div>
                                    <div className="bg-white p-3 rounded-lg border border-green-200">
                                      <p className="text-xs text-gray-500">Duración Sesión</p>
                                      <p className="font-semibold text-gray-900">{generatedEDN360Plan.session_duration_min} min</p>
                                    </div>
                                    <div className="bg-white p-3 rounded-lg border border-green-200">
                                      <p className="text-xs text-gray-500">Programa</p>
                                      <p className="font-semibold text-gray-900">{generatedEDN360Plan.weeks} semanas</p>
                                    </div>
                                  </div>

                                  {/* General Notes */}
                                  {generatedEDN360Plan.general_notes && generatedEDN360Plan.general_notes.length > 0 && (
                                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                                      <h4 className="font-semibold text-blue-900 mb-2">📌 Notas Generales</h4>
                                      <ul className="list-disc list-inside space-y-1 text-sm text-blue-800">
                                        {generatedEDN360Plan.general_notes.map((note, idx) => (
                                          <li key={idx}>{note}</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}

                                  {/* Sessions */}
                                  <div className="space-y-4">
                                    <h4 className="text-xl font-bold text-gray-900">💪 Sesiones de Entrenamiento</h4>
                                    {generatedEDN360Plan.sessions && generatedEDN360Plan.sessions.map((session, sessionIdx) => (
                                      <Card key={sessionIdx} className="border-2 border-blue-300 bg-white">
                                        <CardHeader className="bg-gradient-to-r from-blue-50 to-cyan-50 border-b border-blue-200">
                                          <CardTitle className="text-lg text-blue-900">
                                            {session.id || `Día ${sessionIdx + 1}`} - {session.name}
                                          </CardTitle>
                                          {session.focus && (
                                            <div className="flex flex-wrap gap-2 mt-2">
                                              {(() => {
                                                // Hacer robusto: convertir focus a array si no lo es
                                                const focusArray = Array.isArray(session.focus)
                                                  ? session.focus
                                                  : typeof session.focus === 'string'
                                                  ? [session.focus]
                                                  : [];
                                                
                                                return focusArray.map((focus, idx) => (
                                                  <Badge key={idx} variant="secondary" className="bg-blue-100 text-blue-800">
                                                    {focus}
                                                  </Badge>
                                                ));
                                              })()}
                                            </div>
                                          )}
                                        </CardHeader>
                                        <CardContent className="pt-4">
                                          {/* Session Notes */}
                                          {session.session_notes && (
                                            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-4">
                                              <p className="text-xs font-semibold text-amber-900 mb-1">📝 Notas de la Sesión:</p>
                                              <ul className="list-disc list-inside space-y-1 text-xs text-amber-800">
                                                {(() => {
                                                  // Hacer robusto: convertir session_notes a array si no lo es
                                                  const notesArray = Array.isArray(session.session_notes)
                                                    ? session.session_notes
                                                    : typeof session.session_notes === 'string'
                                                    ? [session.session_notes]
                                                    : [];
                                                  
                                                  return notesArray.map((note, idx) => (
                                                    <li key={idx}>{note}</li>
                                                  ));
                                                })()}
                                              </ul>
                                            </div>
                                          )}

                                          {/* Blocks */}
                                          {session.blocks && session.blocks.map((block, blockIdx) => (
                                            <div key={blockIdx} className="mb-6 last:mb-0">
                                              <div className="bg-gradient-to-r from-purple-100 to-pink-100 p-3 rounded-t-lg border-2 border-purple-300 border-b-0">
                                                <h5 className="font-bold text-purple-900">Bloque {block.id}</h5>
                                                <div className="flex flex-wrap gap-2 mt-2">
                                                  {(() => {
                                                    // Proteger primary_muscles
                                                    const primaryMuscles = Array.isArray(block.primary_muscles)
                                                      ? block.primary_muscles
                                                      : block.primary_muscles
                                                      ? [block.primary_muscles]
                                                      : [];
                                                    
                                                    return primaryMuscles.map((muscle, idx) => (
                                                      <Badge key={idx} className="bg-purple-600 text-white text-xs">
                                                        💪 {muscle}
                                                      </Badge>
                                                    ));
                                                  })()}
                                                  {(() => {
                                                    // Proteger secondary_muscles
                                                    const secondaryMuscles = Array.isArray(block.secondary_muscles)
                                                      ? block.secondary_muscles
                                                      : block.secondary_muscles
                                                      ? [block.secondary_muscles]
                                                      : [];
                                                    
                                                    return secondaryMuscles.map((muscle, idx) => (
                                                      <Badge key={idx} variant="outline" className="border-purple-400 text-purple-700 text-xs">
                                                        {muscle}
                                                      </Badge>
                                                    ));
                                                  })()}
                                                </div>
                                              </div>

                                              {/* Exercises Table */}
                                              <div className="border-2 border-purple-300 border-t-0 rounded-b-lg overflow-hidden">
                                                <table className="w-full">
                                                  <thead className="bg-purple-50 border-b border-purple-200">
                                                    <tr>
                                                      <th className="px-3 py-2 text-left text-xs font-semibold text-purple-900">#</th>
                                                      <th className="px-3 py-2 text-left text-xs font-semibold text-purple-900">Ejercicio</th>
                                                      <th className="px-3 py-2 text-center text-xs font-semibold text-purple-900">Series</th>
                                                      <th className="px-3 py-2 text-center text-xs font-semibold text-purple-900">Reps</th>
                                                      <th className="px-3 py-2 text-center text-xs font-semibold text-purple-900">RPE</th>
                                                      <th className="px-3 py-2 text-center text-xs font-semibold text-purple-900">Video</th>
                                                    </tr>
                                                  </thead>
                                                  <tbody className="bg-white divide-y divide-purple-100">
                                                    {block.exercises && block.exercises.map((exercise, exIdx) => (
                                                      <tr key={exIdx} className="hover:bg-purple-50 transition-colors">
                                                        <td className="px-3 py-3 text-sm font-medium text-gray-900">{exercise.order}</td>
                                                        <td className="px-3 py-3">
                                                          <p className="text-sm font-semibold text-gray-900">{exercise.name}</p>
                                                          <p className="text-xs text-gray-500">
                                                            {exercise.primary_group}
                                                            {exercise.secondary_group && ` / ${exercise.secondary_group}`}
                                                          </p>
                                                        </td>
                                                        <td className="px-3 py-3 text-center text-sm font-semibold text-gray-900">{exercise.series}</td>
                                                        <td className="px-3 py-3 text-center text-sm text-gray-700">{exercise.reps}</td>
                                                        <td className="px-3 py-3 text-center text-sm font-semibold text-blue-700">{exercise.rpe}</td>
                                                        <td className="px-3 py-3 text-center">
                                                          {exercise.video_url && (
                                                            <a
                                                              href={exercise.video_url}
                                                              target="_blank"
                                                              rel="noopener noreferrer"
                                                              className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 hover:underline"
                                                            >
                                                              <ExternalLink className="h-3 w-3" />
                                                              Ver
                                                            </a>
                                                          )}
                                                        </td>
                                                      </tr>
                                                    ))}
                                                  </tbody>
                                                </table>
                                              </div>
                                            </div>
                                          ))}
                                        </CardContent>
                                      </Card>
                                    ))}
                                  </div>
                                </CardContent>
                              </Card>
                            </div>
                          )}
                          
                          {/* Existing Training Plans */}
                          {trainingPlans.length > 0 ? (
                            <div className="space-y-4">
                              <div className="flex justify-between items-center mb-4">
                                <h3 className="text-xl font-bold text-gray-800">💪 Planes de Entrenamiento Mensuales</h3>
                                <span className="text-sm text-gray-500">{trainingPlans.length} plan(es) total</span>
                              </div>

                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {trainingPlans.map((plan, index) => {
                                  const monthNames = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                                                     "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
                                  
                                  return (
                                    <Card 
                                      key={plan.id} 
                                      className="border-2 border-blue-200 hover:border-blue-400 transition-all cursor-pointer hover:shadow-lg"
                                      onClick={() => openTrainingPlanModal(plan)}
                                    >
                                      <CardHeader>
                                        <div className="flex items-center justify-between">
                                          <div className="flex items-center gap-3">
                                            <div className="w-12 h-12 rounded-full flex items-center justify-center bg-blue-500 text-white font-bold text-lg">
                                              {index + 1}
                                            </div>
                                            <div>
                                              <CardTitle className="text-lg">
                                                🏋️ {monthNames[plan.month]} {plan.year}
                                              </CardTitle>
                                              <p className="text-sm text-gray-500">
                                                {new Date(plan.generated_at).toLocaleDateString('es-ES')}
                                              </p>
                                            </div>
                                          </div>
                                        </div>
                                      </CardHeader>
                                      <CardContent>
                                        <div className="flex flex-wrap gap-2">
                                          {plan.pdf_id && (
                                            <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                                              📄 PDF
                                            </Badge>
                                          )}
                                          {plan.sent_email && (
                                            <Badge variant="secondary" className="bg-green-100 text-green-800">
                                              ✉️ Email
                                            </Badge>
                                          )}
                                          {plan.sent_whatsapp && (
                                            <Badge variant="secondary" className="bg-teal-100 text-teal-800">
                                              💬 WhatsApp
                                            </Badge>
                                          )}
                                          {plan.edited && (
                                            <Badge variant="secondary" className="bg-purple-100 text-purple-800">
                                              ✏️ Editado
                                            </Badge>
                                          )}
                                        </div>
                                        <div className="flex gap-2 mt-4">
                                          <Button 
                                            variant="outline" 
                                            className="flex-1"
                                            onClick={(e) => {
                                              e.stopPropagation();
                                              openTrainingPlanModal(plan);
                                            }}
                                          >
                                            Ver Detalles →
                                          </Button>
                                          <Button 
                                            variant="outline" 
                                            className="border-red-300 text-red-600 hover:bg-red-50"
                                            onClick={async (e) => {
                                              e.stopPropagation();
                                              if (window.confirm('⚠️ ¿Eliminar completamente este plan de entrenamiento?\n\nEsta acción NO se puede deshacer.\n\n¿Continuar?')) {
                                                try {
                                                  await axios.delete(
                                                    `${API}/admin/users/${selectedClient.id}/training/${plan.id}`,
                                                    {
                                                      headers: { Authorization: `Bearer ${token}` },
                                                      withCredentials: true
                                                    }
                                                  );
                                                  alert('✅ Plan de entrenamiento eliminado completamente');
                                                  await loadTrainingPlans(selectedClient.id);
                                                  await loadClientDetails(selectedClient.id);
                                                } catch (error) {
                                                  console.error('Error eliminando plan de entrenamiento:', error);
                                                  alert('❌ Error al eliminar: ' + (error.response?.data?.detail || error.message));
                                                }
                                              }
                                            }}
                                          >
                                            <Trash2 className="h-4 w-4" />
                                          </Button>
                                        </div>
                                      </CardContent>
                                    </Card>
                                  );
                                })}
                              </div>
                            </div>
                          ) : (
                            <>
                              {questionnaireSubmissions.length === 0 ? (
                                <div className="bg-gray-50 p-8 rounded-lg text-center">
                                  <Dumbbell className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                                  <h3 className="font-semibold text-lg mb-2 text-gray-700">
                                    Sin Cuestionario
                                  </h3>
                                  <p className="text-gray-500">
                                    Este usuario aún no ha completado el cuestionario. Los planes de entrenamiento se generan desde las respuestas del cuestionario de nutrición.
                                  </p>
                                </div>
                              ) : (
                                <div className="bg-blue-50 p-8 rounded-lg text-center border-2 border-blue-300">
                                  <CheckCircle className="h-16 w-16 text-blue-500 mx-auto mb-4" />
                                  <h3 className="font-semibold text-lg mb-2 text-blue-800">
                                    ✅ Cuestionario Disponible
                                  </h3>
                                  <p className="text-gray-700">
                                    Puedes generar el plan de entrenamiento desde el cuestionario del usuario. Haz clic en el botón arriba.
                                  </p>
                                </div>
                              )}
                            </>
                          )}
                        </TabsContent>



                        {/* Follow-Up Tab - REDISEÑADO */}
                        <TabsContent value="followup" className="space-y-6">
                          <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg border-2 border-purple-200">
                            <h3 className="text-xl font-bold text-purple-900 flex items-center gap-2 mb-2">
                              📊 Informes de Seguimiento
                            </h3>
                            <p className="text-sm text-gray-600">
                              Compara planes anteriores con nuevos y genera informes profesionales explicando las adaptaciones
                            </p>
                          </div>

                          {/* Selector de Planes para Comparar */}
                          <Card className="border-2 border-purple-200">
                            <CardHeader>
                              <CardTitle className="text-lg text-purple-900">⚙️ Configuración de Comparación</CardTitle>
                              <p className="text-sm text-gray-600">Selecciona los planes que quieres comparar</p>
                            </CardHeader>
                            <CardContent className="space-y-6">
                              {/* Comparación de Entrenamientos */}
                              <div className="bg-blue-50 p-4 rounded-lg">
                                <h4 className="font-semibold text-blue-900 mb-3">💪 Comparar Entrenamientos</h4>
                                <div className="grid grid-cols-2 gap-4">
                                  <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                                      Plan ANTERIOR
                                    </label>
                                    <select
                                      value={selectedPreviousTrainingForReport || ''}
                                      onChange={(e) => setSelectedPreviousTrainingForReport(e.target.value)}
                                      className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    >
                                      <option value="">Selecciona plan anterior...</option>
                                      {availableTrainingPlans.map((plan) => (
                                        <option key={plan.id} value={plan.id}>
                                          {plan.label}
                                        </option>
                                      ))}
                                    </select>
                                  </div>
                                  <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                                      Plan NUEVO
                                    </label>
                                    <select
                                      value={selectedNewTrainingForReport || ''}
                                      onChange={(e) => setSelectedNewTrainingForReport(e.target.value)}
                                      className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                    >
                                      <option value="">Selecciona plan nuevo...</option>
                                      {availableTrainingPlans.map((plan) => (
                                        <option key={plan.id} value={plan.id}>
                                          {plan.label}
                                        </option>
                                      ))}
                                    </select>
                                  </div>
                                </div>
                              </div>

                              {/* Comparación de Nutrición */}
                              <div className="bg-green-50 p-4 rounded-lg">
                                <h4 className="font-semibold text-green-900 mb-3">🥗 Comparar Nutrición</h4>
                                <div className="grid grid-cols-2 gap-4">
                                  <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                                      Plan ANTERIOR
                                    </label>
                                    <select
                                      value={selectedPreviousNutritionForReport || ''}
                                      onChange={(e) => setSelectedPreviousNutritionForReport(e.target.value)}
                                      className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                                    >
                                      <option value="">Selecciona plan anterior...</option>
                                      {availableNutritionPlans.map((plan) => (
                                        <option key={plan.id} value={plan.id}>
                                          {plan.label}
                                        </option>
                                      ))}
                                    </select>
                                  </div>
                                  <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                                      Plan NUEVO
                                    </label>
                                    <select
                                      value={selectedNewNutritionForReport || ''}
                                      onChange={(e) => setSelectedNewNutritionForReport(e.target.value)}
                                      className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                                    >
                                      <option value="">Selecciona plan nuevo...</option>
                                      {availableNutritionPlans.map((plan) => (
                                        <option key={plan.id} value={plan.id}>
                                          {plan.label}
                                        </option>
                                      ))}
                                    </select>
                                  </div>
                                </div>
                              </div>

                              {/* NUEVO: Cuestionario de Seguimiento */}
                              <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-200">
                                <h4 className="font-semibold text-gray-800 mb-3">📝 Cuestionario de Seguimiento (REQUERIDO)</h4>
                                <p className="text-sm text-gray-600 mb-3">
                                  El cuestionario permite al sistema generar un análisis inteligente del progreso del cliente
                                </p>
                                <select
                                  value={selectedFollowUpQuestionnaireForReport || ''}
                                  onChange={(e) => setSelectedFollowUpQuestionnaireForReport(e.target.value)}
                                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                >
                                  <option value="">Selecciona cuestionario de seguimiento...</option>
                                  {questionnaireSubmissions.map((q) => (
                                    <option key={q.id} value={q.id}>
                                      {q.label || `📋 Seguimiento (${new Date(q.submitted_at || q.submission_date).toLocaleDateString('es-ES')})`}
                                    </option>
                                  ))}
                                </select>
                                {questionnaireSubmissions.length === 0 && (
                                  <p className="text-sm text-red-600 mt-2">
                                    ⚠️ No se encontraron cuestionarios. Verifica que el cliente haya completado un cuestionario de seguimiento.
                                  </p>
                                )}
                              </div>

                              {/* Botón Generar Informe */}
                              <div className="flex justify-center pt-4">
                                <Button
                                  onClick={generateFollowUpReport}
                                  disabled={generatingReport || !selectedPreviousTrainingForReport || !selectedNewTrainingForReport || !selectedFollowUpQuestionnaireForReport}
                                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-6 text-lg"
                                >
                                  {generatingReport ? (
                                    <>
                                      <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                                      Generando Informe...
                                    </>
                                  ) : (
                                    <>
                                      📊 Generar Informe de Seguimiento
                                    </>
                                  )}
                                </Button>
                              </div>
                            </CardContent>
                          </Card>

                          {/* Lista de Informes Generados */}
                          <div>
                            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                              📋 Informes Generados
                            </h3>
                            
                            {followUpReports.length === 0 ? (
                              <div className="bg-gray-50 p-8 rounded-lg text-center">
                                <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                                <p className="text-gray-500">
                                  Aún no has generado ningún informe de seguimiento para este cliente.
                                </p>
                              </div>
                            ) : (
                              <div className="grid grid-cols-1 gap-4">
                                {followUpReports.map((report, index) => (
                                  <Card
                                    key={report.id}
                                    className="border-2 border-purple-200 hover:shadow-lg transition-all"
                                  >
                                    <CardHeader>
                                      <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                          <div className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 text-white flex items-center justify-center font-bold text-lg">
                                            {followUpReports.length - index}
                                          </div>
                                          <div>
                                            <CardTitle className="text-lg">
                                              Informe #{followUpReports.length - index}
                                            </CardTitle>
                                            <p className="text-sm text-gray-600">
                                              {new Date(report.generated_at).toLocaleDateString('es-ES', {
                                                day: '2-digit',
                                                month: 'long',
                                                year: 'numeric'
                                              })}
                                            </p>
                                          </div>
                                        </div>
                                      </div>
                                    </CardHeader>
                                    <CardContent>
                                      <div className="space-y-3">
                                        <div className="text-sm">
                                          <div className="font-semibold text-gray-700 mb-1">📊 Comparación:</div>
                                          <div className="text-xs text-gray-600 space-y-1">
                                            <div>💪 Entrenamiento: {report.training_comparison_label}</div>
                                            {report.nutrition_comparison_label && (
                                              <div>🥗 Nutrición: {report.nutrition_comparison_label}</div>
                                            )}
                                          </div>
                                        </div>
                                        
                                        <Button 
                                          variant="outline" 
                                          className="w-full"
                                          onClick={() => {
                                            // Abrir modal con el informe
                                            setSelectedReport(report);
                                            setShowReportModal(true);
                                          }}
                                        >
                                          📄 Ver Informe Completo
                                        </Button>
                                      </div>
                                    </CardContent>
                                  </Card>
                                ))}
                              </div>
                            )}
                          </div>
                        </TabsContent>

                        {/* History Tab - Complete Questionnaire History */}
                        <TabsContent value="history" className="space-y-4">
                          <h3 className="text-lg font-semibold flex items-center gap-2">
                            📋 Historial de Cuestionarios
                          </h3>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Cuestionario de Diagnóstico Inicial */}
                            {selectedClientDetails?.forms?.find(f => f.type === 'diagnosis') && (() => {
                              const diagnosisForm = selectedClientDetails.forms.find(f => f.type === 'diagnosis');
                              return (
                                <Card
                                  className="border-2 border-green-200 hover:border-green-400 transition-all cursor-pointer hover:shadow-lg"
                                  onClick={() => setSelectedHistoryItem({ type: 'diagnosis', data: diagnosisForm })}
                                >
                                  <CardHeader className="bg-green-50">
                                    <CardTitle className="text-lg flex items-center gap-2">
                                      🩺 Cuestionario de Diagnóstico
                                    </CardTitle>
                                    <p className="text-sm text-gray-600">
                                      {new Date(diagnosisForm.submitted_at).toLocaleDateString('es-ES')}
                                    </p>
                                  </CardHeader>
                                  <CardContent>
                                    <div className="text-sm text-gray-600 mb-3">
                                      Primer cuestionario completado tras el pago
                                    </div>
                                    <div className="flex gap-2">
                                      <Button 
                                        variant="outline" 
                                        className="flex-1"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          setSelectedHistoryItem({ type: 'diagnosis', data: diagnosisForm });
                                        }}
                                      >
                                        Ver Respuestas
                                      </Button>
                                      <Button 
                                        variant="destructive"
                                        size="icon"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          deleteQuestionnaire(diagnosisForm._id, 'diagnosis');
                                        }}
                                      >
                                        🗑️
                                      </Button>
                                    </div>
                                  </CardContent>
                                </Card>
                              );
                            })()}

                            {/* Cuestionario Inicial de Nutrición */}
                            {(() => {
                              console.log('selectedClientDetails.forms:', selectedClientDetails?.forms);
                              const nutritionForm = selectedClientDetails?.forms?.find(f => f.type === 'nutrition');
                              console.log('nutritionForm found:', nutritionForm);
                              
                              if (!nutritionForm) return null;
                              
                              const data = nutritionForm?.data || {};
                              return (
                                <Card
                                  className="border-2 border-blue-200 hover:border-blue-400 transition-all cursor-pointer hover:shadow-lg"
                                  onClick={() => setSelectedHistoryItem({ type: 'nutrition', data: nutritionForm })}
                                >
                                  <CardHeader className="bg-blue-50">
                                    <CardTitle className="text-lg flex items-center gap-2">
                                      📝 Cuestionario de Nutrición
                                    </CardTitle>
                                    <p className="text-sm text-gray-600">
                                      {new Date(nutritionForm.submitted_at).toLocaleDateString('es-ES')}
                                    </p>
                                  </CardHeader>
                                  <CardContent>
                                    <div className="grid grid-cols-2 gap-2 text-sm mb-3">
                                      <div>
                                        <div className="font-semibold text-gray-600">Peso inicial</div>
                                        <div>{data.peso_actual} kg</div>
                                      </div>
                                      <div>
                                        <div className="font-semibold text-gray-600">Objetivo</div>
                                        <div className="text-xs">{data.objetivo_principal?.substring(0, 20)}...</div>
                                      </div>
                                    </div>
                                    <div className="flex gap-2">
                                      <Button 
                                        variant="outline" 
                                        className="flex-1"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          setSelectedHistoryItem({ type: 'nutrition', data: nutritionForm });
                                        }}
                                      >
                                        Ver Respuestas
                                      </Button>
                                      <Button 
                                        variant="destructive"
                                        size="icon"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          deleteQuestionnaire(nutritionForm._id, 'nutrition');
                                        }}
                                      >
                                        🗑️
                                      </Button>
                                    </div>
                                  </CardContent>
                                </Card>
                              );
                            })()}
                            
                            {/* Seguimientos Mensuales - Cards */}
                            {followUps.map((followUp, index) => (
                              <Card
                                key={followUp.id}
                                className="border-2 border-purple-200 hover:border-purple-400 transition-all cursor-pointer hover:shadow-lg"
                                onClick={() => setSelectedHistoryItem({ type: 'followup', data: followUp })}
                              >
                                <CardHeader className="bg-purple-50">
                                  <div className="flex items-center justify-between">
                                    <div>
                                      <CardTitle className="text-lg flex items-center gap-2">
                                        📊 Seguimiento #{followUps.length - index}
                                      </CardTitle>
                                      <p className="text-sm text-gray-600">
                                        {new Date(followUp.submission_date).toLocaleDateString('es-ES')}
                                      </p>
                                    </div>
                                    <Badge className={
                                      followUp.status === 'pending_analysis' ? 'bg-yellow-100 text-yellow-800' :
                                      followUp.status === 'analyzed' ? 'bg-blue-100 text-blue-800' :
                                      'bg-green-100 text-green-800'
                                    }>
                                      {followUp.status === 'pending_analysis' && '⏳'}
                                      {followUp.status === 'analyzed' && '✅'}
                                      {followUp.status === 'plan_generated' && '🎯'}
                                    </Badge>
                                  </div>
                                </CardHeader>
                                <CardContent>
                                  <div className="grid grid-cols-2 gap-2 text-sm mb-3">
                                    <div>
                                      <div className="font-semibold text-gray-600">Día</div>
                                      <div>{followUp.days_since_last_plan}</div>
                                    </div>
                                    <div>
                                      <div className="font-semibold text-gray-600">Tipo</div>
                                      <div className="text-xs">
                                        {followUp.measurement_type === 'smart_scale' && '📱 Báscula'}
                                        {followUp.measurement_type === 'tape_measure' && '📏 Cinta'}
                                      </div>
                                    </div>
                                  </div>
                                  <div className="flex gap-2">
                                    <Button 
                                      variant="outline" 
                                      className="flex-1"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        setSelectedHistoryItem({ type: 'followup', data: followUp });
                                      }}
                                    >
                                      Ver Respuestas
                                    </Button>
                                    <Button 
                                      variant="destructive"
                                      size="icon"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        deleteFollowUp(followUp.id);
                                      }}
                                    >
                                      🗑️
                                    </Button>
                                  </div>
                                </CardContent>
                              </Card>
                            ))}

                            {/* Empty state */}
                            {!selectedClientDetails?.forms?.find(f => f.type === 'diagnosis') && 
                             !selectedClientDetails?.forms?.find(f => f.type === 'nutrition') && 
                             followUps.length === 0 && (
                              <div className="col-span-2 bg-gray-50 p-8 rounded-lg text-center">
                                <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                                <p className="text-gray-500">
                                  Este cliente aún no ha completado ningún cuestionario.
                                </p>
                              </div>
                            )}
                          </div>
                        </TabsContent>

                        {/* Sessions Tab - placeholder */}
                        <TabsContent value="sessions">
                          <div className="bg-gray-50 p-8 rounded-lg text-center">
                            <Calendar className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                            <h3 className="font-semibold text-lg mb-2">Sesiones de entrenamiento</h3>
                            <p className="text-gray-600 mb-4">
                              Gestiona las sesiones y el calendario del cliente
                            </p>
                            <Button variant="outline">
                              <Calendar className="h-4 w-4 mr-2" />
                              Ver calendario de sesiones
                            </Button>
                          </div>
                        </TabsContent>
                      </Tabs>
                    </CardContent>
                  </>
                ) : (
                  <CardContent className="pt-20 pb-20 text-center">
                    <UserPlus className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500">Selecciona un cliente para gestionar</p>
                  </CardContent>
                )}
              </Card>
            </div>
          </TabsContent>

          {/* Templates Tab */}
          <TabsContent value="templates">
            <TemplatesManager token={token} />
          </TabsContent>

          {/* Calendar Tab */}
          <TabsContent value="calendar">
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Calendario de la Web (existente) */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-blue-600" />
                  Calendario del CRM
                </h3>
                <AdminCalendar />
              </div>
              
              {/* Google Calendar - Acceso Directo */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <CalendarPlus className="h-5 w-5 text-green-600" />
                  Google Calendar
                </h3>
                
                {/* Botón de acceso directo */}
                <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-lg p-6 border-2 border-green-200">
                  <div className="text-center space-y-4">
                    <CalendarPlus className="h-16 w-16 mx-auto text-green-600" />
                    <h4 className="text-xl font-bold text-gray-900">Gestiona tu Google Calendar</h4>
                    <p className="text-gray-600">
                      Abre tu Google Calendar en una nueva pestaña para crear y gestionar tus revisiones con clientes.
                    </p>
                    <Button 
                      onClick={() => window.open('https://calendar.google.com/calendar/u/0/r', '_blank')}
                      className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 text-lg"
                    >
                      <ExternalLink className="h-5 w-5 mr-2" />
                      Abrir Google Calendar
                    </Button>
                    <p className="text-xs text-gray-500 mt-4">
                      💡 Se abrirá en una nueva pestaña. Crea tus eventos allí y podrás verlos actualizados aquí abajo.
                    </p>
                  </div>
                </div>
                
                {/* Visualización del calendario debajo */}
                <div className="mt-6">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-semibold text-gray-700">Vista de tu calendario:</h4>
                    <Button 
                      onClick={() => window.location.reload()}
                      variant="outline"
                      size="sm"
                      className="text-xs"
                    >
                      🔄 Actualizar
                    </Button>
                  </div>
                  <div className="bg-white rounded-lg shadow-lg overflow-hidden" style={{ height: '500px' }}>
                    <iframe
                      src="https://calendar.google.com/calendar/embed?height=600&wkst=2&ctz=Europe%2FMadrid&showPrint=0&mode=WEEK&src=ZWNqdHJhaW5lckBnbWFpbC5jb20&src=ZmI0NmRhZjUyODI3NzBhYjIxNzc5ZTI5MDAxNjkwYzI4MjAxYTcyNzJiODQ5Y2RiYmNhZThhNjI3OTA0NTFlZEBncm91cC5jYWxlbmRhci5nb29nbGUuY29t&color=%2333b679&color=%23ef6c00"
                      style={{ border: 0, width: '100%', height: '100%' }}
                      frameBorder="0"
                      scrolling="no"
                      title="Google Calendar"
                    ></iframe>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>


          {/* Finances Tab */}
          <TabsContent value="finances">
            <div className="space-y-6">
                {/* Header con botón */}
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold">💰 Sistema de Cajas</h2>
                    <p className="text-gray-600">Gestión de pagos Stripe y manuales</p>
                  </div>
                  <Button
                    onClick={() => setShowPaymentModal(true)}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <DollarSign className="h-5 w-5 mr-2" />
                    Registrar Pago Manual
                  </Button>
                </div>

                {/* CAJA A - Stripe + Transferencia + Bizum */}
                <Card className="border-blue-200 border-2">
                  <CardHeader className="bg-blue-50">
                    <CardTitle className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <CreditCard className="h-6 w-6 text-blue-600" />
                        <span>CAJA A - Pagos Digitales</span>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-600">Total</p>
                        <p className="text-2xl font-bold text-blue-600">
                          {(manualPayments
                            .filter(p => ['Stripe', 'Transferencia', 'Bizum'].includes(p.metodo_pago))
                            .reduce((sum, p) => sum + p.amount, 0) || 0).toFixed(2)}€
                        </p>
                      </div>
                    </CardTitle>
                    <p className="text-sm text-gray-600 mt-2">
                      Stripe · Transferencia · Bizum
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {manualPayments.filter(p => ['Stripe', 'Transferencia', 'Bizum'].includes(p.metodo_pago)).length === 0 ? (
                        <p className="text-center py-8 text-gray-500">No hay pagos en Caja A</p>
                      ) : (
                        manualPayments
                          .filter(p => ['Stripe', 'Transferencia', 'Bizum'].includes(p.metodo_pago))
                          .map(payment => (
                            <div key={payment._id} className="flex items-center justify-between p-4 bg-blue-50 rounded-lg group hover:bg-blue-100 transition-colors">
                              <div className="flex-1">
                                <div className="flex items-center gap-3">
                                  <p className="font-bold text-lg">{payment.amount}€</p>
                                  <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-200 text-blue-800">
                                    {payment.metodo_pago}
                                  </span>
                                </div>
                                <p className="text-sm font-medium text-gray-900 mt-1">{payment.concepto}</p>
                                <div className="flex items-center gap-3 mt-1">
                                  <p className="text-xs text-gray-600">
                                    {new Date(payment.fecha).toLocaleDateString('es-ES')}
                                  </p>
                                  {payment.notas && <p className="text-xs text-gray-500">· {payment.notas}</p>}
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="opacity-0 group-hover:opacity-100 transition-opacity"
                                  onClick={() => setEditingManualPayment(payment)}
                                >
                                  <Edit className="h-4 w-4 text-blue-600" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="opacity-0 group-hover:opacity-100 transition-opacity"
                                  onClick={() => deleteManualPayment(payment._id)}
                                >
                                  <Trash2 className="h-4 w-4 text-red-600" />
                                </Button>
                              </div>
                            </div>
                          ))
                      )}
                    </div>
                  </CardContent>
                </Card>

                {/* CAJA B - Efectivo */}
                <Card className="border-orange-200 border-2">
                  <CardHeader className="bg-orange-50">
                    <CardTitle className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <DollarSign className="h-6 w-6 text-orange-600" />
                        <span>CAJA B - Pagos en Efectivo</span>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-600">Total</p>
                        <p className="text-2xl font-bold text-orange-600">
                          {(manualPayments
                            .filter(p => p.metodo_pago === 'Efectivo')
                            .reduce((sum, p) => sum + p.amount, 0) || 0).toFixed(2)}€
                        </p>
                      </div>
                    </CardTitle>
                    <p className="text-sm text-gray-600 mt-2">
                      Efectivo · Cobros en mano
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {manualPayments.filter(p => p.metodo_pago === 'Efectivo').length === 0 ? (
                        <p className="text-center py-8 text-gray-500">No hay pagos en Caja B</p>
                      ) : (
                        manualPayments
                          .filter(p => p.metodo_pago === 'Efectivo')
                          .map(payment => (
                            <div key={payment._id} className="flex items-center justify-between p-4 bg-orange-50 rounded-lg group hover:bg-orange-100 transition-colors">
                              <div className="flex-1">
                                <div className="flex items-center gap-3">
                                  <p className="font-bold text-lg">{payment.amount}€</p>
                                  <span className="px-3 py-1 rounded-full text-sm font-medium bg-orange-200 text-orange-800">
                                    Efectivo
                                  </span>
                                </div>
                                <p className="text-sm font-medium text-gray-900 mt-1">{payment.concepto}</p>
                                <div className="flex items-center gap-3 mt-1">
                                  <p className="text-xs text-gray-600">
                                    {new Date(payment.fecha).toLocaleDateString('es-ES')}
                                  </p>
                                  {payment.notas && <p className="text-xs text-gray-500">· {payment.notas}</p>}
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="opacity-0 group-hover:opacity-100 transition-opacity"
                                  onClick={() => setEditingManualPayment(payment)}
                                >
                                  <Edit className="h-4 w-4 text-orange-600" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="opacity-0 group-hover:opacity-100 transition-opacity"
                                  onClick={() => deleteManualPayment(payment._id)}
                                >
                                  <Trash2 className="h-4 w-4 text-red-600" />
                                </Button>
                              </div>
                            </div>
                          ))
                      )}
                    </div>
                  </CardContent>
                </Card>

                {/* Financial Metrics Overview */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <CreditCard className="h-6 w-6" />
                      Métricas Financieras
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {financialMetrics ? (
                      <>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                            <p className="text-sm text-gray-600 mb-1">Ingresos Totales</p>
                            <p className="text-2xl font-bold text-green-600">
                              {formatAmount(financialMetrics.total_revenue)}
                            </p>
                          </div>
                          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                            <p className="text-sm text-gray-600 mb-1">Ingresos del Mes</p>
                            <p className="text-2xl font-bold text-blue-600">
                              {formatAmount(financialMetrics.monthly_revenue)}
                            </p>
                          </div>
                          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                            <p className="text-sm text-gray-600 mb-1">Ingresos del Año</p>
                            <p className="text-2xl font-bold text-purple-600">
                              {formatAmount(financialMetrics.annual_revenue)}
                            </p>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                          <div className="border border-gray-200 rounded-lg p-4">
                            <p className="text-sm text-gray-600 mb-1">Suscripciones Activas</p>
                            <p className="text-xl font-bold">{financialMetrics.active_subscriptions}</p>
                          </div>
                          <div className="border border-gray-200 rounded-lg p-4">
                            <p className="text-sm text-gray-600 mb-1">MRR (Ingresos Recurrentes Mensuales)</p>
                            <p className="text-xl font-bold">{formatAmount(financialMetrics.mrr)}</p>
                          </div>
                          <div className="border border-gray-200 rounded-lg p-4">
                            <p className="text-sm text-gray-600 mb-1">Total Transacciones</p>
                            <p className="text-xl font-bold">{financialMetrics.total_transactions}</p>
                          </div>
                          <div className="border border-gray-200 rounded-lg p-4">
                            <p className="text-sm text-gray-600 mb-1">Pagos Exitosos / Fallidos</p>
                            <p className="text-xl font-bold">
                              <span className="text-green-600">{financialMetrics.successful_payments}</span>
                              {' / '}
                              <span className="text-red-600">{financialMetrics.failed_payments}</span>
                            </p>
                          </div>
                        </div>
                      </>
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <p>No hay datos financieros disponibles</p>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Payment History */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2">
                        <FileText className="h-6 w-6" />
                        Historial de Pagos ({allPayments.length})
                      </CardTitle>
                      {allPayments.some(p => p.status === 'pending') && (
                        <Button
                          variant="outline"
                          className="border-red-300 text-red-600 hover:bg-red-50"
                          onClick={handleCleanupPendingPayments}
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Limpiar Pagos Pendientes
                        </Button>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    {allPayments.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <FileText className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                        <p>No hay pagos registrados aún</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        <div className="grid grid-cols-6 gap-4 pb-2 border-b font-semibold text-sm">
                          <div>Cliente</div>
                          <div>Fecha</div>
                          <div>Monto</div>
                          <div>Estado</div>
                          <div>ID</div>
                          <div className="text-center">Acciones</div>
                        </div>
                        {allPayments.map((payment) => (
                          <div
                            key={payment.transaction_id}
                            className="grid grid-cols-6 gap-4 p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                          >
                            <div>
                              <p className="font-medium">{payment.user_name}</p>
                              <p className="text-xs text-gray-500">{payment.user_email}</p>
                            </div>
                            <div className="text-sm">
                              {formatDate(payment.date)}
                            </div>
                            <div className="font-semibold">
                              {formatAmount(payment.amount, payment.currency)}
                            </div>
                            <div>
                              <Badge className={payment.status === 'succeeded' ? 'bg-green-500' : 'bg-red-500'}>
                                {payment.status === 'succeeded' ? 'Exitoso' : payment.status}
                              </Badge>
                            </div>
                            <div className="text-xs text-gray-500 truncate">
                              {payment.transaction_id.substring(0, 12)}...
                            </div>
                            <div className="flex justify-center">
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                onClick={() => handleDeletePayment(payment.transaction_id)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

        </Tabs>
        )}
      </div>


      {/* Edit User Modal */}
      {showEditModal && userToEdit && (
        <EditUserModal
          user={userToEdit}
          open={showEditModal}
          onClose={() => {
            setShowEditModal(false);
            setUserToEdit(null);
          }}
          onSuccess={() => {
            loadClients();
            if (selectedClient && userToEdit.id === selectedClient.id) {
              loadClientDetails(userToEdit.id);
            }
          }}
        />
      )}

      {/* Template Selector Modal */}
      {showTemplateSelector && selectedClient && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b flex items-center justify-between sticky top-0 bg-white">
              <div>
                <h3 className="text-xl font-bold">Selecciona un Template</h3>
                <p className="text-sm text-gray-600 mt-1">Para {selectedClient.name}</p>
              </div>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => {
                  setShowTemplateSelector(false);
                  setSelectedTagFilter('');
                }}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            
            {/* Tag Filter Dropdown */}
            <div className="px-6 pt-4 pb-2 bg-gray-50 border-b">
              <Label className="text-sm font-semibold mb-2 block">Filtrar por etiqueta</Label>
              <select
                value={selectedTagFilter}
                onChange={(e) => setSelectedTagFilter(e.target.value)}
                className="w-full border rounded-md px-3 py-2"
              >
                <option value="">Todas las etiquetas</option>
                {allTags.map(tag => (
                  <option key={tag} value={tag}>{tag}</option>
                ))}
              </select>
            </div>
            
            <div className="p-6 space-y-3">
              {templates
                .filter(t => t.type === 'whatsapp')
                .filter(t => {
                  // Filter by selected tag
                  if (selectedTagFilter) {
                    return t.tags && t.tags.includes(selectedTagFilter);
                  }
                  return true;
                })
                .length > 0 ? (
                templates
                  .filter(t => t.type === 'whatsapp')
                  .filter(t => {
                    // Filter by selected tag
                    if (selectedTagFilter) {
                      return t.tags && t.tags.includes(selectedTagFilter);
                    }
                    return true;
                  })
                  .map(template => (
                  <div
                    key={template.id}
                    onClick={() => {
                      openTemplateModal(template);
                      setShowTemplateSelector(false);
                      setSelectedTagFilter('');
                    }}
                    className="p-4 border-2 border-purple-200 rounded-lg hover:bg-purple-50 hover:border-purple-400 cursor-pointer transition-all"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-bold text-gray-900">{template.name}</h4>
                    </div>
                    <p className="text-sm text-gray-600 whitespace-pre-wrap">{template.content}</p>
                    {template.tags && template.tags.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {template.tags.map(tag => (
                          <Badge key={tag} className="text-xs bg-blue-100 text-blue-700">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    )}
                    {template.variables && template.variables.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {template.variables.map(v => (
                          <Badge key={v} variant="outline" className="text-xs">
                            {`{${v}}`}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-12">
                  <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  {selectedTagFilter ? (
                    <>
                      <p className="text-gray-500">No hay templates con la etiqueta "{selectedTagFilter}"</p>
                      <Button
                        className="mt-4"
                        variant="outline"
                        onClick={() => setSelectedTagFilter('')}
                      >
                        Limpiar filtro
                      </Button>
                    </>
                  ) : (
                    <>
                      <p className="text-gray-500">No hay templates de WhatsApp disponibles</p>
                      <Button
                        className="mt-4"
                        onClick={() => {
                          setShowTemplateSelector(false);
                          setSelectedTagFilter('');
                          setActiveView('templates');
                        }}
                      >
                        Crear Templates
                      </Button>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Template Message Modal */}
      {showTemplateModal && selectedTemplate && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg w-full max-w-2xl">
            <div className="p-6 border-b flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold">{selectedTemplate.name}</h3>
                <p className="text-sm text-gray-600 mt-1">Mensaje auto-completado para {selectedClient?.name}</p>
              </div>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setShowTemplateModal(false)}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            
            <div className="p-6 space-y-4">
              {/* Message Preview */}
              <div>
                <label className="text-sm font-semibold text-gray-700 block mb-2">
                  Mensaje personalizado:
                </label>
                <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4">
                  <p className="whitespace-pre-wrap text-gray-900">{templateMessage}</p>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  ✨ Las variables se han reemplazado automáticamente con los datos del cliente
                </p>
              </div>

              {/* Editable Message */}
              <div>
                <label className="text-sm font-semibold text-gray-700 block mb-2">
                  Editar mensaje (opcional):
                </label>
                <textarea
                  value={templateMessage}
                  onChange={(e) => setTemplateMessage(e.target.value)}
                  className="w-full border rounded-lg p-3 min-h-32"
                  placeholder="Edita el mensaje si lo necesitas..."
                />
              </div>

              {/* Actions */}
              <div className="grid grid-cols-2 gap-3 pt-4">
                <Button
                  onClick={() => sendTemplateViaWhatsApp()}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <MessageSquare className="h-4 w-4 mr-2" />
                  WhatsApp
                </Button>
                <Button
                  onClick={() => sendTemplateViaEmail()}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Mail className="h-4 w-4 mr-2" />
                  Email
                </Button>
                <Button
                  onClick={() => sendTemplateAsAlert()}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  <Bell className="h-4 w-4 mr-2" />
                  Alerta
                </Button>
                <Button
                  onClick={() => sendTemplateToChat()}
                  className="bg-orange-600 hover:bg-orange-700"
                >
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Chat Interno
                </Button>
              </div>
              
              {/* Copy button as fallback */}
              <div className="pt-2">
                <Button
                  variant="outline"
                  onClick={() => {
                    navigator.clipboard.writeText(templateMessage);
                    alert('Mensaje copiado al portapapeles');
                  }}
                  className="w-full"
                >
                  <Copy className="h-4 w-4 mr-2" />
                  Copiar al Portapapeles
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chat Modal */}
      {showChat && selectedClient && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center justify-center p-4">
          <div className="bg-white rounded-t-3xl sm:rounded-3xl w-full sm:max-w-2xl max-h-[80vh] flex flex-col shadow-2xl">
            <div className="p-4 border-b flex items-center justify-between">
              <h3 className="text-lg font-bold">Chat con {selectedClient.name}</h3>
              <Button size="sm" variant="ghost" onClick={() => setShowChat(false)}>
                Cerrar
              </Button>
            </div>
            <div className="flex-1 overflow-hidden">
              <ChatBox userId={selectedClient.id} isAdmin={true} />
            </div>
          </div>
        </div>
      )}

      {/* Modal Fullscreen para Plan de Nutrición */}
      <Dialog open={showNutritionModal} onOpenChange={(open) => {
        if (!open) closePlanModal();
      }}>
        <DialogContent className="max-w-[95vw] w-[95vw] h-[95vh] max-h-[95vh] p-0 overflow-hidden flex flex-col">
          {modalPlan ? (
            <>
              {/* Header del Modal */}
              <DialogHeader className="p-6 border-b bg-gradient-to-r from-blue-50 to-green-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 rounded-full flex items-center justify-center bg-blue-500 text-white font-bold text-xl">
                      🥗
                    </div>
                    <div>
                      <DialogTitle className="text-2xl font-bold">
                        Plan de Nutrición - {(() => {
                          const monthNames = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                                             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
                          return `${monthNames[modalPlan.month]} ${modalPlan.year}`;
                        })()}
                      </DialogTitle>
                      <DialogDescription className="text-sm">
                        Generado: {new Date(modalPlan.generated_at).toLocaleDateString('es-ES')} • 
                        Cliente: {selectedClient?.name}
                      </DialogDescription>
                    </div>
                  </div>
                  
                  {/* Status badges */}
                  <div className="flex gap-2">
                    {modalPlan.pdf_id && (
                      <Badge className="bg-orange-500">📄 PDF</Badge>
                    )}
                    {modalPlan.sent_email && (
                      <Badge className="bg-blue-500">✉️ Email</Badge>
                    )}
                    {modalPlan.sent_whatsapp && (
                      <Badge className="bg-green-500">💬 WhatsApp</Badge>
                    )}
                    {modalPlan.edited && (
                      <Badge className="bg-purple-500">✏️ Editado</Badge>
                    )}
                  </div>
                </div>
              </DialogHeader>

              {/* Content del Modal - Scrollable */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {/* Status Details */}
                <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <div className="text-3xl mb-1">{modalPlan.pdf_id ? '✅' : '❌'}</div>
                    <div className="text-sm text-gray-600 font-medium">PDF Generado</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl mb-1">{modalPlan.sent_email ? '✅' : '❌'}</div>
                    <div className="text-sm text-gray-600 font-medium">Enviado Email</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl mb-1">{modalPlan.sent_whatsapp ? '✅' : '❌'}</div>
                    <div className="text-sm text-gray-600 font-medium">Enviado WhatsApp</div>
                  </div>
                </div>

                {/* Editor/Viewer */}
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle>Plan Verificado</CardTitle>
                    <div className="flex gap-2">
                      {!editingNutrition ? (
                        <>
                          <Button
                            onClick={() => {
                              // Close the modal first, then open chat
                              setShowNutritionModal(false);
                              setTimeout(() => setShowNutritionChat(true), 100);
                            }}
                            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                          >
                            <MessageSquare className="h-4 w-4 mr-2" />
                            💬 Chat con IA
                          </Button>
                          <Button
                            onClick={() => setEditingNutrition(true)}
                            variant="outline"
                          >
                            <Edit className="h-4 w-4 mr-2" />
                            Editar Manual
                          </Button>
                        </>
                      ) : (
                        <>
                          <Button
                            onClick={() => {
                              setEditingNutrition(false);
                              setNutritionContent(modalPlan.plan_text || modalPlan.plan_verificado);
                            }}
                            variant="outline"
                          >
                            Cancelar
                          </Button>
                          <Button onClick={saveNutritionChanges}>
                            <Save className="h-4 w-4 mr-2" />
                            Guardar
                          </Button>
                        </>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    {editingNutrition ? (
                      <Textarea
                        value={nutritionContent}
                        onChange={(e) => setNutritionContent(e.target.value)}
                        rows={25}
                        className="font-mono text-sm"
                      />
                    ) : (
                      <div className="prose max-w-none">
                        <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
                          {modalPlan.plan_text
                            ? modalPlan.plan_text
                            : (typeof modalPlan.plan_verificado === 'object'
                                ? JSON.stringify(modalPlan.plan_verificado, null, 2)
                                : modalPlan.plan_verificado)}
                        </pre>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Action Buttons */}
                <div className="space-y-4">
                  {/* Primary Actions Row */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Attach to Documents */}
                    <Card className="border-2 border-orange-200 bg-orange-50">
                      <CardContent className="pt-6">
                        <Button
                          onClick={generateNutritionPDF}
                          disabled={generatingPDF}
                          className="w-full bg-orange-600 hover:bg-orange-700"
                        >
                          {generatingPDF ? (
                            <>
                              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                              Adjuntando...
                            </>
                          ) : (
                            <>
                              <Upload className="h-4 w-4 mr-2" />
                              Adjuntar a Documentos
                            </>
                          )}
                        </Button>
                        <p className="text-xs text-gray-600 mt-2 text-center">
                          Genera PDF y lo sube al dashboard del usuario
                        </p>
                      </CardContent>
                    </Card>

                    {/* Send Email */}
                    <Card className="border-2 border-blue-200 bg-blue-50">
                      <CardContent className="pt-6">
                        <Button
                          onClick={() => sendNutritionByEmail(selectedClient.id)}
                          disabled={sendingNutrition === 'email'}
                          className="w-full bg-blue-600 hover:bg-blue-700"
                        >
                          {sendingNutrition === 'email' ? (
                            <>
                              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                              Enviando...
                            </>
                          ) : (
                            <>
                              <Mail className="h-4 w-4 mr-2" />
                              Enviar Email
                            </>
                          )}
                        </Button>
                        <p className="text-xs text-gray-600 mt-2 text-center">
                          Envía el plan por correo electrónico
                        </p>
                      </CardContent>
                    </Card>

                  </div>
                </div>
              </div>

              {/* Footer del Modal */}
              <div className="p-4 border-t bg-gray-50 flex justify-between items-center">
                <Button 
                  variant="outline" 
                  className="border-red-300 text-red-600 hover:bg-red-50"
                  onClick={async () => {
                    if (window.confirm('⚠️ ¿Estás seguro de que quieres ELIMINAR COMPLETAMENTE este plan de nutrición?\n\nEsta acción NO se puede deshacer. Se eliminará:\n- El plan de nutrición\n- El PDF asociado (si existe)\n- Todas las referencias\n\n¿Continuar?')) {
                      try {
                        await axios.delete(
                          `${API}/admin/users/${selectedClient.id}/nutrition/${modalPlan.id}`,
                          {
                            headers: { Authorization: `Bearer ${token}` },
                            withCredentials: true
                          }
                        );
                        alert('✅ Plan de nutrición eliminado completamente');
                        closePlanModal();
                        await loadNutritionPlan(selectedClient.id);
                        await loadClientDetails(selectedClient.id);
                      } catch (error) {
                        console.error('Error eliminando plan:', error);
                        alert('❌ Error al eliminar el plan: ' + (error.response?.data?.detail || error.message));
                      }
                    }
                  }}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Eliminar Plan
                </Button>
                <Button variant="outline" onClick={closePlanModal}>
                  Cerrar
                </Button>
              </div>
            </>
          ) : (
            <div className="p-6 text-center">
              <p className="text-gray-500">Cargando plan de nutrición...</p>
            </div>
          )}
        </DialogContent>
      </Dialog>


      {/* Training Plan Modal */}
      <Dialog open={showTrainingModal} onOpenChange={(open) => {
        if (!open) {
          setShowTrainingModal(false);
          setEditingTraining(false);
          setModalTrainingPlan(null);
        }
      }}>
        <DialogContent className="max-w-[95vw] w-[95vw] h-[95vh] max-h-[95vh] p-0 overflow-hidden flex flex-col">
          {modalTrainingPlan ? (
            <>
              {/* Header del Modal */}
              <DialogHeader className="p-6 border-b bg-gradient-to-r from-blue-50 to-cyan-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 rounded-full flex items-center justify-center bg-blue-500 text-white font-bold text-xl">
                      🏋️
                    </div>
                    <div>
                      <DialogTitle className="text-2xl font-bold">
                        Plan de Entrenamiento - {(() => {
                          const monthNames = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                                             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
                          return `${monthNames[modalTrainingPlan.month]} ${modalTrainingPlan.year}`;
                        })()}
                      </DialogTitle>
                      <DialogDescription className="text-sm">
                        Generado: {new Date(modalTrainingPlan.generated_at).toLocaleDateString('es-ES')} • 
                        Cliente: {selectedClient?.name}
                      </DialogDescription>
                    </div>
                  </div>
                  
                  {/* Status badges */}
                  <div className="flex gap-2">
                    {modalTrainingPlan.pdf_id && (
                      <Badge className="bg-blue-500">📄 PDF</Badge>
                    )}
                    {modalTrainingPlan.sent_email && (
                      <Badge className="bg-green-500">✉️ Email</Badge>
                    )}
                    {modalTrainingPlan.sent_whatsapp && (
                      <Badge className="bg-teal-500">💬 WhatsApp</Badge>
                    )}
                    {modalTrainingPlan.edited && (
                      <Badge className="bg-purple-500">✏️ Editado</Badge>
                    )}
                  </div>
                </div>
              </DialogHeader>

              {/* Content del Modal - Scrollable */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {/* Status Details */}
                <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <div className="text-3xl mb-1">{modalTrainingPlan.pdf_id ? '✅' : '❌'}</div>
                    <div className="text-sm text-gray-600 font-medium">PDF Generado</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl mb-1">{modalTrainingPlan.sent_email ? '✅' : '❌'}</div>
                    <div className="text-sm text-gray-600 font-medium">Enviado Email</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl mb-1">{modalTrainingPlan.sent_whatsapp ? '✅' : '❌'}</div>
                    <div className="text-sm text-gray-600 font-medium">Enviado WhatsApp</div>
                  </div>
                </div>

                {/* Editor/Viewer */}
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle>Plan Final</CardTitle>
                    <div className="flex gap-2">
                      {!editingTraining ? (
                        <>
                          <Button
                            onClick={() => {
                              // Close the modal first, then open chat
                              setShowTrainingModal(false);
                              setTimeout(() => setShowTrainingChat(true), 100);
                            }}
                            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                          >
                            <MessageSquare className="h-4 w-4 mr-2" />
                            💬 Chat con IA
                          </Button>
                          <Button
                            onClick={() => setEditingTraining(true)}
                            variant="outline"
                          >
                            <Edit className="h-4 w-4 mr-2" />
                            Editar Manual
                          </Button>
                        </>
                      ) : (
                        <>
                          <Button
                            onClick={() => {
                              setEditingTraining(false);
                              setTrainingContent(modalTrainingPlan.plan_text || modalTrainingPlan.plan_final);
                            }}
                            variant="outline"
                          >
                            Cancelar
                          </Button>
                          <Button onClick={saveTrainingChanges}>
                            <Save className="h-4 w-4 mr-2" />
                            Guardar
                          </Button>
                        </>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    {editingTraining ? (
                      <Textarea
                        value={trainingContent}
                        onChange={(e) => setTrainingContent(e.target.value)}
                        rows={25}
                        className="font-mono text-sm"
                      />
                    ) : (
                      <div className="prose max-w-none">
                        <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
                          {modalTrainingPlan.plan_text 
                            ? modalTrainingPlan.plan_text
                            : (typeof modalTrainingPlan.plan_final === 'object' 
                                ? JSON.stringify(modalTrainingPlan.plan_final, null, 2)
                                : modalTrainingPlan.plan_final)}
                        </pre>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Action Buttons */}
                <div className="space-y-4">
                  {/* Primary Actions Row */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Attach to Documents */}
                    <Card className="border-2 border-blue-200 bg-blue-50">
                      <CardContent className="pt-6">
                        <Button
                          onClick={() => generateTrainingPDF(modalTrainingPlan.id)}
                          disabled={generatingTrainingPDF}
                          className="w-full bg-blue-600 hover:bg-blue-700"
                        >
                          {generatingTrainingPDF ? (
                            <>
                              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                              Adjuntando...
                            </>
                          ) : (
                            <>
                              <Upload className="h-4 w-4 mr-2" />
                              Adjuntar a Documentos
                            </>
                          )}
                        </Button>
                        <p className="text-xs text-gray-600 mt-2 text-center">
                          Genera PDF y lo sube al dashboard del usuario
                        </p>
                      </CardContent>
                    </Card>

                    {/* Send Email */}
                    <Card className="border-2 border-green-200 bg-green-50">
                      <CardContent className="pt-6">
                        <Button
                          onClick={() => sendTrainingEmail(modalTrainingPlan.id)}
                          disabled={sendingTraining === 'email'}
                          className="w-full bg-green-600 hover:bg-green-700"
                        >
                          {sendingTraining === 'email' ? (
                            <>
                              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                              Enviando...
                            </>
                          ) : (
                            <>
                              <Mail className="h-4 w-4 mr-2" />
                              Enviar Email
                            </>
                          )}
                        </Button>
                        <p className="text-xs text-gray-600 mt-2 text-center">
                          Envía el plan por correo electrónico
                        </p>
                      </CardContent>
                    </Card>

                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="p-6 text-center">
              <p className="text-gray-500">Cargando plan de entrenamiento...</p>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Training Plan Chat Dialog */}
      {modalTrainingPlan && (
        <TrainingPlanChatDialog
          isOpen={showTrainingChat}
          onClose={() => {
            setShowTrainingChat(false);
            // Reopen the training modal after chat closes
            setTimeout(() => setShowTrainingModal(true), 100);
          }}
          planId={modalTrainingPlan.id}
          planContent={modalTrainingPlan.plan_text || modalTrainingPlan.plan_final}
          token={token}
          onPlanUpdated={(updatedPlan) => {
            // Update the modal display
            setModalTrainingPlan(prev => ({ ...prev, plan_final: updatedPlan }));
            setTrainingContent(updatedPlan);
            // Reload the full plan from server
            if (selectedClient) {
              loadTrainingPlans(selectedClient._id);
            }
          }}
        />
      )}

      {/* Nutrition Plan Chat Dialog */}
      {modalPlan && (
        <NutritionPlanChatDialog
          isOpen={showNutritionChat}
          onClose={() => {
            setShowNutritionChat(false);
            // Reopen the nutrition modal after chat closes
            setTimeout(() => setShowNutritionModal(true), 100);
          }}
          planId={modalPlan.id}
          planContent={modalPlan.plan_text || modalPlan.plan_verificado}
          token={token}
          onPlanUpdated={(updatedPlan) => {
            // Update the modal display
            setModalPlan(prev => ({ ...prev, plan_verificado: updatedPlan, plan_text: updatedPlan }));
            setNutritionContent(updatedPlan);
            // Reload the full plan from server
            if (selectedClient) {
              loadNutritionPlan(selectedClient.id);
            }
          }}
        />
      )}

      {/* History Item Details Modal */}
      {selectedHistoryItem && (
        <Dialog open={!!selectedHistoryItem} onOpenChange={() => setSelectedHistoryItem(null)}>
          <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                {selectedHistoryItem.type === 'diagnosis' && '🩺 Cuestionario de Diagnóstico'}
                {selectedHistoryItem.type === 'nutrition' && '📝 Cuestionario de Nutrición'}
                {selectedHistoryItem.type === 'followup' && '📊 Seguimiento Mensual'}
              </DialogTitle>
              <DialogDescription>
                Fecha: {new Date(selectedHistoryItem.data?.submitted_at || selectedHistoryItem.data?.submission_date).toLocaleDateString('es-ES', {
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric'
                })}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 mt-4">
              {/* Mostrar contenido según el tipo */}
              {selectedHistoryItem.type === 'diagnosis' && (() => {
                const data = selectedHistoryItem.data?.data || {};
                return (
                  <div className="space-y-4">
                    <div className="bg-green-50 p-4 rounded-lg">
                      <h4 className="font-bold mb-3">Información del Diagnóstico</h4>
                      {Object.entries(data).map(([key, value]) => (
                        <div key={key} className="mb-2">
                          <div className="text-sm font-semibold text-gray-700 capitalize">{key.replace(/_/g, ' ')}:</div>
                          <div className="text-gray-900">{typeof value === 'object' ? JSON.stringify(value, null, 2) : value}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })()}

              {selectedHistoryItem.type === 'nutrition' && (() => {
                const data = selectedHistoryItem.data?.data || {};
                return (
                  <div className="space-y-4">
                    <div className="bg-blue-50 p-4 rounded-lg max-h-[600px] overflow-y-auto">
                      <h4 className="font-bold mb-3 text-lg">📋 Todas las Respuestas del Cuestionario de Nutrición</h4>
                      <div className="space-y-3">
                        {Object.entries(data).map(([key, value]) => {
                          if (!value) return null;
                          
                          // Formatear el nombre del campo
                          const fieldName = key
                            .replace(/_/g, ' ')
                            .replace(/\b\w/g, l => l.toUpperCase());
                          
                          // Manejar objetos (como medidas_corporales)
                          let displayValue;
                          if (typeof value === 'object' && value !== null) {
                            displayValue = (
                              <div className="ml-4 mt-1 space-y-1">
                                {Object.entries(value).map(([subKey, subValue]) => (
                                  <div key={subKey} className="text-sm">
                                    <span className="font-medium">{subKey.replace(/_/g, ' ')}:</span> {String(subValue)}
                                  </div>
                                ))}
                              </div>
                            );
                          } else {
                            displayValue = <span className="text-gray-900">{String(value)}</span>;
                          }
                          
                          return (
                            <div key={key} className="border-b border-blue-200 pb-2">
                              <p className="text-sm font-semibold text-blue-900">{fieldName}:</p>
                              {displayValue}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                );
              })()}

              {selectedHistoryItem.type === 'followup' && (() => {
                const followUp = selectedHistoryItem.data;
                return (
                  <div className="space-y-4">
                    {followUp.measurements && (
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h4 className="font-bold mb-3">📊 Mediciones</h4>
                        <div className="grid grid-cols-4 gap-3">
                          {Object.entries(followUp.measurements).map(([key, value]) => (
                            <div key={key}>
                              <div className="text-xs text-gray-600 capitalize">{key.replace(/_/g, ' ')}</div>
                              <div className="font-bold">{value}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="bg-green-50 p-4 rounded-lg">
                      <h4 className="font-bold mb-3">💪 Adherencia</h4>
                      <div className="space-y-2">
                        <div><strong>Entrenamiento:</strong> {followUp.adherence?.constancia_entrenamiento}</div>
                        <div><strong>Alimentación:</strong> {followUp.adherence?.seguimiento_alimentacion}</div>
                      </div>
                    </div>

                    <div className="bg-yellow-50 p-4 rounded-lg">
                      <h4 className="font-bold mb-3">😊 Bienestar</h4>
                      <div className="space-y-2">
                        <div><strong>Energía/Ánimo:</strong> {followUp.wellbeing?.energia_animo_motivacion}</div>
                        <div><strong>Sueño/Estrés:</strong> {followUp.wellbeing?.sueno_estres}</div>
                        {followUp.wellbeing?.factores_externos && (
                          <div><strong>Factores externos:</strong> {followUp.wellbeing.factores_externos}</div>
                        )}
                      </div>
                    </div>

                    <div className="bg-purple-50 p-4 rounded-lg">
                      <h4 className="font-bold mb-3">📈 Cambios Percibidos</h4>
                      <div className="space-y-2">
                        <div><strong>Molestias/Dolor:</strong> {followUp.changes_perceived?.molestias_dolor_lesion}</div>
                        <div><strong>Cambios corporales:</strong> {followUp.changes_perceived?.cambios_corporales}</div>
                        <div><strong>Fuerza/Rendimiento:</strong> {followUp.changes_perceived?.fuerza_rendimiento}</div>
                      </div>
                    </div>

                    <div className="bg-pink-50 p-4 rounded-lg">
                      <h4 className="font-bold mb-3">💬 Feedback</h4>
                      <div className="space-y-2">
                        <div><strong>Objetivo próximo mes:</strong> {followUp.feedback?.objetivo_proximo_mes}</div>
                        <div><strong>Cambios deseados:</strong> {followUp.feedback?.cambios_deseados}</div>
                        {followUp.feedback?.comentarios_adicionales && (
                          <div><strong>Comentarios:</strong> {followUp.feedback.comentarios_adicionales}</div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })()}
            </div>

            <div className="flex gap-2 justify-end mt-6">
              <Button onClick={() => setSelectedHistoryItem(null)} variant="outline">
                Cerrar
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Follow-up Details Modal */}
      {selectedFollowUp && (
        <Dialog open={!!selectedFollowUp} onOpenChange={() => setSelectedFollowUp(null)}>
          <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <MessageSquare className="h-6 w-6 text-purple-600" />
                Seguimiento Mensual - {new Date(selectedFollowUp.submission_date).toLocaleDateString('es-ES')}
              </DialogTitle>
              <DialogDescription>
                Hace {selectedFollowUp.days_since_last_plan} días desde el último plan • Cliente: {selectedClient?.name}
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-6">
              {/* Measurements Section */}
              {selectedFollowUp.measurements && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      📊 Mediciones Actuales
                      <Badge className="ml-2">{
                        selectedFollowUp.measurement_type === 'smart_scale' ? '📱 Báscula inteligente' :
                        selectedFollowUp.measurement_type === 'tape_measure' ? '📏 Cinta métrica' : 'Sin medición'
                      }</Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {Object.entries(selectedFollowUp.measurements).map(([key, value]) => (
                        <div key={key} className="bg-gray-50 p-3 rounded-lg">
                          <div className="text-xs text-gray-500 mb-1 capitalize">{key.replace(/_/g, ' ')}</div>
                          <div className="text-lg font-bold">{value}</div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Adherence */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">💪 Adherencia al Plan</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="border-b pb-3">
                    <div className="font-semibold text-gray-700 mb-1">Constancia en entrenamiento</div>
                    <div className="text-gray-900">{selectedFollowUp.adherence?.constancia_entrenamiento}</div>
                  </div>
                  <div>
                    <div className="font-semibold text-gray-700 mb-1">Seguimiento de alimentación</div>
                    <div className="text-gray-900">{selectedFollowUp.adherence?.seguimiento_alimentacion}</div>
                  </div>
                </CardContent>
              </Card>

              {/* Wellbeing */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">😊 Bienestar General</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="border-b pb-3">
                    <div className="font-semibold text-gray-700 mb-1">Energía, ánimo y motivación</div>
                    <div className="text-gray-900">{selectedFollowUp.wellbeing?.energia_animo_motivacion}</div>
                  </div>
                  <div className="border-b pb-3">
                    <div className="font-semibold text-gray-700 mb-1">Sueño y estrés</div>
                    <div className="text-gray-900">{selectedFollowUp.wellbeing?.sueno_estres}</div>
                  </div>
                  {selectedFollowUp.wellbeing?.factores_externos && (
                    <div>
                      <div className="font-semibold text-gray-700 mb-1">Factores externos</div>
                      <div className="text-gray-900">{selectedFollowUp.wellbeing.factores_externos}</div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Changes Perceived */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">📈 Cambios Percibidos</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="border-b pb-3">
                    <div className="font-semibold text-gray-700 mb-1">Molestias, dolor o lesión</div>
                    <div className="text-gray-900">{selectedFollowUp.changes_perceived?.molestias_dolor_lesion}</div>
                  </div>
                  <div className="border-b pb-3">
                    <div className="font-semibold text-gray-700 mb-1">Cambios corporales</div>
                    <div className="text-gray-900">{selectedFollowUp.changes_perceived?.cambios_corporales}</div>
                  </div>
                  <div>
                    <div className="font-semibold text-gray-700 mb-1">Fuerza y rendimiento</div>
                    <div className="text-gray-900">{selectedFollowUp.changes_perceived?.fuerza_rendimiento}</div>
                  </div>
                </CardContent>
              </Card>

              {/* Feedback */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">💬 Feedback y Objetivos</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="border-b pb-3">
                    <div className="font-semibold text-gray-700 mb-1">Objetivo para el próximo mes</div>
                    <div className="text-gray-900">{selectedFollowUp.feedback?.objetivo_proximo_mes}</div>
                  </div>
                  <div className="border-b pb-3">
                    <div className="font-semibold text-gray-700 mb-1">Cambios deseados en el plan</div>
                    <div className="text-gray-900">{selectedFollowUp.feedback?.cambios_deseados}</div>
                  </div>
                  {selectedFollowUp.feedback?.comentarios_adicionales && (
                    <div>
                      <div className="font-semibold text-gray-700 mb-1">Comentarios adicionales</div>
                      <div className="text-gray-900">{selectedFollowUp.feedback.comentarios_adicionales}</div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Analysis Section */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="text-lg">Análisis del Seguimiento</CardTitle>
                  <div className="flex gap-2">
                    {!editingAnalysis ? (
                      <>
                        <Button
                          onClick={() => {
                            setEditingAnalysis(true);
                            setFollowUpAnalysis(selectedFollowUp.ai_analysis || '');
                          }}
                          variant="outline"
                          size="sm"
                        >
                          <Edit className="h-4 w-4 mr-2" />
                          Editar
                        </Button>
                        <Button
                          onClick={async () => {
                            if (!selectedFollowUp.id || !selectedClient?.id) return;
                            
                            setGeneratingAnalysis(true);
                            try {
                              const response = await axios.post(
                                `${API}/admin/users/${selectedClient.id}/followups/${selectedFollowUp.id}/analyze-with-ia`,
                                {},
                                {
                                  headers: { Authorization: `Bearer ${token}` },
                                  withCredentials: true
                                }
                              );
                              setFollowUpAnalysis(response.data.analysis);
                              setSelectedFollowUp({...selectedFollowUp, ai_analysis: response.data.analysis, status: 'analyzed'});
                              alert('✅ Análisis generado con IA');
                            } catch (error) {
                              alert(`Error: ${error.response?.data?.detail || error.message}`);
                            } finally {
                              setGeneratingAnalysis(false);
                            }
                          }}
                          disabled={generatingAnalysis}
                          className="bg-purple-600 hover:bg-purple-700"
                          size="sm"
                        >
                          {generatingAnalysis ? (
                            <>
                              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                              Generando...
                            </>
                          ) : (
                            <>
                              🤖 Generar con IA
                            </>
                          )}
                        </Button>
                      </>
                    ) : (
                      <>
                        <Button
                          onClick={() => {
                            setEditingAnalysis(false);
                            setFollowUpAnalysis(selectedFollowUp.ai_analysis || '');
                          }}
                          variant="outline"
                          size="sm"
                        >
                          Cancelar
                        </Button>
                        <Button
                          onClick={async () => {
                            if (!selectedFollowUp.id || !selectedClient?.id) return;
                            
                            try {
                              await axios.patch(
                                `${API}/admin/users/${selectedClient.id}/followups/${selectedFollowUp.id}/analysis`,
                                { analysis: followUpAnalysis },
                                {
                                  headers: { Authorization: `Bearer ${token}` },
                                  withCredentials: true
                                }
                              );
                              setSelectedFollowUp({...selectedFollowUp, ai_analysis: followUpAnalysis, ai_analysis_edited: true});
                              setEditingAnalysis(false);
                              alert('✅ Análisis guardado');
                              // Reload follow-ups to update the list
                              loadFollowUps(selectedClient.id);
                            } catch (error) {
                              alert(`Error: ${error.response?.data?.detail || error.message}`);
                            }
                          }}
                          size="sm"
                        >
                          <Save className="h-4 w-4 mr-2" />
                          Guardar
                        </Button>
                      </>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  {editingAnalysis ? (
                    <Textarea
                      value={followUpAnalysis}
                      onChange={(e) => setFollowUpAnalysis(e.target.value)}
                      rows={10}
                      placeholder="Escribe tu análisis del seguimiento aquí..."
                      className="w-full"
                    />
                  ) : (
                    <div className="min-h-[200px] p-4 bg-gray-50 rounded-lg">
                      {selectedFollowUp.ai_analysis ? (
                        <div className="whitespace-pre-wrap font-sans text-sm leading-relaxed prose prose-sm max-w-none">
                          {selectedFollowUp.ai_analysis}
                        </div>
                      ) : (
                        <p className="text-gray-500 italic">
                          No hay análisis disponible. Haz clic en "Editar" para agregar uno manualmente o "🤖 Generar con IA" para crear un análisis automático basado en el seguimiento.
                        </p>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Actions */}
              <div className="flex justify-between items-center gap-2 pt-4 border-t">
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setSelectedFollowUp(null)}
                  >
                    Cerrar
                  </Button>
                </div>
                
                {selectedFollowUp.ai_analysis && (
                  <div className="flex gap-2">
                    {/* Send Email Button */}
                    <Button
                      variant="outline"
                      className="border-blue-300 text-blue-600 hover:bg-blue-50"
                      onClick={async () => {
                        try {
                          const response = await axios.post(
                            `${API}/admin/users/${selectedClient.id}/followups/${selectedFollowUp.id}/send-email`,
                            {},
                            {
                              headers: { Authorization: `Bearer ${token}` },
                              withCredentials: true
                            }
                          );
                          alert(`✅ ${response.data.message}`);
                        } catch (error) {
                          console.error('Error sending email:', error);
                          alert('❌ Error al enviar email: ' + (error.response?.data?.detail || error.message));
                        }
                      }}
                    >
                      📧 Enviar Email
                    </Button>
                    
                    {/* Send WhatsApp Button */}
                    <Button
                      variant="outline"
                      className="border-green-300 text-green-600 hover:bg-green-50"
                      onClick={async () => {
                        try {
                          const response = await axios.post(
                            `${API}/admin/users/${selectedClient.id}/followups/${selectedFollowUp.id}/send-whatsapp`,
                            {},
                            {
                              headers: { Authorization: `Bearer ${token}` },
                              withCredentials: true
                            }
                          );
                          window.open(response.data.whatsapp_url, '_blank');
                        } catch (error) {
                          console.error('Error generating WhatsApp:', error);
                          alert('❌ Error al generar WhatsApp: ' + (error.response?.data?.detail || error.message));
                        }
                      }}
                    >
                      💬 Enviar WhatsApp
                    </Button>
                    
                    {/* Generate PDF Button */}
                    <Button
                      variant="outline"
                      className="border-red-300 text-red-600 hover:bg-red-50"
                      onClick={async () => {
                        try {
                          const response = await axios.post(
                            `${API}/admin/users/${selectedClient.id}/followups/${selectedFollowUp.id}/generate-pdf`,
                            {},
                            {
                              headers: { Authorization: `Bearer ${token}` },
                              withCredentials: true
                            }
                          );
                          alert(`✅ ${response.data.message}`);
                          // Reload client details to show new PDF
                          loadClientDetails(selectedClient.id);
                        } catch (error) {
                          console.error('Error generating PDF:', error);
                          alert('❌ Error al generar PDF: ' + (error.response?.data?.detail || error.message));
                        }
                      }}
                    >
                      📄 Generar PDF
                    </Button>
                  </div>
                )}
                
                <Button
                  onClick={async () => {
                    if (!selectedFollowUp.ai_analysis) {
                      alert('⚠️ Primero debes analizar el seguimiento antes de generar un nuevo plan');
                      return;
                    }
                    
                    if (!window.confirm('¿Generar un nuevo plan de nutrición basado en el análisis de este seguimiento? Esto reemplazará el plan actual del cliente.')) {
                      return;
                    }
                    
                    setGeneratingPlan(true);
                    try {
                      const response = await axios.post(
                        `${API}/admin/users/${selectedClient.id}/followups/${selectedFollowUp.id}/generate-plan`,
                        {},
                        {
                          headers: { Authorization: `Bearer ${token}` },
                          withCredentials: true
                        }
                      );
                      
                      alert(`✅ ${response.data.message}`);
                      setSelectedFollowUp({...selectedFollowUp, status: 'plan_generated', new_plan_id: response.data.plan_id});
                      setSelectedFollowUp(null); // Close modal
                      loadNutritionPlan(selectedClient.id); // Reload nutrition plans
                      loadFollowUps(selectedClient.id); // Reload follow-ups to update status
                    } catch (error) {
                      console.error('Error generating plan:', error);
                      alert(`❌ Error: ${error.response?.data?.detail || error.message}`);
                    } finally {
                      setGeneratingPlan(false);
                    }
                  }}
                  disabled={generatingPlan || !selectedFollowUp.ai_analysis}
                  className="bg-green-600 hover:bg-green-700 disabled:opacity-50"
                >
                  {generatingPlan ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Generando plan...
                    </>
                  ) : (
                    <>
                      🥗 Generar Nuevo Plan
                    </>
                  )}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
      {/* Manual Payment Modal */}
      {showPaymentModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg w-full max-w-md">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold">💰 Registrar Pago Manual</h3>
                <Button size="sm" variant="ghost" onClick={() => setShowPaymentModal(false)}>
                  <X className="h-5 w-5" />
                </Button>
              </div>

              <div className="space-y-4">
                <div>
                  <Label>Concepto *</Label>
                  <Input
                    value={newManualPayment.concepto}
                    onChange={(e) => setNewManualPayment({...newManualPayment, concepto: e.target.value})}
                    placeholder="Ej: Pago de cliente X"
                  />
                </div>

                <div>
                  <Label>Monto (€) *</Label>
                  <Input
                    type="number"
                    value={newManualPayment.amount}
                    onChange={(e) => setNewManualPayment({...newManualPayment, amount: e.target.value})}
                    placeholder="0"
                  />
                </div>

                <div>
                  <Label>Fecha *</Label>
                  <Input
                    type="date"
                    value={newManualPayment.fecha}
                    onChange={(e) => setNewManualPayment({...newManualPayment, fecha: e.target.value})}
                  />
                </div>

                <div>
                  <Label>Método de Pago *</Label>
                  <select
                    value={newManualPayment.metodo_pago}
                    onChange={(e) => setNewManualPayment({...newManualPayment, metodo_pago: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="Transferencia">💳 Transferencia (Caja A)</option>
                    <option value="Bizum">📱 Bizum (Caja A)</option>
                    <option value="Efectivo">💵 Efectivo (Caja B)</option>
                    <option value="Stripe">🔷 Stripe (Caja A)</option>
                  </select>
                </div>

                <div>
                  <Label>Notas</Label>
                  <Textarea
                    value={newManualPayment.notas}
                    onChange={(e) => setNewManualPayment({...newManualPayment, notas: e.target.value})}
                    placeholder="Notas adicionales..."
                    rows={2}
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <Button
                    onClick={createManualPayment}
                    className="flex-1 bg-green-600 hover:bg-green-700"
                  >
                    <DollarSign className="h-4 w-4 mr-2" />
                    Registrar Pago
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowPaymentModal(false)}
                    className="flex-1"
                  >
                    Cancelar
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Manual Payment Modal */}
      {editingManualPayment && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg w-full max-w-md">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold">✏️ Editar Pago</h3>
                <Button size="sm" variant="ghost" onClick={() => setEditingManualPayment(null)}>
                  <X className="h-5 w-5" />
                </Button>
              </div>

              <div className="space-y-4">
                <div>
                  <Label>Concepto *</Label>
                  <Input
                    value={editingManualPayment.concepto}
                    onChange={(e) => setEditingManualPayment({...editingManualPayment, concepto: e.target.value})}
                  />
                </div>

                <div>
                  <Label>Monto (€) *</Label>
                  <Input
                    type="number"
                    value={editingManualPayment.amount}
                    onChange={(e) => setEditingManualPayment({...editingManualPayment, amount: e.target.value})}
                  />
                </div>

                <div>
                  <Label>Fecha *</Label>
                  <Input
                    type="date"
                    value={editingManualPayment.fecha}
                    onChange={(e) => setEditingManualPayment({...editingManualPayment, fecha: e.target.value})}
                  />
                </div>

                <div>
                  <Label>Método de Pago *</Label>
                  <select
                    value={editingManualPayment.metodo_pago}
                    onChange={(e) => setEditingManualPayment({...editingManualPayment, metodo_pago: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="Transferencia">💳 Transferencia (Caja A)</option>
                    <option value="Bizum">📱 Bizum (Caja A)</option>
                    <option value="Efectivo">💵 Efectivo (Caja B)</option>
                    <option value="Stripe">🔷 Stripe (Caja A)</option>
                  </select>
                </div>

                <div>
                  <Label>Notas</Label>
                  <Textarea
                    value={editingManualPayment.notas}
                    onChange={(e) => setEditingManualPayment({...editingManualPayment, notas: e.target.value})}
                    rows={2}
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <Button
                    onClick={updateManualPayment}
                    className="flex-1 bg-blue-600 hover:bg-blue-700"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Actualizar
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setEditingManualPayment(null)}
                    className="flex-1"
                  >
                    Cancelar
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal para ver/editar informe de seguimiento */}
      {showReportModal && selectedReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-2xl font-bold">📊 Informe de Seguimiento</h2>
              <button
                onClick={() => setShowReportModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
              <div className="mb-4 flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const newText = prompt('Editar contenido del informe:', selectedReport.report_text);
                    if (newText && newText !== selectedReport.report_text) {
                      updateFollowUpReport(selectedReport._id, newText);
                    }
                  }}
                >
                  ✏️ Editar
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="text-red-600 hover:text-red-700"
                  onClick={() => deleteFollowUpReport(selectedReport._id)}
                >
                  🗑️ Eliminar
                </Button>
              </div>
              
              <div className="prose max-w-none">
                <pre className="whitespace-pre-wrap font-sans text-sm bg-gray-50 p-4 rounded">
                  {selectedReport.report_text}
                </pre>
              </div>
            </div>
            
            <div className="flex justify-end gap-2 p-6 border-t">
              <Button
                variant="outline"
                onClick={() => setShowReportModal(false)}
              >
                Cerrar
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* EDN360 Input Preview Modal - FASE 2 */}
      {showEDN360InputModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b bg-indigo-50">
              <h2 className="text-2xl font-bold text-indigo-900 flex items-center gap-2">
                <FileText className="h-6 w-6" />
                EDN360 Input Preview
              </h2>
              <button
                onClick={() => setShowEDN360InputModal(false)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ✕
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-160px)]">
              {loadingEDN360Input ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
                  <p className="text-gray-600">Construyendo EDN360Input...</p>
                </div>
              ) : edn360InputData ? (
                <div className="space-y-4">
                  {/* Metadata */}
                  <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200">
                    <h3 className="font-bold text-indigo-900 mb-2">📊 Metadata</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">User ID:</span>
                        <p className="font-mono text-xs">{edn360InputData.user_id}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Cuestionarios:</span>
                        <p className="font-bold">{edn360InputData.metadata.questionnaires_count}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Inicial:</span>
                        <p className="font-bold">{edn360InputData.metadata.has_initial ? '✅ Sí' : '❌ No'}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Followups:</span>
                        <p className="font-bold">{edn360InputData.metadata.has_followups ? '✅ Sí' : '❌ No'}</p>
                      </div>
                    </div>
                  </div>
                  
                  {/* JSON Viewer */}
                  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-bold text-gray-900">📄 EDN360Input JSON</h3>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          navigator.clipboard.writeText(
                            JSON.stringify(edn360InputData.edn360_input, null, 2)
                          );
                          alert('JSON copiado al portapapeles');
                        }}
                      >
                        📋 Copiar JSON
                      </Button>
                    </div>
                    <pre className="bg-gray-900 text-green-400 p-4 rounded overflow-x-auto text-xs max-h-[500px] overflow-y-auto">
                      {JSON.stringify(edn360InputData.edn360_input, null, 2)}
                    </pre>
                  </div>
                  
                  {/* Info Box */}
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                    <p className="text-sm text-blue-900">
                      <strong>ℹ️ FASE 2:</strong> Este JSON es el contrato estándar que usaremos 
                      para llamar a los Workflows de OpenAI (E1-E9, N0-N8). Puedes copiarlo y 
                      testearlo manualmente con tus Workflows.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-600">No se pudo cargar el EDN360Input</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Generation Progress Modal */}
      {showGenerationProgress && currentJobId && (
        <GenerationProgressModal
          jobId={currentJobId}
          onComplete={handleGenerationComplete}
          onError={handleGenerationError}
          onClose={handleGenerationClose}
        />
      )}

    </div>
  );
};

export default AdminDashboard;
