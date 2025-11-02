import React, { useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { CheckCircle, Loader2, ChevronRight, ChevronLeft } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const NutritionQuestionnaire = ({ user, onComplete }) => {
  const [currentSection, setCurrentSection] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    // Datos básicos
    nombre_completo: user?.name || '',
    email: user?.email || '',
    fecha_nacimiento: '',
    sexo: '',
    profesion: '',
    direccion: '',
    telefono: user?.phone || '',
    
    // Medidas corporales
    peso: '',
    altura_cm: '',
    grasa_porcentaje: '',
    cintura_cm: '',
    cadera_cm: '',
    biceps_relajado_cm: '',
    biceps_flexionado_cm: '',
    muslo_cm: '',
    
    // Salud y medicación
    medicamentos: '',
    enfermedad_cronica: '',
    fuma_cantidad: '',
    bebe_cantidad: '',
    retencion_liquidos: '',
    problemas_corazon: '',
    hipertension: '',
    diabetes: '',
    colesterol: '',
    sobrepeso: '',
    epilepsia: '',
    alergias_intolerancias: '',
    problema_ejercicio: '',
    operaciones: '',
    embarazo: '',
    problemas_respiratorios: '',
    problemas_musculares: '',
    varo_valgo: '',
    hernias_protusiones: '',
    artrosis: '',
    menopausia: '',
    osteoporosis: '',
    
    // Trabajo y estrés
    estres_profesion: '',
    movimiento_trabajo: '',
    dia_trabajo: '',
    descansa_trabajo: '',
    horas_trabajo: '',
    actividad_fisica_diaria: '',
    trabajo_fisicamente: '',
    horas_ocio_semana: '',
    
    // Experiencia deportiva
    practicado_deporte: '',
    experiencia_negativa: '',
    constante_deporte: '',
    tiempo_dedicaba: '',
    nivel_deporte: '',
    entrenado_gimnasio: '',
    entrenador_personal: '',
    resistencia_cardiorespiratoria: '',
    fuerza: '',
    flexibilidad: '',
    agilidad_coordinacion: '',
    
    // Disponibilidad y preferencias
    dias_semana_entrenar: '',
    tiempo_sesion: '',
    entrena_manana_tarde: '',
    gimnasio: '',
    material_casa: '',
    actividades_realizar: '',
    tipo_persona: '',
    cuesta_coger_peso: '',
    motivos_entrenar: [],
    
    // Horarios
    hora_levanta: '',
    hora_desayuno: '',
    hora_almuerzo: '',
    hora_comida: '',
    hora_merienda: '',
    hora_cena: '',
    hora_acuesta: '',
    horas_duerme: '',
    
    // Hábitos alimentarios
    comidas_dia: '',
    comidas_fuertes_ligeras: '',
    alimento_no_soporta: '',
    comida_favorita: '',
    comida_basura_frecuencia: '',
    dietas_anteriores: '',
    sustancias_alteran: '',
    suplementacion: '',
    come_fuera_casa: '',
    azucar_dulces_bolleria: '',
    anade_sal: '',
    bebidas_gas: '',
    
    // Objetivos
    objetivo_fisico: '',
    experiencia_ejercicio_constante: '',
    impedido_constancia: '',
    motiva_ejercicio: '',
    nivel_energia_dia: '',
    comentarios_adicionales: ''
  });

  const sections = [
    {
      title: '📋 Datos Básicos',
      fields: [
        { name: 'nombre_completo', label: 'Nombre Completo', type: 'text', required: true },
        { name: 'email', label: 'Email', type: 'email', required: true },
        { name: 'fecha_nacimiento', label: 'Fecha de Nacimiento', type: 'date', required: true },
        { name: 'sexo', label: 'Sexo', type: 'select', options: ['HOMBRE', 'MUJER'], required: true },
        { name: 'profesion', label: 'Profesión', type: 'text', required: true },
        { name: 'direccion', label: 'Dirección', type: 'text' },
        { name: 'telefono', label: 'Teléfono', type: 'tel', required: true }
      ]
    },
    {
      title: '📏 Medidas Corporales',
      fields: [
        { name: 'peso', label: 'Peso (kg)', type: 'number', required: true },
        { name: 'altura_cm', label: 'Altura (cm)', type: 'number', required: true },
        { name: 'grasa_porcentaje', label: '% Grasa Corporal (si lo conoces)', type: 'number' },
        { name: 'cintura_cm', label: 'Cintura (cm)', type: 'number' },
        { name: 'cadera_cm', label: 'Cadera (cm)', type: 'number' },
        { name: 'biceps_relajado_cm', label: 'Bíceps Relajado (cm)', type: 'number' },
        { name: 'biceps_flexionado_cm', label: 'Bíceps Flexionado (cm)', type: 'number' },
        { name: 'muslo_cm', label: 'Muslo (cm)', type: 'number' }
      ]
    },
    {
      title: '🏥 Salud y Medicación',
      fields: [
        { name: 'medicamentos', label: '¿Tomas algún medicamento?', type: 'textarea' },
        { name: 'enfermedad_cronica', label: '¿Tienes alguna enfermedad crónica?', type: 'textarea' },
        { name: 'fuma_cantidad', label: '¿Fumas? ¿Cuánto?', type: 'text' },
        { name: 'bebe_cantidad', label: '¿Bebes alcohol? ¿Cuánto?', type: 'text' },
        { name: 'retencion_liquidos', label: '¿Retención de líquidos?', type: 'select', options: ['No', 'Sí', 'A veces'] },
        { name: 'problemas_corazon', label: '¿Problemas de corazón?', type: 'select', options: ['No', 'Sí'] },
        { name: 'hipertension', label: '¿Hipertensión?', type: 'select', options: ['No', 'Sí'] },
        { name: 'diabetes', label: '¿Diabetes?', type: 'select', options: ['No', 'Tipo 1', 'Tipo 2'] },
        { name: 'colesterol', label: '¿Colesterol alto?', type: 'select', options: ['No', 'Sí'] },
        { name: 'sobrepeso', label: '¿Sobrepeso?', type: 'select', options: ['No', 'Sí'] },
        { name: 'epilepsia', label: '¿Epilepsia?', type: 'select', options: ['No', 'Sí'] },
        { name: 'alergias_intolerancias', label: 'Alergias o intolerancias alimentarias', type: 'textarea' },
        { name: 'problema_ejercicio', label: '¿Algún problema que impida hacer ejercicio?', type: 'textarea' },
        { name: 'operaciones', label: '¿Has tenido operaciones? ¿Cuáles?', type: 'textarea' },
        { name: 'embarazo', label: '¿Embarazo actual o reciente?', type: 'select', options: ['No', 'Sí'] },
        { name: 'problemas_respiratorios', label: '¿Problemas respiratorios (asma, etc.)?', type: 'textarea' },
        { name: 'problemas_musculares', label: '¿Problemas musculares o articulares?', type: 'textarea' },
        { name: 'varo_valgo', label: '¿Varo o valgo en rodillas?', type: 'select', options: ['No', 'Varo', 'Valgo'] },
        { name: 'hernias_protusiones', label: '¿Hernias o protusiones?', type: 'textarea' },
        { name: 'artrosis', label: '¿Artrosis?', type: 'select', options: ['No', 'Sí'] },
        { name: 'menopausia', label: '¿Menopausia?', type: 'select', options: ['No', 'Sí', 'Premenopausia'] },
        { name: 'osteoporosis', label: '¿Osteoporosis?', type: 'select', options: ['No', 'Sí'] }
      ]
    },
    {
      title: '💼 Trabajo y Estrés',
      fields: [
        { name: 'estres_profesion', label: '¿Tu profesión es estresante?', type: 'select', options: ['Poco', 'Medio', 'Mucho'], required: true },
        { name: 'movimiento_trabajo', label: '¿Te mueves mucho en el trabajo?', type: 'select', options: ['Poco', 'Medio', 'Mucho'], required: true },
        { name: 'dia_trabajo', label: 'Describe un día típico de trabajo', type: 'textarea' },
        { name: 'descansa_trabajo', label: '¿Descansas bien durante el trabajo?', type: 'select', options: ['Sí', 'No'], required: true },
        { name: 'horas_trabajo', label: '¿Cuántas horas trabajas al día?', type: 'number', required: true },
        { name: 'actividad_fisica_diaria', label: 'Actividad física en el día', type: 'select', options: ['Sedentario', 'Ligeramente activo', 'Moderadamente activo', 'Muy activo'], required: true },
        { name: 'trabajo_fisicamente', label: '¿Trabajas físicamente?', type: 'select', options: ['No', 'Sí, ligero', 'Sí, moderado', 'Sí, intenso'], required: true },
        { name: 'horas_ocio_semana', label: 'Horas de ocio a la semana', type: 'number' }
      ]
    },
    {
      title: '🏃 Experiencia Deportiva',
      fields: [
        { name: 'practicado_deporte', label: '¿Has practicado deporte?', type: 'select', options: ['No', 'Sí'], required: true },
        { name: 'experiencia_negativa', label: '¿Alguna experiencia negativa con el ejercicio?', type: 'textarea' },
        { name: 'constante_deporte', label: '¿Has sido constante con el deporte?', type: 'select', options: ['No', 'A veces', 'Sí'] },
        { name: 'tiempo_dedicaba', label: 'Tiempo que dedicabas al deporte', type: 'text' },
        { name: 'nivel_deporte', label: 'Nivel de deporte practicado', type: 'select', options: ['Principiante', 'Intermedio', 'Avanzado'] },
        { name: 'entrenado_gimnasio', label: '¿Has entrenado en gimnasio?', type: 'select', options: ['No', 'Sí'] },
        { name: 'entrenador_personal', label: '¿Has tenido entrenador personal?', type: 'select', options: ['No', 'Sí'] },
        { name: 'resistencia_cardiorespiratoria', label: 'Resistencia cardiorespiratoria', type: 'select', options: ['Baja', 'Media', 'Alta'] },
        { name: 'fuerza', label: 'Nivel de fuerza', type: 'select', options: ['Baja', 'Media', 'Alta'] },
        { name: 'flexibilidad', label: 'Flexibilidad', type: 'select', options: ['Baja', 'Media', 'Alta'] },
        { name: 'agilidad_coordinacion', label: 'Agilidad y coordinación', type: 'select', options: ['Baja', 'Media', 'Alta'] }
      ]
    },
    {
      title: '📅 Disponibilidad y Preferencias',
      fields: [
        { name: 'dias_semana_entrenar', label: '¿Cuántos días a la semana puedes entrenar?', type: 'select', options: ['1-2', '3-4', '5-6', '7'], required: true },
        { name: 'tiempo_sesion', label: 'Tiempo por sesión', type: 'select', options: ['30 min', '45 min', '60 min', '90 min'], required: true },
        { name: 'entrena_manana_tarde', label: '¿Prefieres mañana o tarde?', type: 'select', options: ['Mañana', 'Tarde', 'Indiferente'], required: true },
        { name: 'gimnasio', label: '¿Tienes acceso a gimnasio?', type: 'select', options: ['No', 'Sí'], required: true },
        { name: 'material_casa', label: '¿Qué material tienes en casa?', type: 'textarea' },
        { name: 'actividades_realizar', label: 'Actividades que te gustaría realizar', type: 'textarea' },
        { name: 'tipo_persona', label: '¿Qué tipo de persona eres?', type: 'select', options: ['Tranquilo/a', 'Activo/a', 'Muy activo/a'] },
        { name: 'cuesta_coger_peso', label: '¿Te cuesta coger peso?', type: 'select', options: ['No', 'Sí'] }
      ]
    },
    {
      title: '⏰ Horarios',
      fields: [
        { name: 'hora_levanta', label: '¿A qué hora te levantas?', type: 'time', required: true },
        { name: 'hora_desayuno', label: 'Hora del desayuno', type: 'time', required: true },
        { name: 'hora_almuerzo', label: 'Hora del almuerzo (si aplica)', type: 'time' },
        { name: 'hora_comida', label: 'Hora de la comida', type: 'time', required: true },
        { name: 'hora_merienda', label: 'Hora de la merienda (si aplica)', type: 'time' },
        { name: 'hora_cena', label: 'Hora de la cena', type: 'time', required: true },
        { name: 'hora_acuesta', label: '¿A qué hora te acuestas?', type: 'time', required: true },
        { name: 'horas_duerme', label: '¿Cuántas horas duermes?', type: 'number', required: true }
      ]
    },
    {
      title: '🍽️ Hábitos Alimentarios',
      fields: [
        { name: 'comidas_dia', label: '¿Cuántas comidas haces al día?', type: 'select', options: ['2', '3', '4', '5', '6+'], required: true },
        { name: 'comidas_fuertes_ligeras', label: '¿Tus comidas son fuertes o ligeras?', type: 'text' },
        { name: 'alimento_no_soporta', label: 'Alimentos que no soportas', type: 'textarea' },
        { name: 'comida_favorita', label: 'Tu comida favorita', type: 'text' },
        { name: 'comida_basura_frecuencia', label: '¿Con qué frecuencia comes comida basura?', type: 'select', options: ['Nunca', 'Rara vez', '1-2 veces/semana', '3+ veces/semana'] },
        { name: 'dietas_anteriores', label: 'Dietas que has probado antes', type: 'textarea' },
        { name: 'sustancias_alteran', label: '¿Tomas sustancias que alteren el metabolismo?', type: 'textarea' },
        { name: 'suplementacion', label: '¿Tomas suplementos? ¿Cuáles?', type: 'textarea' },
        { name: 'come_fuera_casa', label: '¿Comes fuera de casa?', type: 'select', options: ['Nunca', 'A veces', 'Frecuentemente'], required: true },
        { name: 'azucar_dulces_bolleria', label: '¿Consumes azúcar, dulces o bollería?', type: 'select', options: ['Nunca', 'A veces', 'Frecuentemente'], required: true },
        { name: 'anade_sal', label: '¿Añades sal a las comidas?', type: 'select', options: ['No', 'Sí, poco', 'Sí, mucho'], required: true },
        { name: 'bebidas_gas', label: '¿Tomas bebidas con gas?', type: 'select', options: ['No', 'A veces', 'Frecuentemente'], required: true }
      ]
    },
    {
      title: '🎯 Objetivos',
      fields: [
        { name: 'objetivo_fisico', label: 'Objetivo físico principal', type: 'select', options: ['Perder grasa', 'Ganar músculo', 'Mantener', 'Tonificar', 'Mejorar rendimiento'], required: true },
        { name: 'experiencia_ejercicio_constante', label: '¿Experiencia siendo constante con ejercicio?', type: 'textarea' },
        { name: 'impedido_constancia', label: '¿Qué te ha impedido ser constante antes?', type: 'textarea' },
        { name: 'motiva_ejercicio', label: '¿Qué te motiva a hacer ejercicio?', type: 'textarea' },
        { name: 'nivel_energia_dia', label: 'Nivel de energía durante el día', type: 'select', options: ['Bajo', 'Medio', 'Alto'], required: true },
        { name: 'comentarios_adicionales', label: 'Comentarios adicionales', type: 'textarea' }
      ]
    },
    {
      title: '✅ Revisión Final',
      isReview: true
    }
  ];

  const handleChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleCheckboxChange = (name, value) => {
    setFormData(prev => ({
      ...prev,
      [name]: prev[name].includes(value)
        ? prev[name].filter(v => v !== value)
        : [...prev[name], value]
    }));
  };

  const validateSection = (sectionIndex) => {
    const section = sections[sectionIndex];
    if (section.isReview) return true;
    
    const requiredFields = section.fields.filter(f => f.required);
    return requiredFields.every(field => formData[field.name]?.toString().trim() !== '');
  };

  const handleNext = () => {
    if (validateSection(currentSection)) {
      setCurrentSection(prev => Math.min(prev + 1, sections.length - 1));
      setError('');
    } else {
      setError('Por favor completa todos los campos obligatorios');
    }
  };

  const handlePrevious = () => {
    setCurrentSection(prev => Math.max(prev - 1, 0));
    setError('');
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/nutrition/questionnaire/submit`,
        formData,
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );

      alert('✅ ¡Cuestionario enviado! Tu plan de nutrición se está generando...');
      if (onComplete) {
        onComplete(response.data);
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Error al enviar el cuestionario');
    } finally {
      setLoading(false);
    }
  };

  const renderField = (field) => {
    const { name, label, type, options, required } = field;

    if (type === 'select') {
      return (
        <div key={name} className="space-y-2">
          <Label>
            {label} {required && <span className="text-red-500">*</span>}
          </Label>
          <select
            value={formData[name]}
            onChange={(e) => handleChange(name, e.target.value)}
            className="w-full border rounded px-3 py-2"
            required={required}
          >
            <option value="">Selecciona una opción</option>
            {options.map(opt => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        </div>
      );
    }

    if (type === 'textarea') {
      return (
        <div key={name} className="space-y-2">
          <Label>
            {label} {required && <span className="text-red-500">*</span>}
          </Label>
          <Textarea
            value={formData[name]}
            onChange={(e) => handleChange(name, e.target.value)}
            rows={3}
            required={required}
          />
        </div>
      );
    }

    return (
      <div key={name} className="space-y-2">
        <Label>
          {label} {required && <span className="text-red-500">*</span>}
        </Label>
        <Input
          type={type}
          value={formData[name]}
          onChange={(e) => handleChange(name, e.target.value)}
          required={required}
        />
      </div>
    );
  };

  const currentSectionData = sections[currentSection];

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">
            {currentSectionData.title}
          </CardTitle>
          <div className="flex items-center gap-2 mt-4">
            {sections.map((_, idx) => (
              <div
                key={idx}
                className={`h-2 flex-1 rounded ${
                  idx < currentSection ? 'bg-green-500' :
                  idx === currentSection ? 'bg-blue-500' :
                  'bg-gray-200'
                }`}
              />
            ))}
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Sección {currentSection + 1} de {sections.length}
          </p>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {currentSectionData.isReview ? (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 p-6 rounded-lg">
                <h3 className="text-xl font-bold mb-4 text-blue-900">
                  🎉 ¡Cuestionario Completado!
                </h3>
                <p className="text-gray-700 mb-4">
                  Has completado todas las secciones. Al enviar este cuestionario:
                </p>
                <ul className="list-disc list-inside space-y-2 text-gray-700">
                  <li>Se generará tu plan de nutrición personalizado automáticamente</li>
                  <li>Los agentes calcularán tus macros óptimos</li>
                  <li>Recibirás un menú semanal completo adaptado a ti</li>
                  <li>Tu entrenador revisará el plan antes de enviártelo</li>
                </ul>
              </div>

              <Button
                onClick={handleSubmit}
                disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700 text-white py-6 text-lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Generando tu plan...
                  </>
                ) : (
                  <>
                    <CheckCircle className="mr-2 h-5 w-5" />
                    Enviar Cuestionario y Generar Plan
                  </>
                )}
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {currentSectionData.fields.map(renderField)}
            </div>
          )}

          <div className="flex justify-between mt-8">
            <Button
              onClick={handlePrevious}
              disabled={currentSection === 0}
              variant="outline"
            >
              <ChevronLeft className="mr-2 h-4 w-4" />
              Anterior
            </Button>

            {currentSection < sections.length - 1 && (
              <Button onClick={handleNext}>
                Siguiente
                <ChevronRight className="ml-2 h-4 w-4" />
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default NutritionQuestionnaire;
