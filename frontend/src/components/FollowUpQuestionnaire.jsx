import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Loader2 } from 'lucide-react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const FollowUpQuestionnaire = ({ onSubmitSuccess, daysSinceLastPlan }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  
  // State para el formulario
  const [formData, setFormData] = useState({
    // Paso 1: Tipo de medición
    measurement_type: '',
    
    // Mediciones - Báscula inteligente
    peso: '',
    grasa_corporal: '',
    masa_muscular: '',
    grasa_visceral: '',
    agua_corporal: '',
    
    // Mediciones - Cinta métrica
    circunferencia_pecho: '',
    circunferencia_cintura: '',
    circunferencia_gluteo: '',
    circunferencia_muslo: '',
    circunferencia_brazo_relajado: '',
    circunferencia_brazo_flexionado: '',
    circunferencia_gemelo: '',
    satisfecho_cambios: '',
    
    // Adherencia
    constancia_entrenamiento: '',
    seguimiento_alimentacion: '',
    
    // Bienestar
    factores_externos: '',
    energia_animo_motivacion: '',
    sueno_estres: '',
    
    // Cambios percibidos
    molestias_dolor_lesion: '',
    cambios_corporales: '',
    fuerza_rendimiento: '',
    
    // Feedback
    objetivo_proximo_mes: '',
    cambios_deseados: '',
    comentarios_adicionales: ''
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const token = localStorage.getItem('token');
      
      // Construir el objeto de seguimiento según el tipo de medición
      const followUpData = {
        measurement_type: formData.measurement_type,
        measurements: null,
        adherence: {
          constancia_entrenamiento: formData.constancia_entrenamiento,
          seguimiento_alimentacion: formData.seguimiento_alimentacion
        },
        wellbeing: {
          factores_externos: formData.factores_externos || null,
          energia_animo_motivacion: formData.energia_animo_motivacion,
          sueno_estres: formData.sueno_estres
        },
        changes_perceived: {
          molestias_dolor_lesion: formData.molestias_dolor_lesion,
          cambios_corporales: formData.cambios_corporales,
          fuerza_rendimiento: formData.fuerza_rendimiento
        },
        feedback: {
          objetivo_proximo_mes: formData.objetivo_proximo_mes,
          cambios_deseados: formData.cambios_deseados,
          comentarios_adicionales: formData.comentarios_adicionales || null
        }
      };

      // Agregar mediciones según el tipo
      if (formData.measurement_type === 'smart_scale') {
        followUpData.measurements = {
          peso: formData.peso,
          grasa_corporal: formData.grasa_corporal,
          masa_muscular: formData.masa_muscular,
          grasa_visceral: formData.grasa_visceral,
          agua_corporal: formData.agua_corporal
        };
      } else if (formData.measurement_type === 'tape_measure') {
        followUpData.measurements = {
          peso: formData.peso,
          circunferencia_pecho: formData.circunferencia_pecho,
          circunferencia_cintura: formData.circunferencia_cintura,
          circunferencia_gluteo: formData.circunferencia_gluteo,
          circunferencia_muslo: formData.circunferencia_muslo,
          circunferencia_brazo_relajado: formData.circunferencia_brazo_relajado,
          circunferencia_brazo_flexionado: formData.circunferencia_brazo_flexionado,
          circunferencia_gemelo: formData.circunferencia_gemelo,
          satisfecho_cambios: formData.satisfecho_cambios
        };
      }

      const response = await axios.post(
        `${API}/api/follow-up/submit`,
        followUpData,
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        }
      );

      alert('✅ Cuestionario de seguimiento enviado correctamente. Tu entrenador lo revisará pronto.');
      
      if (onSubmitSuccess) {
        onSubmitSuccess();
      }

    } catch (error) {
      console.error('Error submitting follow-up:', error);
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const goToNextStep = () => {
    setCurrentStep(prev => prev + 1);
  };

  const goToPrevStep = () => {
    setCurrentStep(prev => prev - 1);
  };

  // Validar paso actual
  const isStepValid = () => {
    switch (currentStep) {
      case 1:
        return formData.measurement_type !== '';
      case 2:
        if (formData.measurement_type === 'smart_scale') {
          return formData.peso && formData.grasa_corporal && formData.masa_muscular && 
                 formData.grasa_visceral && formData.agua_corporal;
        } else if (formData.measurement_type === 'tape_measure') {
          return formData.peso && formData.circunferencia_pecho && formData.circunferencia_cintura && 
                 formData.circunferencia_gluteo && formData.circunferencia_muslo && 
                 formData.circunferencia_brazo_relajado && formData.circunferencia_brazo_flexionado && 
                 formData.circunferencia_gemelo && formData.satisfecho_cambios;
        } else {
          return true; // none
        }
      case 3:
        return formData.constancia_entrenamiento && formData.seguimiento_alimentacion;
      case 4:
        return formData.energia_animo_motivacion && formData.sueno_estres;
      case 5:
        return formData.molestias_dolor_lesion && formData.cambios_corporales && formData.fuerza_rendimiento;
      case 6:
        return formData.objetivo_proximo_mes && formData.cambios_deseados;
      default:
        return true;
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl">
          📊 Cuestionario de Seguimiento Mensual
        </CardTitle>
        <p className="text-sm text-gray-600">
          Han pasado <strong>{daysSinceLastPlan}</strong> días desde tu último plan. 
          Completa este cuestionario para que podamos ajustar tu nutrición y entrenamiento.
        </p>
        <div className="flex items-center gap-2 mt-4">
          {[1, 2, 3, 4, 5, 6].map((step) => (
            <div
              key={step}
              className={`h-2 flex-1 rounded ${
                step === currentStep ? 'bg-blue-500' : 
                step < currentStep ? 'bg-green-500' : 'bg-gray-200'
              }`}
            />
          ))}
        </div>
        <p className="text-xs text-gray-500 mt-2">Paso {currentStep} de 6</p>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit}>
          {/* PASO 1: Tipo de medición */}
          {currentStep === 1 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">1. ¿Cómo te mediste este mes?</h3>
              
              <div className="space-y-3">
                <label className="flex items-center p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition">
                  <input
                    type="radio"
                    name="measurement_type"
                    value="smart_scale"
                    checked={formData.measurement_type === 'smart_scale'}
                    onChange={handleInputChange}
                    className="mr-3"
                  />
                  <div>
                    <div className="font-semibold">Báscula inteligente</div>
                    <div className="text-sm text-gray-600">Con datos de % grasa, % músculo, etc.</div>
                  </div>
                </label>

                <label className="flex items-center p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition">
                  <input
                    type="radio"
                    name="measurement_type"
                    value="tape_measure"
                    checked={formData.measurement_type === 'tape_measure'}
                    onChange={handleInputChange}
                    className="mr-3"
                  />
                  <div>
                    <div className="font-semibold">Báscula + Cinta métrica</div>
                    <div className="text-sm text-gray-600">Con circunferencias corporales</div>
                  </div>
                </label>

                <label className="flex items-center p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition">
                  <input
                    type="radio"
                    name="measurement_type"
                    value="none"
                    checked={formData.measurement_type === 'none'}
                    onChange={handleInputChange}
                    className="mr-3"
                  />
                  <div>
                    <div className="font-semibold">No me medí</div>
                    <div className="text-sm text-gray-600">Pasar a las siguientes preguntas</div>
                  </div>
                </label>
              </div>
            </div>
          )}

          {/* PASO 2: Mediciones (condicional) */}
          {currentStep === 2 && formData.measurement_type === 'smart_scale' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">2. Mediciones con Báscula Inteligente</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Peso (kg)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    name="peso"
                    value={formData.peso}
                    onChange={handleInputChange}
                    placeholder="70.5"
                    required
                  />
                </div>

                <div>
                  <Label>% Grasa Corporal</Label>
                  <Input
                    type="number"
                    step="0.1"
                    name="grasa_corporal"
                    value={formData.grasa_corporal}
                    onChange={handleInputChange}
                    placeholder="15.2"
                    required
                  />
                </div>

                <div>
                  <Label>% Masa Muscular</Label>
                  <Input
                    type="number"
                    step="0.1"
                    name="masa_muscular"
                    value={formData.masa_muscular}
                    onChange={handleInputChange}
                    placeholder="42.5"
                    required
                  />
                </div>

                <div>
                  <Label>Grasa Visceral</Label>
                  <Input
                    type="number"
                    step="0.1"
                    name="grasa_visceral"
                    value={formData.grasa_visceral}
                    onChange={handleInputChange}
                    placeholder="8"
                    required
                  />
                </div>

                <div>
                  <Label>% Agua Corporal</Label>
                  <Input
                    type="number"
                    step="0.1"
                    name="agua_corporal"
                    value={formData.agua_corporal}
                    onChange={handleInputChange}
                    placeholder="58.3"
                    required
                  />
                </div>
              </div>
            </div>
          )}

          {currentStep === 2 && formData.measurement_type === 'tape_measure' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">2. Mediciones con Cinta Métrica</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Peso (kg)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    name="peso"
                    value={formData.peso}
                    onChange={handleInputChange}
                    placeholder="70.5"
                    required
                  />
                </div>

                <div>
                  <Label>Circunferencia Pecho (cm)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    name="circunferencia_pecho"
                    value={formData.circunferencia_pecho}
                    onChange={handleInputChange}
                    placeholder="95"
                    required
                  />
                </div>

                <div>
                  <Label>Circunferencia Cintura (cm)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    name="circunferencia_cintura"
                    value={formData.circunferencia_cintura}
                    onChange={handleInputChange}
                    placeholder="80"
                    required
                  />
                </div>

                <div>
                  <Label>Circunferencia Glúteo (cm)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    name="circunferencia_gluteo"
                    value={formData.circunferencia_gluteo}
                    onChange={handleInputChange}
                    placeholder="98"
                    required
                  />
                </div>

                <div>
                  <Label>Circunferencia Muslo (cm)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    name="circunferencia_muslo"
                    value={formData.circunferencia_muslo}
                    onChange={handleInputChange}
                    placeholder="55"
                    required
                  />
                </div>

                <div>
                  <Label>Brazo Relajado (cm)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    name="circunferencia_brazo_relajado"
                    value={formData.circunferencia_brazo_relajado}
                    onChange={handleInputChange}
                    placeholder="32"
                    required
                  />
                </div>

                <div>
                  <Label>Brazo Flexionado (cm)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    name="circunferencia_brazo_flexionado"
                    value={formData.circunferencia_brazo_flexionado}
                    onChange={handleInputChange}
                    placeholder="35"
                    required
                  />
                </div>

                <div>
                  <Label>Circunferencia Gemelo (cm)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    name="circunferencia_gemelo"
                    value={formData.circunferencia_gemelo}
                    onChange={handleInputChange}
                    placeholder="38"
                    required
                  />
                </div>

                <div className="col-span-2">
                  <Label>¿Estás satisfecho con los cambios?</Label>
                  <select
                    name="satisfecho_cambios"
                    value={formData.satisfecho_cambios}
                    onChange={handleInputChange}
                    className="w-full p-2 border rounded"
                    required
                  >
                    <option value="">Selecciona...</option>
                    <option value="SI">Sí</option>
                    <option value="NO">No</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {currentStep === 2 && formData.measurement_type === 'none' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">2. Sin mediciones</h3>
              <p className="text-gray-600">
                No te preocupes, continuaremos con las siguientes preguntas sobre tu adherencia y progreso.
              </p>
            </div>
          )}

          {/* PASO 3: Adherencia */}
          {currentStep === 3 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">3. Adherencia al Plan</h3>
              
              <div>
                <Label>¿Cómo ha sido tu constancia en el entrenamiento?</Label>
                <Textarea
                  name="constancia_entrenamiento"
                  value={formData.constancia_entrenamiento}
                  onChange={handleInputChange}
                  placeholder="Ej: He entrenado 4 días a la semana de forma constante..."
                  rows={3}
                  required
                />
              </div>

              <div>
                <Label>¿Has seguido el plan de alimentación?</Label>
                <Textarea
                  name="seguimiento_alimentacion"
                  value={formData.seguimiento_alimentacion}
                  onChange={handleInputChange}
                  placeholder="Ej: He seguido el plan al 90%, solo algunos días..."
                  rows={3}
                  required
                />
              </div>
            </div>
          )}

          {/* PASO 4: Bienestar */}
          {currentStep === 4 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">4. ¿Cómo te sentiste este mes?</h3>
              
              <div>
                <Label>¿Ha habido factores externos que te hayan afectado? (opcional)</Label>
                <Textarea
                  name="factores_externos"
                  value={formData.factores_externos}
                  onChange={handleInputChange}
                  placeholder="Ej: Estrés laboral, cambios en mi rutina..."
                  rows={3}
                />
              </div>

              <div>
                <Label>¿Cómo ha sido tu energía, ánimo y motivación?</Label>
                <Textarea
                  name="energia_animo_motivacion"
                  value={formData.energia_animo_motivacion}
                  onChange={handleInputChange}
                  placeholder="Ej: Me he sentido con buena energía y motivado..."
                  rows={3}
                  required
                />
              </div>

              <div>
                <Label>¿Cómo ha sido tu sueño y nivel de estrés?</Label>
                <Textarea
                  name="sueno_estres"
                  value={formData.sueno_estres}
                  onChange={handleInputChange}
                  placeholder="Ej: He dormido 7 horas diarias, estrés moderado..."
                  rows={3}
                  required
                />
              </div>
            </div>
          )}

          {/* PASO 5: Cambios percibidos */}
          {currentStep === 5 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">5. Cambios Percibidos</h3>
              
              <div>
                <Label>¿Has tenido molestias, dolores o lesiones?</Label>
                <Textarea
                  name="molestias_dolor_lesion"
                  value={formData.molestias_dolor_lesion}
                  onChange={handleInputChange}
                  placeholder="Ej: No he tenido molestias / Leve dolor en rodilla..."
                  rows={3}
                  required
                />
              </div>

              <div>
                <Label>¿Qué cambios has notado en tu cuerpo?</Label>
                <Textarea
                  name="cambios_corporales"
                  value={formData.cambios_corporales}
                  onChange={handleInputChange}
                  placeholder="Ej: He notado más definición muscular, perdí grasa..."
                  rows={3}
                  required
                />
              </div>

              <div>
                <Label>¿Cómo ha evolucionado tu fuerza y rendimiento?</Label>
                <Textarea
                  name="fuerza_rendimiento"
                  value={formData.fuerza_rendimiento}
                  onChange={handleInputChange}
                  placeholder="Ej: He aumentado peso en todos mis ejercicios..."
                  rows={3}
                  required
                />
              </div>
            </div>
          )}

          {/* PASO 6: Feedback y objetivos */}
          {currentStep === 6 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">6. Ajustes y Próximo Mes</h3>
              
              <div>
                <Label>¿Cuál es tu objetivo para el próximo mes?</Label>
                <Textarea
                  name="objetivo_proximo_mes"
                  value={formData.objetivo_proximo_mes}
                  onChange={handleInputChange}
                  placeholder="Ej: Seguir ganando músculo, mantener el déficit calórico..."
                  rows={3}
                  required
                />
              </div>

              <div>
                <Label>¿Qué cambios te gustaría hacer en tu plan?</Label>
                <Textarea
                  name="cambios_deseados"
                  value={formData.cambios_deseados}
                  onChange={handleInputChange}
                  placeholder="Ej: Más variedad en las comidas, aumentar días de entrenamiento..."
                  rows={3}
                  required
                />
              </div>

              <div>
                <Label>Comentarios adicionales (opcional)</Label>
                <Textarea
                  name="comentarios_adicionales"
                  value={formData.comentarios_adicionales}
                  onChange={handleInputChange}
                  placeholder="Cualquier otra observación que quieras compartir..."
                  rows={4}
                />
              </div>
            </div>
          )}

          {/* Botones de navegación */}
          <div className="flex justify-between mt-6">
            <Button
              type="button"
              variant="outline"
              onClick={goToPrevStep}
              disabled={currentStep === 1 || isSubmitting}
            >
              Anterior
            </Button>

            {currentStep < 6 ? (
              <Button
                type="button"
                onClick={goToNextStep}
                disabled={!isStepValid()}
              >
                Siguiente
              </Button>
            ) : (
              <Button
                type="submit"
                disabled={isSubmitting || !isStepValid()}
                className="bg-green-600 hover:bg-green-700"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Enviando...
                  </>
                ) : (
                  '✅ Enviar Cuestionario'
                )}
              </Button>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default FollowUpQuestionnaire;
