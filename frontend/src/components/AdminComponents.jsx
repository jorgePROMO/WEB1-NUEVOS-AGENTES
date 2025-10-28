import React, { useState } from 'react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Loader2, Mail, Edit } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const EditUserModal = ({ user, open, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    subscription_status: user?.subscription?.status || 'pending',
    subscription_plan: user?.subscription?.plan || 'team',
    payment_status: user?.subscription?.payment_status || 'pending'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const token = localStorage.getItem('token');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.patch(`${API}/admin/users/${user.id}`, formData, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });

      if (onSuccess) {
        onSuccess();
      }
      alert('Usuario actualizado correctamente');
      onClose();
    } catch (error) {
      console.error('Error updating user:', error);
      setError(error.response?.data?.detail || 'Error al actualizar el usuario');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Editar Usuario - {user?.name}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
              {error}
            </div>
          )}

          <div>
            <Label htmlFor="userName">Nombre</Label>
            <Input
              id="userName"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>

          <div>
            <Label htmlFor="userEmail">Email</Label>
            <Input
              id="userEmail"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />
          </div>

          <div>
            <Label htmlFor="subStatus">Estado de Suscripción</Label>
            <select
              id="subStatus"
              value={formData.subscription_status}
              onChange={(e) => setFormData({ ...formData, subscription_status: e.target.value })}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value="pending">Pendiente</option>
              <option value="active">Activa</option>
              <option value="cancelled">Cancelada</option>
              <option value="archived">Archivada</option>
            </select>
          </div>

          <div>
            <Label htmlFor="subPlan">Plan</Label>
            <select
              id="subPlan"
              value={formData.subscription_plan}
              onChange={(e) => setFormData({ ...formData, subscription_plan: e.target.value })}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value="team">Trabaja con mi equipo</option>
              <option value="direct">Trabaja conmigo</option>
            </select>
          </div>

          <div>
            <Label htmlFor="payStatus">Estado de Pago</Label>
            <select
              id="payStatus"
              value={formData.payment_status}
              onChange={(e) => setFormData({ ...formData, payment_status: e.target.value })}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value="pending">Pendiente</option>
              <option value="verified">Verificado</option>
            </select>
          </div>

          <div className="flex gap-2 justify-end pt-4">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Guardando...
                </>
              ) : (
                'Guardar Cambios'
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export const SendPasswordResetButton = ({ userId, userName }) => {
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem('token');

  const handleSend = async () => {
    if (!window.confirm(`¿Enviar email de recuperación de contraseña a ${userName}?`)) {
      return;
    }

    setLoading(true);

    try {
      await axios.post(`${API}/admin/users/${userId}/send-password-reset`, {}, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });

      alert(`Email de recuperación enviado a ${userName}`);
    } catch (error) {
      alert('Error al enviar el email: ' + (error.response?.data?.detail || 'Error desconocido'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      size="sm"
      variant="outline"
      onClick={handleSend}
      disabled={loading}
      className="w-full"
    >
      {loading ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Enviando...
        </>
      ) : (
        <>
          <Mail className="mr-2 h-4 w-4" />
          Enviar Reset de Contraseña
        </>
      )}
    </Button>
  );
};

export default { EditUserModal, SendPasswordResetButton };
