/**
 * ⚠️ MOCK TEMPORAL para testing del flujo EDN360
 * 
 * Este mock simula la respuesta del workflow de OpenAI Agents SDK
 * para permitir testing end-to-end sin el código real de Agent Builder.
 * 
 * Jorge: Cuando tengas el código real del Agent Builder, reemplaza
 * TODO este archivo con ese código completo.
 */

export type WorkflowInput = {
  input_as_text: string;
};

/**
 * Mock temporal de runWorkflow.
 * Devuelve un training plan válido pero simplificado.
 */
export const runWorkflow = async (workflow: WorkflowInput): Promise<any> => {
  console.log('⚠️ USANDO MOCK del workflow EDN360');
  console.log(`📥 Input recibido: ${workflow.input_as_text.substring(0, 200)}...`);
  
  // Simular procesamiento (para testing realista)
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Parse input para obtener datos del usuario
  let userProfile: any = {};
  try {
    const inputData = JSON.parse(workflow.input_as_text);
    userProfile = inputData.user_profile || {};
  } catch (e) {
    console.warn('No se pudo parsear input, usando valores por defecto');
  }
  
  // Generar un plan de entrenamiento MOCK válido
  const mockTrainingPlan = {
    client_training_program_enriched: {
      title: `Plan de Hipertrofia ${userProfile.main_goal || 'Personalizado'} (MOCK)`,
      summary: `Plan de 4 semanas diseñado para ${userProfile.name || 'el usuario'} basado en perfil y cuestionarios.`,
      weeks: 4,
      sessions_per_week: 4,
      split_type: "upper_lower",
      sessions: [
        {
          id: "session-1",
          name: "Tren Superior - Empuje",
          session_number: 1,
          day: "Lunes",
          focus: ["Fuerza", "Hipertrofia", "Empuje"],
          session_notes: ["Enfoque en técnica perfecta", "No sacrificar forma por peso"],
          warmup: "5-10 min cardio ligero + movilidad articular",
          exercises: [
            {
              name: "Press Banca Barra",
              sets: "4",
              reps: "8-10",
              rest: "90s",
              notes: "Control en excéntrica, 2-0-1 tempo"
            },
            {
              name: "Press Militar con Mancuernas",
              sets: "3",
              reps: "10-12",
              rest: "75s",
              notes: "Mantener core activado"
            },
            {
              name: "Fondos en Paralelas",
              sets: "3",
              reps: "10-12",
              rest: "60s",
              notes: "Con asistencia si es necesario"
            }
          ],
          cooldown: "5 min estiramientos estáticos"
        },
        {
          id: "session-2",
          name: "Tren Inferior - Dominante Rodilla",
          session_number: 2,
          day: "Miércoles",
          focus: ["Fuerza", "Hipertrofia", "Piernas"],
          session_notes: ["Mantener postura neutral", "Profundidad completa en sentadillas"],
          warmup: "5-10 min cardio + activación glúteos",
          exercises: [
            {
              name: "Sentadilla Barra",
              sets: "4",
              reps: "8-10",
              rest: "120s",
              notes: "Profundidad completa, mantener neutro lumbar"
            },
            {
              name: "Prensa 45°",
              sets: "3",
              reps: "12-15",
              rest: "90s",
              notes: "Rango completo de movimiento"
            },
            {
              name: "Zancadas con Mancuernas",
              sets: "3",
              reps: "10 por pierna",
              rest: "60s",
              notes: "Alternar piernas"
            }
          ],
          cooldown: "5 min estiramientos + foam roller"
        }
      ],
      progression_notes: [
        "Aumentar peso cuando puedas completar todas las series en el rango alto de reps",
        "Semana 1-2: Fase de adaptación, enfoque en técnica",
        "Semana 3-4: Incremento de intensidad progresivo"
      ],
      nutrition_integration: {
        pre_workout: "Comida 1-2h antes: carbohidratos + proteína moderada",
        post_workout: "Dentro de 1h: proteína + carbohidratos",
        daily_protein_target: `${userProfile.weight_kg ? Math.round(userProfile.weight_kg * 2) : 160}g aprox`
      },
      recovery_guidelines: [
        "Mínimo 7-8h sueño por noche",
        "2-3 días de descanso activo por semana",
        "Hidratación: 2-3L agua diarios"
      ],
      red_flags: [
        "Si experimentas dolor articular agudo, reduce intensidad",
        "Monitorear fatiga acumulada cada 2 semanas"
      ],
      _metadata: {
        generated_by: "EDN360 Workflow (MOCK)",
        version: "mock-v1.0",
        timestamp: new Date().toISOString()
      }
    }
  };
  
  console.log('✅ Plan MOCK generado correctamente');
  return mockTrainingPlan;
};
