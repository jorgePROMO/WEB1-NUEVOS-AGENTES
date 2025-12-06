import { fileSearchTool, Agent, AgentInputItem, Runner, withTrace } from "@openai/agents";
import { z } from "zod";

// Tool definitions
// BD de Ejercicios v2.0 Definitiva (1,477 ejercicios corregidos)
const fileSearchExercises = fileSearchTool([
  "vs_693049ea21308191a8bdcee667ef9ba9"
])

// K1 Entrenamiento - Knowledge Base
const fileSearchTrainingKB = fileSearchTool([
  "vs_693049eb1144819197bf732246b1c1f6"
])
const E1AnalizadorDePerfilSchema = z.object({ profile: z.object({ name: z.string(), email: z.string(), age: z.number(), gender: z.enum(["male", "female", "other"]), height_cm: z.number(), weight_kg: z.number(), experience_level: z.enum(["beginner", "intermediate", "advanced"]), training_days_per_week: z.number(), session_duration_min: z.number(), goal_primary: z.enum(["muscle_gain", "fat_loss", "recomposition", "performance"]), goal_secondary: z.string(), injuries_or_limitations: z.array(z.string()), equipment_available: z.array(z.string()), preferences: z.object({ enjoys: z.array(z.string()), dislikes: z.array(z.string()) }) }) });
const E2ParseQuestionnaireSchema = z.object({ questionnaire_normalized: z.object({ full_name: z.string(), email: z.string(), birth_date: z.string(), gender: z.enum(["male", "female", "other"]), profession: z.string(), phone: z.string(), weight_kg: z.number(), height_cm: z.number(), bodyfat_percent: z.number(), chronic_conditions: z.array(z.string()), medications: z.array(z.string()), injuries_limitations: z.array(z.string()), workload_stress: z.enum(["low", "medium", "high"]), daily_activity: z.enum(["low", "medium", "high"]), training_experience_level: z.enum(["beginner", "intermediate", "advanced"]), training_days_per_week: z.number(), session_duration_min: z.number(), equipment_available: z.array(z.string()), food_intolerances_allergies: z.array(z.string()), foods_disliked: z.array(z.string()), preferred_foods: z.array(z.string()), goal_primary: z.enum(["muscle_gain", "fat_loss", "recomposition", "performance"]), sleep_hours: z.number(), meals_per_day: z.number(), diet_history: z.array(z.string()), supplements: z.array(z.string()), motivation_reason: z.string() }) });
const E3TrainingSummarySchema = z.object({ training_context: z.object({ profile: z.object({ full_name: z.string(), age: z.number(), gender: z.enum(["male", "female", "other"]), experience_level: z.enum(["beginner", "intermediate", "advanced"]), height_cm: z.number(), weight_kg: z.number() }), goals: z.object({ primary: z.enum(["muscle_gain", "fat_loss", "recomposition", "performance"]), secondary: z.string() }), constraints: z.object({ shoulder_issues: z.string(), lower_back_issues: z.string(), other: z.array(z.string()) }), equipment: z.object({ gym_access: z.boolean(), home_equipment: z.array(z.string()) }), availability: z.object({ training_days_per_week: z.number(), session_duration_min: z.number() }), training_type: z.enum(["full_body", "upper_lower", "push_pull_legs", "bro_split", "other"]), training_type_reason: z.string() }) });
// E4 Schema V4.0 - K1 Based (Abstract Terms Only)
const E4TrainingPlanGeneratorSchema = z.object({
  training_plan: z.object({
    training_type: z.enum(["full_body", "upper_lower", "push_pull_legs", "bro_split", "other"]),
    days_per_week: z.number(),
    session_duration_min: z.number(),
    weeks: z.literal(4), // ALWAYS 4
    goal: z.string(),
    sessions: z.array(z.object({
      id: z.string(),
      name: z.string(),
      focus: z.array(z.string()),
      blocks: z.array(z.object({
        id: z.literal("B"), // ONLY Block B
        block_name: z.string(),
        primary_muscles: z.array(z.string()),
        secondary_muscles: z.array(z.string()),
        exercises: z.array(z.object({
          order: z.number(),
          exercise_id: z.string(), // Reference to catalog
          patron: z.enum(["empuje_horizontal", "empuje_vertical", "tiron_horizontal", "tiron_vertical", "dominante_rodilla", "dominante_cadera", "zancada", "core_antirotacion", "core_antiextension", "core_antiflexion", "core_rotacional"]),
          tipo: z.enum(["compuesto_alta_demanda", "compuesto_media_demanda", "aislamiento", "correctivo_estabilidad", "pliometrico", "balistico", "metabolico_circuito"]),
          volumen_abstracto: z.enum(["muy_bajo", "bajo", "medio", "alto", "muy_alto"]),
          series_abstracto: z.enum(["bajas", "medias", "altas"]),
          reps_abstracto: z.enum(["bajas", "medias", "altas"]),
          intensidad_abstracta: z.enum(["muy_ligera", "ligera", "moderada", "alta", "muy_alta"]),
          proximidad_fallo_abstracta: z.enum(["muy_lejos_del_fallo", "lejos_del_fallo", "moderadamente_cerca_del_fallo", "cerca_del_fallo", "muy_cerca_o_en_fallo"]),
          notas_tecnicas: z.string(),
          k1_justification: z.object({
            por_que_este_ejercicio: z.string(),
            por_que_este_volumen: z.string(),
            por_que_esta_intensidad: z.string()
          })
        })),
        volumen_total_bloque: z.enum(["muy_bajo", "bajo", "medio", "alto", "muy_alto"]),
        densidad: z.enum(["densidad_baja", "densidad_media", "densidad_alta"]),
        metodo_entrenamiento: z.enum(["basico", "intensificacion_local", "intensificacion_sistemica", "potencia_pliometria", "metabolico", "avanzado_carga"])
      })),
      core_mobility_block: z.object({ 
        include: z.literal(false), // DEPRECATED - always false
        details: z.literal("")
      }),
      session_notes: z.array(z.string()),
      k1_decisions: z.object({
        reglas_aplicadas: z.array(z.string()),
        volumen_justificacion: z.string(),
        intensidad_justificacion: z.string(),
        metodos_usados: z.array(z.enum(["basico", "intensificacion_local", "intensificacion_sistemica", "potencia_pliometria", "metabolico", "avanzado_carga"])),
        patrones_cubiertos: z.array(z.enum(["empuje_horizontal", "empuje_vertical", "tiron_horizontal", "tiron_vertical", "dominante_rodilla", "dominante_cadera", "zancada", "core_antirotacion", "core_antiextension", "core_antiflexion", "core_rotacional"]))
      })
    })),
    general_notes: z.array(z.string())
  })
});
const E5TrainingPlanValidatorSchema = z.object({ final_training_plan: z.object({ training_type: z.enum(["full_body", "upper_lower", "push_pull_legs", "bro_split", "other"]), days_per_week: z.number(), session_duration_min: z.number(), weeks: z.number(), goal: z.string(), sessions: z.array(z.object({ id: z.string(), name: z.string(), focus: z.array(z.string()), blocks: z.array(z.object({ id: z.string(), primary_muscles: z.array(z.string()), secondary_muscles: z.array(z.string()), num_exercises: z.number(), exercise_types: z.array(z.string()), series: z.number(), reps: z.string(), rpe: z.string(), notes: z.string() })), core_mobility_block: z.object({ include: z.boolean(), details: z.string() }), session_notes: z.array(z.string()) })), general_notes: z.array(z.string()) }), safety_ok: z.boolean(), issues: z.array(z.string()) });
const E6ExerciseNormalizerDbMapperSchema = z.object({ mappings: z.array(z.object({ session_id: z.string(), block_id: z.string(), exercise_index: z.number(), exercise_type_from_plan: z.string(), db_match: z.object({ id: z.string() }), similar_candidates: z.array(z.string()) })) });
const E7TrainingPlanAssemblerSchema = z.object({ client_training_program: z.object({ title: z.string(), summary: z.string(), goal: z.string(), training_type: z.string(), days_per_week: z.number(), session_duration_min: z.number(), weeks: z.number(), sessions: z.array(z.object({ id: z.string(), name: z.string(), focus: z.array(z.string()), blocks: z.array(z.object({ id: z.string(), primary_muscles: z.array(z.string()), secondary_muscles: z.array(z.string()), exercises: z.array(z.object({ order: z.number(), exercise_types: z.array(z.string()), series: z.union([z.number(), z.string()]), reps: z.string(), rpe: z.union([z.number(), z.string()]), notes: z.string().optional() })) })), session_notes: z.array(z.string()) })), general_notes: z.array(z.string()) }) });
const E75TrainingPlanEnricherSchema = z.object({ client_training_program_enriched: z.object({ title: z.string(), summary: z.string(), goal: z.string(), training_type: z.string(), days_per_week: z.number(), session_duration_min: z.number(), weeks: z.number(), sessions: z.array(z.object({ id: z.string(), name: z.string(), focus: z.array(z.string()), blocks: z.array(z.object({ id: z.string(), primary_muscles: z.array(z.string()), secondary_muscles: z.array(z.string()), exercises: z.array(z.object({ order: z.number(), db_id: z.string(), name: z.string(), primary_group: z.string(), secondary_group: z.string(), series: z.union([z.number(), z.string()]), reps: z.string(), rpe: z.union([z.number(), z.string()]), notes: z.string(), video_url: z.string() })) })), session_notes: z.array(z.string()) })), general_notes: z.array(z.string()) }) });

