import React, { useState } from 'react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Upload, FileText, Loader2 } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const EditProfileForm = ({ user, onUpdate }) => {
  const [formData, setFormData] = useState({
    name: user.name || '',
    email: user.email || '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const token = localStorage.getItem('token');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (formData.password && formData.password !== formData.confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }

    setLoading(true);

    try {
      const updateData = {
        name: formData.name,
        email: formData.email
      };

      if (formData.password) {
        updateData.password = formData.password;
      }

      const response = await axios.patch(`${API}/users/me`, updateData, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });

      setSuccess('Perfil actualizado correctamente');
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      if (onUpdate) {
        onUpdate(response.data.user);
      }

      // Clear password fields
      setFormData({
        ...formData,
        password: '',
        confirmPassword: ''
      });
    } catch (error) {
      setError(error.response?.data?.detail || 'Error al actualizar el perfil');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
          {success}
        </div>
      )}

      <div>
        <Label htmlFor="name">Nombre</Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />
      </div>

      <div>
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          required
        />
      </div>

      <div className="border-t pt-4 mt-4">
        <h4 className="font-semibold mb-3">Cambiar Contraseña (opcional)</h4>
        <div className="space-y-3">
          <div>
            <Label htmlFor="password">Nueva Contraseña</Label>
            <Input
              id="password"
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="Dejar en blanco para no cambiar"
            />
          </div>

          {formData.password && (
            <div>
              <Label htmlFor="confirmPassword">Confirmar Nueva Contraseña</Label>
              <Input
                id="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
              />
            </div>
          )}
        </div>
      </div>

      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Guardando...
          </>
        ) : (
          'Guardar Cambios'
        )}
      </Button>
    </form>
  );
};

export const UploadDocumentForm = ({ userId, onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [type, setType] = useState('general');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const token = localStorage.getItem('token');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Por favor selecciona un archivo');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('type', type);

    try {
      const response = await axios.post(`${API}/documents/upload`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        withCredentials: true
      });

      setFile(null);
      setTitle('');
      setType('general');
      setError(''); // Clear any previous errors
      
      if (onUploadSuccess) {
        onUploadSuccess();
      }

      alert('Documento subido correctamente. Tu entrenador lo verá en su panel.');
    } catch (error) {
      console.error('Upload error:', error);
      setError(error.response?.data?.detail || error.message || 'Error al subir el documento');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div>
        <Label htmlFor="docTitle">Título del Documento</Label>
        <Input
          id="docTitle"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Ej: Análisis de sangre, Plan de entrenamiento..."
          required
        />
      </div>

      <div>
        <Label htmlFor="docType">Tipo de Documento</Label>
        <select
          id="docType"
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="w-full border rounded-md px-3 py-2"
        >
          <option value="general">General</option>
          <option value="medical">Médico</option>
          <option value="nutrition">Nutrición</option>
          <option value="training">Entrenamiento</option>
        </select>
      </div>

      <div>
        <Label htmlFor="docFile">Archivo</Label>
        <Input
          id="docFile"
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
          required
        />
        <p className="text-sm text-gray-500 mt-1">
          Formatos aceptados: PDF, DOC, DOCX, JPG, PNG
        </p>
      </div>

      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Subiendo...
          </>
        ) : (
          <>
            <Upload className="mr-2 h-4 w-4" />
            Subir Documento
          </>
        )}
      </Button>
    </form>
  );
};

export default { EditProfileForm, UploadDocumentForm };
