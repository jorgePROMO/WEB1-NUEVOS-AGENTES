import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { 
  AlertTriangle,
  AlertCircle, 
  CheckCircle,
  Mail,
  MessageSquare,
  Eye,
  RefreshCw
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const ClientsAtRisk = ({ token, onClientSelect }) => {
  const [clientsAtRisk, setClientsAtRisk] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterLevel, setFilterLevel] = useState('all');
  const [stats, setStats] = useState({ total_red: 0, total_yellow: 0 });

  useEffect(() => {
    loadClientsAtRisk();
    // Refresh every 5 minutes
    const interval = setInterval(loadClientsAtRisk, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const loadClientsAtRisk = async () => {
    try {
      const response = await axios.get(`${API}/admin/clients-at-risk`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setClientsAtRisk(response.data.clients_at_risk || []);
      setStats({
        total_red: response.data.total_red || 0,
        total_yellow: response.data.total_yellow || 0
      });
      setLoading(false);
    } catch (error) {
      console.error('Error loading clients at risk:', error);
      setLoading(false);
    }
  };

  const filteredClients = filterLevel === 'all' 
    ? clientsAtRisk 
    : clientsAtRisk.filter(c => c.risk_level === filterLevel);

  const getRiskIcon = (level) => {
    switch(level) {
      case 'red': return <AlertTriangle className="h-5 w-5 text-red-600" />;
      case 'yellow': return <AlertCircle className="h-5 w-5 text-yellow-600" />;
      default: return <CheckCircle className="h-5 w-5 text-green-600" />;
    }
  };

  const getRiskBadge = (level) => {
    switch(level) {
      case 'red':
        return <Badge className="bg-red-100 text-red-800 border-red-300">🔴 Crítico</Badge>;
      case 'yellow':
        return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-300">🟡 Atención</Badge>;
      default:
        return <Badge className="bg-green-100 text-green-800 border-green-300">🟢 OK</Badge>;
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="pt-6 text-center">
          <p className="text-gray-500">Cargando clientes en riesgo...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <Card className="bg-gradient-to-r from-red-50 to-orange-50 border-red-200">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl flex items-center gap-2">
                <AlertTriangle className="h-6 w-6 text-red-600" />
                Clientes que Requieren Atención
              </CardTitle>
              <p className="text-gray-600 mt-1">Indicadores de riesgo basados en actividad</p>
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={loadClientsAtRisk}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Actualizar
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg border border-red-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold text-red-600">{stats.total_red}</p>
                  <p className="text-sm text-gray-600">Críticos</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-red-400" />
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-yellow-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold text-yellow-600">{stats.total_yellow}</p>
                  <p className="text-sm text-gray-600">Requieren Atención</p>
                </div>
                <AlertCircle className="h-8 w-8 text-yellow-400" />
              </div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-green-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold text-green-600">
                    {stats.total_red + stats.total_yellow}
                  </p>
                  <p className="text-sm text-gray-600">Total en Seguimiento</p>
                </div>
                <Eye className="h-8 w-8 text-green-400" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Filters */}
      <div className="flex gap-2">
        <Button
          variant={filterLevel === 'all' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setFilterLevel('all')}
        >
          Todos ({clientsAtRisk.length})
        </Button>
        <Button
          variant={filterLevel === 'red' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setFilterLevel('red')}
          className={filterLevel === 'red' ? 'bg-red-600' : ''}
        >
          🔴 Críticos ({stats.total_red})
        </Button>
        <Button
          variant={filterLevel === 'yellow' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setFilterLevel('yellow')}
          className={filterLevel === 'yellow' ? 'bg-yellow-600' : ''}
        >
          🟡 Atención ({stats.total_yellow})
        </Button>
      </div>

      {/* Clients List */}
      <div className="space-y-3">
        {filteredClients.map(client => (
          <Card 
            key={client.client_id} 
            className={`border-2 ${
              client.risk_level === 'red' 
                ? 'border-red-300 bg-red-50' 
                : 'border-yellow-300 bg-yellow-50'
            }`}
          >
            <CardContent className="pt-4">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3 flex-1">
                  {getRiskIcon(client.risk_level)}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-bold text-lg">{client.client_name}</h3>
                      {getRiskBadge(client.risk_level)}
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{client.client_email}</p>
                    
                    {/* Risk Reasons */}
                    <div className="space-y-1">
                      {client.risk_reasons.map((reason, idx) => (
                        <div key={idx} className="flex items-center gap-2">
                          <span className="text-xs">⚠️</span>
                          <p className="text-sm font-medium text-gray-700">{reason}</p>
                        </div>
                      ))}
                    </div>

                    {/* Last Activity */}
                    {client.last_activity_date && (
                      <p className="text-xs text-gray-500 mt-2">
                        Última actividad: {new Date(client.last_activity_date).toLocaleDateString('es-ES')}
                      </p>
                    )}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2 ml-4">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => onClientSelect && onClientSelect(client.client_id)}
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    Ver
                  </Button>
                  <Button
                    size="sm"
                    className="bg-green-600 hover:bg-green-700"
                    onClick={() => window.open(`https://wa.me/`, '_blank')}
                  >
                    <MessageSquare className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {filteredClients.length === 0 && (
          <Card>
            <CardContent className="pt-12 pb-12 text-center">
              <CheckCircle className="h-16 w-16 text-green-400 mx-auto mb-4" />
              <p className="text-gray-600 text-lg">
                {filterLevel === 'all' 
                  ? '¡Excelente! No hay clientes que requieran atención inmediata' 
                  : `No hay clientes en nivel ${filterLevel === 'red' ? 'crítico' : 'de atención'}`
                }
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default ClientsAtRisk;