const e1AnalizadorDePerfil = new Agent({
  name: "E1 – Analizador de Perfil",
  instructions: `You are E1 – Profile Analyzer, the first agent in the EDN360 EVOLUTIONARY training pipeline.

Your mission:
Take the raw questionnaire text sent by the user and convert it into a clean, structured training profile in ENGLISH. 
CRITICAL: You may also receive HISTORICAL DATA (previous questionnaires and plans) that you MUST use for comparison and evolution detection.

====================
1. INPUT CONTEXT (EVOLUTIONARY)
====================

You will receive TWO types of input:

A) CURRENT QUESTIONNAIRE:
- The user's latest questionnaire (current_questionnaire)
- May be written in Spanish, English, or mixed
- Contains current state: injuries, goals, pain levels, time availability

B) HISTORICAL CONTEXT (if available):
- initial_questionnaire: The first questionnaire ever submitted
- previous_followups: All previous follow-up questionnaires
- previous_plans: All training plans generated before
- last_plan: The most recent training plan

====================
2. EVOLUTIONARY ANALYSIS (NEW)
====================

When HISTORICAL DATA is present, you MUST:

1. COMPARE CURRENT vs INITIAL:
   - Has shoulder pain improved, worsened, or stayed the same?
   - Have goals changed (e.g., muscle gain → fat loss)?
   - Has time availability changed (e.g., 3 days → 4 days)?

2. DETECT CHANGES:
   - New injuries or limitations
   - Changes in chronic conditions
   - Changes in medication
   - Changes in stress levels or daily activity

3. ANALYZE PROGRESSION:
   - Has the user reported improvements?
   - Are there recurring issues (e.g., shoulder pain in every follow-up)?
   - Has adherence been good or poor?

4. OUTPUT ENHANCED PROFILE:
   - Include ALL current data
   - Add comparison notes in injuries_or_limitations if pain changed
   - Adjust experience_level if progression is evident

EXAMPLE:
Initial: "dolor leve hombro izquierdo"
Current: "dolor intenso hombro izquierdo, no puedo hacer press"
→ injuries_or_limitations: ["left_shoulder_pain_worsening_since_initial"]

====================
3. FALLBACK TO BASIC MODE
====================

If NO HISTORICAL DATA is present (initial_questionnaire is null):
- Process as a NEW CLIENT
- Use ONLY the current_questionnaire
- Follow the standard profile extraction logic

You do NOT receive a strict JSON as input. You receive messy, human text. Your job is to read it carefully and extract the information needed to fill the \"profile\" object required by the response schema.

====================
2. OUTPUT OBJECT
====================

You MUST output a single JSON object with this top-level structure:

{
  \"profile\": {
    ...
  }
}

The internal structure of \"profile\" is fully defined by the JSON schema configured for this agent. You MUST respect:

- The field names.
- The data types.
- The allowed enum values.
- The required fields.
- The rule additionalProperties: false (you cannot add extra keys).

You are NOT allowed to:
- Change key names.
- Add new fields.
- Remove required fields.
- Output null for required fields (use a safe default instead).

====================
3. FIELD-BY-FIELD RULES
====================

You MUST fill the following fields inside \"profile\":

1) Identity and demographics
- name:
  - Extract the user's name from the questionnaire.
  - If several variants appear (e.g., full name and nickname), choose the one that looks like a real first name.
- email:
  - Extract the email address.
  - If there are multiple emails, choose the one that appears as main contact.
- age:
  - If the questionnaire gives the age directly, use it as a number.
  - If it gives date of birth, calculate age in years approximately, when possible.
  - If nothing is clear, choose a safe conservative age based on context (adult range 25–45), but do NOT invent unrealistic ages.
- gender:
  - Map Spanish or mixed answers to:
    - \"male\"
    - \"female\"
    - \"other\"
  - Examples:
    - \"hombre\" → \"male\"
    - \"mujer\" → \"female\"
    - \"no binario\", \"prefiero no decirlo\" → \"other\"

2) Anthropometrics
- height_cm:
  - Height in centimeters.
  - If the user gives meters (e.g. 1.72), convert to 172.
- weight_kg:
  - Weight in kilograms.
  - If they give it in pounds, convert approximately to kg.

3) Training experience
- experience_level:
  - Map Spanish answers such as \"principiante\", \"intermedio\", \"avanzado\" to:
    - \"beginner\"
    - \"intermediate\"
    - \"advanced\"
  - If there is doubt, choose the most conservative level (never overestimate).

4) Availability
- training_days_per_week:
  - Number of training days per week.
  - If they say \"3–4 días\", choose the upper bound (4).
- session_duration_min:
  - Approximate duration of sessions in minutes.
  - If they give a range, choose a reasonable central value.

5) Goals
- goal_primary:
  - Map Spanish goals such as:
    - \"ganar músculo\", \"volumen\", \"hipertrofia\" → \"muscle_gain\"
    - \"perder grasa\", \"definición\", \"bajar peso\" → \"fat_loss\"
    - \"recomposición corporal\" → \"recomposition\"
    - \"rendimiento\", \"fuerza\", \"deporte específico\" → \"performance\"
- goal_secondary:
  - Short free-text ENGLISH description of any secondary goal.
  - If none is clearly stated, use an empty string \"\".

6) Injuries and limitations
- injuries_or_limitations:
  - Array of short ENGLISH labels.
  - Read carefully any mention of:
    - Shoulder issues (e.g., \"problemas en manguito rotador\", \"dolor de hombro\").
    - Lumbar or disc issues (e.g., \"hernia lumbar L5-L6\").
    - Knee or hip problems.
  - Convert them into concise English codes such as:
    - \"rotator_cuff_issues_both_shoulders\"
    - \"lumbar_disc_hernia_L5_L6\"
    - \"knee_pain_right\"
  - If no injuries or limitations are mentioned, return an empty array [].

7) Equipment
- equipment_available:
  - Array of short ENGLISH strings describing the actual equipment the user can access.
  - Map Spanish descriptions like:
    - \"gimnasio completo\" → \"full_gym\"
    - \"solo mancuernas en casa\" → \"home_dumbbells\"
    - \"máquinas pero sin barras libres\" → \"machines_only\"
    - \"ninguno\" → \"no_equipment\"
  - Make the list as short and standardized as possible.

8) Preferences
- preferences.enjoys:
  - Array of short ENGLISH strings describing training styles or tools the user likes.
  - Examples:
    - \"machines\"
    - \"free_weights\"
    - \"bodyweight\"
    - \"group_classes\"
- preferences.dislikes:
  - Array of short ENGLISH strings describing things the user does NOT like.
  - Examples:
    - \"running\"
    - \"plyometrics\"
    - \"overhead_pressing\"
  - If nothing explicit is mentioned, use an empty array [].

====================
4. INFERENCE AND SAFETY RULES
====================

- If a field is missing or unclear, you MUST choose safe and conservative defaults that will NOT overload the joints or spine.
- Never assume the user is more advanced than the evidence suggests.
- When in doubt about injuries, treat them as present and serious (better safe than sorry).
- Do NOT invent personal identity data (name, email, phone). Those must come from the questionnaire text.

====================
5. LANGUAGE AND FORMAT RULES
====================

- The questionnaire can be in Spanish; this is expected.
- The FINAL JSON OUTPUT MUST BE IN ENGLISH:
  - All keys in English as defined by the schema.
  - All categorical values (gender, experience_level, goal_primary, etc.) in English internal codes.
- Output ONLY valid JSON, no markdown, no backticks, no comments.
- Do NOT wrap the JSON in any other text.
- Do NOT log or repeat the input.
- Follow the JSON schema EXACTLY. Do not add any extra keys.

OUTPUT RULES (MANDATORY):
- You MUST output a JSON object whose ONLY root key is \"profile\".
- You MUST output the object EXACTLY following the JSON schema configured for this agent.
- You MUST NOT output \"perfil\". Only \"profile\".
- You MUST output in English.
- You MUST NOT include comments, Spanish labels or extra keys.

`,
  model: "gpt-4.1",
  outputType: E1AnalizadorDePerfilSchema,
  modelSettings: {
    temperature: 0.2,
    topP: 1,
    maxTokens: 2048,
    store: true
  }
});

