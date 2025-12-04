import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent } from '../components/ui/dialog';
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
  UtensilsCrossed,
  RefreshCw,
  Dumbbell,
  Mail,
  FileDown,
  ChevronDown,
  ChevronUp,
  X
} from 'lucide-react';
import ChatBox from '../components/ChatBox';
import { UserCalendar } from '../components/Calendar';
import { EditProfileForm, UploadDocumentForm } from '../components/ProfileComponents';
import NutritionQuestionnaire from '../components/NutritionQuestionnaire';
import FollowUpQuestionnaire from '../components/FollowUpQuestionnaire';

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
  const [showFollowUpQuestionnaire, setShowFollowUpQuestionnaire] = useState(false);
  const [daysSinceLastPlan, setDaysSinceLastPlan] = useState(0);
  const [documentFilter, setDocumentFilter] = useState('all'); // all, nutrition, training
  const [loading, setLoading] = useState(true);
  const [trainingPlan, setTrainingPlan] = useState(null);
  const [loadingTrainingPlan, setLoadingTrainingPlan] = useState(false);
  const [expandedSessions, setExpandedSessions] = useState({});
  const [videoModalOpen, setVideoModalOpen] = useState(false);
  const [currentVideoUrl, setCurrentVideoUrl] = useState(null);
  const [planCollapsed, setPlanCollapsed] = useState(true);
  
  // Subscription states
  const [subscription, setSubscription] = useState(null);
  const [hasSubscription, setHasSubscription] = useState(false);
  const [payments, setPayments] = useState([]);
  const [loadingSubscription, setLoadingSubscription] = useState(false);

  const loadDashboardData = useCallback(async () => {
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
      
      // Calcular días desde el último plan de nutrición
      if (response.data.user?.nutrition_plan?.generated_at) {
        const planDate = new Date(response.data.user.nutrition_plan.generated_at);
        const now = new Date();
        const diffTime = Math.abs(now - planDate);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        setDaysSinceLastPlan(diffDays);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard:', error);
      setLoading(false);
    }
  }, [token]);

  const loadTrainingPlan = useCallback(async () => {
    try {
      setLoadingTrainingPlan(true);
      const response = await axios.get(`${API}/users/${user.id}/training-plans/latest`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setTrainingPlan(response.data);
    } catch (error) {
      if (error.response?.status !== 404) {
        console.error('Error loading training plan:', error);
      }
      setTrainingPlan(null);
    } finally {
      setLoadingTrainingPlan(false);
    }
  }, [user?.id, token]);

  const handleSendTrainingPlanEmail = useCallback(async () => {
    try {
      await axios.post(
        `${API}/users/${user.id}/training-plans/send-to-me`,
        {},
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      alert('✅ Plan enviado a tu email correctamente');
    } catch (error) {
      console.error('Error sending training plan email:', error);
      alert('❌ Error enviando el email. Inténtalo de nuevo.');
    }
  }, [user?.id, token]);

  const handleDownloadTrainingPlanPDF = useCallback(async () => {
    try {
      const response = await axios.get(
        `${API}/users/${user.id}/training-plans/download-pdf`,
        { 
          headers: { 'Authorization': `Bearer ${token}` },
          responseType: 'blob'
        }
      );
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Plan_Entrenamiento_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('❌ Error descargando el PDF. Inténtalo de nuevo.');
    }
  }, [user?.id, token]);

  const handleOpenVideoModal = useCallback((videoUrl) => {
    setCurrentVideoUrl(videoUrl);
    setVideoModalOpen(true);
  }, []);

  const handleCloseVideoModal = useCallback(() => {
    setVideoModalOpen(false);
    setCurrentVideoUrl(null);
  }, []);

  const toggleSessionExpand = useCallback((sessionIdx) => {
    setExpandedSessions(prev => ({
      ...prev,
      [sessionIdx]: !prev[sessionIdx]
    }));
  }, []);

  useEffect(() => {
    loadDashboardData();
    loadTrainingPlan();
    
    // Auto-reload data every 30 seconds to catch updates from admin
    const interval = setInterval(() => {
      loadDashboardData();
      loadTrainingPlan();
    }, 30000); // 30 seconds
    
    return () => clearInterval(interval);
  }, [loadDashboardData, loadTrainingPlan]);


  const markAlertAsRead = useCallback(async (alertId) => {
    try {
      await axios.patch(`${API}/alerts/${alertId}/read`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        withCredentials: true
      });
      
      // Update local state
      setAlerts(prevAlerts => prevAlerts.map(alert => 
        alert.id === alertId ? { ...alert, read: true } : alert
      ));
      
      // Update unread count
      setUnreadAlerts(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking alert as read:', error);
    }
  }, [token]);

  const handleDownloadPDF = useCallback(async (pdfId, pdfTitle) => {
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
  }, [token]);

  const handleLogout = useCallback(() => {
    logout();
    navigate('/');
  }, [logout, navigate]);

  const loadSubscriptionData = useCallback(async () => {
    try {
      setLoadingSubscription(true);
      
      // Cargar suscripción
      const subResponse = await axios.get(`${API}/stripe/my-subscription`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      setHasSubscription(subResponse.data.has_subscription);
      setSubscription(subResponse.data.subscription);
      
      // Cargar historial de pagos
      const paymentsResponse = await axios.get(`${API}/stripe/my-payments`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      setPayments(paymentsResponse.data.payments || []);
      
      setLoadingSubscription(false);
    } catch (error) {
      console.error('Error loading subscription data:', error);
      setLoadingSubscription(false);
    }
  }, [token]);

  const handleActivateSubscription = useCallback(async () => {
    try {
      setLoadingSubscription(true);
      
      // Obtener origin para construir URLs dinámicamente
      const origin = window.location.origin;
      
      const response = await axios.post(
        `${API}/stripe/create-subscription-session`,
        { plan_type: "monthly" },
        {
          headers: { 
            'Authorization': `Bearer ${token}`,
            'origin': origin
          }
        }
      );
      
      // Redirigir a Stripe Checkout
      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
      
    } catch (error) {
      console.error('Error activating subscription:', error);
      alert('Error al activar suscripción. Por favor, inténtalo de nuevo.');
      setLoadingSubscription(false);
    }
  }, [token]);

  const handleCancelSubscription = useCallback(async () => {
    if (!window.confirm('¿Estás seguro de que deseas cancelar tu suscripción?')) {
      return;
    }
    
    try {
      setLoadingSubscription(true);
      
      await axios.post(
        `${API}/stripe/cancel-subscription`,
        {},
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      
      alert('Suscripción cancelada exitosamente');
      loadSubscriptionData(); // Recargar datos
      
    } catch (error) {
      console.error('Error cancelling subscription:', error);
      alert('Error al cancelar suscripción. Por favor, inténtalo de nuevo.');
      setLoadingSubscription(false);
    }
  }, [token, loadSubscriptionData]);

  const handlePayment = useCallback(async () => {
    // Usar el nuevo sistema de Stripe integrado
    await handleActivateSubscription();
  }, [handleActivateSubscription]);

  const formatDate = useCallback((dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }, []);

  const formatAmount = useCallback((amount, currency = 'EUR') => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: currency.toUpperCase()
    }).format(amount);
  }, []);

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
                onClick={() => {
                  loadDashboardData();
                }}
                className="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm px-2 sm:px-4"
                title="Actualizar datos"
              >
                <RefreshCw className="h-3 w-3 sm:h-4 sm:w-4" />
                <span className="hidden sm:inline">Actualizar</span>
              </Button>
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
        <Tabs defaultValue="overview" className="space-y-4 md:space-y-6" onValueChange={(value) => { if (value === 'subscription') loadSubscriptionData(); }}>
          <TabsList className="grid grid-cols-3 sm:grid-cols-8 w-full gap-1 h-auto p-1">
            <TabsTrigger value="overview" className="text-xs sm:text-sm py-2">
              Resumen
            </TabsTrigger>
            <TabsTrigger value="training" className="text-xs sm:text-sm py-2">
              <UtensilsCrossed className="h-3 w-3 sm:h-4 sm:w-4 sm:mr-2" />
              <span className="hidden sm:inline">Mi Entrenamiento</span>
              <span className="sm:hidden">Entre</span>
            </TabsTrigger>
            <TabsTrigger value="subscription" className="text-xs sm:text-sm py-2">
              <CreditCard className="h-3 w-3 sm:h-4 sm:w-4 sm:mr-2" />
              <span className="hidden sm:inline">Suscripción</span>
              <span className="sm:hidden">Sub</span>
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


              {/* Nutrition Questionnaire Button - Only for team plan + verified payment + no submission yet */}
              {userData.subscription?.plan === 'team' && 
               userData.subscription?.payment_status === 'verified' && 
               !userData.nutrition_plan && 
               !forms.some(f => f.type === 'nutrition') && (
                <Card className="md:col-span-2 border-4 border-green-500 bg-gradient-to-r from-green-50 to-emerald-50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-2xl text-green-800">
                      <UtensilsCrossed className="h-8 w-8 text-green-600" />
                      ¡Cuéntanos sobre ti!
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700 mb-6">
                      Completa el cuestionario para que Jorge y su equipo puedan conocerte mejor y diseñar 
                      un plan de nutrición 100% personalizado para ti.
                    </p>
                    <Button
                      onClick={() => setShowNutritionQuestionnaire(true)}
                      className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white text-lg py-6"
                    >
                      <UtensilsCrossed className="mr-3 h-6 w-6" />
                      Comenzar Cuestionario
                    </Button>
                  </CardContent>
                </Card>
              )}

              {/* Show nutrition status if plan exists AND no documents yet */}
              {userData.subscription?.plan === 'team' && 
               userData.subscription?.payment_status === 'verified' && 
               userData.nutrition_plan && 
               pdfs.length === 0 && (
                <Card className="md:col-span-2 border-2 border-blue-200 bg-blue-50">
                  <CardContent className="pt-6">
                    <p className="text-gray-700 text-center text-lg">
                      ✅ El equipo de Jorge está revisando tu cuestionario. Tu plan estará listo en un plazo de 24 horas.
                    </p>
                  </CardContent>
                </Card>
              )}

              {/* Monthly Follow-Up Questionnaire - Show if activated by admin */}
              {userData.subscription?.plan === 'team' && 
               userData.subscription?.payment_status === 'verified' && 
               userData.followup_activated && (
                <Card className="md:col-span-2 border-4 border-purple-500 bg-gradient-to-r from-purple-50 to-pink-50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-2xl text-purple-800">
                      📊 ¡Es hora de tu seguimiento mensual!
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700 mb-4">
                      <strong>Tu entrenador ha solicitado que completes este cuestionario de seguimiento.</strong>
                      <br />
                      Por favor, responde para que pueda evaluar tu progreso y ajustar tus planes según sea necesario.
                    </p>
                    <Button
                      onClick={() => setShowFollowUpQuestionnaire(true)}
                      className="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white text-lg py-6"
                    >
                      📊 Completar Cuestionario de Seguimiento
                    </Button>
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



          {/* Subscription Tab */}
          <TabsContent value="subscription" className="space-y-6">
            {loadingSubscription ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            ) : (
              <>
                {/* Estado de Suscripción */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <CreditCard className="h-5 w-5" />
                      Estado de tu Suscripción
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {hasSubscription && subscription ? (
                      <>
                        {/* Suscripción Activa */}
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-2">
                              <CheckCircle className="h-5 w-5 text-green-600" />
                              <span className="font-semibold text-green-900">Suscripción Activa</span>
                            </div>
                            <Badge className={subscription.status === 'active' ? 'bg-green-500' : 'bg-gray-500'}>
                              {subscription.status === 'active' ? 'Activa' : subscription.status === 'cancelled' ? 'Cancelada' : 'Pendiente'}
                            </Badge>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <p className="text-sm text-gray-600">Plan</p>
                              <p className="font-medium">Plan Mensual</p>
                            </div>
                            <div>
                              <p className="text-sm text-gray-600">Monto</p>
                              <p className="font-medium">{formatAmount(subscription.amount, subscription.currency)}/mes</p>
                            </div>
                            <div>
                              <p className="text-sm text-gray-600">Fecha de Inicio</p>
                              <p className="font-medium">{formatDate(subscription.start_date)}</p>
                            </div>
                            {subscription.status === 'active' && subscription.next_billing_date && (
                              <div>
                                <p className="text-sm text-gray-600">Próximo Pago</p>
                                <p className="font-medium">{formatDate(subscription.next_billing_date)}</p>
                              </div>
                            )}
                            {subscription.status === 'cancelled' && subscription.cancelled_at && (
                              <div>
                                <p className="text-sm text-gray-600">Cancelada el</p>
                                <p className="font-medium">{formatDate(subscription.cancelled_at)}</p>
                              </div>
                            )}
                          </div>
                          
                          {subscription.status === 'active' && (
                            <div className="mt-4 pt-4 border-t border-green-200">
                              <Button
                                variant="outline"
                                className="w-full border-red-300 text-red-600 hover:bg-red-50"
                                onClick={handleCancelSubscription}
                              >
                                Cancelar Suscripción
                              </Button>
                            </div>
                          )}
                        </div>
                      </>
                    ) : (
                      <>
                        {/* Sin Suscripción */}
                        <div className="text-center py-8">
                          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-2xl p-8 max-w-md mx-auto">
                            <CreditCard className="h-16 w-16 text-blue-600 mx-auto mb-4" />
                            <h3 className="text-2xl font-bold text-gray-900 mb-3">
                              Suscripción Mensual
                            </h3>
                            <div className="mb-6">
                              <span className="text-5xl font-bold text-blue-600">49,9€</span>
                              <span className="text-gray-600 ml-2">/mes</span>
                            </div>
                            <p className="text-gray-600 mb-8">
                              Acceso completo a todos los servicios y funcionalidades del equipo de Jorge Calcerrada.
                            </p>
                            <Button
                              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white py-6 text-lg font-semibold shadow-lg"
                              onClick={handleActivateSubscription}
                              disabled={loadingSubscription}
                            >
                              {loadingSubscription ? 'Procesando...' : '🚀 Activar Suscripción'}
                            </Button>
                          </div>
                        </div>
                      </>
                    )}
                  </CardContent>
                </Card>

                {/* Historial de Pagos */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="h-5 w-5" />
                      Historial de Pagos
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {payments.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <FileText className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                        <p>No hay pagos registrados</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {payments.map((payment) => (
                          <div
                            key={payment.transaction_id}
                            className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                  <Badge className="bg-green-500">
                                    {payment.payment_status === 'succeeded' ? 'Exitoso' : payment.payment_status}
                                  </Badge>
                                  <span className="text-sm text-gray-600">
                                    {formatDate(payment.created_at)}
                                  </span>
                                </div>
                                <div className="flex items-center gap-4">
                                  <span className="font-semibold text-lg">
                                    {formatAmount(payment.amount, payment.currency)}
                                  </span>
                                  <span className="text-sm text-gray-500">
                                    ID: {payment.transaction_id.substring(0, 8)}...
                                  </span>
                                </div>
                              </div>
                              <CheckCircle className="h-5 w-5 text-green-500" />
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </>
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
                    <div className="flex gap-2 mt-4">
                      <Button
                        size="sm"
                        variant={documentFilter === 'all' ? 'default' : 'outline'}
                        onClick={() => setDocumentFilter('all')}
                      >
                        Todos
                      </Button>
                      <Button
                        size="sm"
                        variant={documentFilter === 'nutrition' ? 'default' : 'outline'}
                        onClick={() => setDocumentFilter('nutrition')}
                        className={documentFilter === 'nutrition' ? 'bg-green-600' : ''}
                      >
                        🥗 Nutrición
                      </Button>
                      <Button
                        size="sm"
                        variant={documentFilter === 'training' ? 'default' : 'outline'}
                        onClick={() => setDocumentFilter('training')}
                        className={documentFilter === 'training' ? 'bg-blue-600' : ''}
                      >
                        💪 Entrenamiento
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {pdfs.filter(pdf => documentFilter === 'all' || pdf.type === documentFilter).length > 0 ? (
                      <div className="grid md:grid-cols-2 gap-4">
                        {pdfs.filter(pdf => documentFilter === 'all' || pdf.type === documentFilter).map((pdf) => (
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
                      <p className="text-gray-500 text-center py-8">
                        {documentFilter === 'all' 
                          ? 'No hay documentos disponibles aún' 
                          : `No hay documentos de ${documentFilter === 'nutrition' ? 'nutrición' : 'entrenamiento'} disponibles`}
                      </p>
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


          {/* Training Plan Tab */}
          <TabsContent value="training" className="space-y-4 sm:space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Dumbbell className="h-5 w-5" />
                  Mi Plan de Entrenamiento
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loadingTrainingPlan ? (
                  <div className="text-center py-8">
                    <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
                    <p className="text-gray-600">Cargando tu plan...</p>
                  </div>
                ) : trainingPlan && trainingPlan.status === 'sent' ? (
                  <div className="space-y-6">
                    {/* Plan Info */}
                    <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg p-6 border border-blue-200">
                      <h3 className="text-xl font-bold text-blue-900 mb-2">
                        {trainingPlan.plan.title}
                      </h3>
                      <p className="text-blue-700 mb-4">{trainingPlan.plan.goal}</p>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-gray-600">Días por semana</p>
                          <p className="font-bold text-gray-900">{trainingPlan.plan.days_per_week} días</p>
                        </div>
                        <div>
                          <p className="text-gray-600">Duración sesión</p>
                          <p className="font-bold text-gray-900">{trainingPlan.plan.session_duration_min} min</p>
                        </div>
                        <div>
                          <p className="text-gray-600">Duración programa</p>
                          <p className="font-bold text-gray-900">{trainingPlan.plan.weeks} semanas</p>
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-col sm:flex-row gap-3">
                      <Button
                        onClick={handleSendTrainingPlanEmail}
                        className="flex-1 bg-green-600 hover:bg-green-700"
                      >
                        <Mail className="h-4 w-4 mr-2" />
                        Enviarme por Email
                      </Button>
                      <Button
                        onClick={handleDownloadTrainingPlanPDF}
                        className="flex-1 bg-blue-600 hover:bg-blue-700"
                      >
                        <FileDown className="h-4 w-4 mr-2" />
                        Descargar PDF
                      </Button>
                    </div>

                    {/* Sessions */}
                    <div className="space-y-4">
                      <h4 className="text-lg font-semibold text-gray-900">Sesiones de Entrenamiento</h4>
                      {trainingPlan.plan.sessions.map((session, idx) => (
                        <Card key={idx}>
                          <CardHeader>
                            <CardTitle className="text-base">{session.name}</CardTitle>
                            {session.focus && session.focus.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-2">
                                {session.focus.map((f, i) => (
                                  <Badge key={i} variant="secondary" className="text-xs">
                                    {f}
                                  </Badge>
                                ))}
                              </div>
                            )}
                          </CardHeader>
                          <CardContent className="space-y-4">
                            {/* Session Notes */}
                            {session.session_notes && session.session_notes.length > 0 && (
                              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                                <p className="text-sm font-semibold text-red-800 mb-2">⚠️ Notas Importantes:</p>
                                <ul className="space-y-1">
                                  {session.session_notes.map((note, i) => (
                                    <li key={i} className="text-sm text-red-700 flex items-start gap-2">
                                      <span>•</span>
                                      <span>{note}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Blocks */}
                            {session.blocks.map((block, blockIdx) => (
                              <div key={blockIdx} className="bg-gray-50 rounded-lg p-4">
                                <h5 className="font-semibold text-gray-800 mb-3">
                                  Bloque {block.id} - {block.primary_muscles.join(', ')}
                                </h5>
                                
                                {/* Table Headers */}
                                <div className="grid grid-cols-12 gap-2 items-center bg-gray-200 px-2 py-2 rounded mb-2">
                                  <div className="col-span-1 text-xs font-semibold text-gray-700 text-center">#</div>
                                  <div className="col-span-5 text-xs font-semibold text-gray-700">Ejercicio</div>
                                  <div className="col-span-2 text-xs font-semibold text-gray-700">Series</div>
                                  <div className="col-span-2 text-xs font-semibold text-gray-700">Reps</div>
                                  <div className="col-span-2 text-xs font-semibold text-gray-700">RPE</div>
                                </div>

                                {/* Exercises */}
                                <div className="space-y-2">
                                  {block.exercises.map((exercise, exIdx) => (
                                    <div key={exIdx} className="bg-white rounded border border-gray-200 p-3">
                                      <div className="grid grid-cols-12 gap-2 items-center mb-2">
                                        <div className="col-span-1 text-center text-sm font-bold text-gray-600">
                                          {exercise.order}
                                        </div>
                                        <div className="col-span-5 text-sm font-semibold text-gray-900">
                                          {exercise.name}
                                        </div>
                                        <div className="col-span-2 text-sm text-center text-gray-900">
                                          {exercise.series}
                                        </div>
                                        <div className="col-span-2 text-sm text-center text-gray-900">
                                          {exercise.reps}
                                        </div>
                                        <div className="col-span-2 text-sm text-center text-gray-900">
                                          {exercise.rpe}
                                        </div>
                                      </div>
                                      {exercise.notes && (
                                        <p className="text-xs text-gray-600 mb-2 pl-2">{exercise.notes}</p>
                                      )}
                                      {exercise.video_url && (
                                        <Button
                                          onClick={() => window.open(exercise.video_url, '_blank')}
                                          size="sm"
                                          variant="outline"
                                          className="w-full text-xs border-blue-300 text-blue-700 hover:bg-blue-50"
                                        >
                                          <ExternalLink className="h-3 w-3 mr-1" />
                                          Ver Video del Ejercicio
                                        </Button>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Dumbbell className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                    <p className="text-gray-600 text-lg mb-2">Aún no tienes un plan de entrenamiento</p>
                    <p className="text-gray-500 text-sm">Tu entrenador te enviará un plan personalizado pronto</p>
                  </div>
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
                  // Reload dashboard to show updated nutrition status (hide button)
                  loadDashboardData();
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Modal - Follow-Up Questionnaire */}
      {showFollowUpQuestionnaire && (
        <div className="fixed inset-0 bg-black/50 z-50 overflow-y-auto">
          <div className="min-h-screen p-4">
            <div className="bg-white rounded-lg max-w-5xl mx-auto my-8">
              <div className="p-4 border-b flex items-center justify-between sticky top-0 bg-white z-10">
                <h3 className="text-xl font-bold">Cuestionario de Seguimiento Mensual</h3>
                <Button 
                  size="sm" 
                  variant="ghost" 
                  onClick={() => setShowFollowUpQuestionnaire(false)}
                >
                  Cerrar
                </Button>
              </div>
              <FollowUpQuestionnaire 
                daysSinceLastPlan={daysSinceLastPlan}
                onSubmitSuccess={() => {
                  setShowFollowUpQuestionnaire(false);
                  alert('✅ Tu cuestionario ha sido enviado. Jorge lo revisará y te contactará pronto.');
                  loadDashboardData();
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