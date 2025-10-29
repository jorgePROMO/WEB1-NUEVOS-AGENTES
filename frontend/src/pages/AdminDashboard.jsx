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
  Target
} from 'lucide-react';
import ChatBox from '../components/ChatBox';
import { AdminCalendar } from '../components/Calendar';
import { EditUserModal, SendPasswordResetButton } from '../components/AdminComponents';
import ProspectsCRM from '../components/ProspectsCRM';
import TeamClientsCRM from '../components/TeamClientsCRM';
import ExternalClientsCRM from '../components/ExternalClientsCRM';

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

        {/* Main Content with Tabs */}
        <Tabs defaultValue="clients" className="space-y-6">
          <TabsList className="grid w-full max-w-4xl mx-auto grid-cols-5">
            <TabsTrigger value="prospects">
              <Target className="h-4 w-4 mr-2" />
              Prospectos
            </TabsTrigger>
            <TabsTrigger value="team-clients">
              <Users className="h-4 w-4 mr-2" />
              Clientes Equipo
            </TabsTrigger>
            <TabsTrigger value="external-clients">
              <Target className="h-4 w-4 mr-2" />
              Clientes Externos
            </TabsTrigger>
            <TabsTrigger value="clients">
              <Users className="h-4 w-4 mr-2" />
              Gestión Clientes
            </TabsTrigger>
            <TabsTrigger value="calendar">
              <Calendar className="h-4 w-4 mr-2" />
              Calendario
            </TabsTrigger>
          </TabsList>

          {/* Prospects CRM Tab */}
          <TabsContent value="prospects">
            <ProspectsCRM token={token} />
          </TabsContent>

          {/* Team Clients CRM Tab */}
          <TabsContent value="team-clients">
            <TeamClientsCRM token={token} />
          </TabsContent>

          {/* External Clients CRM Tab */}
          <TabsContent value="external-clients">
            <ExternalClientsCRM token={token} />
          </TabsContent>

          {/* Clients Management Tab */}
          <TabsContent value="clients">
            <TeamClientsCRM token={token} />
          </TabsContent>

        </Tabs>
      </div>
        </Tabs>
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