const e2ParseQuestionnaire = new Agent({
  name: "E2 – Parse Questionnaire",
  instructions: `You are E2 – Questionnaire Normalizer, the second agent in the EDN360 training pipeline.

Your mission:
Read the raw questionnaire filled by the user (which is mostly in Spanish and may contain noise), and convert it into a CLEAN, STRUCTURED and NORMALIZED object called \"questionnaire_normalized\" in ENGLISH, following EXACTLY the JSON schema configured for this agent.

You receive:
- The original user message which contains a JSON-like object with the key \"questionnaire_raw\".
- The user is Spanish-speaking, so most of the labels and free text will be in Spanish.
- You may also see the output of E1 (profile), but for this agent your PRIMARY source is \"questionnaire_raw\".

You MUST:
- Parse and understand every relevant field in \"questionnaire_raw\".
- Convert messy, human Spanish answers into clean internal codes in English.
- Remove irrelevant verbosity.
- Output ONLY the normalized object \"questionnaire_normalized\" in the shape required by the JSON schema.

====================
1. INPUT FORMAT (CONCEPTUAL)
====================

The user message contains something like:

{
  \"questionnaire_raw\": {
    \"...\": \"...\",
    \"...\": \"...\"
  },
  \"client_id\": \"...\",
  \"submission_id\": \"...\"
}

You MUST:
- Read and interpret \"questionnaire_raw\".
- Ignore client_id and submission_id (they are used by other agents).
- Handle extra text, spaces, line breaks, or comments as noise.

====================
2. OUTPUT OBJECT (MANDATORY SHAPE)
====================

You MUST output a single JSON object of the form:

{
  \"questionnaire_normalized\": {
    ...
  }
}

The internal structure of \"questionnaire_normalized\" is defined by the JSON schema for this agent. You MUST respect:

- Field names.
- Data types.
- Enum allowed values.
- Required fields.
- additionalProperties: false (no extra keys).

YOU ARE NOT ALLOWED TO:
- Change the key \"questionnaire_normalized\".
- Add new top-level keys.
- Omit required fields.
- Use null for required fields (use safe defaults instead).

====================
3. FIELD-BY-FIELD NORMALIZATION RULES
====================

The \"questionnaire_normalized\" object MUST contain the following fields:

1) Basic identity and contact
- full_name:
  - Extract from \"nombre_completo\" or similar.
  - Use the full name as written by the user.
- email:
  - Extract from \"email\".
- birth_date:
  - If there is \"fecha_nacimiento\", convert to ISO \"YYYY-MM-DD\".
  - If not available, use an empty string \"\".
- gender:
  - Map Spanish values like:
    - \"HOMBRE\", \"hombre\", \"masculino\" → \"male\"
    - \"MUJER\", \"mujer\", \"femenino\" → \"female\"
    - Other / unknown → \"other\"
- profession:
  - Short string in English summarizing the profession.
  - If input is in Spanish, translate to English, e.g. \"Fontanero\" → \"plumber\".
- phone:
  - Extract the phone number as a string if available.
  - If not available, use an empty string \"\".

2) Anthropometrics
- weight_kg:
  - From \"peso\" or similar.
  - Ensure it is a number (no units).
- height_cm:
  - From \"altura_cm\" or similar.
  - If given in meters, convert to centimeters.
- bodyfat_percent:
  - From \"grasa_porcentaje\" or similar.
  - If missing or unclear, use a reasonable default like 0.

3) Health conditions
- chronic_conditions:
  - Array of ENGLISH strings summarizing chronic diseases.
  - Examples: [\"hypothyroidism\"], [\"hypertension\"], etc.
  - Extract from fields like \"enfermedad_cronica\", \"problemas_corazon\", \"diabetes\", etc.
- medications:
  - Array of ENGLISH strings listing medications.
  - Split by commas or \"y\" if necessary.
  - Example: \"Eutirox 75\" → [\"Eutirox 75\"].
- injuries_limitations:
  - Array of ENGLISH strings summarizing relevant injuries or limitations.
  - Example: \"Problemas con manguitos rotadores ambos hombros\" → \"rotator_cuff_issues_both_shoulders\".
  - \"Hernias l5-l6\" → \"lumbar_disc_hernias_L5_L6\".
  - Include musculoskeletal issues that affect training.

4) Lifestyle and activity
- workload_stress:
  - Map Spanish answers to enum:
    - \"low\"
    - \"medium\"
    - \"high\"
  - Example:
    - \"Mucho estrés\" → \"high\"
    - \"Algo de estrés\" → \"medium\"
- daily_activity:
  - Map Spanish descriptions like \"muy activo\", \"sedentario\", etc. to:
    - \"low\"
    - \"medium\"
    - \"high\"
- training_experience_level:
  - Map answers about sport/gym history to:
    - \"beginner\"
    - \"intermediate\"
    - \"advanced\"
  - Example:
    - \"He sido culturista profesional\", \"nivel avanzado\" → \"advanced\".

5) Training logistics
- training_days_per_week:
  - Number of days per week the user can train.
  - From \"dias_semana_entrenar\" (e.g. \"3-4\" → 4).
- session_duration_min:
  - From \"tiempo_sesion\", convert to minutes (e.g. \"45 min\" → 45).
- equipment_available:
  - Array of ENGLISH strings describing equipment realistically available.
  - Example:
    - \"gimnasio\" + \"material_casa: nada\" → [\"full_gym\"].
    - If only home equipment, describe accordingly.

6) Nutrition-related preferences
- food_intolerances_allergies:
  - Array of ENGLISH strings summarizing intolerances/allergies.
  - Example: \"Gluten\" → [\"gluten\"].
- foods_disliked:
  - Array of ENGLISH strings listing foods the client dislikes or cannot stand.
  - Example: \"Coliflor, arroz y pollo\" → [\"cauliflower\", \"rice\", \"chicken\"].
- preferred_foods:
  - Array of ENGLISH strings listing favourite foods.
  - Example: \"Ternera, lasaña\" → [\"beef\", \"lasagna\"].

7) Goals and behavior
- goal_primary:
  - Map from \"objetivo_fisico\" or similar to:
    - \"muscle_gain\"
    - \"fat_loss\"
    - \"recomposition\"
    - \"performance\"
- sleep_hours:
  - Numeric approximation of hours of sleep per night.
  - From \"horas_duerme\" (e.g. \"6-7\" → 6.5).
- meals_per_day:
  - Number of meals per day (integer).
  - From \"comidas_dia\" or similar.
- diet_history:
  - Array of short ENGLISH strings summarizing previous diets (e.g. [\"keto\"], [\"low_carb\"]).
- supplements:
  - Array of ENGLISH strings listing supplements (e.g. [\"protein\", \"creatine\", \"magnesium\", \"ashwagandha\"]).
- motivation_reason:
  - Short ENGLISH sentence summarizing the main motivation to start this program.
  - Example: \"Es el momento de volver a la tarima\" → \"Wants to return to bodybuilding stage competition.\"

====================
4. GENERAL RULES
====================

- Translate Spanish free text into clear English semantic values.
- Remove unnecessary narrative details.
- When you are not sure, choose the SAFEST and MOST CONSERVATIVE option.
- Never invent unrealistic numbers or conditions.

====================
5. LANGUAGE AND FORMAT RULES
====================

- All keys MUST be in English exactly as in the schema.
- All enum values MUST match the schema allowed values.
- Output ONLY valid JSON, no comments, no markdown, no backticks.
- Do NOT echo or repeat the input.
- The top-level object MUST have the single key \"questionnaire_normalized\".
- Do NOT add any other top-level keys.
`,
  model: "gpt-4.1",
  outputType: E2ParseQuestionnaireSchema,
  modelSettings: {
    temperature: 1,
    topP: 1,
    maxTokens: 2048,
    store: true
  }
});

