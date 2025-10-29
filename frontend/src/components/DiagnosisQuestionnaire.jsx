import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Loader2, CheckCircle, ChevronRight, ChevronLeft } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DiagnosisQuestionnaire = ({ onClose }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    // Datos Personales
    nombre: '',
    edad: '',
    email: '',
    whatsapp: '',
    
    // Contexto Actual
    objetivo: '',
    intentos_previos: '',
    dificultades: [],
    dificultades_otro: '',
    tiempo_semanal: '',
    entrena: '',
    
    // Nutrición
    alimentacion: '',
    salud_info: '',
    
    // Motivación
    por_que_ahora: '',
    dispuesto_invertir: '',
    tipo_acompanamiento: '',
    presupuesto: '',
    comentarios_adicionales: ''
  });

  const totalSteps = 4;

  const handleInputChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleCheckboxChange = (field, value) => {
    const current = formData[field] || [];
    if (current.includes(value)) {
      handleInputChange(field, current.filter(v => v !== value));
    } else {
      handleInputChange(field, [...current, value]);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    
    // Validación adicional antes de enviar
    if (!formData.nombre || !formData.edad || !formData.email || !formData.whatsapp) {
      alert('Por favor completa todos los campos obligatorios de datos personales');
      setLoading(false);
      return;
    }
    
    if (!formData.objetivo || !formData.intentos_previos || !formData.tiempo_semanal || !formData.entrena) {
      alert('Por favor completa todos los campos obligatorios de contexto actual');
      setLoading(false);
      return;
    }
    
    if (!formData.alimentacion || !formData.salud_info) {
      alert('Por favor completa todos los campos obligatorios de nutrición');
      setLoading(false);
      return;
    }
    
    if (!formData.por_que_ahora || !formData.dispuesto_invertir || !formData.tipo_acompanamiento || !formData.presupuesto) {
      alert('Por favor completa todos los campos obligatorios de motivación');
      setLoading(false);
      return;
    }
    
    try {
      // Asegurar que dificultades siempre sea un array
      const dataToSend = {
        ...formData,
        dificultades: Array.isArray(formData.dificultades) ? formData.dificultades : [],
        dificultades_otro: formData.dificultades_otro || '',
        comentarios_adicionales: formData.comentarios_adicionales || ''
      };
      
      console.log('Enviando cuestionario...', dataToSend);
      const response = await axios.post(`${API}/questionnaire/submit`, dataToSend, {
        timeout: 30000, // 30 segundos de timeout
        headers: {
          'Content-Type': 'application/json'
        }
      });
      console.log('Respuesta del servidor:', response.data);
      setSubmitted(true);
    } catch (error) {
      console.error('Error completo:', error);
      
      let errorMessage = 'Error al enviar el cuestionario.';
      
      if (error.response) {
        // El servidor respondió con un código de error
        errorMessage = `Error del servidor: ${error.response.data?.detail || error.response.statusText}`;
        console.error('Error response:', error.response.data);
      } else if (error.request) {
        // La petición se hizo pero no hubo respuesta
        errorMessage = 'No se recibió respuesta del servidor. Verifica tu conexión a internet.';
        console.error('Error request:', error.request);
      } else {
        // Error al configurar la petición
        errorMessage = `Error: ${error.message}`;
        console.error('Error message:', error.message);
      }
      
      alert(errorMessage + '\n\nPor favor, inténtalo de nuevo o contacta con soporte.');
      setLoading(false);
    }
  };

  const canGoNext = () => {
    if (currentStep === 1) {
      return formData.nombre && formData.edad && formData.email && formData.whatsapp;
    }
    if (currentStep === 2) {
      return formData.objetivo && formData.intentos_previos && formData.tiempo_semanal && formData.entrena;
    }
    if (currentStep === 3) {
      return formData.alimentacion && formData.salud_info;
    }
    return true;
  };

  if (submitted) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-20 px-6">
        <div className="bg-green-50 rounded-full p-6 mb-6">
          <CheckCircle className="h-16 w-16 text-green-500" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">¡Gracias por tu tiempo!</h2>
        <p className="text-lg text-gray-600 text-center max-w-md mb-8">
          He recibido tu diagnóstico inicial. Me pondré en contacto contigo pronto para analizar tu caso y ofrecerte la mejor solución.
        </p>
        <Button
          onClick={onClose}
          className="bg-gradient-to-r from-blue-500 to-orange-500 hover:from-blue-600 hover:to-orange-600"
        >
          Cerrar
        </Button>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Progress Bar */}
      <div className="bg-gray-100 h-2 flex-shrink-0">
        <div
          className="bg-gradient-to-r from-blue-500 to-orange-500 h-full transition-all duration-300"
          style={{ width: `${(currentStep / totalSteps) * 100}%` }}
        />
      </div>

      {/* Form Content - Scrollable */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden px-4 md:px-6 py-6">
        {/* STEP 1: Datos Personales */}
        {currentStep === 1 && (
          <div className="space-y-6 animate-fade-in pb-24">
            <div>
              <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-500 to-orange-500 bg-clip-text text-transparent mb-2">
                Datos Personales
              </h2>
              <p className="text-gray-600">Empecemos conociéndonos</p>
            </div>

            <div>
              <Label htmlFor="nombre" className="text-base font-semibold">
                Nombre y apellidos <span className="text-red-500">*</span>
              </Label>
              <Input
                id="nombre"
                value={formData.nombre}
                onChange={(e) => handleInputChange('nombre', e.target.value)}
                placeholder="Ej: Juan García"
                className="mt-2"
                required
              />
            </div>

            <div>
              <Label htmlFor="edad" className="text-base font-semibold">
                Edad <span className="text-red-500">*</span>
              </Label>
              <Input
                id="edad"
                type="number"
                value={formData.edad}
                onChange={(e) => handleInputChange('edad', e.target.value)}
                placeholder="Ej: 30"
                className="mt-2"
                required
              />
            </div>

            <div>
              <Label htmlFor="email" className="text-base font-semibold">
                Correo electrónico <span className="text-red-500">*</span>
              </Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                placeholder="tu@email.com"
                className="mt-2"
                required
              />
            </div>

            <div>
              <Label htmlFor="whatsapp" className="text-base font-semibold">
                WhatsApp <span className="text-red-500">*</span>
              </Label>
              <Input
                id="whatsapp"
                type="tel"
                value={formData.whatsapp}
                onChange={(e) => handleInputChange('whatsapp', e.target.value)}
                placeholder="+34 600 000 000"
                className="mt-2"
                required
              />
            </div>
          </div>
        )}

        {/* STEP 2: Contexto Actual */}
        {currentStep === 2 && (
          <div className="space-y-6 animate-fade-in pb-24">
            <div>
              <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-500 to-orange-500 bg-clip-text text-transparent mb-2">
                Contexto Actual
              </h2>
              <p className="text-gray-600">Cuéntame sobre tu situación</p>
            </div>

            <div>
              <Label htmlFor="objetivo" className="text-base font-semibold">
                ¿Cuál es tu objetivo principal? <span className="text-red-500">*</span>
              </Label>
              <p className="text-sm text-gray-500 mt-1">Ej: perder grasa, ganar músculo, mejorar salud, tonificar, etc.</p>
              <Textarea
                id="objetivo"
                value={formData.objetivo}
                onChange={(e) => handleInputChange('objetivo', e.target.value)}
                placeholder="Describe tu objetivo..."
                className="mt-2"
                rows={3}
                required
              />
            </div>

            <div>
              <Label htmlFor="intentos_previos" className="text-base font-semibold">
                ¿Qué has intentado antes y qué resultados tuviste? <span className="text-red-500">*</span>
              </Label>
              <p className="text-sm text-gray-500 mt-1">Sé sincero/a. Dietas, apps, entrenadores, gimnasio, etc.</p>
              <Textarea
                id="intentos_previos"
                value={formData.intentos_previos}
                onChange={(e) => handleInputChange('intentos_previos', e.target.value)}
                placeholder="Cuéntame tu experiencia..."
                className="mt-2"
                rows={4}
                required
              />
            </div>

            <div>
              <Label className="text-base font-semibold">
                ¿Qué es lo que más te cuesta mantener en el tiempo?
              </Label>
              <p className="text-sm text-gray-500 mt-1 mb-3">Selecciona todos los que correspondan</p>
              <div className="space-y-2">
                {['La dieta', 'El entrenamiento', 'La motivación', 'La constancia', 'Otro'].map((option) => (
                  <label key={option} className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.dificultades.includes(option)}
                      onChange={() => handleCheckboxChange('dificultades', option)}
                      className="w-5 h-5 text-blue-500"
                    />
                    <span>{option}</span>
                  </label>
                ))}
              </div>
              {formData.dificultades.includes('Otro') && (
                <Input
                  value={formData.dificultades_otro}
                  onChange={(e) => handleInputChange('dificultades_otro', e.target.value)}
                  placeholder="Especifica..."
                  className="mt-2"
                />
              )}
            </div>

            <div>
              <Label className="text-base font-semibold">
                ¿Cuánto tiempo puedes dedicarle semanalmente? <span className="text-red-500">*</span>
              </Label>
              <div className="grid grid-cols-2 gap-3 mt-3">
                {['Menos de 3h', '3 a 5h', '6 a 8h', 'Más de 8h'].map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => handleInputChange('tiempo_semanal', option)}
                    className={`p-4 border-2 rounded-lg font-medium transition-all ${
                      formData.tiempo_semanal === option
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <Label className="text-base font-semibold">
                ¿Entrenas actualmente? <span className="text-red-500">*</span>
              </Label>
              <div className="grid grid-cols-3 gap-3 mt-3">
                {['Sí, en gimnasio', 'Sí, en casa', 'No entreno aún'].map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => handleInputChange('entrena', option)}
                    className={`p-4 border-2 rounded-lg font-medium transition-all ${
                      formData.entrena === option
                        ? 'border-orange-500 bg-orange-50 text-orange-700'
                        : 'border-gray-200 hover:border-orange-300'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* STEP 3: Nutrición y Estilo de Vida */}
        {currentStep === 3 && (
          <div className="space-y-6 animate-fade-in pb-24">
            <div>
              <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-500 to-orange-500 bg-clip-text text-transparent mb-2">
                Nutrición y Estilo de Vida
              </h2>
              <p className="text-gray-600">Hábitos y salud</p>
            </div>

            <div>
              <Label htmlFor="alimentacion" className="text-base font-semibold">
                ¿Cómo comes actualmente? <span className="text-red-500">*</span>
              </Label>
              <p className="text-sm text-gray-500 mt-1">¿Cuántas veces comes al día? ¿Comida casera o fuera? ¿Sigues algún tipo de dieta?</p>
              <Textarea
                id="alimentacion"
                value={formData.alimentacion}
                onChange={(e) => handleInputChange('alimentacion', e.target.value)}
                placeholder="Describe tus hábitos alimenticios..."
                className="mt-2"
                rows={4}
                required
              />
            </div>

            <div>
              <Label htmlFor="salud_info" className="text-base font-semibold">
                ¿Hay algo que deba saber sobre tu salud, cuerpo o estilo de vida? <span className="text-red-500">*</span>
              </Label>
              <p className="text-sm text-gray-500 mt-1">Ej: medicación, lesiones, enfermedades, turnos de trabajo, estrés, etc.</p>
              <Textarea
                id="salud_info"
                value={formData.salud_info}
                onChange={(e) => handleInputChange('salud_info', e.target.value)}
                placeholder="Información relevante sobre tu salud..."
                className="mt-2"
                rows={4}
                required
              />
            </div>
          </div>
        )}

        {/* STEP 4: Motivación y Compromiso */}
        {currentStep === 4 && (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-500 to-orange-500 bg-clip-text text-transparent mb-2">
                Motivación y Compromiso
              </h2>
              <p className="text-gray-600">Último paso</p>
            </div>

            <div>
              <Label htmlFor="por_que_ahora" className="text-base font-semibold">
                ¿Por qué ahora? ¿Qué ha cambiado? <span className="text-red-500">*</span>
              </Label>
              <p className="text-sm text-gray-500 mt-1">Cuéntame qué te ha hecho dar el paso</p>
              <Textarea
                id="por_que_ahora"
                value={formData.por_que_ahora}
                onChange={(e) => handleInputChange('por_que_ahora', e.target.value)}
                placeholder="Tu momento actual..."
                className="mt-2"
                rows={4}
                required
              />
            </div>

            <div>
              <Label className="text-base font-semibold">
                ¿Estarías dispuesto/a a invertir en ti? <span className="text-red-500">*</span>
              </Label>
              <div className="space-y-2 mt-3">
                {[
                  'Sí, si el servicio encaja conmigo',
                  'No lo sé aún, necesito verlo claro',
                  'Solo busco orientación gratuita'
                ].map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => handleInputChange('dispuesto_invertir', option)}
                    className={`w-full p-4 border-2 rounded-lg text-left transition-all ${
                      formData.dispuesto_invertir === option
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <Label className="text-base font-semibold">
                ¿Qué tipo de acompañamiento buscas? <span className="text-red-500">*</span>
              </Label>
              <div className="space-y-2 mt-3">
                {[
                  'Solo necesito una guía clara y estructura para seguir por mi cuenta',
                  'Quiero un seguimiento intensivo, correcciones, soporte 1 a 1',
                  'No lo tengo claro, necesito más información'
                ].map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => handleInputChange('tipo_acompanamiento', option)}
                    className={`w-full p-4 border-2 rounded-lg text-left transition-all ${
                      formData.tipo_acompanamiento === option
                        ? 'border-orange-500 bg-orange-50 text-orange-700'
                        : 'border-gray-200 hover:border-orange-300'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <Label className="text-base font-semibold">
                ¿Qué presupuesto mensual estarías dispuesto/a a invertir? <span className="text-red-500">*</span>
              </Label>
              <div className="grid grid-cols-2 gap-3 mt-3">
                {[
                  'Menos de 50€/mes',
                  '50-100€/mes',
                  '100-200€/mes',
                  '200-500€/mes',
                  'Más de 500€/mes'
                ].map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => handleInputChange('presupuesto', option)}
                    className={`p-4 border-2 rounded-lg font-medium transition-all ${
                      formData.presupuesto === option
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <Label htmlFor="comentarios_adicionales" className="text-base font-semibold">
                ¿Algo más que quieras contarme?
              </Label>
              <p className="text-sm text-gray-500 mt-1">Este espacio es tuyo</p>
              <Textarea
                id="comentarios_adicionales"
                value={formData.comentarios_adicionales}
                onChange={(e) => handleInputChange('comentarios_adicionales', e.target.value)}
                placeholder="Puedes contarme lo que quieras..."
                className="mt-2"
                rows={4}
              />
            </div>
          </div>
        )}
      </div>

      {/* Navigation Buttons */}
      <div className="border-t p-6 bg-gray-50 flex justify-between">
        <Button
          type="button"
          variant="outline"
          onClick={() => setCurrentStep(currentStep - 1)}
          disabled={currentStep === 1}
          className="flex items-center gap-2"
        >
          <ChevronLeft className="h-4 w-4" />
          Anterior
        </Button>

        {currentStep < totalSteps ? (
          <Button
            type="button"
            onClick={() => setCurrentStep(currentStep + 1)}
            disabled={!canGoNext()}
            className="bg-gradient-to-r from-blue-500 to-orange-500 hover:from-blue-600 hover:to-orange-600 flex items-center gap-2"
          >
            Siguiente
            <ChevronRight className="h-4 w-4" />
          </Button>
        ) : (
          <Button
            type="button"
            onClick={handleSubmit}
            disabled={loading || !formData.por_que_ahora || !formData.dispuesto_invertir || !formData.tipo_acompanamiento || !formData.presupuesto}
            className="bg-gradient-to-r from-blue-500 to-orange-500 hover:from-blue-600 hover:to-orange-600 flex items-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Enviando...
              </>
            ) : (
              <>
                Enviar Diagnóstico
                <CheckCircle className="h-4 w-4" />
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  );
};

export default DiagnosisQuestionnaire;
