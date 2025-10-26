import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import axios from 'axios';
import { 
  CreditCard, 
  FileText, 
  Download, 
  Bell, 
  MessageSquare,
  Calendar,
  LogOut,
  User,
  CheckCircle,
  AlertCircle,
  ExternalLink
} from 'lucide-react';
import ChatBox from '../components/ChatBox';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UserDashboard = () => {
  const { user, logout, token } = useAuth();
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [forms, setForms] = useState([]);
  const [pdfs, setPdfs] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [unreadAlerts, setUnreadAlerts] = useState(0);
  const [showChat, setShowChat] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/users/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setUserData(response.data.user);
      setForms(response.data.forms || []);
      setPdfs(response.data.pdfs || []);
      setAlerts(response.data.alerts || []);
      setUnreadAlerts(response.data.unread_alerts || 0);
      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard:', error);
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handlePayment = () => {
    window.open('https://buy.stripe.com/fZu6oGamGbw1444gr1cs80d', '_blank');
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

  if (!userData) {
    return <div className="min-h-screen flex items-center justify-center">Error al cargar datos</div>;
  }

  const isPending = userData.subscription?.payment_status === 'pending';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-gray-900">Panel de Usuario</h1>
            {isPending && (
              <Badge className="bg-orange-100 text-orange-700 border-orange-300">
                Pago pendiente
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="font-semibold text-gray-900">{userData.name}</p>
              <p className="text-sm text-gray-500">@{userData.username}</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleLogout}
              className="flex items-center gap-2"
            >
              <LogOut className="h-4 w-4" />
              Salir
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Payment Alert */}
        {isPending && (
          <Card className="mb-6 border-orange-200 bg-orange-50">
            <CardContent className="pt-6">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  <AlertCircle className="h-8 w-8 text-orange-500" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-gray-900 mb-2">
                    ¡Completa tu pago para activar tu plan!
                  </h3>
                  <p className="text-gray-700 mb-4">
                    Tu cuenta ha sido creada exitosamente. Para comenzar a recibir tu plan de entrenamiento y nutrición, completa el pago.
                  </p>
                  <Button
                    onClick={handlePayment}
                    className="bg-gradient-to-r from-orange-400 to-orange-500 hover:from-orange-500 hover:to-orange-600 text-white"
                  >
                    <CreditCard className="mr-2 h-5 w-5" />
                    Pagar ahora - 49,90€/mes
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Main Content */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 lg:w-auto">
            <TabsTrigger value="overview">Resumen</TabsTrigger>
            <TabsTrigger value="documents">Documentos</TabsTrigger>
            <TabsTrigger value="alerts" className="relative">
              Alertas
              {unreadAlerts > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {unreadAlerts}
                </span>
              )}
            </TabsTrigger>
            <TabsTrigger value="chat">Chat</TabsTrigger>
            <TabsTrigger value="profile">Perfil</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              {/* Subscription Status */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    Estado de suscripción
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Plan:</span>
                    <span className="font-semibold">Trabaja con mi equipo</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Estado:</span>
                    <Badge className={isPending ? 'bg-orange-100 text-orange-700' : 'bg-green-100 text-green-700'}>
                      {isPending ? 'Pago pendiente' : 'Activo'}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Inicio:</span>
                    <span className="font-semibold">{new Date(userData.subscription.start_date).toLocaleDateString('es-ES')}</span>
                  </div>
                  {userData.next_review && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Próxima revisión:</span>
                      <span className="font-semibold">{new Date(userData.next_review).toLocaleDateString('es-ES')}</span>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Quick Actions */}
              <Card>
                <CardHeader>
                  <CardTitle>Acciones rápidas</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {isPending ? (
                    <Button
                      onClick={handlePayment}
                      className="w-full bg-gradient-to-r from-orange-400 to-orange-500 hover:from-orange-500 hover:to-orange-600 text-white"
                    >
                      <CreditCard className="mr-2 h-5 w-5" />
                      Completar pago
                    </Button>
                  ) : (
                    <>
                      <Button
                        onClick={() => setShowChat(true)}
                        className="w-full bg-blue-500 hover:bg-blue-600 text-white"
                      >
                        <MessageSquare className="mr-2 h-5 w-5" />
                        Abrir chat
                      </Button>
                      <Button
                        variant="outline"
                        className="w-full"
                        onClick={() => document.querySelector('[value="documents"]').click()}
                      >
                        <FileText className="mr-2 h-5 w-5" />
                        Ver mis documentos
                      </Button>
                    </>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            {!isPending && (
              <Card>
                <CardHeader>
                  <CardTitle>Actividad reciente</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {pdfs.length > 0 && (
                      <div className="flex items-start gap-3 pb-3 border-b">
                        <Download className="h-5 w-5 text-blue-500 mt-0.5" />
                        <div>
                          <p className="font-medium">Nuevo documento recibido</p>
                          <p className="text-sm text-gray-600">{pdfs[pdfs.length - 1].title}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date(pdfs[pdfs.length - 1].upload_date).toLocaleDateString('es-ES')}
                          </p>
                        </div>
                      </div>
                    )}
                    {forms.length > 0 && (
                      <div className="flex items-start gap-3">
                        <FileText className="h-5 w-5 text-green-500 mt-0.5" />
                        <div>
                          <p className="font-medium">Formulario {forms[0].completed ? 'completado' : 'recibido'}</p>
                          <p className="text-sm text-gray-600">{forms[0].title}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date(forms[0].sent_date).toLocaleDateString('es-ES')}
                          </p>
                        </div>
                      </div>
                    )}
                    {pdfs.length === 0 && forms.length === 0 && (
                      <p className="text-gray-500 text-center py-4">No hay actividad reciente</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Documents Tab */}
          <TabsContent value="documents" className="space-y-6">
            {isPending ? (
              <Card>
                <CardContent className="pt-6 text-center py-12">
                  <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-4">Completa el pago para acceder a tus documentos</p>
                  <Button onClick={handlePayment}>
                    Completar pago
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <>
                {/* Forms */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="h-5 w-5" />
                      Formularios
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {forms.length > 0 ? (
                      <div className="space-y-3">
                        {forms.map((form) => (
                          <div key={form.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                            <div>
                              <p className="font-medium">{form.title}</p>
                              <p className="text-sm text-gray-600">Enviado: {new Date(form.sent_date).toLocaleDateString('es-ES')}</p>
                            </div>
                            <Button
                              size="sm"
                              variant={form.completed ? 'outline' : 'default'}
                              onClick={() => window.open(form.url, '_blank')}
                            >
                              {form.completed ? 'Ver' : 'Completar'}
                              <ExternalLink className="ml-2 h-4 w-4" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-center py-8">No hay formularios disponibles aún</p>
                    )}
                  </CardContent>
                </Card>

                {/* PDFs */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Download className="h-5 w-5" />
                      Planes y documentos
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {pdfs.length > 0 ? (
                      <div className="grid md:grid-cols-2 gap-4">
                        {pdfs.map((pdf) => (
                          <div key={pdf.id} className="p-4 bg-gradient-to-br from-blue-50 to-orange-50 rounded-lg border">
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex-1">
                                <p className="font-semibold text-gray-900">{pdf.title}</p>
                                <p className="text-sm text-gray-600 mt-1">
                                  Subido: {new Date(pdf.upload_date).toLocaleDateString('es-ES')}
                                </p>
                              </div>
                              <Badge className={pdf.type === 'training' ? 'bg-blue-100 text-blue-700' : 'bg-orange-100 text-orange-700'}>
                                {pdf.type === 'training' ? 'Entrenamiento' : 'Nutrición'}
                              </Badge>
                            </div>
                            <Button 
                              size="sm" 
                              className="w-full mt-3" 
                              variant="outline"
                              onClick={() => {
                                const token = localStorage.getItem('token');
                                window.open(`${BACKEND_URL}/api/pdfs/${pdf.id}/download?token=${token}`, '_blank');
                              }}
                            >
                              <Download className="mr-2 h-4 w-4" />
                              Descargar PDF
                            </Button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-center py-8">No hay documentos disponibles aún</p>
                    )}
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          {/* Alerts Tab */}
          <TabsContent value="alerts">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="h-5 w-5" />
                  Notificaciones y alertas
                </CardTitle>
              </CardHeader>
              <CardContent>
                {alerts.length > 0 ? (
                  <div className="space-y-3">
                    {alerts.map((alert) => (
                      <div
                        key={alert.id}
                        className={`p-4 rounded-lg border ${
                          alert.read ? 'bg-gray-50' : 'bg-blue-50 border-blue-200'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-semibold text-gray-900">{alert.title}</h4>
                              {!alert.read && <Badge className="bg-blue-500">Nuevo</Badge>}
                            </div>
                            <p className="text-sm text-gray-600 mb-2">{alert.message}</p>
                            <p className="text-xs text-gray-500">{new Date(alert.date).toLocaleDateString('es-ES')}</p>
                          </div>
                        </div>
                        {alert.link && (
                          <Button
                            size="sm"
                            className="mt-3"
                            onClick={() => window.open(alert.link, '_blank')}
                          >
                            Ir al cuestionario
                            <ExternalLink className="ml-2 h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-8">No tienes notificaciones</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Chat Tab */}
          <TabsContent value="chat">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  Chat con el equipo
                </CardTitle>
              </CardHeader>
              <CardContent>
                {isPending ? (
                  <div className="text-center py-12">
                    <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-4">Completa el pago para acceder al chat</p>
                    <Button onClick={handlePayment}>
                      Completar pago
                    </Button>
                  </div>
                ) : (
                  <ChatBox userId={userData.id} />
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Profile Tab */}
          <TabsContent value="profile">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Mi perfil
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Nombre de usuario</label>
                    <p className="mt-1 text-gray-900">{userData.username}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Email</label>
                    <p className="mt-1 text-gray-900">{userData.email}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Plan</label>
                    <p className="mt-1 text-gray-900">Trabaja con mi equipo</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Miembro desde</label>
                    <p className="mt-1 text-gray-900">{new Date(userData.subscription.startDate).toLocaleDateString('es-ES')}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Floating Chat Button */}
      {!isPending && !showChat && (
        <button
          onClick={() => setShowChat(true)}
          className="fixed bottom-6 right-6 bg-blue-500 hover:bg-blue-600 text-white rounded-full p-4 shadow-2xl transition-all duration-300 hover:scale-110 z-50"
        >
          <MessageSquare className="h-6 w-6" />
        </button>
      )}

      {/* Chat Modal */}
      {showChat && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center justify-center p-4">
          <div className="bg-white rounded-t-3xl sm:rounded-3xl w-full sm:max-w-2xl max-h-[80vh] flex flex-col shadow-2xl">
            <div className="p-4 border-b flex items-center justify-between">
              <h3 className="text-lg font-bold">Chat con el equipo</h3>
              <Button size="sm" variant="ghost" onClick={() => setShowChat(false)}>
                Cerrar
              </Button>
            </div>
            <div className="flex-1 overflow-hidden">
              <ChatBox userId={userData.id} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserDashboard;