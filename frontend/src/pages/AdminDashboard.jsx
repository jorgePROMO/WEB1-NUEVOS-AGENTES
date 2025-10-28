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
  Mail
} from 'lucide-react';
import ChatBox from '../components/ChatBox';
import { AdminCalendar } from '../components/Calendar';
import { EditUserModal, SendPasswordResetButton } from '../components/AdminComponents';

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
  }, [isAdmin, navigate]);

  useEffect(() => {
    if (selectedClient) {
      loadClientDetails(selectedClient.id);
    }
  }, [selectedClient]);

  const loadClients = async () => {
    try {
      const response = await axios.get(`${API}/admin/clients`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setClients(response.data.clients || []);
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
        }
      });
      setSelectedClientDetails(response.data);
    } catch (error) {
      console.error('Error loading client details:', error);
      setSelectedClientDetails({ user: selectedClient, forms: [], pdfs: [], alerts: [] });
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
    
    const isArchived = client.subscription?.archived === true;
    
    return matchesSearch && (showArchived ? isArchived : !isArchived);
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

        {/* Main Content with Tabs */}
        <Tabs defaultValue="clients" className="space-y-6">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2">
            <TabsTrigger value="clients">
              <Users className="h-4 w-4 mr-2" />
              Gestión de Clientes
            </TabsTrigger>
            <TabsTrigger value="calendar">
              <Calendar className="h-4 w-4 mr-2" />
              Calendario General
            </TabsTrigger>
          </TabsList>

          {/* Clients Management Tab */}
          <TabsContent value="clients">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Client List */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Lista de clientes
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
                      <p className="font-semibold text-gray-900">{client.name}</p>
                      <Badge
                        className={
                          client.subscription?.payment_status === 'verified'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-orange-100 text-orange-700'
                        }
                      >
                        {client.subscription?.payment_status === 'verified' ? 'Activo' : 'Pendiente'}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600">@{client.username}</p>
                    <p className="text-xs text-gray-500 mt-1">{client.email}</p>
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
                        onClick={() => setShowChat(true)}
                      >
                        <MessageSquare className="h-4 w-4 mr-2" />
                        Chat
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
                  <Tabs defaultValue="forms" className="space-y-4">
                    <TabsList className="grid w-full grid-cols-5">
                      <TabsTrigger value="data">Datos</TabsTrigger>
                      <TabsTrigger value="forms">Formularios</TabsTrigger>
                      <TabsTrigger value="pdfs">PDFs</TabsTrigger>
                      <TabsTrigger value="alerts">Alertas</TabsTrigger>
                      <TabsTrigger value="calendar">Calendario</TabsTrigger>
                    </TabsList>

                    {/* Data Tab - NEW */}
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
                              {selectedClient.subscription?.stripe_customer_id && (
                                <div className="md:col-span-2">
                                  <label className="text-sm font-semibold text-gray-700">Stripe Customer ID</label>
                                  <p className="text-gray-900 bg-white p-2 rounded border font-mono text-sm">{selectedClient.subscription.stripe_customer_id}</p>
                                </div>
                              )}
                            </div>
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

                      {/* Sent Forms */}
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

                      {/* Uploaded PDFs */}
                      <div>
                        <h4 className="font-semibold mb-3">Documentos subidos</h4>
                        {selectedClientDetails?.pdfs?.length > 0 ? (
                          <div className="grid md:grid-cols-2 gap-3">
                            {selectedClientDetails.pdfs.map((pdf) => (
                              <div key={pdf.id} className="p-3 bg-gray-50 rounded-lg">
                                <div className="flex items-start justify-between mb-2">
                                  <p className="font-medium text-sm">{pdf.title}</p>
                                  <Badge className={pdf.type === 'training' ? 'bg-blue-100 text-blue-700' : 'bg-orange-100 text-orange-700'}>
                                    {pdf.type === 'training' ? 'Entrenamiento' : 'Nutrición'}
                                  </Badge>
                                </div>
                                <p className="text-xs text-gray-600">Subido: {new Date(pdf.upload_date).toLocaleDateString('es-ES')}</p>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-gray-500 text-center py-4">No hay documentos subidos</p>
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

                      {/* Sent Alerts */}
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

                    {/* Calendar Tab */}
                    <TabsContent value="calendar">
                      <div className="bg-green-50 p-6 rounded-lg text-center">
                        <Calendar className="h-12 w-12 text-green-500 mx-auto mb-4" />
                        <h3 className="font-semibold text-lg mb-2">Calendario de seguimiento</h3>
                        <p className="text-gray-600 mb-4">
                          Próxima revisión programada: {selectedClient?.next_review ? new Date(selectedClient.next_review).toLocaleDateString('es-ES') : 'No programada'}
                        </p>
                        <Button variant="outline">
                          <Calendar className="h-4 w-4 mr-2" />
                          Programar revisión
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

          {/* Calendar Tab */}
          <TabsContent value="calendar">
            <AdminCalendar />
          </TabsContent>
        </Tabs>
      </div>

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