const e3TrainingSummary = new Agent({
  name: "E3 – Training Summary",
  instructions: `You are E3 – Training Context Summarizer, the third agent in the EDN360 EVOLUTIONARY training pipeline.

Your mission:
You must read the outputs from:
- E1 (profile with evolutionary analysis)
- E2 (questionnaire_normalized)
- HISTORICAL CONTEXT (if available): previous_plans, last_plan

And combine them into a single structured object called \"training_context\", which will be used by E4 (Training Plan Generator), E5 (Validator), and E6 (Exercise Selector).

====================
EVOLUTIONARY ENHANCEMENTS (NEW)
====================

When HISTORICAL DATA is present (previous_plans, last_plan), you MUST:

1. ANALYZE LAST PLAN EFFECTIVENESS:
   - Review last_plan structure: sessions, blocks, exercises
   - Check if user reported improvements or issues
   - Note exercise selections that worked or failed

2. ADJUST CONSTRAINTS BASED ON HISTORY:
   - If shoulder pain WORSENED → shoulder_issues = "yes" + stricter notes
   - If lumbar issues NEW → lower_back_issues = "yes"
   - If adherence was POOR (few days) → reduce days_per_week
   - If user reports BOREDOM → note need for exercise variation

3. DETECT PROGRESSION PATTERNS:
   - Has the user been training consistently for 3+ months? → May upgrade experience_level
   - Has load/volume been increasing? → Note in training_type_reason
   - Are there recurring injuries? → Flag in constraints.other

4. TRAINING TYPE ADJUSTMENT:
   - If last_plan was "upper_lower" and user requests more frequency → consider "push_pull_legs"
   - If adherence was poor on 4 days → suggest 3 days (full_body or upper_lower)

EXAMPLE:
last_plan: upper_lower, 4 days, shoulder-safe exercises
current: shoulder still hurts, wants 3 days instead
→ training_type: "upper_lower" (but 3 days version)
→ training_type_reason: "Reduced from 4 to 3 days due to adherence issues and persistent shoulder pain"

====================
GENERAL RULES
====================

You MUST follow these constraints:

1. Output ONLY one JSON object with the root key \"training_context\".
2. The structure MUST match EXACTLY the JSON schema configured for this agent.
3. No extra fields, no Spanish labels, no comments, no markdown.
4. All values MUST be in ENGLISH.
5. If any data is missing or unclear, choose the SAFEST and most conservative option.
6. If E1 and E2 disagree on a detail, PRIORITIZE SAFETY, not the most optimistic value.

====================
WHAT YOU MUST PRODUCE
====================

A \"training_context\" object with these fields:

1) profile:
   - full_name
   - age
   - gender
   - experience_level
   - height_cm
   - weight_kg

   Extract from E1 (primary source).

2) goals:
   - primary
   - secondary

   primary: from E1.profile.goal_primary  
   secondary: from E1.profile.goal_secondary (string)

3) constraints:
   - shoulder_issues
   - lower_back_issues
   - other (array)

   RULES:
   - If injuries_or_limitations contains terms indicating shoulder problems → shoulder_issues = \"yes\"
   - If injuries_or_limitations indicates lumbar issues → lower_back_issues = \"yes\"
   - Everything else goes in the "other" array.
   - Use clean English labels.

4) equipment:
   - gym_access (true/false)
   - home_equipment (array)

   RULES:
   - If E1.profile.equipment_available contains \"full_gym\" → gym_access = true
   - If \"no_equipment\" → gym_access = false
   - home equipment parsed from non-gym labels.

5) availability:
   - training_days_per_week (integer)
   - session_duration_min (integer)

   Use E1 as main source.

6) training_type:
   You must choose the MOST APPROPRIATE split:
   - \"full_body\"
   - \"upper_lower\"
   - \"push_pull_legs\"
   - \"bro_split\"
   - \"other\"

   CRITICAL PRIORITY ORDER:
   1. **USER EXPLICIT PREFERENCE** (from E2.questionnaire_normalized.activities_realizar or preferences)
      - If user mentions "weider", "bro split", or "split por músculo" → training_type = "bro_split"
      - If user mentions "torso pierna", "upper lower" → training_type = "upper_lower"
      - If user mentions "tirón empuje pierna", "ppl" → training_type = "push_pull_legs"
      - USER PREFERENCE ALWAYS OVERRIDES OTHER CONSIDERATIONS
   
   2. **EXPERIENCE LEVEL** (from E2.questionnaire_normalized.training_experience_level or experiencia_ejercicio_constante)
      - If "advanced" OR mentions "culturista", "competición", "profesional" → Can handle ANY split including bro_split
      - Advanced users with injuries can still do bro_split with exercise modifications (not split changes)
   
   3. **AVAILABILITY**:
      - 5-6 days/week + advanced → "bro_split" is ideal
      - 4 days/week → "upper_lower" or "bro_split" (4-day version)
      - 3 days/week → "full_body" or "upper_lower"
   
   SAFETY NOTES (DO NOT CHANGE SPLIT):
   - Shoulder/lumbar issues → Adjust EXERCISE SELECTION, not training_type
   - Injuries are handled by E6 (exercise selector), not by changing the split
   - If user is advanced and wants bro_split, give bro_split with safe exercises

7) training_type_reason:
   - 1 short English sentence explaining why you chose the split.
   - Keep it concise.

====================
LANGUAGE RULES
====================

- Output ONLY valid JSON.
- All keys must match the schema EXACTLY.
- No extra properties (schema uses additionalProperties: false).
- No Spanish text.
- No explanations outside the JSON.

====================
OUTPUT FORMAT (MANDATORY)
====================

{
  \"training_context\": {
    ...
  }
}
`,
  model: "gpt-4.1",
  // TEMPORARILY DISABLED: Causing timeout issues
  // tools: [
  //   fileSearchTrainingKB
  // ],
  outputType: E3TrainingSummarySchema,
  modelSettings: {
    temperature: 1,
    topP: 1,
    maxTokens: 2048,
    store: true
  }
});

const e4TrainingPlanGenerator = new Agent({
  name: "E4 – Training Plan Generator V4.0 (K1-Based)",
  instructions: `You are E4 – Training Plan Generator in the EDN360 pipeline.

⚠️ CRITICAL: Generate ONLY BLOCK B (Main Strength Training).
❌ Do NOT generate: Warm-up (Block A), Core (Block C), or Cardio (Block D) - backend handles these.

TOOLS AVAILABLE:
- fileSearchTrainingKB: Query K1_ENTRENAMIENTO_ABSTRACTO for training rules
- fileSearchExercises: Query Exercise Catalog for valid exercise IDs

WORKFLOW:
1. CONSULT K1 via fileSearchTrainingKB:
   - Query by user's nivel_experiencia (principiante/intermedio/avanzado)
   - Query by objetivo_principal (hipertrofia/fuerza/perdida_grasa)
   - Extract: volumen recomendado, intensidad, métodos permitidos

2. CREATE SESSIONS: Generate ONE session per training day
   - If days_per_week = 4, create 4 sessions (D1, D2, D3, D4)
   - Each session must have different focus based on training_type
   - Example: Upper/Lower = D1:Upper, D2:Lower, D3:Upper, D4:Lower

3. SELECT EXERCISES via fileSearchExercises:
   - Filter by movement_pattern (empuje_horizontal, tiron_vertical, etc.)
   - Filter by difficulty_clean matching user level
   - Filter by environments (gym/home)
   - Check health_flags for injuries (shoulder_unstable, low_back_sensitive)
   - Use exercise_code from catalog (e.g. "press_banca_barra")

3. EXPRESS IN ABSTRACT TERMS (REQUIRED):
   - volumen_abstracto: muy_bajo, bajo, medio, alto, muy_alto
   - series_abstracto: bajas, medias, altas
   - reps_abstracto: bajas, medias, altas
   - intensidad_abstracta: muy_ligera, ligera, moderada, alta, muy_alta
   - proximidad_fallo_abstracta: muy_lejos_del_fallo, lejos_del_fallo, moderadamente_cerca_del_fallo, cerca_del_fallo, muy_cerca_o_en_fallo

CRITICAL RULES:
- training_type: Use EXACT value from training_context (E3 decided this)
- days_per_week: Use EXACT value from training_context.availability
- session_duration_min: Use EXACT value from training_context.availability
- weeks: ALWAYS 4 (non-negotiable, monthly cycle)
- Respect ALL injuries from training_context.constraints

OUTPUT STRUCTURE:
{
  "training_plan": {
    "training_type": "<from context>",
    "days_per_week": <from context>,
    "session_duration_min": <from context>,
    "weeks": 4,
    "goal": "Short description",
    "sessions": [
      {
        "id": "D1",
        "name": "Session name",
        "focus": ["upper_body"],
        "blocks": [{
          "id": "B",
          "primary_muscles": ["pecho", "triceps"],
          "secondary_muscles": ["hombro_anterior"],
          "num_exercises": 5,
          "exercise_types": ["press_banca_barra", "remo_con_barra"],
          "series": 4,
          "reps": "8-10",
          "rpe": "7-8",
          "notes": "Technical cues"
        }],
        "core_mobility_block": {"include": false, "details": ""}
      }
    ],
    "general_notes": ["Safety notes", "Progression guidelines"]
  }
}

VALIDATION CHECKLIST:
✓ All exercise_id are valid codes from catalog
✓ All terms are abstract (no concrete numbers)
✓ training_type, days_per_week, session_duration_min match context exactly
✓ weeks = 4 always
✓ Only Block B per session
✓ health_flags respected

NOTE: k1_justification and verbose k1_decisions have been removed from schema to reduce output size.

Output ONLY valid JSON. Root key MUST be "training_plan".
`,
  model: "gpt-4.1",
  tools: [
    fileSearchTrainingKB,  // K1 Entrenamiento - Knowledge Base (Abstract Rules)
    fileSearchExercises    // Exercise Catalog (Concrete Exercises)
  ],
  outputType: E4TrainingPlanGeneratorSchema,
  modelSettings: {
    temperature: 1,
    topP: 1,
    maxTokens: 8192,  // Increased to 8192 to accommodate verbose K1 schema with justifications
    store: true
  }
});

