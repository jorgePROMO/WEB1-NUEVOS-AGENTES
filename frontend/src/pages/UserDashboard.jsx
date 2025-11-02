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
  ExternalLink,
  Upload,
  Trash2,
  UtensilsCrossed
} from 'lucide-react';
import ChatBox from '../components/ChatBox';
import { UserCalendar } from '../components/Calendar';
import { EditProfileForm, UploadDocumentForm } from '../components/ProfileComponents';
import NutritionQuestionnaire from '../components/NutritionQuestionnaire';

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
  const [showNutritionQuestionnaire, setShowNutritionQuestionnaire] = useState(false);
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

  const markAlertAsRead = async (alertId) => {
    try {
      await axios.patch(`${API}/alerts/${alertId}/read`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        withCredentials: true
      });
      
      // Update local state
      setAlerts(alerts.map(alert => 
        alert.id === alertId ? { ...alert, read: true } : alert
      ));
      
      // Update unread count
      setUnreadAlerts(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking alert as read:', error);
    }
  };

  const handleDownloadPDF = async (pdfId, pdfTitle) => {
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
      link.setAttribute('download', `${pdfTitle}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Error al descargar el PDF');
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
      {/* Header - Mobile Optimized */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-3 sm:px-6 py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 sm:gap-4 min-w-0 flex-1">
              <h1 className="text-lg sm:text-2xl font-bold text-gray-900 truncate">Panel Usuario</h1>
              {isPending && (
                <Badge className="bg-orange-100 text-orange-700 border-orange-300 text-xs whitespace-nowrap">
                  Pago pendiente
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-2 sm:gap-4">
              <div className="text-right hidden sm:block">
                <p className="font-semibold text-gray-900">{userData.name}</p>
                <p className="text-sm text-gray-500">@{userData.username}</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
                className="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm px-2 sm:px-4"
              >
                <LogOut className="h-3 w-3 sm:h-4 sm:w-4" />
                <span className="hidden sm:inline">Salir</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-3 sm:px-6 py-4 sm:py-8">
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
        <Tabs defaultValue="overview" className="space-y-4 md:space-y-6">
          <TabsList className="grid grid-cols-3 sm:grid-cols-6 w-full gap-1 h-auto p-1">
            <TabsTrigger value="overview" className="text-xs sm:text-sm py-2">
              Resumen
            </TabsTrigger>
            <TabsTrigger value="calendar" className="text-xs sm:text-sm py-2">
              <Calendar className="h-3 w-3 sm:h-4 sm:w-4 sm:mr-2" />
              <span className="hidden sm:inline">Calendario</span>
              <span className="sm:hidden">Cal</span>
            </TabsTrigger>
            <TabsTrigger value="documents" className="text-xs sm:text-sm py-2">
              Docs
            </TabsTrigger>
            <TabsTrigger value="alerts" className="relative text-xs sm:text-sm py-2">
              Alertas
              {unreadAlerts > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 sm:h-5 sm:w-5 flex items-center justify-center">
                  {unreadAlerts}
                </span>
              )}
            </TabsTrigger>
            <TabsTrigger value="chat" className="text-xs sm:text-sm py-2">
              Chat
            </TabsTrigger>
            <TabsTrigger value="profile" className="text-xs sm:text-sm py-2">
              Perfil
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4 sm:space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
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
                    <span className="font-semibold">
                      {userData.subscription?.plan === 'team' ? 'Trabaja con mi equipo' : 
                       userData.subscription?.plan === 'individual' ? 'Individual' : 
                       'Sin plan'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Estado:</span>
                    <Badge className={
                      userData.subscription?.status === 'active' ? 'bg-green-100 text-green-700' :
                      userData.subscription?.status === 'paused' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }>
                      {userData.subscription?.status === 'active' ? 'Activo' :
                       userData.subscription?.status === 'paused' ? 'Pausado' :
                       'Inactivo'}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Pago:</span>
                    <Badge className={
                      userData.subscription?.payment_status === 'verified' ? 'bg-green-100 text-green-700' :
                      userData.subscription?.payment_status === 'pending' ? 'bg-orange-100 text-orange-700' :
                      'bg-red-100 text-red-700'
                    }>
                      {userData.subscription?.payment_status === 'verified' ? 'Verificado' :
                       userData.subscription?.payment_status === 'pending' ? 'Pendiente' :
                       'No verificado'}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Inicio:</span>
                    <span className="font-semibold">{userData.subscription?.start_date ? new Date(userData.subscription.start_date).toLocaleDateString('es-ES') : 'N/A'}</span>
                  </div>
                  {userData.next_review && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Próxima revisión:</span>
                      <span className="font-semibold">{new Date(userData.next_review).toLocaleDateString('es-ES')}</span>
                    </div>
                  )}
                </CardContent>
              </Card>


              {/* Nutrition Questionnaire Button - Only for team plan + verified payment */}
              {userData.subscription?.plan === 'team' && 
               userData.subscription?.payment_status === 'verified' && 
               !userData.nutrition_plan && (
                <Card className="md:col-span-2 border-4 border-green-500 bg-gradient-to-r from-green-50 to-emerald-50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-2xl text-green-800">
                      <UtensilsCrossed className="h-8 w-8 text-green-600" />
                      ¡Completa tu Cuestionario de Nutrición!
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700 mb-6">
                      Genera tu plan de nutrición personalizado. Nuestros agentes calcularán tus macros ideales 
                      y crearán un menú semanal adaptado específicamente a ti.
                    </p>
                    <Button
                      onClick={() => setShowNutritionQuestionnaire(true)}
                      className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white text-lg py-6"
                    >
                      <UtensilsCrossed className="mr-3 h-6 w-6" />
                      Empezar Cuestionario de Nutrición
                    </Button>
                  </CardContent>
                </Card>
              )}

              {/* Show nutrition status if plan exists */}
              {userData.subscription?.plan === 'team' && 
               userData.subscription?.payment_status === 'verified' && 
               userData.nutrition_plan && (
                <Card className="md:col-span-2 border-2 border-green-200 bg-green-50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-green-800">
                      <CheckCircle className="h-6 w-6 text-green-600" />
                      Plan de Nutrición Generado
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700">
                      ✅ Tu plan de nutrición ha sido generado y está siendo revisado por tu entrenador. 
                      {userData.nutrition_plan.pdf_generated && (
                        <span className="block mt-2 text-green-700 font-semibold">
                          📄 Tu plan está disponible en la pestaña "Documentos"
                        </span>
                      )}
                    </p>
                  </CardContent>
                </Card>
              )}

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


          {/* Calendar Tab */}
          <TabsContent value="calendar">
            {user && <UserCalendar userId={user.id} />}
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
                              onClick={() => handleDownloadPDF(pdf.id, pdf.title)}
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
                          {!alert.read && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => markAlertAsRead(alert.id)}
                              className="ml-3"
                            >
                              <CheckCircle className="h-4 w-4 mr-1" />
                              Marcar leída
                            </Button>
                          )}
                        </div>
                        {alert.link && (
                          <Button
                            size="sm"
                            className="mt-3"
                            onClick={() => {
                              if (!alert.read) {
                                markAlertAsRead(alert.id);
                              }
                              window.open(alert.link, '_blank');
                            }}
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
            <div className="grid md:grid-cols-2 gap-6">
              {/* Edit Profile */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5" />
                    Editar Mi Perfil
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <EditProfileForm 
                    user={userData} 
                    onUpdate={(updatedUser) => {
                      setUserData({ ...userData, ...updatedUser });
                    }}
                  />
                </CardContent>
              </Card>

              {/* Upload Documents */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Upload className="h-5 w-5" />
                    Subir Documentos
                  </CardTitle>
                  <p className="text-sm text-gray-500 mt-1">
                    Comparte documentos médicos, análisis, fotos de progreso, etc.
                  </p>
                </CardHeader>
                <CardContent>
                  <UploadDocumentForm 
                    userId={userData.id}
                    onUploadSuccess={() => {
                      loadDashboardData();
                      alert('Documento subido exitosamente. El admin lo verá en su panel.');
                    }}
                  />
                </CardContent>
              </Card>
            </div>

            {/* My Uploaded Documents */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Mis Documentos Subidos
                </CardTitle>
              </CardHeader>
              <CardContent>
                {pdfs && pdfs.filter(pdf => pdf.uploaded_by === 'user').length > 0 ? (
                  <div className="grid md:grid-cols-3 gap-3">
                    {pdfs.filter(pdf => pdf.uploaded_by === 'user').map((pdf) => (
                      <div key={pdf.id} className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <p className="font-medium text-sm">{pdf.title}</p>
                        </div>
                        <p className="text-xs text-gray-600 mb-2">
                          Subido: {new Date(pdf.upload_date).toLocaleDateString('es-ES')}
                        </p>
                        <Button
                          size="sm"
                          variant="outline"
                          className="w-full border-red-200 text-red-600 hover:bg-red-50"
                          onClick={async () => {
                            if (!window.confirm('¿Eliminar este documento?')) return;
                            try {
                              await axios.delete(`${BACKEND_URL}/api/pdfs/${pdf.id}`, {
                                headers: { Authorization: `Bearer ${token}` },
                                withCredentials: true
                              });
                              alert('Documento eliminado');
                              loadDashboardData();
                            } catch (error) {
                              alert('Error al eliminar: ' + (error.response?.data?.detail || 'Error'));
                            }
                          }}
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Eliminar
                        </Button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">No has subido documentos aún</p>
                )}
              </CardContent>
            </Card>

            {/* Documents Received from Admin */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Download className="h-5 w-5 text-green-600" />
                  Documentos Recibidos del Entrenador
                </CardTitle>
              </CardHeader>
              <CardContent>
                {pdfs && pdfs.filter(pdf => pdf.uploaded_by === 'admin').length > 0 ? (
                  <div className="grid md:grid-cols-3 gap-3">
                    {pdfs.filter(pdf => pdf.uploaded_by === 'admin').map((pdf) => (
                      <div key={pdf.id} className="p-3 bg-green-50 border border-green-200 rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <p className="font-medium text-sm">{pdf.title}</p>
                          <Badge className={pdf.type === 'training' ? 'bg-blue-100 text-blue-700' : 'bg-orange-100 text-orange-700'}>
                            {pdf.type === 'training' ? 'Entrenamiento' : 'Nutrición'}
                          </Badge>
                        </div>
                        <p className="text-xs text-gray-600 mb-2">
                          Recibido: {new Date(pdf.upload_date).toLocaleDateString('es-ES')}
                        </p>
                        <Button
                          size="sm"
                          variant="outline"
                          className="w-full"
                          onClick={() => handleDownloadPDF(pdf.id, pdf.title)}
                        >
                          <Download className="h-4 w-4 mr-2" />
                          Descargar
                        </Button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">No has recibido documentos aún</p>
                )}
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
      {/* Nutrition Questionnaire Modal */}
      {showNutritionQuestionnaire && (
        <div className="fixed inset-0 bg-black/50 z-50 overflow-y-auto">
          <div className="min-h-screen p-4">
            <div className="bg-white rounded-lg max-w-5xl mx-auto my-8">
              <div className="p-4 border-b flex items-center justify-between sticky top-0 bg-white z-10">
                <h3 className="text-xl font-bold">Cuestionario de Nutrición</h3>
                <Button 
                  size="sm" 
                  variant="ghost" 
                  onClick={() => setShowNutritionQuestionnaire(false)}
                >
                  Cerrar
                </Button>
              </div>
              <NutritionQuestionnaire 
                user={userData}
                onComplete={(result) => {
                  setShowNutritionQuestionnaire(false);
                  // Reload user data to show updated nutrition status
                  fetchUserData();
                }}
              />
            </div>
          </div>
        </div>
      )}

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