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
  X,
  Mail,
  Phone,
  Calendar,
  CreditCard,
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  Save,
  UserCheck,
  ArrowRightLeft,
  Target
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const TeamClientsCRM = ({ token }) => {
  const [clients, setClients] = useState([]);
  const [selectedClient, setSelectedClient] = useState(null);
  const [showDetail, setShowDetail] = useState(false);
  const [showMoveModal, setShowMoveModal] = useState(false);
  const [clientToMove, setClientToMove] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [newNote, setNewNote] = useState('');

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async (status = null) => {
    try {
      const params = status ? `?status=${status}` : '';
      const response = await axios.get(`${API}/admin/team-clients${params}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setClients(response.data.clients || []);
    } catch (error) {
      console.error('Error loading team clients:', error);
    }
  };

  const loadClientDetail = async (clientId) => {
    try {
      const response = await axios.get(`${API}/admin/team-clients/${clientId}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setSelectedClient(response.data);
      setShowDetail(true);
    } catch (error) {
      console.error('Error loading client detail:', error);
    }
  };

  const addNote = async () => {
    if (!newNote.trim() || !selectedClient) return;
    
    try {
      await axios.post(`${API}/admin/team-clients/${selectedClient.id}/notes`,
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
      await axios.patch(`${API}/admin/team-clients/${clientId}/status`,
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
      await axios.post(`${API}/admin/team-clients/${clientToMove.id}/move`,
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
      alert(`Cliente movido a ${targetCRM === 'external' ? 'Clientes Externos' : 'otro CRM'} exitosamente`);
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
      case 'inactive': return 'bg-gray-100 text-gray-800 border-gray-300';
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default: return 'bg-blue-100 text-blue-800 border-blue-300';
    }
  };

  const getStatusText = (status) => {
    switch(status) {
      case 'active': return 'Activo';
      case 'inactive': return 'Inactivo';
      case 'pending': return 'Pendiente';
      default: return status;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">CRM Clientes Equipo</h2>
          <p className="text-gray-600">Clientes registrados en la plataforma web</p>
        </div>
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
                <option value="pending">Pendiente</option>
                <option value="inactive">Inactivo</option>
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
                {clients.filter(c => c.status === 'pending').length}
              </p>
              <p className="text-sm text-gray-600">Pendientes</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-600">
                {clients.filter(c => c.status === 'inactive').length}
              </p>
              <p className="text-sm text-gray-600">Inactivos</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Clients Table */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Clientes Equipo ({filteredClients.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3">Nombre</th>
                  <th className="text-left p-3">Email</th>
                  <th className="text-left p-3">Fecha Registro</th>
                  <th className="text-left p-3">Estado</th>
                  <th className="text-left p-3">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredClients.map(client => (
                  <tr key={client.id} className="border-b hover:bg-gray-50">
                    <td className="p-3 font-medium">{client.nombre || client.username}</td>
                    <td className="p-3 text-sm">{client.email}</td>
                    <td className="p-3 text-sm">
                      {client.created_at ? new Date(client.created_at).toLocaleDateString('es-ES') : '-'}
                    </td>
                    <td className="p-3">
                      <select
                        value={client.status || 'pending'}
                        onChange={(e) => updateStatus(client.id, e.target.value)}
                        className={`border-2 rounded-md px-3 py-1 text-sm font-medium ${getStatusColor(client.status || 'pending')}`}
                      >
                        <option value="pending">Pendiente</option>
                        <option value="active">Activo</option>
                        <option value="inactive">Inactivo</option>
                      </select>
                    </td>
                    <td className="p-3">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => loadClientDetail(client.id)}
                        title="Ver detalle"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                ))}
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

      {/* Detail Modal */}
      {showDetail && selectedClient && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-4 flex items-center justify-between">
              <h3 className="text-xl font-bold">Detalle del Cliente</h3>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setShowDetail(false)}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>

            <div className="p-6 space-y-6">
              {/* Info Cards */}
              <div className="grid md:grid-cols-2 gap-4">
                <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                  <Mail className="h-5 w-5 text-blue-600" />
                  <div>
                    <p className="text-sm text-gray-600">Email</p>
                    <p className="font-medium">{selectedClient.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                  <UserCheck className="h-5 w-5 text-green-600" />
                  <div>
                    <p className="text-sm text-gray-600">Estado</p>
                    <p className="font-medium">{getStatusText(selectedClient.status)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg">
                  <Calendar className="h-5 w-5 text-purple-600" />
                  <div>
                    <p className="text-sm text-gray-600">Fecha de registro</p>
                    <p className="font-medium">
                      {selectedClient.created_at ? new Date(selectedClient.created_at).toLocaleDateString('es-ES') : '-'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-orange-50 rounded-lg">
                  <Phone className="h-5 w-5 text-orange-600" />
                  <div>
                    <p className="text-sm text-gray-600">WhatsApp</p>
                    <p className="font-medium">{selectedClient.whatsapp || 'No disponible'}</p>
                  </div>
                </div>
              </div>

              {/* Prospect Data if converted */}
              {selectedClient.prospect_data && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Datos del Diagnóstico Inicial</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label className="font-semibold">Objetivo</Label>
                      <p className="mt-1">{selectedClient.prospect_data.objetivo}</p>
                    </div>
                    <div>
                      <Label className="font-semibold">Presupuesto</Label>
                      <p className="mt-1">{selectedClient.prospect_data.presupuesto}</p>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Notes Section */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Notas de Seguimiento</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Add Note */}
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

                  {/* Notes List */}
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
    </div>
  );
};

export default TeamClientsCRM;