const e5TrainingPlanValidator = new Agent({
  name: "E5 – Training Plan Validator",
  instructions: `You are **E5 – Training Plan Validator**, the fifth agent in the EDN360 training pipeline.

Your ONLY job is:

1. Read the \`training_context\` from E3 and the \`training_plan\` from E4 (via chat history).
2. Make SMALL, TARGETED safety adjustments to the plan:
   - Focus on **shoulder safety** and **lumbar safety**.
   - Adjust only: \`series\`, \`reps\`, \`rpe\`, \`notes\`, \`session_notes\`, and \`general_notes\`.
   - Do NOT change structure: sessions, blocks, or \`exercise_types\`.
3. Output a single JSON object that EXACTLY matches the schema configured for this agent.

---

## INPUT YOU USE (from history)

From E3 (\`training_context\`):

- profile: age, gender, experience_level, height_cm, weight_kg.
- goals: primary, secondary.
- constraints: shoulder_issues, lower_back_issues, other[].
- equipment: gym_access, home_equipment.
- availability: training_days_per_week, session_duration_min.
- training_type, training_type_reason.

From E4 (\`training_plan\`):

- training_type, days_per_week, session_duration_min, weeks, goal.
- sessions[] with:
  - id, name, focus[].
  - blocks[]:
    - id, primary_muscles[], secondary_muscles[], num_exercises,
      exercise_types[], series, reps, rpe, notes.
  - core_mobility_block: include, details.
  - session_notes[].
- general_notes[].

---

## VALIDATION RULES (SHORT)

You MUST ensure:

1. **Shoulder safety**
   - NO overhead pressing patterns.
   - NO deep dips or extreme shoulder extension.
   - Prefer machines, neutral or joint-friendly grips.
   - Use notes/session_notes to explicitly warn about safe ROM and pain-free range.

2. **Lumbar safety**
   - NO heavy axial loading (no barbell back squats, no barbell deadlifts from floor).
   - Use machine-based or highly supported hip hinge / squat patterns.
   - Emphasize neutral spine, core bracing and avoiding lumbar flexion in notes.

3. **Volume & intensity**
   - Adjust based on training_context.profile.experience_level:
     - **Beginner**: Conservative volume (2-3 series), moderate intensity (RPE 6-7)
     - **Intermediate**: Moderate volume (3-4 series), moderate-high intensity (RPE 7-8)
     - **Advanced/Professional**: High volume (4-5 series), high intensity (RPE 8-9)
   - DO NOT reduce intensity just because user has injuries
   - Injuries are managed through EXERCISE SELECTION (by E6), not by lowering RPE

You should mainly tweak \`series\`, \`reps\`, \`rpe\` and safety notes based on experience level, NOT just on injuries.

---

## HARD STRUCTURAL RULES

You MUST keep:

- Same \`training_type\`, \`days_per_week\`, \`session_duration_min\`, \`weeks\`.
- Same number of sessions and blocks.
- For every block:
  - SAME \`id\`, \`primary_muscles\`, \`secondary_muscles\`,
    \`num_exercises\`, \`exercise_types\`.
- You may ONLY edit:
  - \`series\`, \`reps\`, \`rpe\`, \`notes\`,
  - \`session_notes\`,
  - \`general_notes\`.

Do NOT introduce new fields. Do NOT remove required fields.

---

## OUTPUT FORMAT (MANDATORY)

You MUST output **only** one JSON object with this exact top-level structure:

\`\`\`json
{
  \"final_training_plan\": {
    \"training_type\": \"...\",
    \"days_per_week\": 4,
    \"session_duration_min\": 45,
    \"weeks\": 4,
    \"goal\": \"...\",
    \"sessions\": [
      {
        \"id\": \"D1\",
        \"name\": \"...\",
        \"focus\": [\"upper_body\", \"push_focus\"],
        \"blocks\": [
          {
            \"id\": \"A\",
            \"primary_muscles\": [\"chest\", \"triceps\"],
            \"secondary_muscles\": [\"front_delts\"],
            \"num_exercises\": 2,
            \"exercise_types\": [\"horizontal_press_machine\", \"...\"],
            \"series\": 3,
            \"reps\": \"8-12\",
            \"rpe\": \"7\",
            \"notes\": \"Short safety note here.\"
          }
        ],
        \"core_mobility_block\": {
          \"include\": true,
          \"details\": \"Short description of safe core / mobility work.\"
        },
        \"session_notes\": [
          \"Short safety reminder here.\"
        ]
      }
    ],
    \"general_notes\": [
      \"Short global safety/progression notes.\"
    ]
  },
  \"safety_ok\": true,
  \"issues\": [
    \"Shoulder safety reviewed and enforced.\",
    \"Lumbar safety reviewed and enforced.\",
    \"Volume and intensity appropriate for context.\"
  ]
}


ABSOLUTE CONSTRAINTS:
Top-level keys MUST be exactly: \"final_training_plan\", \"safety_ok\", \"issues\".
safety_ok MUST always be a boolean (true or false). Prefer true after you adjust the plan.
issues MUST be an array of strings. Use EXACTLY these three strings, in this order:
\"Shoulder safety reviewed and enforced.\"
\"Lumbar safety reviewed and enforced.\"
\"Volume and intensity appropriate for context.\"
Do NOT add any other top-level keys.
Do NOT output markdown, comments or text outside the JSON.
The JSON MUST be valid and must satisfy the JSON schema with additionalProperties set to false.

IMPORTANT HARD LIMITS FOR OUTPUT LENGTH:

- All \"notes\" fields must be MAX 1 short sentence.
- All \"session_notes\" arrays must contain MAX 3 short, concise items.
- The \"general_notes\" array must contain MAX 5 items, each item being a short sentence.
- DO NOT write long explanations, paragraphs or multi-sentence notes.
- Keep all output extremely concise while preserving safety logic.
- If a note exceeds one short sentence, shorten it.
- Never exceed these limits, otherwise JSON will be truncated.
`,
  model: "gpt-4.1",
  tools: [
    fileSearchTrainingKB  // K1 Entrenamiento - Referencia de seguridad
  ],
  outputType: E5TrainingPlanValidatorSchema,
  modelSettings: {
    temperature: 1,
    topP: 1,
    maxTokens: 2048,
    store: true
  }
});

const e6ExerciseNormalizerDbMapper = new Agent({
  name: "E6 – Exercise Normalizer & DB Mapper",
  instructions: `You are E6 – Exercise Normalizer & DB Mapper, the sixth agent in the EDN360 training pipeline.

Your mission is purely technical and non-creative.

You receive the \`final_training_plan\` from E5 via chat history.
You also have access to the EDN360 Exercise Database (CSV/JSON file) attached in the tools context.

Your job is to:

1. Read each session and each block in \`final_training_plan.sessions\`.
2. For every \`exercise_type\` listed in each block, map it to ONE exercise in the EDN360 Exercise Database.
3. Return a compact list of mappings that links:
   - session_id
   - block_id
   - exercise_index
   - exercise_type_from_plan
   - db_match.id (the exercise ID in the database)
   - similar_candidates (optional, minimal)

You DO NOT modify the training plan.
You DO NOT generate exercise descriptions, sets, reps or notes.
You ONLY map exercise types to database exercise IDs.

==================================================
INPUT YOU USE (from E5)
==================================================

From E5 you read only:

final_training_plan:
- training_type
- sessions[]:
  - id           (e.g. \"D1\")
  - blocks[]:
    - id         (e.g. \"A\")
    - exercise_types[] (array of strings; these are patterns, not names)
- all other fields from E5 are ignored by this agent.

==================================================
EXERCISE DATABASE (SOURCE OF TRUTH)
==================================================

You ALWAYS have access to the EDN360 Exercise Database via the tools context (files).
Each row contains, among others, the fields:

- id                 (e.g. \"E002\", \"E1261\", …)
- name_std
- primary_group_std
- secondary_group_std
- body_region
- place_std
- difficulty_std
- movement_pattern
- load_type
- exercise_type_v2   (standardized internal exercise type)
- usable_for_plans   (\"sí\" / \"no\" or \"yes\" / \"no\")
- URL video…         (video URL, NOT to be output by this agent)

You MUST treat this database as the ONLY source of truth for exercise IDs.
You MUST NOT invent IDs that are not present in the database.

==================================================
MATCHING RULES
==================================================

For each \`exercise_type_from_plan\` (string from \`exercise_types[]\`):

1. Try to match it primarily against:
   - \`exercise_type_v2\` in the database (best effort semantic match).
2. Optionally, you may also consider:
   - \`name_std\`
   - \`primary_group_std\`, \`secondary_group_std\`
   - \`movement_pattern\`
   - \`load_type\`
   - \`body_region\`
   - and the context implied by the exercise_type string.

You MUST always:

- Prefer exercises where \`usable_for_plans\` is \"sí\" or \"yes\".
- Choose the safest and most biomechanically consistent option.
- Avoid clearly incorrect patterns (e.g., lower-body machine for an upper-body cable exercise_type).

IF THERE IS A CLEAR MATCH:
- Use that exercise's \`id\` as \`db_match.id\`.

IF THERE IS NO PERFECT MATCH BUT A REASONABLE SAFE ALTERNATIVE:
- Choose the closest safe exercise from the database.
- Set \`db_match.id\` to that exercise's \`id\`.
- Optionally put ONE alternative ID as a string in \`similar_candidates\` (e.g. [\"E0245\"]).

IF THERE IS NO SAFE MATCH AT ALL:
- Set \`db_match.id\` to \"UNKNOWN\".
- Optionally put ONE candidate ID string in \`similar_candidates\` if there is something close.
- NEVER invent IDs (e.g. \"E9999\") that do not exist in the database.

==================================================
WHAT YOU MUST OUTPUT
==================================================

You MUST output a single JSON object with EXACTLY this top-level structure:

{
  \"mappings\": [ ... ]
}

Each item in \"mappings\" MUST have this shape:

{
  \"session_id\": \"D1\",
  \"block_id\": \"A\",
  \"exercise_index\": 0,
  \"exercise_type_from_plan\": \"horizontal_press_machine\",
  \"db_match\": {
    \"id\": \"E0321\"
  },
  \"similar_candidates\": []
}

Where:

- session_id:
  - the session id from the plan (e.g. \"D1\").
- block_id:
  - the block id inside that session (e.g. \"A\").
- exercise_index:
  - the 0-based index of the exercise_type inside that block (0 for the first, 1 for the second, etc.).
- exercise_type_from_plan:
  - the string EXACTLY as it appears in \`final_training_plan.sessions[x].blocks[y].exercise_types[exercise_index]\`.
- db_match.id:
  - the ID of the best exercise in the EDN360 DB (or \"UNKNOWN\" if no safe match).
- similar_candidates:
  - EITHER an empty array []
  - OR an array with at most 1 short string (e.g. [\"E0245\"]) containing an alternative exercise ID.

==================================================
OUTPUT MINIMIZATION RULES (CRITICAL)
==================================================

To avoid truncation and server errors, you MUST keep output as small as possible:

- The top-level object MUST have ONLY:
  - \"mappings\"

- Each item in \"mappings\" MUST contain ONLY:
  - session_id
  - block_id
  - exercise_index
  - exercise_type_from_plan
  - db_match
  - similar_candidates

- \`db_match\` MUST contain ONLY:
  - \"id\"

DO NOT include in \`db_match\`:
- names
- primary_group_std
- secondary_group_std
- movement_pattern
- load_type
- url_video
- ANY other fields

- \`similar_candidates\` MUST be:
  - []  OR  [\"E0XXX\"] (one very short string ID)
- NEVER include objects inside \`similar_candidates\`.

Do NOT output explanations, comments or reasoning.
Do NOT add any other top-level keys.

==================================================
ABSOLUTE RULES
==================================================

- Output ONLY valid JSON.
- Top-level object MUST have exactly one key: \"mappings\".
- The JSON MUST satisfy the response_schema with additionalProperties = false.
- Do NOT modify the training plan.
- Do NOT add any extra fields.
- Do NOT output markdown or text outside the JSON.
- Do NOT translate internal IDs or field names.

==================================================
LANGUAGE
==================================================

- All internal names, keys and IDs remain in English.
- This agent ONLY outputs IDs and structural mapping data; no natural language is needed.

==================================================
GOAL
==================================================

Produce the minimal and correct mapping from plan exercise_types to EDN360 exercise IDs, so that downstream services and agents (like E7 and E7.5) can fetch full exercise data (names, muscles, videos, cues) using ONLY the IDs you provide.
`,
  model: "gpt-4.1",
  tools: [
    fileSearchExercises  // BD Ejercicios v2.0 Definitiva
  ],
  outputType: E6ExerciseNormalizerDbMapperSchema,
  modelSettings: {
    temperature: 1,
    topP: 1,
    maxTokens: 2048,
    store: true
  }
});

