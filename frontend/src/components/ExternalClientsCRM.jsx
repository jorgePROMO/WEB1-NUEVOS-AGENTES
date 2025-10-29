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
  Mail,
  Phone,
  Calendar,
  CreditCard,
  CheckCircle,
  XCircle,
  Clock,
  DollarSign,
  Save,
  AlertCircle,
  TrendingUp,
  ArrowRightLeft,
  Users
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WEEK_OPTIONS = [4, 8, 12, 16, 20, 24];

export const ExternalClientsCRM = ({ token }) => {
  const [clients, setClients] = useState([]);
  const [selectedClient, setSelectedClient] = useState(null);
  const [showDetail, setShowDetail] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [showMoveModal, setShowMoveModal] = useState(false);
  const [clientToMove, setClientToMove] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [newNote, setNewNote] = useState('');
  
  const [newClient, setNewClient] = useState({
    nombre: '',
    email: '',
    whatsapp: '',
    objetivo: '',
    plan_weeks: 12,
    start_date: '',
    amount_paid: '',
    notes: ''
  });

  const [newPayment, setNewPayment] = useState({
    amount: '',
    date: new Date().toISOString().split('T')[0],
    notes: ''
  });

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async (status = null) => {
    try {
      const params = status ? `?status=${status}` : '';
      const response = await axios.get(`${API}/admin/external-clients${params}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setClients(response.data.clients || []);
    } catch (error) {
      console.error('Error loading external clients:', error);
    }
  };

  const loadClientDetail = async (clientId) => {
    try {
      const response = await axios.get(`${API}/admin/external-clients/${clientId}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setSelectedClient(response.data);
      setShowDetail(true);
    } catch (error) {
      console.error('Error loading client detail:', error);
    }
  };

  const createClient = async () => {
    try {
      await axios.post(`${API}/admin/external-clients`, newClient, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setShowCreateModal(false);
      setNewClient({
        nombre: '',
        email: '',
        whatsapp: '',
        objetivo: '',
        plan_weeks: 12,
        start_date: '',
        amount_paid: '',
        notes: ''
      });
      loadClients(filterStatus);
      alert('Cliente creado exitosamente');
    } catch (error) {
      alert('Error al crear cliente');
    }
  };

  const deleteClient = async (clientId) => {
    if (!window.confirm('¿Estás seguro de eliminar este cliente? Esta acción no se puede deshacer.')) {
      return;
    }
    
    try {
      await axios.delete(`${API}/admin/external-clients/${clientId}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      loadClients(filterStatus);
      if (showDetail && selectedClient?.id === clientId) {
        setShowDetail(false);
        setSelectedClient(null);
      }
      alert('Cliente eliminado correctamente');
    } catch (error) {
      alert('Error al eliminar cliente');
    }
  };

  const addPayment = async () => {
    if (!selectedClient || !newPayment.amount) return;
    
    try {
      await axios.post(`${API}/admin/external-clients/${selectedClient.id}/payments`, newPayment, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setNewPayment({
        amount: '',
        date: new Date().toISOString().split('T')[0],
        notes: ''
      });
      setShowPaymentModal(false);
      loadClientDetail(selectedClient.id);
      alert('Pago registrado correctamente');
    } catch (error) {
      alert('Error al registrar pago');
    }
  };

  const addNote = async () => {
    if (!newNote.trim() || !selectedClient) return;
    
    try {
      await axios.post(`${API}/admin/external-clients/${selectedClient.id}/notes`,
        { note: newNote },
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      setNewNote('');
      loadClientDetail(selectedClient.id);
    } catch (error) {
      alert('Error al agregar nota');
    }
  };

  const updateStatus = async (clientId, newStatus) => {
    try {
      await axios.patch(`${API}/admin/external-clients/${clientId}/status`,
        { status: newStatus },
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      loadClients(filterStatus);
      if (selectedClient && selectedClient.id === clientId) {
        loadClientDetail(clientId);
      }
    } catch (error) {
      alert('Error al actualizar estado');
    }
  };

  const openMoveModal = (client) => {
    setClientToMove(client);
    setShowMoveModal(true);
  };

  const moveClient = async (targetCRM) => {
    if (!clientToMove) return;
    
    try {
      await axios.post(`${API}/admin/external-clients/${clientToMove.id}/move`,
        { target_crm: targetCRM },
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );
      setShowMoveModal(false);
      setClientToMove(null);
      setShowDetail(false);
      loadClients(filterStatus);
      alert(`Cliente movido a ${targetCRM === 'team' ? 'Clientes Equipo' : 'otro CRM'} exitosamente`);
    } catch (error) {
      alert('Error al mover cliente');
    }
  };

  const filteredClients = clients.filter(c => {
    const matchesSearch = c.nombre?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         c.email?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = !filterStatus || c.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status) => {
    switch(status) {
      case 'active': return 'bg-green-100 text-green-800 border-green-300';
      case 'paused': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'completed': return 'bg-blue-100 text-blue-800 border-blue-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusText = (status) => {
    switch(status) {
      case 'active': return 'Activo';
      case 'paused': return 'Pausado';
      case 'completed': return 'Finalizado';
      default: return status;
    }
  };

  const calculateProgress = (client) => {
    if (!client.weeks_completed || !client.plan_weeks) return 0;
    return Math.round((client.weeks_completed / client.plan_weeks) * 100);
  };

  const isRenewalClose = (client) => {
    if (!client.next_payment_date) return false;
    const nextDate = new Date(client.next_payment_date);
    const today = new Date();
    const daysUntil = Math.ceil((nextDate - today) / (1000 * 60 * 60 * 24));
    return daysUntil <= 7 && daysUntil >= 0;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">CRM Clientes Externos</h2>
          <p className="text-gray-600">Gestión de clientes Harbiz (trabajo directo)</p>
        </div>
        <Button
          onClick={() => setShowCreateModal(true)}
          className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600"
        >
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Cliente
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
                value={filterStatus}
                onChange={(e) => {
                  setFilterStatus(e.target.value);
                  loadClients(e.target.value || null);
                }}
                className="w-full border rounded-md px-10 py-2"
              >
                <option value="">Todos los estados</option>
                <option value="active">Activo</option>
                <option value="paused">Pausado</option>
                <option value="completed">Finalizado</option>
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
              <p className="text-2xl font-bold">{clients.length}</p>
              <p className="text-sm text-gray-600">Total Clientes</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {clients.filter(c => c.status === 'active').length}
              </p>
              <p className="text-sm text-gray-600">Activos</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">
                {clients.filter(c => c.status === 'paused').length}
              </p>
              <p className="text-sm text-gray-600">Pausados</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">
                {clients.filter(c => isRenewalClose(c)).length}
              </p>
              <p className="text-sm text-gray-600">Próximas Renovaciones</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Clients Table */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Clientes Externos ({filteredClients.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3">Nombre</th>
                  <th className="text-left p-3">Email</th>
                  <th className="text-left p-3">Plan</th>
                  <th className="text-left p-3">Progreso</th>
                  <th className="text-left p-3">Renovación</th>
                  <th className="text-left p-3">Estado</th>
                  <th className="text-left p-3">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredClients.map(client => {
                  const progress = calculateProgress(client);
                  const renewalClose = isRenewalClose(client);
                  
                  return (
                    <tr key={client.id} className="border-b hover:bg-gray-50">
                      <td className="p-3 font-medium">{client.nombre}</td>
                      <td className="p-3 text-sm">{client.email}</td>
                      <td className="p-3 text-sm">
                        {client.plan_weeks} semanas
                      </td>
                      <td className="p-3">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full"
                              style={{ width: `${progress}%` }}
                            />
                          </div>
                          <span className="text-xs font-medium">{progress}%</span>
                        </div>
                      </td>
                      <td className="p-3 text-sm">
                        {client.next_payment_date ? (
                          <div className="flex items-center gap-1">
                            {renewalClose && <AlertCircle className="h-4 w-4 text-orange-600" />}
                            {new Date(client.next_payment_date).toLocaleDateString('es-ES')}
                          </div>
                        ) : '-'}
                      </td>
                      <td className="p-3">
                        <select
                          value={client.status || 'active'}
                          onChange={(e) => updateStatus(client.id, e.target.value)}
                          className={`border-2 rounded-md px-3 py-1 text-sm font-medium ${getStatusColor(client.status || 'active')}`}
                        >
                          <option value="active">Activo</option>
                          <option value="paused">Pausado</option>
                          <option value="completed">Finalizado</option>
                        </select>
                      </td>
                      <td className="p-3">
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => loadClientDetail(client.id)}
                            title="Ver detalle"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="bg-red-50 hover:bg-red-100 text-red-700 border-red-300"
                            onClick={() => deleteClient(client.id)}
                            title="Eliminar"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {filteredClients.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No hay clientes para mostrar
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Create Client Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-4 flex items-center justify-between">
              <h3 className="text-xl font-bold">Nuevo Cliente Externo</h3>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setShowCreateModal(false)}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>

            <div className="p-6 space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label>Nombre *</Label>
                  <Input
                    value={newClient.nombre}
                    onChange={(e) => setNewClient({...newClient, nombre: e.target.value})}
                    placeholder="Nombre completo"
                  />
                </div>
                <div>
                  <Label>Email *</Label>
                  <Input
                    type="email"
                    value={newClient.email}
                    onChange={(e) => setNewClient({...newClient, email: e.target.value})}
                    placeholder="email@ejemplo.com"
                  />
                </div>
                <div>
                  <Label>WhatsApp *</Label>
                  <Input
                    value={newClient.whatsapp}
                    onChange={(e) => setNewClient({...newClient, whatsapp: e.target.value})}
                    placeholder="+34 600 000 000"
                  />
                </div>
                <div>
                  <Label>Plan (semanas) *</Label>
                  <select
                    value={newClient.plan_weeks}
                    onChange={(e) => setNewClient({...newClient, plan_weeks: parseInt(e.target.value)})}
                    className="w-full border rounded-md px-3 py-2"
                  >
                    {WEEK_OPTIONS.map(weeks => (
                      <option key={weeks} value={weeks}>{weeks} semanas</option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label>Fecha de Inicio *</Label>
                  <Input
                    type="date"
                    value={newClient.start_date}
                    onChange={(e) => setNewClient({...newClient, start_date: e.target.value})}
                  />
                </div>
                <div>
                  <Label>Monto Pagado</Label>
                  <Input
                    type="number"
                    value={newClient.amount_paid}
                    onChange={(e) => setNewClient({...newClient, amount_paid: e.target.value})}
                    placeholder="0"
                  />
                </div>
              </div>

              <div>
                <Label>Objetivo</Label>
                <Textarea
                  value={newClient.objetivo}
                  onChange={(e) => setNewClient({...newClient, objetivo: e.target.value})}
                  placeholder="Objetivo del cliente..."
                  rows={3}
                />
              </div>

              <div>
                <Label>Notas Iniciales</Label>
                <Textarea
                  value={newClient.notes}
                  onChange={(e) => setNewClient({...newClient, notes: e.target.value})}
                  placeholder="Notas adicionales..."
                  rows={2}
                />
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  onClick={createClient}
                  disabled={!newClient.nombre || !newClient.email || !newClient.whatsapp || !newClient.start_date}
                  className="flex-1 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600"
                >
                  <Save className="h-4 w-4 mr-2" />
                  Crear Cliente
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

      {/* Client Detail Modal */}
      {showDetail && selectedClient && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg w-full max-w-5xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-4 flex items-center justify-between">
              <h3 className="text-xl font-bold">Detalle del Cliente</h3>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => openMoveModal(selectedClient)}
                  className="bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-300"
                >
                  <ArrowRightLeft className="h-4 w-4 mr-2" />
                  Mover Cliente
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setShowDetail(false)}
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Info Cards */}
              <div className="grid md:grid-cols-3 gap-4">
                <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                  <Mail className="h-5 w-5 text-blue-600" />
                  <div>
                    <p className="text-sm text-gray-600">Email</p>
                    <p className="font-medium text-sm">{selectedClient.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                  <Phone className="h-5 w-5 text-green-600" />
                  <div>
                    <p className="text-sm text-gray-600">WhatsApp</p>
                    <p className="font-medium text-sm">{selectedClient.whatsapp}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-orange-50 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-orange-600" />
                  <div>
                    <p className="text-sm text-gray-600">Progreso</p>
                    <p className="font-medium text-sm">
                      {selectedClient.weeks_completed || 0} / {selectedClient.plan_weeks} semanas
                    </p>
                  </div>
                </div>
              </div>

              {/* Plan Info */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Información del Plan</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm text-gray-600">Fecha de Inicio</Label>
                      <p className="font-medium">
                        {selectedClient.start_date ? new Date(selectedClient.start_date).toLocaleDateString('es-ES') : '-'}
                      </p>
                    </div>
                    <div>
                      <Label className="text-sm text-gray-600">Próxima Renovación</Label>
                      <p className="font-medium flex items-center gap-2">
                        {selectedClient.next_payment_date ? (
                          <>
                            {isRenewalClose(selectedClient) && <AlertCircle className="h-4 w-4 text-orange-600" />}
                            {new Date(selectedClient.next_payment_date).toLocaleDateString('es-ES')}
                          </>
                        ) : '-'}
                      </p>
                    </div>
                    <div>
                      <Label className="text-sm text-gray-600">Duración del Plan</Label>
                      <p className="font-medium">{selectedClient.plan_weeks} semanas</p>
                    </div>
                    <div>
                      <Label className="text-sm text-gray-600">Estado</Label>
                      <Badge className={getStatusColor(selectedClient.status)}>
                        {getStatusText(selectedClient.status)}
                      </Badge>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div>
                    <Label className="text-sm text-gray-600">Progreso del Programa</Label>
                    <div className="flex items-center gap-3 mt-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-3">
                        <div 
                          className="bg-gradient-to-r from-orange-500 to-red-500 h-3 rounded-full transition-all"
                          style={{ width: `${calculateProgress(selectedClient)}%` }}
                        />
                      </div>
                      <span className="text-sm font-bold">{calculateProgress(selectedClient)}%</span>
                    </div>
                  </div>

                  {selectedClient.objetivo && (
                    <div>
                      <Label className="text-sm text-gray-600">Objetivo</Label>
                      <p className="mt-1">{selectedClient.objetivo}</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Payment History */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="text-lg">Historial de Pagos</CardTitle>
                  <Button
                    size="sm"
                    onClick={() => setShowPaymentModal(true)}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <DollarSign className="h-4 w-4 mr-2" />
                    Registrar Pago
                  </Button>
                </CardHeader>
                <CardContent>
                  {selectedClient.payment_history && selectedClient.payment_history.length > 0 ? (
                    <div className="space-y-2">
                      {selectedClient.payment_history.map((payment, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <p className="font-medium">{payment.amount}€</p>
                            <p className="text-xs text-gray-600">
                              {new Date(payment.date).toLocaleDateString('es-ES')}
                            </p>
                            {payment.notes && <p className="text-xs text-gray-500 mt-1">{payment.notes}</p>}
                          </div>
                          <CheckCircle className="h-5 w-5 text-green-600" />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-4">No hay pagos registrados</p>
                  )}
                </CardContent>
              </Card>

              {/* Notes */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Notas de Seguimiento</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Textarea
                      placeholder="Agregar nota..."
                      value={newNote}
                      onChange={(e) => setNewNote(e.target.value)}
                      rows={3}
                    />
                    <Button onClick={addNote} disabled={!newNote.trim()}>
                      <Save className="h-4 w-4 mr-2" />
                      Guardar Nota
                    </Button>
                  </div>

                  <div className="space-y-3">
                    {selectedClient.notes && selectedClient.notes.length > 0 ? (
                      selectedClient.notes.map(note => (
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

      {/* Payment Modal */}
      {showPaymentModal && selectedClient && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg w-full max-w-md">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold">Registrar Pago</h3>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setShowPaymentModal(false)}
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>

              <div className="space-y-4">
                <div>
                  <Label>Cliente</Label>
                  <p className="font-medium">{selectedClient.nombre}</p>
                </div>

                <div>
                  <Label>Monto (€) *</Label>
                  <Input
                    type="number"
                    value={newPayment.amount}
                    onChange={(e) => setNewPayment({...newPayment, amount: e.target.value})}
                    placeholder="0"
                  />
                </div>

                <div>
                  <Label>Fecha de Pago *</Label>
                  <Input
                    type="date"
                    value={newPayment.date}
                    onChange={(e) => setNewPayment({...newPayment, date: e.target.value})}
                  />
                </div>

                <div>
                  <Label>Notas</Label>
                  <Textarea
                    value={newPayment.notes}
                    onChange={(e) => setNewPayment({...newPayment, notes: e.target.value})}
                    placeholder="Notas sobre este pago..."
                    rows={2}
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <Button
                    onClick={addPayment}
                    disabled={!newPayment.amount}
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
    </div>
  );
};

export default ExternalClientsCRM;
