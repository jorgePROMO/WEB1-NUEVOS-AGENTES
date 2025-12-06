import { z } from "zod";

// K1 Abstract Term Schemas
const K1VolumenAbstracto = z.enum(["muy_bajo", "bajo", "medio", "alto", "muy_alto"]);
const K1IntensidadAbstracta = z.enum(["muy_ligera", "ligera", "moderada", "alta", "muy_alta"]);
const K1ProximidadFalloAbstracta = z.enum([
  "muy_lejos_del_fallo",
  "lejos_del_fallo", 
  "moderadamente_cerca_del_fallo",
  "cerca_del_fallo",
  "muy_cerca_o_en_fallo"
]);
const K1DensidadAbstracta = z.enum(["densidad_baja", "densidad_media", "densidad_alta"]);
const K1MetodoEntrenamiento = z.enum([
  "basico",
  "intensificacion_local",
  "intensificacion_sistemica",
  "potencia_pliometria",
  "metabolico",
  "avanzado_carga"
]);

// K1 Pattern (from taxonomy - STRICT)
const K1Patron = z.enum([
  "empuje_horizontal",
  "empuje_vertical",
  "tiron_horizontal",
  "tiron_vertical",
  "dominante_rodilla",
  "dominante_cadera",
  "zancada",
  "core_antirotacion",
  "core_antiextension",
  "core_antiflexion",
  "core_rotacional"
]);

// K1 Exercise Type (from taxonomy - STRICT)
const K1TipoEjercicio = z.enum([
  "compuesto_alta_demanda",
  "compuesto_media_demanda",
  "aislamiento",
  "correctivo_estabilidad",
  "pliometrico",
  "balistico",
  "metabolico_circuito"
]);

// Exercise in Block B (K1-based) - SIMPLIFIED
const E4ExerciseK1 = z.object({
  order: z.number(),
  exercise_id: z.string(), // Reference to catalog
  patron: K1Patron,
  tipo: K1TipoEjercicio,
  volumen_abstracto: K1VolumenAbstracto,
  series_abstracto: z.enum(["bajas", "medias", "altas"]),
  reps_abstracto: z.enum(["bajas", "medias", "altas"]),
  intensidad_abstracta: K1IntensidadAbstracta,
  proximidad_fallo_abstracta: K1ProximidadFalloAbstracta,
  notas_tecnicas: z.string()
  // k1_justification removed to reduce output verbosity
});

// Block B (only block E4 generates)
const E4BlockB = z.object({
  id: z.literal("B"),
  block_name: z.string(), // "Bloque B - Entrenamiento Principal Fuerza"
  primary_muscles: z.array(z.string()),
  secondary_muscles: z.array(z.string()),
  exercises: z.array(E4ExerciseK1),
  volumen_total_bloque: K1VolumenAbstracto,
  densidad: K1DensidadAbstracta,
  metodo_entrenamiento: K1MetodoEntrenamiento
});

// K1 Decisions (for logging/audit)
const K1Decisions = z.object({
  reglas_aplicadas: z.array(z.string()),
  volumen_justificacion: z.string(),
  intensidad_justificacion: z.string(),
  metodos_usados: z.array(K1MetodoEntrenamiento),
  patrones_cubiertos: z.array(K1Patron)
});

// Session
const E4SessionK1 = z.object({
  id: z.string(),
  name: z.string(),
  focus: z.array(z.string()),
  blocks: z.array(E4BlockB), // Only Block B
  core_mobility_block: z.object({ 
    include: z.literal(false), // DEPRECATED - always false
    details: z.literal("") 
  }),
  session_notes: z.array(z.string()),
  k1_decisions: K1Decisions
});

// Main E4 Output Schema (K1-based)
export const E4TrainingPlanGeneratorSchemaK1 = z.object({ 
  training_plan: z.object({ 
    training_type: z.enum(["full_body", "upper_lower", "push_pull_legs", "bro_split", "other"]), 
    days_per_week: z.number(), 
    session_duration_min: z.number(), 
    weeks: z.literal(4), // ALWAYS 4
    goal: z.string(), 
    sessions: z.array(E4SessionK1),
    general_notes: z.array(z.string()) 
  }) 
});