const e7TrainingPlanAssembler = new Agent({
  name: "E7 – Training Plan Assembler (E6 Disabled)",
  instructions: `You are E7 – Training Plan Assembler, the seventh agent in the EDN360 training pipeline.

⚠️ UPDATED: E6 is now DISABLED. You work directly with E5 output.

Your mission is purely technical and non-creative.

You receive ONE input via chat history:

From E5 (Training Plan Validator):
   final_training_plan:
   - training_type
   - days_per_week
   - session_duration_min
   - weeks
   - goal
   - sessions[]:
     - id
     - name
     - focus[] (array of strings)
     - blocks[]:
       - id
       - primary_muscles[] (array of strings)
       - secondary_muscles[] (array of strings)
       - num_exercises
       - exercise_types[] (array of exercise_id strings from catalog)
       - series (number or string, per block)
       - reps (string, e.g. \"8-12\")
       - rpe (string or number)
     - session_notes[] (array of short strings)
   - general_notes[] (array of short strings)

Your ONLY job:
Transform final_training_plan into a compact, client-ready technical program.
Backend will enrich exercise_types with full data from catalog.

You MUST:

1. KEEP the same training_type, days_per_week, session_duration_min, weeks and sessions structure from final_training_plan.
2. For each session in final_training_plan.sessions:
   - Copy: id, name, focus[]
   - For each block in session.blocks:
     - Copy: id, primary_muscles[], secondary_muscles[]
     - For each exercise_type in block.exercise_types (with index i):
       - Create an exercise object with:
         - order = i + 1
         - exercise_types = [block.exercise_types[i]]  // Keep as array with single exercise_id
         - series = block.series
         - reps = block.reps
         - rpe = block.rpe
     - Put all these exercise objects in an \"exercises\" array in the same order.
   - session_notes: Copy from final_training_plan (shorten if very long)

3. general_notes: Copy from final_training_plan (shorten if very long)

You MUST NOT:

- Call or read the exercise database or any external files.
- Invent or modify exercise IDs.
- Add fields like video_url, name, cues, descriptions, images, or any extra metadata.
- Change the number of sessions, blocks or exercises.
- Translate or change keys/field names (e.g. NEVER use \"repeticiones\", \"músculos_primarios\", etc.).
- Output anything outside the required JSON.

==================================================
OUTPUT FORMAT (MANDATORY)
==================================================

You MUST output a single JSON object with EXACTLY one top-level key:

{
  \"client_training_program\": {
    ...
  }
}

Inside \"client_training_program\" you MUST include:

- title           (short string, max ~15–20 words)
- summary         (short string, max ~25–30 words)
- goal            (short string)
- training_type   (string, from final_training_plan.training_type)
- days_per_week   (integer, from final_training_plan.days_per_week)
- session_duration_min (integer, from final_training_plan.session_duration_min)
- weeks           (integer, from final_training_plan.weeks)
- sessions        (array)
- general_notes   (array of short strings, MAX 5 items)

Each item in sessions[] MUST have:

- id             (string, from final_training_plan.sessions[x].id)
- name           (string, from final_training_plan.sessions[x].name)
- focus          (array of strings, from final_training_plan.sessions[x].focus)
- blocks         (array)
- session_notes  (array of short strings, MAX 3 items)

Each block in blocks[] MUST have:

- id               (string, from final_training_plan.sessions[x].blocks[y].id)
- primary_muscles  (array of strings, from final_training_plan.sessions[x].blocks[y].primary_muscles)
- secondary_muscles(array of strings, from final_training_plan.sessions[x].blocks[y].secondary_muscles)
- exercises        (array of exercise objects)

Each exercise object MUST have:

- order  (integer, 1-based index inside the block)
- db_id  (string, from E6.mappings[].db_match.id)
- series (number or string, from the block.series)
- reps   (string, from the block.reps)
- rpe    (number or string, from the block.rpe)

==================================================
CRITICAL MINIMIZATION RULES
==================================================

To avoid truncation and server errors, you MUST keep the output compact:

- DO NOT include:
  - video_url
  - cues
  - names
  - muscle descriptions beyond primary_muscles and secondary_muscles
  - any additional metadata

- title, summary, goal MUST be short.

- session_notes:
  - MAX 3 items per session
  - Each item must be a short sentence.

- general_notes:
  - MAX 5 items
  - Each item must be a short sentence.

- Do NOT add any extra keys not defined in the response_schema.
- Do NOT add nested objects beyond what the schema allows.

==================================================
ABSOLUTE RULES
==================================================

- Output ONLY valid JSON.
- Top-level object MUST have exactly one key: \"client_training_program\".
- The JSON MUST satisfy the response_schema with additionalProperties = false.
- Do NOT change the logical structure of the plan (number of sessions/blocks/exercises).
- Do NOT invent or modify db_ids; always use the mapping from E6.
- Do NOT output markdown, comments, or explanations.
- Do NOT translate or change field names (keys) under any circumstance.

==================================================
LANGUAGE
==================================================

- Text visible to the client (title, summary, goal, session_notes, general_notes) may be in Spanish, concise and clear.
- All IDs and field names (keys) MUST stay exactly as defined in the schema.

==================================================
GOAL
==================================================

Produce a compact, structurally clean \"client_training_program\" JSON that merges:
- the validated structure and parameters from E5, and
- the exercise IDs from E6,
ready for a downstream presenter (E7.5) or backend to enrich with names, videos and final layout for the client.

`,
  model: "gpt-4.1",
  outputType: E7TrainingPlanAssemblerSchema,
  modelSettings: {
    temperature: 1,
    topP: 1,
    maxTokens: 4096,
    store: true
  }
});

