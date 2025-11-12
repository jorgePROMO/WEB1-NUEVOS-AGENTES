import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Activity, Target, Utensils, Calendar, AlertCircle } from 'lucide-react';

const EDN360PlanViewer = ({ plan }) => {
  if (!plan) return null;

  const trainingPlan = plan.training_plan || {};
  const nutritionPlan = plan.nutrition_plan || {};

  // Formatear datos de entrenamiento
  const renderTrainingSection = () => {
    if (!trainingPlan || Object.keys(trainingPlan).length === 0) {
      return <p className="text-gray-500">No hay datos de entrenamiento disponibles</p>;
    }

    return (
      <div className="space-y-4">
        {/* E1 - Perfil Técnico */}
        {trainingPlan.E1 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Perfil del Cliente</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 text-sm">
                {trainingPlan.E1.perfil_tecnico && (
                  <>
                    <div>
                      <span className="font-medium">Edad:</span> {trainingPlan.E1.perfil_tecnico.edad} años
                    </div>
                    <div>
                      <span className="font-medium">IMC:</span> {trainingPlan.E1.perfil_tecnico.imc?.toFixed(1)}
                    </div>
                    <div>
                      <span className="font-medium">Peso:</span> {trainingPlan.E1.perfil_tecnico.peso_kg} kg
                    </div>
                    <div>
                      <span className="font-medium">Altura:</span> {trainingPlan.E1.perfil_tecnico.altura_cm} cm
                    </div>
                  </>
                )}
              </div>
              {trainingPlan.E1.experiencia && (
                <div className="mt-4">
                  <Badge>{trainingPlan.E1.experiencia.nivel?.toUpperCase()}</Badge>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* E2 - Capacidad y Riesgo */}
        {trainingPlan.E2 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Evaluación de Capacidad</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-medium">SEG Score:</span>
                <Badge className={
                  trainingPlan.E2.seg_score >= 8 ? 'bg-green-500' :
                  trainingPlan.E2.seg_score >= 6 ? 'bg-yellow-500' :
                  'bg-red-500'
                }>
                  {trainingPlan.E2.seg_score}/10
                </Badge>
              </div>
              {trainingPlan.E2.split_recomendado && (
                <div>
                  <span className="font-medium">Split:</span>{' '}
                  {trainingPlan.E2.split_recomendado.tipo}
                </div>
              )}
              {trainingPlan.E2.tiempo_sesion && (
                <div>
                  <span className="font-medium">Tiempo máximo sesión:</span>{' '}
                  {trainingPlan.E2.tiempo_sesion.maximo_minutos} min
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* E4 - Programa Mesociclo */}
        {trainingPlan.E4 && trainingPlan.E4.mesociclo && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Mesociclo (4 semanas)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {trainingPlan.E4.semanas && trainingPlan.E4.semanas.map((semana, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 border rounded">
                    <div>
                      <span className="font-medium">Semana {semana.numero}:</span>{' '}
                      <span className="text-sm text-gray-600">{semana.fase}</span>
                    </div>
                    <div className="flex gap-2">
                      <Badge variant="outline">{semana.volumen_pct}% vol</Badge>
                      <Badge variant="outline">RIR {semana.rir_objetivo?.join('-')}</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* E7 - Carga y Recuperación */}
        {trainingPlan.E7 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Métricas de Carga</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-4">
              {trainingPlan.E7.cit_semanal && (
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4" />
                  <div>
                    <div className="text-sm text-gray-600">CIT Semanal</div>
                    <div className="font-medium">{trainingPlan.E7.cit_semanal}</div>
                  </div>
                </div>
              )}
              {trainingPlan.E7.irg_score && (
                <div className="flex items-center gap-2">
                  <Target className="h-4 w-4" />
                  <div>
                    <div className="text-sm text-gray-600">IRG Score</div>
                    <div className="font-medium">{trainingPlan.E7.irg_score}</div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  // Formatear datos de nutrición
  const renderNutritionSection = () => {
    if (!nutritionPlan || Object.keys(nutritionPlan).length === 0) {
      return <p className="text-gray-500">No hay datos de nutrición disponibles</p>;
    }

    return (
      <div className="space-y-4">
        {/* N1 - Análisis Metabólico */}
        {nutritionPlan.N1 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Análisis Metabólico</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-4">
              {nutritionPlan.N1.tdee && (
                <div>
                  <div className="text-sm text-gray-600">TDEE</div>
                  <div className="font-medium">{nutritionPlan.N1.tdee} kcal</div>
                </div>
              )}
              {nutritionPlan.N1.bmr && (
                <div>
                  <div className="text-sm text-gray-600">BMR</div>
                  <div className="font-medium">{nutritionPlan.N1.bmr} kcal</div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* N2 - Objetivo Energético */}
        {nutritionPlan.N2 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Plan Nutricional</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {nutritionPlan.N2.kcal_objetivo && (
                <div className="flex items-center justify-between">
                  <span className="font-medium">Calorías Objetivo:</span>
                  <Badge className="bg-blue-500">{nutritionPlan.N2.kcal_objetivo} kcal</Badge>
                </div>
              )}
              {nutritionPlan.N2.macros_gkg && (
                <div className="space-y-2">
                  <div className="text-sm font-medium">Macros (g/kg):</div>
                  <div className="grid grid-cols-3 gap-2">
                    <div className="text-center p-2 bg-red-50 rounded">
                      <div className="text-xs text-gray-600">Proteína</div>
                      <div className="font-medium">{nutritionPlan.N2.macros_gkg.P} g/kg</div>
                    </div>
                    <div className="text-center p-2 bg-yellow-50 rounded">
                      <div className="text-xs text-gray-600">Grasa</div>
                      <div className="font-medium">{nutritionPlan.N2.macros_gkg.G} g/kg</div>
                    </div>
                    <div className="text-center p-2 bg-green-50 rounded">
                      <div className="text-xs text-gray-600">Carbos</div>
                      <div className="font-medium">{nutritionPlan.N2.macros_gkg.C} g/kg</div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* N4 - Sistema A/M/B */}
        {nutritionPlan.N4 && nutritionPlan.N4.calendario_mensual && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Calendario A/M/B</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-gray-600 mb-2">
                Sistema de días: Alta demanda (A), Media (M), Baja (B)
              </div>
              {nutritionPlan.N4.distribucion_amb && (
                <div className="flex gap-2">
                  <Badge className="bg-red-500">A: {nutritionPlan.N4.distribucion_amb.A} días</Badge>
                  <Badge className="bg-yellow-500">M: {nutritionPlan.N4.distribucion_amb.M} días</Badge>
                  <Badge className="bg-green-500">B: {nutritionPlan.N4.distribucion_amb.B} días</Badge>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* N5 - Timing de Comidas */}
        {nutritionPlan.N5 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Distribución de Comidas</CardTitle>
            </CardHeader>
            <CardContent>
              {nutritionPlan.N5.comidas_por_dia && (
                <div className="mb-2">
                  <span className="font-medium">Comidas por día:</span> {nutritionPlan.N5.comidas_por_dia}
                </div>
              )}
              {nutritionPlan.N5.horarios_comidas && (
                <div className="text-sm text-gray-600">
                  Horarios: {nutritionPlan.N5.horarios_comidas.join(', ')}
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  // Renderizar validaciones
  const renderValidations = () => {
    const validation = plan.validation;
    if (!validation) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            Validaciones del Plan
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center gap-2">
            <Badge className={validation.valid ? 'bg-green-500' : 'bg-yellow-500'}>
              {validation.valid ? 'Plan Válido' : 'Plan con Advertencias'}
            </Badge>
          </div>
          
          {validation.errors && validation.errors.length > 0 && (
            <div>
              <div className="font-medium text-red-600 mb-2">Errores:</div>
              <ul className="list-disc list-inside text-sm space-y-1">
                {validation.errors.map((error, idx) => (
                  <li key={idx} className="text-red-600">{error}</li>
                ))}
              </ul>
            </div>
          )}
          
          {validation.warnings && validation.warnings.length > 0 && (
            <div>
              <div className="font-medium text-yellow-600 mb-2">Advertencias:</div>
              <ul className="list-disc list-inside text-sm space-y-1">
                {validation.warnings.map((warning, idx) => (
                  <li key={idx} className="text-yellow-600">{warning}</li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Plan E.D.N.360 Completo</CardTitle>
          <div className="flex gap-2 mt-2">
            <Badge>ID: {plan._id}</Badge>
            <Badge>Versión: {plan.current_version || 1}</Badge>
            <Badge className="bg-blue-500">{plan.plan_type}</Badge>
          </div>
        </CardHeader>
      </Card>

      <Tabs defaultValue="training" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="training">
            <Activity className="h-4 w-4 mr-2" />
            Entrenamiento
          </TabsTrigger>
          <TabsTrigger value="nutrition">
            <Utensils className="h-4 w-4 mr-2" />
            Nutrición
          </TabsTrigger>
          <TabsTrigger value="validation">
            <AlertCircle className="h-4 w-4 mr-2" />
            Validaciones
          </TabsTrigger>
        </TabsList>

        <TabsContent value="training">
          {renderTrainingSection()}
        </TabsContent>

        <TabsContent value="nutrition">
          {renderNutritionSection()}
        </TabsContent>

        <TabsContent value="validation">
          {renderValidations()}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default EDN360PlanViewer;
