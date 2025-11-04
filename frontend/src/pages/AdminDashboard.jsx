import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
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
  ChevronDown
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
  const [selectedPlan, setSelectedPlan] = useState(null); // Plan seleccionado actualmente
  const [editingNutrition, setEditingNutrition] = useState(false);
  const [nutritionContent, setNutritionContent] = useState('');
  const [generatingPDF, setGeneratingPDF] = useState(false);
  const [sendingNutrition, setSendingNutrition] = useState(null);


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

  useEffect(() => {
    if (selectedClient) {
      // Reset accordion state when changing clients
      setSelectedPlan(null);
      loadClientDetails(selectedClient.id);
      loadNutritionPlan(selectedClient.id);
    }
  }, [selectedClient]);

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
      console.error('Error loading client details:', error);
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

  // Load nutrition plans (historial)
  const loadNutritionPlan = async (userId) => {
    try {
      const response = await axios.get(`${API}/admin/users/${userId}/nutrition`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setNutritionPlans(response.data.plans || []);
      // REMOVED: setSelectedPlan(null) - esto causaba que el acordeón se cerrara inmediatamente
      // El acordeón ahora mantiene su estado al recargar datos
    } catch (error) {
      if (error.response?.status !== 404) {
        console.error('Error loading nutrition plan:', error);
      }
      setNutritionPlans([]);
      // REMOVED: setSelectedPlan(null) - dejar que el usuario controle el estado del acordeón
    }
  };

  // Save nutrition plan changes
  const saveNutritionChanges = async () => {
    if (!selectedPlan) return;
    
    try {
      await axios.patch(
        `${API}/admin/users/${selectedClient.id}/nutrition/${selectedPlan.id}`,
        { plan_content: nutritionContent },
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      alert('✅ Plan de nutrición actualizado');
      setEditingNutrition(false);
      loadNutritionPlan(selectedClient.id);
    } catch (error) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  // Generate PDF and upload to user documents
  const generateNutritionPDF = async () => {
    if (!selectedPlan) {
      alert('No hay plan seleccionado');
      return;
    }
    
    if (!window.confirm('¿Generar PDF y subirlo a los documentos del usuario?')) {
      return;
    }

    setGeneratingPDF(true);
    try {
      const response = await axios.post(
        `${API}/admin/users/${selectedClient.id}/nutrition-pdf?plan_id=${selectedPlan.id}`,
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

  // Send nutrition plan by email
  const sendNutritionByEmail = async (userId) => {
    if (!selectedPlan) {
      alert('No hay plan seleccionado');
      return;
    }
    
    if (!window.confirm('¿Enviar el plan de nutrición por email al cliente?')) {
      return;
    }

    setSendingNutrition('email');
    try {
      const response = await axios.post(
        `${API}/admin/users/${userId}/nutrition/send-email?plan_id=${selectedPlan.id}`,
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
  const sendNutritionByWhatsApp = async (userId) => {
    if (!selectedPlan) {
      alert('No hay plan seleccionado');
      return;
    }
    
    setSendingNutrition('whatsapp');
    try {
      const response = await axios.get(
        `${API}/admin/users/${userId}/nutrition/whatsapp-link?plan_id=${selectedPlan.id}`,
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      
      if (response.data.whatsapp_link) {
        window.open(response.data.whatsapp_link, '_blank');
        alert('✅ Link de WhatsApp generado. Se abrirá en una nueva ventana.');
        // Recargar el plan para actualizar los estados
        await loadNutritionPlan(userId);
      }
    } catch (error) {
      alert(`Error al generar link de WhatsApp: ${error.response?.data?.detail || error.message}`);
    } finally {
      setSendingNutrition(null);
    }
  };

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

  const handleArchiveClient = async (clientId) => {
    const reason = prompt('Razón del archivado (opcional):');
    try {
      await axios.post(`${API}/admin/archive-client/${clientId}`, null, {
        params: { reason },
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      alert('Cliente archivado correctamente');
      loadClients();
      setSelectedClient(null);
    } catch (error) {
      console.error('Error archiving client:', error);
      alert('Error al archivar cliente');
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

  const handleUnarchiveClient = async (clientId) => {
    try {
      await axios.post(`${API}/admin/unarchive-client/${clientId}`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      alert('Cliente desarchivado correctamente');
      loadClients();
    } catch (error) {
      console.error('Error unarchiving client:', error);
      alert('Error al desarchivar cliente');
    }
  };

  const handleDeleteClient = async (clientId, clientName) => {
    if (!window.confirm(`¿Estás seguro de que quieres ELIMINAR PERMANENTEMENTE a ${clientName}?\n\nEsto borrará:\n- Todos sus datos\n- Formularios\n- PDFs\n- Alertas\n- Mensajes\n- Sesiones\n\nEsta acción NO se puede deshacer.`)) {
      return;
    }

    try {
      await axios.delete(`${API}/admin/delete-client/${clientId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      alert('Cliente eliminado correctamente');
      setSelectedClient(null);
      loadClients();
    } catch (error) {
      console.error('Error deleting client:', error);
      alert('Error al eliminar cliente');
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
            className="cursor-pointer hover:shadow-lg transition-shadow border-2 border-red-200 hover:border-red-400"
            onClick={() => setActiveView('at-risk')}
          >
            <CardContent className="pt-6 text-center">
              <div className="relative">
                <Target className="h-12 w-12 text-red-500 mx-auto mb-3" />
                {/* Add notification badge if there are at-risk clients */}
                <div className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center font-bold">
                  !
                </div>
              </div>
              <h3 className="text-lg font-bold mb-2">⚠️ Clientes en Riesgo</h3>
              <p className="text-sm text-gray-600">Requieren tu atención</p>
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
        </div>

        {/* Conditional View Rendering */}
        {activeView === 'at-risk' && (
          <div>
            <Button 
              variant="outline" 
              className="mb-4"
              onClick={() => setActiveView('clients')}
            >
              ← Volver a Gestión de Clientes
            </Button>
            <ClientsAtRisk 
              token={token} 
              onClientSelect={(clientId) => {
                // Find and select the client
                const client = clients.find(c => c.id === clientId);
                if (client) {
                  setSelectedClient(client);
                  setActiveView('clients');
                }
              }}
            />
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

        {(activeView === 'clients' || activeView === 'calendar') && (
          <Tabs value={activeView} onValueChange={setActiveView} className="space-y-6">
            <TabsList className="grid w-full max-w-4xl mx-auto grid-cols-3">
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
                              client.status === 'active'
                                ? 'bg-green-100 text-green-700'
                                : client.status === 'pending'
                                ? 'bg-orange-100 text-orange-700'
                                : 'bg-gray-100 text-gray-700'
                            }
                          >
                            {client.status === 'active' ? 'Activo' : client.status === 'pending' ? 'Pendiente' : 'Inactivo'}
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
                {selectedClient ? (
                  <>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span>Gestión de {selectedClient.name}</span>
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
                          
                          {/* Templates Button */}
                          <Button
                            size="sm"
                            variant="outline"
                            className="bg-purple-50 border-purple-300 text-purple-700 hover:bg-purple-100"
                            onClick={() => setShowTemplateSelector(true)}
                          >
                            <FileText className="h-4 w-4 mr-2" />
                            Templates
                          </Button>
                          
                          {selectedClient.subscription?.archived ? (
                            <Button
                              size="sm"
                              onClick={() => handleUnarchiveClient(selectedClient.id)}
                              className="bg-green-500 hover:bg-green-600"
                            >
                              Desarchivar
                            </Button>
                          ) : (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleArchiveClient(selectedClient.id)}
                              className="border-orange-300 text-orange-600 hover:bg-orange-50"
                            >
                              Archivar
                            </Button>
                          )}
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
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDeleteClient(selectedClient.id, selectedClient.name)}
                            className="border-red-300 text-red-600 hover:bg-red-50"
                          >
                            Eliminar
                          </Button>
                        </div>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Tabs defaultValue="data" className="space-y-4">
                        <TabsList className="grid w-full grid-cols-5">
                          <TabsTrigger value="data">Datos</TabsTrigger>
                          <TabsTrigger value="forms">Formularios</TabsTrigger>
                          <TabsTrigger value="pdfs">PDFs</TabsTrigger>
                          <TabsTrigger value="nutrition">🥗 Nutrición</TabsTrigger>
                          <TabsTrigger value="alerts">Alertas</TabsTrigger>
                          <TabsTrigger value="sessions">Sesiones</TabsTrigger>
                        </TabsList>

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

                              <div className="border-t pt-4 mt-4">
                                <h4 className="font-semibold text-lg mb-3">Suscripción</h4>
                                <div className="grid md:grid-cols-2 gap-4">
                                  <div>
                                    <label className="text-sm font-semibold text-gray-700">Plan</label>
                                    <p className="text-gray-900 bg-white p-2 rounded border">{selectedClient.subscription?.plan === 'team' ? 'Equipo' : 'Directo'}</p>
                                  </div>
                                  <div>
                                    <label className="text-sm font-semibold text-gray-700">Estado</label>
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
                          <div className="bg-blue-50 p-4 rounded-lg">
                            <h3 className="font-semibold mb-3 flex items-center gap-2">
                              <Send className="h-5 w-5" />
                              Enviar nuevo formulario
                            </h3>
                            <div className="space-y-3">
                              <div>
                                <Label htmlFor="form-title">Título del formulario</Label>
                                <Input
                                  id="form-title"
                                  placeholder="Ej: Cuestionario de seguimiento mensual"
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
                                    <p className="text-xs text-gray-600 mb-2">Subido: {new Date(pdf.upload_date).toLocaleDateString('es-ES')}</p>
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
                                    <p className="text-xs text-gray-600 mb-2">Recibido: {new Date(pdf.upload_date).toLocaleDateString('es-ES')}</p>
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
                          {nutritionPlans.length > 0 ? (
                            <div className="space-y-4">
                              <div className="flex justify-between items-center mb-4">
                                <h3 className="text-xl font-bold text-gray-800">📋 Planes de Nutrición Mensuales</h3>
                                <span className="text-sm text-gray-500">{nutritionPlans.length} plan(es) total</span>
                              </div>

                              {/* Lista de planes apilados */}
                              {nutritionPlans.map((plan, index) => {
                                const monthNames = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                                                   "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
                                const isExpanded = selectedPlan?.id === plan.id;
                                
                                return (
                                  <Card 
                                    key={plan.id} 
                                    className={`border-2 ${isExpanded ? 'border-green-500 shadow-lg' : 'border-gray-200'} transition-all`}
                                  >
                                    {/* Plan Header - Siempre visible */}
                                    <CardHeader 
                                      className="cursor-pointer hover:bg-gray-50"
                                      onClick={() => {
                                        console.log('Click en plan, isExpanded:', isExpanded, 'plan.id:', plan.id);
                                        if (isExpanded) {
                                          setSelectedPlan(null);
                                        } else {
                                          setSelectedPlan(plan);
                                          setNutritionContent(plan.plan_verificado);
                                          setEditingNutrition(false);
                                        }
                                      }}
                                    >
                                      <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${isExpanded ? 'bg-green-500' : 'bg-blue-500'} text-white font-bold`}>
                                            {index + 1}
                                          </div>
                                          <div>
                                            <CardTitle className="text-lg">
                                              🥗 {monthNames[plan.month]} {plan.year}
                                            </CardTitle>
                                            <p className="text-sm text-gray-500">
                                              Generado: {new Date(plan.generated_at).toLocaleDateString('es-ES')}
                                            </p>
                                          </div>
                                        </div>
                                        
                                        <div className="flex items-center gap-4">
                                          {/* Status badges */}
                                          <div className="flex gap-2">
                                            {plan.pdf_id && (
                                              <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full">
                                                📄 PDF
                                              </span>
                                            )}
                                            {plan.sent_email && (
                                              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                                ✉️ Email
                                              </span>
                                            )}
                                            {plan.sent_whatsapp && (
                                              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                                                💬 WhatsApp
                                              </span>
                                            )}
                                            {plan.edited && (
                                              <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                                                ✏️ Editado
                                              </span>
                                            )}
                                          </div>
                                          
                                          {/* Expand/Collapse icon */}
                                          <ChevronDown className={`h-6 w-6 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                                        </div>
                                      </div>
                                    </CardHeader>

                                    {/* Plan Content - Solo visible cuando está expandido */}
                                    {isExpanded && (
                                      <CardContent className="pt-6 space-y-6">
                                        {/* Status Details */}
                                        <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
                                          <div className="text-center">
                                            <div className="text-2xl mb-1">{plan.pdf_id ? '✅' : '❌'}</div>
                                            <div className="text-xs text-gray-600">PDF Generado</div>
                                          </div>
                                          <div className="text-center">
                                            <div className="text-2xl mb-1">{plan.sent_email ? '✅' : '❌'}</div>
                                            <div className="text-xs text-gray-600">Enviado Email</div>
                                          </div>
                                          <div className="text-center">
                                            <div className="text-2xl mb-1">{plan.sent_whatsapp ? '✅' : '❌'}</div>
                                            <div className="text-xs text-gray-600">Enviado WhatsApp</div>
                                          </div>
                                        </div>

                                        {/* Editor/Viewer */}
                                        <Card>
                                          <CardHeader className="flex flex-row items-center justify-between">
                                            <CardTitle>Plan Verificado</CardTitle>
                                            <div className="flex gap-2">
                                              {!editingNutrition ? (
                                                <Button
                                                  onClick={() => setEditingNutrition(true)}
                                                  variant="outline"
                                                >
                                                  <Edit className="h-4 w-4 mr-2" />
                                                  Editar
                                                </Button>
                                              ) : (
                                                <>
                                                  <Button
                                                    onClick={() => {
                                                      setEditingNutrition(false);
                                                      setNutritionContent(plan.plan_verificado);
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
                                                rows={20}
                                                className="font-mono text-sm"
                                              />
                                            ) : (
                                              <div className="prose max-w-none">
                                                <pre className="whitespace-pre-wrap font-sans text-sm">
                                                  {plan.plan_verificado}
                                                </pre>
                                              </div>
                                            )}
                                          </CardContent>
                                        </Card>

                                        {/* Action Buttons */}
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                          {/* Generate PDF */}
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
                                                    Generando...
                                                  </>
                                                ) : (
                                                  <>
                                                    <FileText className="h-4 w-4 mr-2" />
                                                    Generar PDF
                                                  </>
                                                )}
                                              </Button>
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
                                            </CardContent>
                                          </Card>

                                          {/* Send WhatsApp */}
                                          <Card className="border-2 border-green-200 bg-green-50">
                                            <CardContent className="pt-6">
                                              <Button
                                                onClick={() => sendNutritionByWhatsApp(selectedClient.id)}
                                                disabled={sendingNutrition === 'whatsapp'}
                                                className="w-full bg-green-600 hover:bg-green-700"
                                              >
                                                {sendingNutrition === 'whatsapp' ? (
                                                  <>
                                                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                                    Abriendo...
                                                  </>
                                                ) : (
                                                  <>
                                                    <MessageSquare className="h-4 w-4 mr-2" />
                                                    Enviar WhatsApp
                                                  </>
                                                )}
                                              </Button>
                                            </CardContent>
                                          </Card>
                                        </div>
                                      </CardContent>
                                    )}
                                  </Card>
                                );
                              })}
                            </div>
                          ) : (
                            <div className="bg-gray-50 p-8 rounded-lg text-center">
                              <UtensilsCrossed className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                              <h3 className="font-semibold text-lg mb-2 text-gray-700">
                                Sin Plan de Nutrición
                              </h3>
                              <p className="text-gray-500">
                                Este usuario aún no ha completado el cuestionario de nutrición.
                              </p>
                            </div>
                          )}
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
    </div>
  );
};

export default AdminDashboard;
