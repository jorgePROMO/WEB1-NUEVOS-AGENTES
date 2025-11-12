import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2, CheckCircle, Clock, Send, MessageSquare, FileText, ArrowRight } from 'lucide-react';

const EDN360Manager = () => {
  const [activeTab, setActiveTab] = useState('generate');
  const [clients, setClients] = useState([]);
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedClient, setSelectedClient] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

  // Cargar clientes
  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/admin/users`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setClients(data.users || []);
      }
    } catch (error) {
      console.error('Error loading clients:', error);
    }
  };

  // Cargar planes de un cliente
  const loadClientPlans = async (clientId) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/admin/edn360/client/${clientId}/plans`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPlans(data.plans || []);
      }
    } catch (error) {
      console.error('Error loading plans:', error);
    } finally {
      setLoading(false);
    }
  };

  // Generar plan inicial
  const generateInitialPlan = async () => {
    if (!selectedClient) {
      alert('Por favor selecciona un cliente');
      return;
    }

    try {
      setGenerating(true);
      const token = localStorage.getItem('token');
      
      // Obtener cuestionario del cliente
      const questResponse = await fetch(`${BACKEND_URL}/api/admin/users/${selectedClient}/questionnaires`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!questResponse.ok) {
        throw new Error('No se encontró cuestionario para este cliente');
      }

      const questData = await questResponse.json();
      const questionnaireId = questData.questionnaires?.[0]?._id;

      if (!questionnaireId) {
        throw new Error('Cliente no tiene cuestionario completado');
      }

      // Generar plan
      const formData = new FormData();
      formData.append('questionnaire_id', questionnaireId);
      formData.append('client_id', selectedClient);

      const response = await fetch(`${BACKEND_URL}/api/admin/edn360/generate-initial-plan`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Plan generado exitosamente!\nID: ${data.plan_id}\nDuración: ${Math.round(data.duration_seconds)}s`);
        loadClientPlans(selectedClient);
        setActiveTab('plans');
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Error generando plan');
      }
    } catch (error) {
      console.error('Error:', error);
      alert(`Error: ${error.message}`);
    } finally {
      setGenerating(false);
    }
  };

  // Aprobar plan
  const approvePlan = async (planId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/admin/edn360/plans/${planId}/approve`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        alert('Plan aprobado exitosamente');
        loadClientPlans(selectedClient);
      }
    } catch (error) {
      console.error('Error approving plan:', error);
      alert('Error al aprobar plan');
    }
  };

  // Enviar mensaje de chat para modificar plan
  const sendChatMessage = async () => {
    if (!chatMessage.trim() || !selectedPlan) return;

    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('message', chatMessage);

      const response = await fetch(`${BACKEND_URL}/api/admin/edn360/plans/${selectedPlan._id}/chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        
        // Añadir al historial de chat
        setChatHistory([
          ...chatHistory,
          {
            type: 'user',
            message: chatMessage,
            timestamp: new Date()
          },
          {
            type: 'assistant',
            message: data.ai_response,
            timestamp: new Date(),
            modificationsApplied: data.modifications_made
          }
        ]);

        setChatMessage('');

        if (data.modifications_made) {
          alert(`Plan modificado exitosamente (versión ${data.new_version})`);
          loadClientPlans(selectedClient);
        }
      }
    } catch (error) {
      console.error('Error in chat:', error);
      alert('Error al procesar mensaje');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      draft: { color: 'bg-yellow-500', text: 'Borrador' },
      approved: { color: 'bg-green-500', text: 'Aprobado' },
      sent: { color: 'bg-blue-500', text: 'Enviado' },
      generating: { color: 'bg-gray-500', text: 'Generando' }
    };

    const config = statusConfig[status] || statusConfig.draft;
    return <Badge className={`${config.color} text-white`}>{config.text}</Badge>;
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-6 w-6" />
            Sistema E.D.N.360
          </CardTitle>
          <CardDescription>
            Generación automática de planes con 26 agentes especializados
          </CardDescription>
        </CardHeader>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="generate">Generar Plan</TabsTrigger>
          <TabsTrigger value="plans">Planes Generados</TabsTrigger>
          <TabsTrigger value="modify">Modificar Plan</TabsTrigger>
        </TabsList>

        {/* TAB: Generar Plan */}
        <TabsContent value="generate" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Generar Nuevo Plan E.D.N.360</CardTitle>
              <CardDescription>
                Selecciona un cliente para generar su plan inicial (2-4 minutos)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Cliente
                </label>
                <select
                  value={selectedClient || ''}
                  onChange={(e) => {
                    setSelectedClient(e.target.value);
                    loadClientPlans(e.target.value);
                  }}
                  className="w-full p-2 border rounded-lg"
                >
                  <option value="">Selecciona un cliente...</option>
                  {clients.map(client => (
                    <option key={client._id} value={client._id}>
                      {client.name} ({client.email})
                    </option>
                  ))}
                </select>
              </div>

              {selectedClient && (
                <Alert>
                  <Clock className="h-4 w-4" />
                  <AlertDescription>
                    El sistema ejecutará 18 agentes (E1-E9 + N0-N8) para crear un plan completo de entrenamiento y nutrición.
                  </AlertDescription>
                </Alert>
              )}

              <Button
                onClick={generateInitialPlan}
                disabled={!selectedClient || generating}
                className="w-full"
              >
                {generating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generando Plan...
                  </>
                ) : (
                  <>
                    <ArrowRight className="mr-2 h-4 w-4" />
                    Generar Plan Inicial
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* TAB: Planes Generados */}
        <TabsContent value="plans" className="space-y-4">
          {loading ? (
            <div className="flex justify-center p-8">
              <Loader2 className="h-8 w-8 animate-spin" />
            </div>
          ) : plans.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center text-gray-500">
                No hay planes generados para este cliente
              </CardContent>
            </Card>
          ) : (
            plans.map(plan => (
              <Card key={plan._id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">{plan.client_name}</CardTitle>
                      <CardDescription>
                        ID: {plan._id}
                      </CardDescription>
                    </div>
                    {getStatusBadge(plan.status)}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Tipo:</span> {plan.plan_type}
                    </div>
                    <div>
                      <span className="font-medium">Versión:</span> {plan.current_version || 1}
                    </div>
                    <div>
                      <span className="font-medium">Creado:</span>{' '}
                      {new Date(plan.created_at).toLocaleDateString()}
                    </div>
                    <div>
                      <span className="font-medium">Duración:</span>{' '}
                      {Math.round(plan.total_duration_seconds || 0)}s
                    </div>
                  </div>

                  {plan.validation && (
                    <Alert className={plan.validation.valid ? 'border-green-500' : 'border-yellow-500'}>
                      <CheckCircle className="h-4 w-4" />
                      <AlertDescription>
                        {plan.validation.valid ? (
                          'Plan validado correctamente'
                        ) : (
                          <>
                            Advertencias: {plan.validation.warnings?.length || 0}
                          </>
                        )}
                      </AlertDescription>
                    </Alert>
                  )}

                  <div className="flex gap-2">
                    {plan.status === 'draft' && (
                      <Button onClick={() => approvePlan(plan._id)} size="sm">
                        <CheckCircle className="mr-2 h-4 w-4" />
                        Aprobar Plan
                      </Button>
                    )}
                    
                    <Button
                      onClick={() => {
                        setSelectedPlan(plan);
                        setChatHistory(plan.chat_history || []);
                        setActiveTab('modify');
                      }}
                      variant="outline"
                      size="sm"
                    >
                      <MessageSquare className="mr-2 h-4 w-4" />
                      Modificar con IA
                    </Button>

                    {plan.status === 'approved' && (
                      <Button variant="outline" size="sm">
                        <Send className="mr-2 h-4 w-4" />
                        Enviar
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        {/* TAB: Modificar Plan */}
        <TabsContent value="modify" className="space-y-4">
          {!selectedPlan ? (
            <Card>
              <CardContent className="p-8 text-center text-gray-500">
                Selecciona un plan desde la pestaña "Planes Generados" para modificarlo
              </CardContent>
            </Card>
          ) : (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Modificar Plan con IA</CardTitle>
                  <CardDescription>
                    Plan: {selectedPlan._id} (v{selectedPlan.current_version || 1})
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="border rounded-lg p-4 h-96 overflow-y-auto bg-gray-50">
                    {chatHistory.length === 0 ? (
                      <div className="text-center text-gray-500 mt-20">
                        Escribe un mensaje para modificar el plan
                        <div className="text-sm mt-2">
                          Ejemplo: "Reduce las series de press banca en 2"
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {chatHistory.map((msg, idx) => (
                          <div
                            key={idx}
                            className={`p-3 rounded-lg ${
                              msg.type === 'user'
                                ? 'bg-blue-100 ml-8'
                                : 'bg-white mr-8 border'
                            }`}
                          >
                            <div className="text-sm font-medium mb-1">
                              {msg.type === 'user' ? 'Tú' : 'IA'}
                            </div>
                            <div className="text-sm whitespace-pre-wrap">
                              {msg.message || msg.user_message || msg.ai_response}
                            </div>
                            {msg.modificationsApplied && (
                              <Badge className="mt-2 bg-green-500">
                                Modificaciones aplicadas
                              </Badge>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={chatMessage}
                      onChange={(e) => setChatMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                      placeholder="Escribe tu solicitud de modificación..."
                      className="flex-1 p-2 border rounded-lg"
                      disabled={loading}
                    />
                    <Button
                      onClick={sendChatMessage}
                      disabled={!chatMessage.trim() || loading}
                    >
                      {loading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Send className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default EDN360Manager;
