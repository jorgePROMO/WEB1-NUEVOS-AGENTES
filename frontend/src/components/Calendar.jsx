import React, { useState, useEffect } from 'react';
import { Calendar as BigCalendar, dateFnsLocalizer } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay } from 'date-fns';
import { es } from 'date-fns/locale';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import axios from 'axios';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Loader2, X, Calendar as CalendarIcon, Clock, User } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const locales = {
  'es': es,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek: () => startOfWeek(new Date(), { locale: es }),
  getDay,
  locales,
});

const messages = {
  allDay: 'Todo el día',
  previous: 'Anterior',
  next: 'Siguiente',
  today: 'Hoy',
  month: 'Mes',
  week: 'Semana',
  day: 'Día',
  agenda: 'Agenda',
  date: 'Fecha',
  time: 'Hora',
  event: 'Evento',
  noEventsInRange: 'No hay eventos en este rango',
  showMore: total => `+ Ver más (${total})`
};

export const AdminCalendar = () => {
  const [events, setEvents] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [formData, setFormData] = useState({
    user_id: '',
    title: 'Revisión Mensual',
    description: '',
    date: '',
    duration: 60,
    type: 'review'
  });

  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchClients();
    fetchSessions();
  }, []);

  const fetchClients = async () => {
    try {
      const response = await axios.get(`${API}/admin/clients`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setClients(response.data.clients);
    } catch (error) {
      console.error('Error fetching clients:', error);
    }
  };

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/sessions/admin/all`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      const formattedEvents = response.data.sessions.map(session => ({
        id: session.id || session._id,
        title: session.title,
        start: new Date(session.date),
        end: new Date(new Date(session.date).getTime() + (session.duration * 60000)),
        resource: session
      }));
      
      setEvents(formattedEvents);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching sessions:', error);
      setLoading(false);
    }
  };

  const handleCreateSession = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/sessions/create`, {
        ...formData,
        date: new Date(formData.date).toISOString()
      }, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      setShowCreateModal(false);
      setFormData({
        user_id: '',
        title: 'Revisión Mensual',
        description: '',
        date: '',
        duration: 60,
        type: 'review'
      });
      fetchSessions();
    } catch (error) {
      console.error('Error creating session:', error);
      alert('Error al crear la sesión');
    }
  };

  const handleReschedule = async (e) => {
    e.preventDefault();
    try {
      await axios.patch(`${API}/sessions/${selectedEvent.id}/reschedule`, {
        date: new Date(formData.date).toISOString()
      }, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      setShowEditModal(false);
      setSelectedEvent(null);
      fetchSessions();
    } catch (error) {
      console.error('Error rescheduling session:', error);
      alert('Error al reagendar la sesión');
    }
  };

  const handleDeleteSession = async () => {
    if (!window.confirm('¿Estás seguro de eliminar esta sesión?')) return;
    
    try {
      await axios.delete(`${API}/sessions/${selectedEvent.id}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      setShowEditModal(false);
      setSelectedEvent(null);
      fetchSessions();
    } catch (error) {
      console.error('Error deleting session:', error);
      alert('Error al eliminar la sesión');
    }
  };

  const handleSelectEvent = (event) => {
    setSelectedEvent(event);
    setFormData({
      ...formData,
      date: format(event.start, "yyyy-MM-dd'T'HH:mm")
    });
    setShowEditModal(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Calendario de Sesiones</h2>
        <Button onClick={() => setShowCreateModal(true)} className="bg-blue-500 hover:bg-blue-600">
          <CalendarIcon className="mr-2 h-4 w-4" />
          Nueva Sesión
        </Button>
      </div>

      <div className="bg-white p-4 rounded-lg shadow" style={{ height: '600px' }}>
        <BigCalendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          messages={messages}
          culture="es"
          onSelectEvent={handleSelectEvent}
          views={['month', 'week', 'day', 'agenda']}
          defaultView="month"
          style={{ height: '100%' }}
        />
      </div>

      {/* Create Session Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Crear Nueva Sesión</DialogTitle>
            <DialogDescription>Programa una sesión con un cliente</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateSession} className="space-y-4">
            <div>
              <Label htmlFor="client">Cliente</Label>
              <Select value={formData.user_id} onValueChange={(value) => setFormData({...formData, user_id: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona un cliente" />
                </SelectTrigger>
                <SelectContent>
                  {clients.map(client => (
                    <SelectItem key={client.id} value={client.id}>
                      {client.name} ({client.email})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="title">Título</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                required
              />
            </div>
            
            <div>
              <Label htmlFor="date">Fecha y Hora</Label>
              <Input
                id="date"
                type="datetime-local"
                value={formData.date}
                onChange={(e) => setFormData({...formData, date: e.target.value})}
                required
              />
            </div>
            
            <div>
              <Label htmlFor="duration">Duración (minutos)</Label>
              <Input
                id="duration"
                type="number"
                value={formData.duration}
                onChange={(e) => setFormData({...formData, duration: parseInt(e.target.value)})}
                required
              />
            </div>
            
            <div className="flex gap-2 justify-end">
              <Button type="button" variant="outline" onClick={() => setShowCreateModal(false)}>
                Cancelar
              </Button>
              <Button type="submit" className="bg-blue-500 hover:bg-blue-600">
                Crear Sesión
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit Session Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Gestionar Sesión</DialogTitle>
            <DialogDescription>
              {selectedEvent && (
                <div className="mt-2 space-y-1">
                  <p><strong>Cliente:</strong> {selectedEvent.resource?.user_id}</p>
                  <p><strong>Título:</strong> {selectedEvent.title}</p>
                </div>
              )}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleReschedule} className="space-y-4">
            <div>
              <Label htmlFor="editDate">Nueva Fecha y Hora</Label>
              <Input
                id="editDate"
                type="datetime-local"
                value={formData.date}
                onChange={(e) => setFormData({...formData, date: e.target.value})}
                required
              />
            </div>
            
            <div className="flex gap-2 justify-between">
              <Button 
                type="button" 
                variant="destructive" 
                onClick={handleDeleteSession}
              >
                Eliminar
              </Button>
              <div className="flex gap-2">
                <Button type="button" variant="outline" onClick={() => setShowEditModal(false)}>
                  Cancelar
                </Button>
                <Button type="submit" className="bg-blue-500 hover:bg-blue-600">
                  Reagendar
                </Button>
              </div>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export const UserCalendar = ({ userId }) => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showRescheduleModal, setShowRescheduleModal] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [newDate, setNewDate] = useState('');

  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchSessions();
  }, [userId]);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/sessions/user/${userId}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      const formattedEvents = response.data.sessions.map(session => ({
        id: session.id || session._id,
        title: session.title,
        start: new Date(session.date),
        end: new Date(new Date(session.date).getTime() + (session.duration * 60000)),
        resource: session
      }));
      
      setEvents(formattedEvents);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching sessions:', error);
      setLoading(false);
    }
  };

  const handleReschedule = async (e) => {
    e.preventDefault();
    try {
      await axios.patch(`${API}/sessions/${selectedEvent.id}/reschedule`, {
        date: new Date(newDate).toISOString()
      }, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      
      setShowRescheduleModal(false);
      setSelectedEvent(null);
      fetchSessions();
      alert('Sesión reagendada correctamente. Se ha enviado una notificación por email.');
    } catch (error) {
      console.error('Error rescheduling session:', error);
      alert('Error al reagendar la sesión');
    }
  };

  const handleSelectEvent = (event) => {
    setSelectedEvent(event);
    setNewDate(format(event.start, "yyyy-MM-dd'T'HH:mm"));
    setShowRescheduleModal(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Mis Sesiones Programadas</h2>

      <div className="bg-white p-4 rounded-lg shadow" style={{ height: '600px' }}>
        <BigCalendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          messages={messages}
          culture="es"
          onSelectEvent={handleSelectEvent}
          views={['month', 'week', 'day', 'agenda']}
          defaultView="month"
          style={{ height: '100%' }}
        />
      </div>

      {/* Reschedule Modal */}
      <Dialog open={showRescheduleModal} onOpenChange={setShowRescheduleModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reagendar Sesión</DialogTitle>
            <DialogDescription>
              {selectedEvent && (
                <div className="mt-2 space-y-1">
                  <p><strong>Título:</strong> {selectedEvent.title}</p>
                  <p><strong>Fecha actual:</strong> {format(selectedEvent.start, 'dd/MM/yyyy HH:mm', { locale: es })}</p>
                </div>
              )}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleReschedule} className="space-y-4">
            <div>
              <Label htmlFor="newDate">Nueva Fecha y Hora</Label>
              <Input
                id="newDate"
                type="datetime-local"
                value={newDate}
                onChange={(e) => setNewDate(e.target.value)}
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                * Recibirás un email de confirmación
              </p>
            </div>
            
            <div className="flex gap-2 justify-end">
              <Button type="button" variant="outline" onClick={() => setShowRescheduleModal(false)}>
                Cancelar
              </Button>
              <Button type="submit" className="bg-blue-500 hover:bg-blue-600">
                Confirmar Reagendamiento
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};
