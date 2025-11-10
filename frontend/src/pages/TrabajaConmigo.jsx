import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, ChevronLeft, Loader2 } from 'lucide-react';
import axios from 'axios';

const TrabajaConmigo = () => {
  const navigate = useNavigate();
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
  
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});
  
  // Estado del formulario
  const [formData, setFormData] = useState({
    // 1. Datos básicos
    nombre_apellidos: '',
    email: '',
    telefono: '',
    edad: '',
    ciudad_pais: '',
    como_conociste: '',
    
    // 2. Capacidad económica
    inversion_mensual: '',
    invierte_actualmente: '',
    frase_representa: '',
    
    // 3. Objetivos y motivación
    objetivo_principal: '',
    por_que_ahora: '',
    intentado_antes: '',
    como_verte_3_meses: '',
    
    // 4. Experiencia y hábitos
    entrenas_actualmente: '',
    dias_semana_entrenar: '',
    nivel_experiencia: '',
    limitaciones_fisicas: '',
    
    // 5. Disponibilidad y compromiso
    tiempo_semanal: '',
    nivel_compromiso: '',
    que_pasaria_sin_cambiar: '',
    
    // 6. Personalidad y afinidad
    preferencia_comunicacion: '',
    que_motiva_mas: '',
    esperas_del_coach: '',
    
    // 7. Disponibilidad entrevista
    disponibilidad_llamada: ''
  });
  
  // Cargar datos guardados del localStorage
  useEffect(() => {
    const saved = localStorage.getItem('waitlist_form_draft');
    if (saved) {
      setFormData(JSON.parse(saved));
    }
  }, []);
  
  // Guardar en localStorage cada vez que cambia
  useEffect(() => {
    localStorage.setItem('waitlist_form_draft', JSON.stringify(formData));
  }, [formData]);
  
  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Limpiar error del campo
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };
  
  const validateStep = (step) => {
    const newErrors = {};
    
    switch(step) {
      case 1:
        if (!formData.nombre_apellidos) newErrors.nombre_apellidos = 'Campo requerido';
        if (!formData.email) newErrors.email = 'Campo requerido';
        if (!formData.telefono) newErrors.telefono = 'Campo requerido';
        if (!formData.edad) newErrors.edad = 'Campo requerido';
        if (!formData.ciudad_pais) newErrors.ciudad_pais = 'Campo requerido';
        if (!formData.como_conociste) newErrors.como_conociste = 'Campo requerido';
        break;
      case 2:
        if (!formData.inversion_mensual) newErrors.inversion_mensual = 'Selecciona una opción';
        if (!formData.invierte_actualmente) newErrors.invierte_actualmente = 'Selecciona una opción';
        if (!formData.frase_representa) newErrors.frase_representa = 'Selecciona una opción';
        break;
      case 3:
        if (!formData.objetivo_principal) newErrors.objetivo_principal = 'Selecciona una opción';
        if (!formData.por_que_ahora) newErrors.por_que_ahora = 'Selecciona una opción';
        if (!formData.intentado_antes) newErrors.intentado_antes = 'Selecciona una opción';
        if (!formData.como_verte_3_meses || formData.como_verte_3_meses.length < 20) {
          newErrors.como_verte_3_meses = 'Describe tu visión (mínimo 20 caracteres)';
        }
        break;
      case 4:
        if (!formData.entrenas_actualmente) newErrors.entrenas_actualmente = 'Selecciona una opción';
        if (!formData.dias_semana_entrenar) newErrors.dias_semana_entrenar = 'Selecciona una opción';
        if (!formData.nivel_experiencia) newErrors.nivel_experiencia = 'Selecciona una opción';
        break;
      case 5:
        if (!formData.tiempo_semanal) newErrors.tiempo_semanal = 'Selecciona una opción';
        if (!formData.nivel_compromiso) newErrors.nivel_compromiso = 'Selecciona una opción';
        if (!formData.que_pasaria_sin_cambiar) newErrors.que_pasaria_sin_cambiar = 'Selecciona una opción';
        break;
      case 6:
        if (!formData.preferencia_comunicacion) newErrors.preferencia_comunicacion = 'Selecciona una opción';
        if (!formData.que_motiva_mas) newErrors.que_motiva_mas = 'Selecciona una opción';
        if (!formData.esperas_del_coach) newErrors.esperas_del_coach = 'Selecciona una opción';
        break;
      case 7:
        if (!formData.disponibilidad_llamada) newErrors.disponibilidad_llamada = 'Selecciona una opción';
        break;
      default:
        break;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const nextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, 7));
      window.scrollTo(0, 0);
    }
  };
  
  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
    window.scrollTo(0, 0);
  };
  
  const handleSubmit = async () => {
    if (!validateStep(7)) return;
    
    setIsSubmitting(true);
    
    try {
      const response = await axios.post(`${BACKEND_URL}/api/waitlist/submit`, formData);
      
      // Guardar resultado para la página de confirmación
      localStorage.setItem('waitlist_result', JSON.stringify({
        score: response.data.score,
        prioridad: response.data.prioridad,
        nombre: formData.nombre_apellidos
      }));
      
      // Limpiar borrador
      localStorage.removeItem('waitlist_form_draft');
      
      // Redirigir a página de confirmación
      navigate('/waitlist-confirmacion');
      
    } catch (error) {
      console.error('Error submitting form:', error);
      alert('Error al enviar el formulario. Por favor, intenta de nuevo.');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const renderStep = () => {
    switch(currentStep) {
      case 1:
        return <Step1 formData={formData} handleChange={handleChange} errors={errors} />;
      case 2:
        return <Step2 formData={formData} handleChange={handleChange} errors={errors} />;
      case 3:
        return <Step3 formData={formData} handleChange={handleChange} errors={errors} />;
      case 4:
        return <Step4 formData={formData} handleChange={handleChange} errors={errors} />;
      case 5:
        return <Step5 formData={formData} handleChange={handleChange} errors={errors} />;
      case 6:
        return <Step6 formData={formData} handleChange={handleChange} errors={errors} />;
      case 7:
        return <Step7 formData={formData} handleChange={handleChange} errors={errors} />;
      default:
        return null;
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Lista Prioritaria - Trabaja con Jorge
          </h1>
          <p className="text-xl text-gray-700 font-semibold mb-4">
            Tu acceso a un programa personal y exigente
          </p>
        </div>

        {/* Texto Introductorio */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <div className="prose prose-lg max-w-none">
            <p className="text-gray-700 mb-4">
              Este breve cuestionario (3–4 minutos) <strong>no es una prueba ni una entrevista</strong>: es una forma de saber si este programa encaja contigo y si realmente estás preparado para comprometerte con tu proceso.
            </p>
            
            <p className="text-gray-700 mb-4">
              <strong>No se trata de si puedes o no pagarlo.</strong><br />
              Se trata de si estás dispuesto a invertir en ti mismo, en tu salud, en tu físico y en el tipo de vida que quieres construir.
            </p>
            
            <p className="text-gray-700 mb-4">
              Este programa no es barato, y no pretende serlo. Es un acompañamiento cercano, exigente y profundamente personalizado.<br />
              Por eso selecciono personalmente a cada persona antes de abrir plaza: porque <strong>no busco cantidad, busco compromiso real</strong>.
            </p>
            
            <p className="text-gray-700 mb-6">
              Si respondes con sinceridad, podré valorar si formas parte del grupo reducido que recibe acceso prioritario a la próxima tanda.
            </p>

            <div className="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-500">
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-center">
                  <span className="mr-2">✅</span>
                  Dura menos de 5 minutos
                </li>
                <li className="flex items-center">
                  <span className="mr-2">✅</span>
                  No compromete a nada
                </li>
                <li className="flex items-center">
                  <span className="mr-2">✅</span>
                  Pero puede ser el inicio de un cambio real
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">
              Paso {currentStep} de 7
            </span>
            <span className="text-sm font-medium text-blue-600">
              {Math.round((currentStep / 7) * 100)}% completado
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-blue-600 to-cyan-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / 7) * 100}%` }}
            />
          </div>
        </div>
        
        {/* Form Card */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
          {renderStep()}
        </div>
        
        {/* Navigation Buttons */}
        <div className="flex justify-between">
          <button
            onClick={prevStep}
            disabled={currentStep === 1}
            className={`flex items-center px-6 py-3 rounded-lg font-medium transition-colors ${
              currentStep === 1
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-gray-600 text-white hover:bg-gray-700'
            }`}
          >
            <ChevronLeft className="w-5 h-5 mr-2" />
            Anterior
          </button>
          
          {currentStep < 7 ? (
            <button
              onClick={nextStep}
              className="flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-cyan-700 transition-colors"
            >
              Siguiente
              <ChevronRight className="w-5 h-5 ml-2" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="flex items-center px-8 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg font-medium hover:from-green-700 hover:to-emerald-700 transition-colors disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Enviando...
                </>
              ) : (
                'Enviar Solicitud'
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

// ==================== STEP COMPONENTS ====================

const Step1 = ({ formData, handleChange, errors }) => (
  <div className="space-y-6">
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">🧠 Datos Básicos</h2>
      <p className="text-gray-600">Comencemos con tu información de contacto</p>
    </div>
    
    <InputField
      label="Nombre y apellidos"
      value={formData.nombre_apellidos}
      onChange={(e) => handleChange('nombre_apellidos', e.target.value)}
      error={errors.nombre_apellidos}
      required
    />
    
    <InputField
      label="Correo electrónico"
      type="email"
      value={formData.email}
      onChange={(e) => handleChange('email', e.target.value)}
      error={errors.email}
      required
    />
    
    <InputField
      label="Teléfono"
      type="tel"
      value={formData.telefono}
      onChange={(e) => handleChange('telefono', e.target.value)}
      error={errors.telefono}
      required
    />
    
    <InputField
      label="Edad"
      type="number"
      value={formData.edad}
      onChange={(e) => handleChange('edad', e.target.value)}
      error={errors.edad}
      required
    />
    
    <InputField
      label="Ciudad o país"
      value={formData.ciudad_pais}
      onChange={(e) => handleChange('ciudad_pais', e.target.value)}
      error={errors.ciudad_pais}
      required
    />
    
    <SelectField
      label="¿Cómo conociste a Jorge?"
      value={formData.como_conociste}
      onChange={(e) => handleChange('como_conociste', e.target.value)}
      error={errors.como_conociste}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: 'Instagram', label: 'Instagram' },
        { value: 'YouTube', label: 'YouTube' },
        { value: 'Recomendación', label: 'Recomendación de alguien' },
        { value: 'Google', label: 'Búsqueda en Google' },
        { value: 'Otro', label: 'Otro' }
      ]}
      required
    />
  </div>
);

const Step2 = ({ formData, handleChange, errors }) => (
  <div className="space-y-6">
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">💰 Capacidad Económica y Prioridades</h2>
      <p className="text-gray-600">Esto nos ayuda a entender tu compromiso</p>
    </div>
    
    <SelectField
      label="¿Qué nivel de inversión mensual estarías dispuesto a hacer?"
      value={formData.inversion_mensual}
      onChange={(e) => handleChange('inversion_mensual', e.target.value)}
      error={errors.inversion_mensual}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: '< 50€/mes', label: '< 50€/mes' },
        { value: '100-200€/mes', label: '100-200€/mes' },
        { value: '200-500€/mes', label: '200-500€/mes' },
        { value: '500+€/mes', label: '500+€/mes' }
      ]}
      required
    />
    
    <SelectField
      label="¿En qué inviertes actualmente para mejorar tu físico o salud?"
      value={formData.invierte_actualmente}
      onChange={(e) => handleChange('invierte_actualmente', e.target.value)}
      error={errors.invierte_actualmente}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: 'No invierto en nada', label: 'No invierto en nada' },
        { value: 'Gimnasio o suplementos', label: 'Gimnasio o suplementos' },
        { value: 'Comidas, entrenadores, y hábitos', label: 'Comidas, entrenadores, y hábitos' },
        { value: 'Ya invierto activamente en mi bienestar', label: 'Ya invierto activamente en mi bienestar' }
      ]}
      required
    />
    
    <SelectField
      label="¿Cuál de estas frases te representa mejor?"
      value={formData.frase_representa}
      onChange={(e) => handleChange('frase_representa', e.target.value)}
      error={errors.frase_representa}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: 'Busco algo económico', label: 'Busco algo económico' },
        { value: 'Busco resultados reales, aunque cueste más', label: 'Busco resultados reales, aunque cueste más' },
        { value: 'Estoy dispuesto a invertir si veo compromiso y resultados medibles', label: 'Estoy dispuesto a invertir si veo compromiso y resultados medibles' }
      ]}
      required
    />
  </div>
);

const Step3 = ({ formData, handleChange, errors }) => (
  <div className="space-y-6">
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">🔥 Objetivos y Motivación</h2>
      <p className="text-gray-600">¿Qué te impulsa a buscar este cambio?</p>
    </div>
    
    <SelectField
      label="¿Cuál es tu objetivo principal ahora mismo?"
      value={formData.objetivo_principal}
      onChange={(e) => handleChange('objetivo_principal', e.target.value)}
      error={errors.objetivo_principal}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: 'Perder grasa', label: 'Perder grasa' },
        { value: 'Ganar músculo', label: 'Ganar músculo' },
        { value: 'Cambiar hábitos', label: 'Cambiar hábitos' },
        { value: 'Prepararme para algo concreto', label: 'Prepararme para algo concreto (competición, evento...)' },
        { value: 'No lo tengo claro', label: 'No lo tengo claro' }
      ]}
      required
    />
    
    <SelectField
      label="¿Por qué quieres hacerlo AHORA y no antes?"
      value={formData.por_que_ahora}
      onChange={(e) => handleChange('por_que_ahora', e.target.value)}
      error={errors.por_que_ahora}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: 'Porque tengo una razón clara o fecha límite', label: 'Porque tengo una razón clara o fecha límite' },
        { value: 'Porque estoy cansado/a de posponerlo', label: 'Porque estoy cansado/a de posponerlo' },
        { value: 'Porque quiero mejorar mi salud', label: 'Porque quiero mejorar mi salud' },
        { value: 'No tengo una razón concreta', label: 'No tengo una razón concreta' }
      ]}
      required
    />
    
    <SelectField
      label="¿Qué has intentado antes y por qué crees que no funcionó?"
      value={formData.intentado_antes}
      onChange={(e) => handleChange('intentado_antes', e.target.value)}
      error={errors.intentado_antes}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: 'No he hecho nada serio antes', label: 'No he hecho nada serio antes' },
        { value: 'Dietas o rutinas por mi cuenta', label: 'Dietas o rutinas por mi cuenta' },
        { value: 'He tenido entrenador, pero no era lo que buscaba', label: 'He tenido entrenador, pero no era lo que buscaba' },
        { value: 'He invertido antes, pero busco un método más profesional', label: 'He invertido antes, pero busco un método más profesional' }
      ]}
      required
    />
    
    <TextAreaField
      label="¿Cómo te gustaría verte o sentirte dentro de 3 meses?"
      value={formData.como_verte_3_meses}
      onChange={(e) => handleChange('como_verte_3_meses', e.target.value)}
      error={errors.como_verte_3_meses}
      placeholder="Describe con detalle cómo te imaginas dentro de 3 meses..."
      rows={4}
      required
    />
  </div>
);

const Step4 = ({ formData, handleChange, errors }) => (
  <div className="space-y-6">
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">⚙️ Experiencia y Hábitos Actuales</h2>
      <p className="text-gray-600">Entendamos tu punto de partida</p>
    </div>
    
    <SelectField
      label="¿Entrenas actualmente?"
      value={formData.entrenas_actualmente}
      onChange={(e) => handleChange('entrenas_actualmente', e.target.value)}
      error={errors.entrenas_actualmente}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: 'Sí, con entrenador', label: 'Sí, con entrenador' },
        { value: 'Sí, por mi cuenta', label: 'Sí, por mi cuenta' },
        { value: 'Lo he dejado, pero quiero retomarlo', label: 'Lo he dejado, pero quiero retomarlo' },
        { value: 'No entreno actualmente', label: 'No entreno actualmente' }
      ]}
      required
    />
    
    <SelectField
      label="¿Cuántos días a la semana puedes comprometerte a entrenar?"
      value={formData.dias_semana_entrenar}
      onChange={(e) => handleChange('dias_semana_entrenar', e.target.value)}
      error={errors.dias_semana_entrenar}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: '1-2 días', label: '1-2 días' },
        { value: '3-4 días', label: '3-4 días' },
        { value: '5 o más días', label: '5 o más días' }
      ]}
      required
    />
    
    <SelectField
      label="¿Qué nivel de experiencia tienes en nutrición o entrenamiento?"
      value={formData.nivel_experiencia}
      onChange={(e) => handleChange('nivel_experiencia', e.target.value)}
      error={errors.nivel_experiencia}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: 'Principiante', label: 'Principiante' },
        { value: 'Intermedio', label: 'Intermedio' },
        { value: 'Avanzado', label: 'Avanzado' }
      ]}
      required
    />
    
    <TextAreaField
      label="¿Tienes alguna limitación física o médica que deba conocer? (Opcional)"
      value={formData.limitaciones_fisicas}
      onChange={(e) => handleChange('limitaciones_fisicas', e.target.value)}
      placeholder="Lesiones, condiciones médicas, etc."
      rows={3}
    />
  </div>
);

const Step5 = ({ formData, handleChange, errors }) => (
  <div className="space-y-6">
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">🧩 Disponibilidad y Compromiso</h2>
      <p className="text-gray-600">¿Cuánto estás dispuesto a invertir en ti mismo?</p>
    </div>
    
    <SelectField
      label="¿Cuánto tiempo estás dispuesto a dedicar semanalmente al proceso?"
      value={formData.tiempo_semanal}
      onChange={(e) => handleChange('tiempo_semanal', e.target.value)}
      error={errors.tiempo_semanal}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: 'Menos de 2h', label: 'Menos de 2h' },
        { value: '3-4h', label: '3-4h' },
        { value: '5-6h', label: '5-6h' },
        { value: 'Más de 6h', label: 'Más de 6h' }
      ]}
      required
    />
    
    <SelectField
      label="En una escala del 1 al 10, ¿cuánto te comprometerías con el proceso?"
      value={formData.nivel_compromiso}
      onChange={(e) => handleChange('nivel_compromiso', e.target.value)}
      error={errors.nivel_compromiso}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: '1-4', label: '1-4 (Compromiso bajo)' },
        { value: '5-6', label: '5-6 (Compromiso medio)' },
        { value: '7-8', label: '7-8 (Compromiso alto)' },
        { value: '9-10', label: '9-10 (Compromiso total)' }
      ]}
      required
    />
    
    <SelectField
      label="¿Qué pasaría si no cambias nada durante los próximos 3 meses?"
      value={formData.que_pasaria_sin_cambiar}
      onChange={(e) => handleChange('que_pasaria_sin_cambiar', e.target.value)}
      error={errors.que_pasaria_sin_cambiar}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: 'No pasaría nada grave', label: 'No pasaría nada grave' },
        { value: 'Me frustraría seguir igual', label: 'Me frustraría seguir igual' },
        { value: 'Sé que empeoraría', label: 'Sé que empeoraría' },
        { value: 'No quiero ni imaginarlo', label: 'No quiero ni imaginarlo' }
      ]}
      required
    />
  </div>
);

const Step6 = ({ formData, handleChange, errors }) => (
  <div className="space-y-6">
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">🎯 Personalidad y Afinidad</h2>
      <p className="text-gray-600">¿Encajamos en estilo de trabajo?</p>
    </div>
    
    <SelectField
      label="¿Prefieres una comunicación directa y exigente, o más progresiva y flexible?"
      value={formData.preferencia_comunicacion}
      onChange={(e) => handleChange('preferencia_comunicacion', e.target.value)}
      error={errors.preferencia_comunicacion}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: 'Directa y exigente', label: 'Directa y exigente' },
        { value: 'Un punto intermedio', label: 'Un punto intermedio' },
        { value: 'Más progresiva y flexible', label: 'Más progresiva y flexible' }
      ]}
      required
    />
    
    <SelectField
      label="¿Qué te motiva más?"
      value={formData.que_motiva_mas}
      onChange={(e) => handleChange('que_motiva_mas', e.target.value)}
      error={errors.que_motiva_mas}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: 'Resultados visibles y medibles', label: 'Resultados visibles y medibles' },
        { value: 'Sentirme mejor física y mentalmente', label: 'Sentirme mejor física y mentalmente' },
        { value: 'No lo tengo claro', label: 'No lo tengo claro' }
      ]}
      required
    />
    
    <SelectField
      label="¿Qué esperas de mí como coach si trabajamos juntos?"
      value={formData.esperas_del_coach}
      onChange={(e) => handleChange('esperas_del_coach', e.target.value)}
      error={errors.esperas_del_coach}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: 'Que me exijas y me lleves al límite', label: 'Que me exijas y me lleves al límite' },
        { value: 'Que me acompañes con estructura y motivación', label: 'Que me acompañes con estructura y motivación' },
        { value: 'Que me apoyes sin exigirme demasiado', label: 'Que me apoyes sin exigirme demasiado' }
      ]}
      required
    />
  </div>
);

const Step7 = ({ formData, handleChange, errors }) => (
  <div className="space-y-6">
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">📞 Disponibilidad para Entrevista</h2>
      <p className="text-gray-600">Último paso - ¡casi listo!</p>
    </div>
    
    <SelectField
      label="Si quedaras seleccionado, ¿podrías tener una breve videollamada de 15 min esta semana?"
      value={formData.disponibilidad_llamada}
      onChange={(e) => handleChange('disponibilidad_llamada', e.target.value)}
      error={errors.disponibilidad_llamada}
      options={[
        { value: '', label: 'Selecciona una opción' },
        { value: 'Sí, puedo adaptarme', label: 'Sí, puedo adaptarme' },
        { value: 'Prefiero que me contactes por WhatsApp', label: 'Prefiero que me contactes por WhatsApp' },
        { value: 'No lo sé', label: 'No lo sé' }
      ]}
      required
    />
    
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-6">
      <h3 className="font-bold text-blue-900 mb-2">📝 Resumen</h3>
      <p className="text-blue-800 text-sm">
        Has completado todos los pasos. Al enviar, revisaré tu candidatura personalmente 
        y te contactaré si encajas con el programa. ¡Gracias por tu interés!
      </p>
    </div>
  </div>
);

// ==================== HELPER COMPONENTS ====================

const InputField = ({ label, type = 'text', value, onChange, error, required, ...props }) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-2">
      {label} {required && <span className="text-red-500">*</span>}
    </label>
    <input
      type={type}
      value={value}
      onChange={onChange}
      className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
        error ? 'border-red-500' : 'border-gray-300'
      }`}
      {...props}
    />
    {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
  </div>
);

const SelectField = ({ label, value, onChange, options, error, required }) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-2">
      {label} {required && <span className="text-red-500">*</span>}
    </label>
    <select
      value={value}
      onChange={onChange}
      className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
        error ? 'border-red-500' : 'border-gray-300'
      }`}
    >
      {options.map((option, index) => (
        <option key={index} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
    {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
  </div>
);

const TextAreaField = ({ label, value, onChange, error, required, ...props }) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-2">
      {label} {required && <span className="text-red-500">*</span>}
    </label>
    <textarea
      value={value}
      onChange={onChange}
      className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
        error ? 'border-red-500' : 'border-gray-300'
      }`}
      {...props}
    />
    {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
  </div>
);

export default TrabajaConmigo;