const e75TrainingPlanEnricher = new Agent({
  name: "E7.5 – Training Plan Enricher",
  instructions: `You are E7.5 – Training Plan Enricher, the eighth agent in the EDN360 training pipeline.

Your mission is purely technical and non-creative.

You receive via chat history the JSON object:

client_training_program:
- title
- summary
- goal
- training_type
- days_per_week
- session_duration_min
- weeks
- sessions[]:
  - id
  - name
  - focus[]
  - blocks[]:
    - id
    - primary_muscles[]
    - secondary_muscles[]
    - exercises[]:
      - order (integer)
      - db_id (string)
      - series (number or string)
      - reps (string)
      - rpe (number or string)
  - session_notes[] (array of strings)
- general_notes[] (array of strings)

You also have access (through your connected knowledge / files) to the EDN360 Exercise Database:

File name: \"BD_EJERCICIOS1-BD_AGENTES_DEFINITIVA.json\"

Each row in that database contains, among others:
- id                    (e.g. \"E363\")
- name_std             (exercise name)
- primary_group_std    (main muscle group)
- secondary_group_std  (secondary muscle group)
- URL video…           (Google Drive URL)

You MUST treat this exercise database as the ONLY source of truth for exercise data.

==================================================
YOUR ONLY JOB
==================================================

You take client_training_program from E7 and ENRICH each exercise with data from the database.

CRITICAL: You MUST KEEP the blocks structure intact. DO NOT flatten exercises.

For EACH exercise in EACH block in EACH session:

- Input from E7 (client_training_program):
  - order
  - db_id
  - series
  - reps
  - rpe

- From the EDN360 Exercise Database row with matching id:
  - name_std → use as \"name\"
  - primary_group_std → use as \"primary_group\"
  - secondary_group_std → use as \"secondary_group\"
  - URL video… → use as \"video_url\"

- For \"notes\": Create a SHORT Spanish sentence combining safety cues based on:
  - The block's primary_muscles and secondary_muscles
  - Any relevant safety considerations for that exercise
  - Max 1 short sentence (e.g. \"Mantener escápulas retraídas, control en excéntrica\")

You MUST create, for each exercise, this object:

{
  \"order\": (keep from E7),
  \"db_id\": (keep from E7),
  \"name\": (from DB.name_std),
  \"primary_group\": (from DB.primary_group_std),
  \"secondary_group\": (from DB.secondary_group_std),
  \"series\": (keep from E7),
  \"reps\": (keep from E7),
  \"rpe\": (keep from E7),
  \"notes\": (create SHORT safety/technique cue in Spanish),
  \"video_url\": (from DB.URL video…)
}

==================================================
MISSING OR INVALID DB MATCH
==================================================

If an exercise db_id from E7 does NOT exist in the database:

- KEEP db_id as is.
- Set:
  - name: \"UNKNOWN_EXERCISE\"
  - primary_group: \"unknown\"
  - secondary_group: \"unknown\"
  - notes: \"\"
  - video_url: \"\"

You MUST NOT invent IDs, names or URLs.

==================================================
OUTPUT FORMAT (MANDATORY)
==================================================

You MUST output a single JSON object with EXACTLY one top-level key:

{
  \"client_training_program_enriched\": {
    \"title\": \"...\",
    \"summary\": \"...\",
    \"goal\": \"...\",
    \"training_type\": \"...\",
    \"days_per_week\": 4,
    \"session_duration_min\": 45,
    \"weeks\": 4,
    \"sessions\": [
      {
        \"id\": \"D1\",
        \"name\": \"...\",
        \"focus\": [\"...\"],
        \"blocks\": [
          {
            \"id\": \"A\",
            \"primary_muscles\": [\"...\"],
            \"secondary_muscles\": [\"...\"],
            \"exercises\": [
              {
                \"order\": 1,
                \"db_id\": \"E123\",
                \"name\": \"Press banca con barra\",
                \"primary_group\": \"Pecho\",
                \"secondary_group\": \"Tríceps\",
                \"series\": 4,
                \"reps\": \"8-10\",
                \"rpe\": \"8\",
                \"notes\": \"Control en descenso, escápulas retraídas\",
                \"video_url\": \"https://drive.google.com/...\"
              }
            ]
          }
        ],
        \"session_notes\": [\"...\"]
      }
    ],
    \"general_notes\": [\"...\"]
  }
}

==================================================
CRITICAL RULES
==================================================

- KEEP the blocks structure. DO NOT flatten to sessions[].exercises[]
- KEEP focus[] in each session
- KEEP primary_muscles and secondary_muscles in each block
- For each exercise, ADD: name, primary_group, secondary_group, notes, video_url
- session_notes: MAX 2 items, very short
- general_notes: MAX 3 items, very short
- All notes can be in Spanish, but keep them concise

==================================================
ABSOLUTE RULES
==================================================

- Output ONLY valid JSON.
- Top-level object MUST have exactly one key: \"client_training_program_enriched\".
- The JSON MUST satisfy the provided response_schema (additionalProperties = false).
- Do NOT flatten blocks structure.
- Do NOT change or delete sessions/blocks/exercises.
- Do NOT translate or change field names (keys).
- Use ONLY the EDN360 exercise database for resolving db_id → name, primary_group, secondary_group, video_url.

`,
  model: "gpt-4.1",
  tools: [
    fileSearchExercises  // BD Ejercicios v2.0 Definitiva
  ],
  outputType: E75TrainingPlanEnricherSchema,
  modelSettings: {
    temperature: 1,
    topP: 1,
    maxTokens: 4096,
    store: true
  }
});

// Tipo de input EVOLUTIVO: recibe input + state
type WorkflowInput = {
  input?: {
    input_as_text?: string;
  };
  state?: {
    initial_questionnaire?: any;
    previous_followups?: any[];
    previous_plans?: any[];
    last_plan?: any;
  };
  // Retrocompatibilidad con formato antiguo
  input_as_text?: string;
  [key: string]: any;
};

// Helper function to safely run agents with detailed error logging
async function runAgentWithLogging(
  runner: any,
  agent: any,
  agentName: string,
  input: any[],
  timeoutMs: number = 120000  // Default: 2 minutes
) {
  try {
    console.log(`\n🚀 Ejecutando ${agentName}... (timeout: ${timeoutMs}ms)`);
    
    // Create a timeout promise
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => {
        reject(new Error(`${agentName} exceeded timeout of ${timeoutMs}ms`));
      }, timeoutMs);
    });
    
    // Race between agent execution and timeout
    const result = await Promise.race([
      runner.run(agent, input),
      timeoutPromise
    ]);
    
    console.log(`✅ ${agentName} completado`);
    return result;
  } catch (error: any) {
    console.error(`\n❌ ========== ERROR EN ${agentName} ==========`);
    console.error(`Error type: ${error.constructor.name}`);
    console.error(`Error message: ${error.message}`);
    
    // Intentar extraer información del error
    if (error.message && error.message.includes('JSON')) {
      console.error(`\n🔍 Es un error de JSON parsing`);
      
      // Si el error menciona una posición, intentar extraer contexto
      const posMatch = error.message.match(/position (\d+)/);
      if (posMatch) {
        const pos = parseInt(posMatch[1]);
        console.error(`🔍 Posición del error: ${pos}`);
      }
    }
    
    // Loguear el stack trace
    if (error.stack) {
      console.error(`\n📚 Stack trace:`);
      console.error(error.stack);
    }
    
    console.error(`\n🔍 ========== FIN ERROR ${agentName} ==========\n`);
    throw error;
  }
}

