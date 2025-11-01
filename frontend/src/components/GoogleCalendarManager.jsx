import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import axios from 'axios';
import { Calendar, CalendarPlus, Trash2, ExternalLink, CheckCircle, AlertCircle } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export const GoogleCalendarManager = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [upcomingEvents, setUpcomingEvents] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newEvent, setNewEvent] = useState({
    title: '',
    start: '',
    end: '',
    description: '',
    client_id: ''
  });
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkCalendarStatus();
    loadClients();
  }, []);

  const checkCalendarStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/calendar/status`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      setIsConnected(response.data.connected);
      
      if (response.data.connected) {
        loadUpcomingEvents();
      }
    } catch (error) {
      console.error('Error checking calendar status:', error);
    }
  };

  const loadClients = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/admin/users`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setClients(response.data.filter(u => u.role === 'user' && !u.is_deleted));
    } catch (error) {
      console.error('Error loading clients:', error);
    }
  };

  const loadUpcomingEvents = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/calendar/events`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      if (response.data.connected) {
        setUpcomingEvents(response.data.events || []);
      }
    } catch (error) {
      console.error('Error loading events:', error);
    } finally {
      setLoading(false);
    }
  };

  const connectGoogleCalendar = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/auth/google/calendar/login`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      // Abrir ventana de autorización
      window.location.href = response.data.authorization_url;
    } catch (error) {
      console.error('Error connecting calendar:', error);
      alert('Error al conectar con Google Calendar');
    }
  };

  const createEvent = async () => {
    try {
      if (!newEvent.title || !newEvent.start || !newEvent.end) {
        alert('Por favor completa título, fecha y hora de inicio y fin');
        return;
      }

      setLoading(true);
      const token = localStorage.getItem('token');
      
      await axios.post(`${API}/calendar/events`, newEvent, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      alert('✅ Evento creado y añadido a tu Google Calendar');
      setShowCreateModal(false);
      setNewEvent({ title: '', start: '', end: '', description: '', client_id: '' });
      loadUpcomingEvents();
    } catch (error) {
      console.error('Error creating event:', error);
      alert('Error al crear evento: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const deleteEvent = async (eventId) => {
    if (!window.confirm('¿Eliminar este evento del calendario?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/calendar/events/${eventId}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      alert('✅ Evento eliminado');
      loadUpcomingEvents();
    } catch (error) {
      console.error('Error deleting event:', error);
      alert('Error al eliminar evento');
    }
  };

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <Calendar className="h-6 w-6" />
            Estado de Google Calendar
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isConnected ? (
            <div className="flex items-center gap-3">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="text-green-700 font-semibold">Conectado</span>
              <Badge className="bg-green-100 text-green-800">Activo</Badge>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center gap-3 mb-4">
                <AlertCircle className="h-5 w-5 text-orange-600" />
                <span className="text-gray-700">No conectado</span>
              </div>
              <Button onClick={connectGoogleCalendar} className="bg-blue-600 hover:bg-blue-700">
                <Calendar className="h-4 w-4 mr-2" />
                Conectar Google Calendar
              </Button>
              <p className="text-sm text-gray-600 mt-2">
                Conecta tu Google Calendar para crear eventos automáticamente y gestionar revisiones con clientes.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {isConnected && (
        <>
          {/* Create Event Button */}
          <Button onClick={() => setShowCreateModal(true)} className="w-full bg-green-600 hover:bg-green-700">
            <CalendarPlus className="h-4 w-4 mr-2" />
            Crear Nueva Revisión
          </Button>

          {/* Upcoming Events */}
          <Card>
            <CardHeader>
              <CardTitle>Próximas Revisiones ({upcomingEvents.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <p className="text-center text-gray-500">Cargando eventos...</p>
              ) : upcomingEvents.length === 0 ? (
                <p className="text-center text-gray-500">No hay eventos próximos</p>
              ) : (
                <div className="space-y-3">
                  {upcomingEvents.map((event) => (
                    <Card key={event.id} className="border-l-4 border-l-blue-500">
                      <CardContent className="p-4">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-900">{event.summary}</h4>
                            <p className="text-sm text-gray-600 mt-1">
                              {new Date(event.start.dateTime || event.start.date).toLocaleString('es-ES', {
                                weekday: 'long',
                                day: 'numeric',
                                month: 'long',
                                hour: event.start.dateTime ? '2-digit' : undefined,
                                minute: event.start.dateTime ? '2-digit' : undefined
                              })}
                            </p>
                            {event.description && (
                              <p className="text-sm text-gray-500 mt-1">{event.description}</p>
                            )}
                            {event.attendees && (
                              <div className="flex gap-2 mt-2">
                                {event.attendees.map((attendee, idx) => (
                                  <Badge key={idx} variant="outline" className="text-xs">
                                    {attendee.email}
                                  </Badge>
                                ))}
                              </div>
                            )}
                          </div>
                          <div className="flex gap-2">
                            {event.htmlLink && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => window.open(event.htmlLink, '_blank')}
                                title="Ver en Google Calendar"
                              >
                                <ExternalLink className="h-4 w-4" />
                              </Button>
                            )}
                            <Button
                              size="sm"
                              variant="outline"
                              className="text-red-600 hover:bg-red-50"
                              onClick={() => deleteEvent(event.id)}
                              title="Eliminar evento"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* Create Event Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardHeader className="border-b">
              <CardTitle className="flex items-center justify-between">
                <span>Nueva Revisión</span>
                <Button variant="ghost" size="sm" onClick={() => setShowCreateModal(false)}>
                  <X className="h-5 w-5" />
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              <div>
                <Label>Título de la revisión *</Label>
                <Input
                  placeholder="Ej: Revisión mensual con María"
                  value={newEvent.title}
                  onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
                />
              </div>

              <div>
                <Label>Cliente (opcional)</Label>
                <select
                  className="w-full p-2 border rounded"
                  value={newEvent.client_id}
                  onChange={(e) => setNewEvent({ ...newEvent, client_id: e.target.value })}
                >
                  <option value="">Sin cliente específico</option>
                  {clients.map((client) => (
                    <option key={client.id} value={client.id}>
                      {client.name} ({client.email})
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Si seleccionas un cliente, se le enviará invitación automática por email
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label>Fecha y hora de inicio *</Label>
                  <Input
                    type="datetime-local"
                    value={newEvent.start}
                    onChange={(e) => setNewEvent({ ...newEvent, start: e.target.value })}
                  />
                </div>
                <div>
                  <Label>Fecha y hora de fin *</Label>
                  <Input
                    type="datetime-local"
                    value={newEvent.end}
                    onChange={(e) => setNewEvent({ ...newEvent, end: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <Label>Descripción (opcional)</Label>
                <Textarea
                  placeholder="Ej: Revisión de progreso, ajuste de rutina y plan nutricional"
                  value={newEvent.description}
                  onChange={(e) => setNewEvent({ ...newEvent, description: e.target.value })}
                  rows={3}
                />
              </div>

              <div className="flex gap-3 pt-4">
                <Button onClick={createEvent} disabled={loading} className="flex-1 bg-green-600 hover:bg-green-700">
                  <CalendarPlus className="h-4 w-4 mr-2" />
                  {loading ? 'Creando...' : 'Crear Revisión'}
                </Button>
                <Button variant="outline" onClick={() => setShowCreateModal(false)} className="flex-1">
                  Cancelar
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default GoogleCalendarManager;