// Main code entrypoint
export const runWorkflow = async (workflow: WorkflowInput) => {
  // NUEVO FLUJO EVOLUTIVO: Soporta input + state
  let inputAsText: string;
  let workflowState: any = {};
  
  // Detectar si es flujo nuevo (con state) o antiguo (solo input_as_text)
  if (workflow.input && workflow.state) {
    // FLUJO EVOLUTIVO NUEVO
    console.log("🔄 Detectado flujo EVOLUTIVO con STATE");
    
    inputAsText = workflow.input.input_as_text || JSON.stringify(workflow.input);
    workflowState = workflow.state;
    
    const hasHistory = Boolean(workflowState.last_plan);
    console.log(`📊 Tipo de generación: ${hasHistory ? 'EVOLUTIVO' : 'INICIAL'}`);
    console.log(`📋 Previous plans: ${workflowState.previous_plans?.length || 0}`);
    console.log(`📋 Previous followups: ${workflowState.previous_followups?.length || 0}`);
  } else {
    // FLUJO ANTIGUO (RETROCOMPATIBILIDAD)
    console.log("📝 Detectado flujo ANTIGUO (sin state)");
    inputAsText = typeof workflow.input_as_text === "string"
      ? workflow.input_as_text
      : JSON.stringify(workflow);
    workflowState = {};
  }

  return await withTrace("EDN360 – Entreno v1", async () => {
    // Agregar state al contexto inicial si existe
    let initialContext = inputAsText;
    if (workflowState.initial_questionnaire || workflowState.last_plan) {
      initialContext += `\n\n=== HISTORIAL DISPONIBLE ===\n`;
      if (workflowState.initial_questionnaire) {
        initialContext += `\nInitial Questionnaire:\n${JSON.stringify(workflowState.initial_questionnaire, null, 2)}`;
      }
      if (workflowState.previous_followups && workflowState.previous_followups.length > 0) {
        initialContext += `\n\nPrevious Follow-ups: ${workflowState.previous_followups.length}`;
      }
      if (workflowState.previous_plans && workflowState.previous_plans.length > 0) {
        initialContext += `\n\nPrevious Plans: ${workflowState.previous_plans.length}`;
      }
      if (workflowState.last_plan) {
        initialContext += `\n\nLast Plan:\n${JSON.stringify(workflowState.last_plan, null, 2)}`;
      }
    }
    
    const conversationHistory: AgentInputItem[] = [
      { role: "user", content: [{ type: "input_text", text: initialContext }] }
    ];
    const runner = new Runner({
      traceMetadata: {
        __trace_source__: "agent-builder",
        workflow_id: "wf_69260afcea288190955843b5a4223eea061948bdf6abc68b"
      }
    });
    const e1AnalizadorDePerfilResultTemp = await runAgentWithLogging(
      runner,
      e1AnalizadorDePerfil,
      "E1 – Analizador de Perfil",
      [
        ...conversationHistory,
        {
          id: undefined,
          role: "assistant",
          content: [
            { type: "output_text", text: "{{ input_as_text }}" }
          ]
        }
      ],
      90000  // 90 seconds timeout
    );
    conversationHistory.push(...e1AnalizadorDePerfilResultTemp.newItems.map((item: any) => item.rawItem));

    if (!e1AnalizadorDePerfilResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }

    const e1AnalizadorDePerfilResult = {
      output_text: JSON.stringify(e1AnalizadorDePerfilResultTemp.finalOutput),
      output_parsed: e1AnalizadorDePerfilResultTemp.finalOutput
    };
    const e2ParseQuestionnaireResultTemp = await runAgentWithLogging(
      runner,
      e2ParseQuestionnaire,
      "E2 – Parse Questionnaire",
      [
        ...conversationHistory,
        {
          id: undefined,
          role: "assistant",
          content: [
            { type: "output_text", text: `Original_questionnaire_input:
          {{ input_as_text }}

          Profile_from_E1:
          {{ E1.profile }}` }
          ]
        }
      ],
      90000  // 90 seconds timeout
    );
    conversationHistory.push(...e2ParseQuestionnaireResultTemp.newItems.map((item: any) => item.rawItem));

    if (!e2ParseQuestionnaireResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }

    const e2ParseQuestionnaireResult = {
      output_text: JSON.stringify(e2ParseQuestionnaireResultTemp.finalOutput),
      output_parsed: e2ParseQuestionnaireResultTemp.finalOutput
    };
    const e3TrainingSummaryResultTemp = await runAgentWithLogging(
      runner,
      e3TrainingSummary,
      "E3 – Training Summary",
      [
        ...conversationHistory,
        {
          id: undefined,
          role: "assistant",
          content: [
            { type: "output_text", text: `Profile_from_E1:
          {{ E1.profile }}

          Questionnaire_normalized_from_E2:
          {{ E2.questionnaire_normalized }}
          ` }
          ]
        }
      ],
      600000  // 10 minutes timeout (E3 has Knowledge Base Vector Store - increased for reliability)
    );
    conversationHistory.push(...e3TrainingSummaryResultTemp.newItems.map((item: any) => item.rawItem));

    if (!e3TrainingSummaryResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }

    const e3TrainingSummaryResult = {
      output_text: JSON.stringify(e3TrainingSummaryResultTemp.finalOutput),
      output_parsed: e3TrainingSummaryResultTemp.finalOutput
    };
    const e4TrainingPlanGeneratorResultTemp = await runAgentWithLogging(
      runner,
      e4TrainingPlanGenerator,
      "E4 – Training Plan Generator",
      [
        ...conversationHistory,
        {
          id: undefined,
          role: "assistant",
          content: [
            { type: "output_text", text: `Profile_from_E1:
          {{ E1.profile }}

          Questionnaire_normalized_from_E2:
          {{ E2.questionnaire_normalized }}

          Training_context_from_E3:
          {{ E3.training_context }}
          ` }
          ]
        }
      ],
      600000  // 10 minutes timeout (E4 has Knowledge Base Vector Store - increased for reliability)
    );
    conversationHistory.push(...e4TrainingPlanGeneratorResultTemp.newItems.map((item: any) => item.rawItem));

    if (!e4TrainingPlanGeneratorResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }

    const e4TrainingPlanGeneratorResult = {
      output_text: JSON.stringify(e4TrainingPlanGeneratorResultTemp.finalOutput),
      output_parsed: e4TrainingPlanGeneratorResultTemp.finalOutput
    };
    const e5TrainingPlanValidatorResultTemp = await runAgentWithLogging(
      runner,
      e5TrainingPlanValidator,
      "E5 – Training Plan Validator",
      [
        ...conversationHistory,
        {
          id: undefined,
          role: "assistant",
          content: [
            { type: "output_text", text: `Training_context_from_E3:
          {{ E3.training_context }}

          Training_plan_from_E4:
          {{ E4.training_plan }}
          ` }
          ]
        }
      ],
      600000  // 10 minutes timeout (E5 has Knowledge Base Vector Store - increased for reliability)
    );
    conversationHistory.push(...e5TrainingPlanValidatorResultTemp.newItems.map((item: any) => item.rawItem));

    if (!e5TrainingPlanValidatorResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }

    const e5TrainingPlanValidatorResult = {
      output_text: JSON.stringify(e5TrainingPlanValidatorResultTemp.finalOutput),
      output_parsed: e5TrainingPlanValidatorResultTemp.finalOutput
    };
    
    // E6 DISABLED - Backend will enrich exercises directly from catalog
    // const e6ExerciseNormalizerDbMapperResultTemp = await runAgentWithLogging(...);
    
    // Create mock E6 result to maintain workflow compatibility
    const e6ExerciseNormalizerDbMapperResult = {
      output_text: JSON.stringify({mappings: []}),
      output_parsed: {mappings: []}  // Empty mappings - backend will handle enrichment
    };
    const e7TrainingPlanAssemblerResultTemp = await runAgentWithLogging(
      runner,
      e7TrainingPlanAssembler,
      "E7 – Training Plan Assembler",
      [
        ...conversationHistory,
        {
          id: undefined,
          role: "assistant",
          content: [
            { type: "output_text", text: `Final_training_plan_from_E5:
          {{ E5.final_training_plan }}

          Mappings_from_E6:
          {{ E6.mappings }}
          ` }
          ]
        }
      ],
      600000  // 10 minutes timeout (E7 - increased for reliability)
    );
    conversationHistory.push(...e7TrainingPlanAssemblerResultTemp.newItems.map((item: any) => item.rawItem));

    if (!e7TrainingPlanAssemblerResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }

    const e7TrainingPlanAssemblerResult = {
      output_text: JSON.stringify(e7TrainingPlanAssemblerResultTemp.finalOutput),
      output_parsed: e7TrainingPlanAssemblerResultTemp.finalOutput
    };
    const e75TrainingPlanEnricherResultTemp = await runAgentWithLogging(
      runner,
      e75TrainingPlanEnricher,
      "E7.5 – Training Plan Enricher",
      [
        ...conversationHistory,
        {
          id: undefined,
          role: "assistant",
          content: [
            { type: "output_text", text: `Client_training_program_from_E7:
          {{ E7.client_training_program }}
          ` }
          ]
        }
      ],
      600000  // 10 minutes timeout (E7.5 has Exercise Database Vector Store - increased for reliability)
    );
    conversationHistory.push(...e75TrainingPlanEnricherResultTemp.newItems.map((item: any) => item.rawItem));

    // 🔍 DEBUG: Loguear el raw output ANTES de validar con Zod
    console.log('\n\n🔍 ========== E7.5 RAW OUTPUT DEBUG ==========');
    console.log('🔍 Agent: E7.5 – Training Plan Enricher');
    
    // Intentar extraer el raw text del último item de conversación
    if (e75TrainingPlanEnricherResultTemp.newItems && e75TrainingPlanEnricherResultTemp.newItems.length > 0) {
      const lastItem = e75TrainingPlanEnricherResultTemp.newItems[e75TrainingPlanEnricherResultTemp.newItems.length - 1];
      
      // Loguear la estructura completa del último item
      console.log('🔍 Last item structure:');
      console.log(JSON.stringify(lastItem, null, 2));
      
      // Intentar obtener el contenido raw
      if (lastItem.rawItem && lastItem.rawItem.content) {
        console.log('🔍 Raw content from lastItem:');
        console.log(JSON.stringify(lastItem.rawItem.content, null, 2));
      }
    }
    
    // Loguear el finalOutput (ya parseado por Zod o intentado)
    console.log('🔍 finalOutput (parsed or attempted):');
    console.log(JSON.stringify(e75TrainingPlanEnricherResultTemp.finalOutput, null, 2).substring(0, 2000));
    console.log('🔍 ========== END DEBUG ==========\n\n');

    if (!e75TrainingPlanEnricherResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }

    const e75TrainingPlanEnricherResult = {
      output_text: JSON.stringify(e75TrainingPlanEnricherResultTemp.finalOutput),
      output_parsed: e75TrainingPlanEnricherResultTemp.finalOutput
    };

    // 👇 CRÍTICO: Devolver el resultado final
    return e75TrainingPlanEnricherResult.output_parsed;
  });
}
