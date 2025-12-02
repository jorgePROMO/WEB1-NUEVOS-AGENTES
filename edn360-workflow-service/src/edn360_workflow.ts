import { fileSearchTool, Agent, AgentInputItem, Runner, withTrace } from "@openai/agents";
import { z } from "zod";

// Tool definitions
const fileSearch = fileSearchTool([
  "vs_6924b7574b7c8191b6008068aa8a1df0"
])
const fileSearch1 = fileSearchTool([
  "vs_692c510043dc81919e4e7887a299d583"
])
const E1AnalizadorDePerfilSchema = z.object({ profile: z.object({ name: z.string(), email: z.string(), age: z.number(), gender: z.enum(["male", "female", "other"]), height_cm: z.number(), weight_kg: z.number(), experience_level: z.enum(["beginner", "intermediate", "advanced"]), training_days_per_week: z.number(), session_duration_min: z.number(), goal_primary: z.enum(["muscle_gain", "fat_loss", "recomposition", "performance"]), goal_secondary: z.string(), injuries_or_limitations: z.array(z.string()), equipment_available: z.array(z.string()), preferences: z.object({ enjoys: z.array(z.string()), dislikes: z.array(z.string()) }) }) });
const E2ParseQuestionnaireSchema = z.object({ questionnaire_normalized: z.object({ full_name: z.string(), email: z.string(), birth_date: z.string(), gender: z.enum(["male", "female", "other"]), profession: z.string(), phone: z.string(), weight_kg: z.number(), height_cm: z.number(), bodyfat_percent: z.number(), chronic_conditions: z.array(z.string()), medications: z.array(z.string()), injuries_limitations: z.array(z.string()), workload_stress: z.enum(["low", "medium", "high"]), daily_activity: z.enum(["low", "medium", "high"]), training_experience_level: z.enum(["beginner", "intermediate", "advanced"]), training_days_per_week: z.number(), session_duration_min: z.number(), equipment_available: z.array(z.string()), food_intolerances_allergies: z.array(z.string()), foods_disliked: z.array(z.string()), preferred_foods: z.array(z.string()), goal_primary: z.enum(["muscle_gain", "fat_loss", "recomposition", "performance"]), sleep_hours: z.number(), meals_per_day: z.number(), diet_history: z.array(z.string()), supplements: z.array(z.string()), motivation_reason: z.string() }) });
const E3TrainingSummarySchema = z.object({ training_context: z.object({ profile: z.object({ full_name: z.string(), age: z.number(), gender: z.enum(["male", "female", "other"]), experience_level: z.enum(["beginner", "intermediate", "advanced"]), height_cm: z.number(), weight_kg: z.number() }), goals: z.object({ primary: z.enum(["muscle_gain", "fat_loss", "recomposition", "performance"]), secondary: z.string() }), constraints: z.object({ shoulder_issues: z.string(), lower_back_issues: z.string(), other: z.array(z.string()) }), equipment: z.object({ gym_access: z.boolean(), home_equipment: z.array(z.string()) }), availability: z.object({ training_days_per_week: z.number(), session_duration_min: z.number() }), training_type: z.enum(["full_body", "upper_lower", "push_pull_legs", "bro_split", "other"]), training_type_reason: z.string() }) });
const E4TrainingPlanGeneratorSchema = z.object({ training_plan: z.object({ training_type: z.enum(["full_body", "upper_lower", "push_pull_legs", "bro_split", "other"]), days_per_week: z.number(), session_duration_min: z.number(), weeks: z.number(), goal: z.string(), sessions: z.array(z.object({ id: z.string(), name: z.string(), focus: z.array(z.string()), blocks: z.array(z.object({ id: z.string(), primary_muscles: z.array(z.string()), secondary_muscles: z.array(z.string()), num_exercises: z.number(), exercise_types: z.array(z.string()), series: z.number(), reps: z.string(), rpe: z.string(), notes: z.string() })), core_mobility_block: z.object({ include: z.boolean(), details: z.string() }), session_notes: z.array(z.string()) })), general_notes: z.array(z.string()) }) });
const E5TrainingPlanValidatorSchema = z.object({ final_training_plan: z.object({ training_type: z.enum(["full_body", "upper_lower", "push_pull_legs", "bro_split", "other"]), days_per_week: z.number(), session_duration_min: z.number(), weeks: z.number(), goal: z.string(), sessions: z.array(z.object({ id: z.string(), name: z.string(), focus: z.array(z.string()), blocks: z.array(z.object({ id: z.string(), primary_muscles: z.array(z.string()), secondary_muscles: z.array(z.string()), num_exercises: z.number(), exercise_types: z.array(z.string()), series: z.number(), reps: z.string(), rpe: z.string(), notes: z.string() })), core_mobility_block: z.object({ include: z.boolean(), details: z.string() }), session_notes: z.array(z.string()) })), general_notes: z.array(z.string()) }), safety_ok: z.boolean(), issues: z.array(z.string()) });
const E6ExerciseNormalizerDbMapperSchema = z.object({ mappings: z.array(z.object({ session_id: z.string(), block_id: z.string(), exercise_index: z.number(), exercise_type_from_plan: z.string(), db_match: z.object({ id: z.string() }), similar_candidates: z.array(z.string()) })) });
const E7TrainingPlanAssemblerSchema = z.object({ client_training_program: z.object({ title: z.string(), summary: z.string(), goal: z.string(), training_type: z.string(), days_per_week: z.number(), session_duration_min: z.number(), weeks: z.number(), sessions: z.array(z.object({ id: z.string(), name: z.string(), focus: z.array(z.string()), blocks: z.array(z.object({ id: z.string(), primary_muscles: z.array(z.string()), secondary_muscles: z.array(z.string()), exercises: z.array(z.object({ order: z.number(), db_id: z.string(), name: z.string(), primary_group: z.string(), secondary_group: z.string(), series: z.union([z.number(), z.string()]), reps: z.string(), rpe: z.union([z.number(), z.string()]), notes: z.string(), video_url: z.string() })) })), session_notes: z.array(z.string()) })), general_notes: z.array(z.string()) }) });
const E75TrainingPlanEnricherSchema = z.object({ client_training_program_enriched: z.object({ title: z.string(), summary: z.string(), goal: z.string(), training_type: z.string(), days_per_week: z.number(), session_duration_min: z.number(), weeks: z.number(), sessions: z.array(z.object({ id: z.string(), name: z.string(), focus: z.array(z.string()), blocks: z.array(z.object({ id: z.string(), primary_muscles: z.array(z.string()), secondary_muscles: z.array(z.string()), exercises: z.array(z.object({ order: z.number(), db_id: z.string(), name: z.string(), primary_group: z.string(), secondary_group: z.string(), series: z.union([z.number(), z.string()]), reps: z.string(), rpe: z.union([z.number(), z.string()]), notes: z.string(), video_url: z.string() })) })), session_notes: z.array(z.string()) })), general_notes: z.array(z.string()) }) });

const e1AnalizadorDePerfil = new Agent({
  name: "E1 – Analizador de Perfil",
  instructions: `You are E1 – Profile Analyzer, the first agent in the EDN360 training pipeline.

Your mission:
Take the raw questionnaire text sent by the user (which may be written in Spanish, English, or a mix of both) and convert it into a clean, structured, normalized training profile in ENGLISH, following exactly the JSON schema defined for this agent.

====================
1. INPUT CONTEXT
====================

- The user has filled in a free-form questionnaire about their training, health, injuries and goals.
- Answers may be:
  - Written in Spanish (most likely).
  - Written in a mix of Spanish and English.
  - Noisy, with extra explanations, jokes, emojis or irrelevant comments.
- You MUST ignore anything that is not relevant for building a training profile.

You do NOT receive a strict JSON as input. You receive messy, human text (which in our case will usually be a JSON-like questionnaire, but you treat it as text). Your job is to read it carefully and extract the information needed to fill the \"profile\" object required by the response schema.

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
  instructions: `You are E3 – Training Context Summarizer, the third agent in the EDN360 training pipeline.

Your mission:
You must read the outputs from:
- E1 (profile)
- E2 (questionnaire_normalized)

And combine them into a single structured object called \"training_context\", which will be used by E4 (Training Plan Generator), E5 (Validator), and E6 (Exercise Selector).

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

   RULES:
   - 4 days/week + advanced → usually "upper_lower".
   - If serious shoulder issues → avoid push/pull/legs.
   - If lumbar issues → avoid bro_split with heavy axial loading.
   - Use the safest high-performance option.

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
  outputType: E3TrainingSummarySchema,
  modelSettings: {
    temperature: 1,
    topP: 1,
    maxTokens: 2048,
    store: true
  }
});

const e4TrainingPlanGenerator = new Agent({
  name: "E4 – Training Plan Generator",
  instructions: `You are E4 – Training Plan Generator, the fourth agent in the EDN360 training pipeline.

Your mission:
Use the structured \"training_context\" created by E3 (and indirectly the information from E1 and E2) to produce a SAFE, JOINT-FRIENDLY, STRUCTURED training program for strength and hypertrophy.

The program you create will be used by:
- E5 (Training Plan Validator)
- E6 (Exercise Selector, which maps exercise_types to real exercises from a database)
- E8 (Final formatting for coach and client)

You MUST strictly follow the JSON schema configured for this agent. The ONLY root key of your output MUST be \"training_plan\".


====================
1. INPUT YOU RELY ON
====================

From previous agents (via chat history), you have access to:

- E1: profile
  - name, email, age, gender
  - height_cm, weight_kg
  - experience_level
  - training_days_per_week
  - session_duration_min
  - goal_primary / goal_secondary
  - injuries_or_limitations
  - equipment_available
  - preferences

- E2: questionnaire_normalized
  - chronic_conditions
  - medications
  - lifestyle, sleep, nutrition, etc.

- E3: training_context
  - profile:
    - full_name, age, gender, experience_level, height_cm, weight_kg
  - goals:
    - primary, secondary
  - constraints:
    - shoulder_issues (\"yes\"/\"no\")
    - lower_back_issues (\"yes\"/\"no\")
    - other (e.g. hypothyroidism, gluten intolerance, etc.)
  - equipment:
    - gym_access (true/false)
    - home_equipment (array)
  - availability:
    - training_days_per_week
    - session_duration_min
  - training_type:
    - \"full_body\" | \"upper_lower\" | \"push_pull_legs\" | \"bro_split\" | \"other\"
  - training_type_reason (short sentence)

You MUST respect this context. You are NOT allowed to ignore injuries, availability or training type.

For the current test client:
- Advanced lifter.
- 4 training days per week.
- 45 min sessions.
- Primary goal: muscle_gain.
- Shoulder issues: yes.
- Lumbar disc issues (L5-L6): yes.
- Gym access: full_gym.


====================
2. WHAT YOU MUST OUTPUT (\"training_plan\")
====================

You MUST output a single JSON object:

{
  \"training_plan\": {
    \"training_type\": \"...\",
    \"days_per_week\": ...,
    \"session_duration_min\": ...,
    \"weeks\": ...,
    \"goal\": \"...\",
    \"sessions\": [ ... ],
    \"general_notes\": [ ... ]
  }
}

The internal structure is fully defined by the JSON schema. You MUST respect:

- Field names.
- Types (numbers, strings, arrays, booleans).
- Enums for training_type.
- No extra keys (additionalProperties: false).


====================
3. DESIGN RULES – HIGH LEVEL
====================

1) Training type
- You MUST use the training_type suggested in training_context, unless it is clearly unsafe.
- For this specific client (advanced, 4 days, shoulder + lumbar issues), \"upper_lower\" is a highly appropriate and safe choice.

2) Days per week
- Use the value from training_context.availability.training_days_per_week.
- For this client: 4.

3) Session duration
- Use training_context.availability.session_duration_min.
- For this client: ~45 minutes.

4) Weeks
- Set \"weeks\" to 4 for now (a 4-week block that can be repeated or progressed).

5) Goal
- A short ENGLISH string summarizing the plan goal, e.g. \"Hypertrophy-focused strength training with joint-friendly approach\".


====================
4. SESSIONS STRUCTURE (\"sessions\")
====================

The \"sessions\" array MUST contain one entry per training day (e.g. D1, D2, D3, D4).

Each session object MUST have:

- id: a short ID like \"D1\", \"D2\", \"D3\", \"D4\".
- name: short descriptive name in English, e.g. \"Upper 1 – Push emphasis\", \"Lower 1 – Quad emphasis\".
- focus: array of 1–3 short strings describing the main goal of the session, e.g. [\"upper_body\", \"push_focus\"].

- blocks: array of 2–3 blocks per session.
  Each block object MUST have:
  - id: a letter per block, e.g. \"A\", \"B\", \"C\".
  - primary_muscles: array of short muscle group labels, e.g. [\"chest\", \"triceps\"].
  - secondary_muscles: array of secondary muscles, e.g. [\"front_delts\"].
  - num_exercises: integer, usually 1–3 exercises per block.
  - exercise_types: array of short internal codes that describe BIOMECHANICAL PATTERNS, NOT SPECIFIC EXERCISES.
    Examples:
      - \"horizontal_press\"
      - \"horizontal_row\"
      - \"vertical_pull_machine\"
      - \"lat_pulldown\"
      - \"quad_dominant_machine\"
      - \"hamstring_curl_machine\"
      - \"glute_bridge_pattern\"
      - \"leg_press_machine\"
      - \"hip_hinge_machine\"
    These placeholders WILL BE RESOLVED by E6 into specific actual exercises from the database.

  - series: integer number of sets per exercise block (e.g. 3 or 4).
  - reps: short string range, e.g. \"6-8\", \"8-10\", \"10-12\".
  - rpe: short string, e.g. \"7-8\", \"8-9\".
  - notes: short guidance in English about execution or load (e.g. \"Controlled tempo, no pain in shoulders, stop 2 reps before failure.\").

- core_mobility_block:
  - include: boolean.
  - details: short text describing what to do if include is true (e.g. \"Core stability and anti-rotation work, lumbar-friendly, 5-10 minutes.\").

- session_notes: array of short strings with reminders or cues for that session (e.g. [\"Warm up shoulders thoroughly.\", \"Avoid any shoulder pain.\", \"Keep lumbar neutral at all times.\"]).

You MUST design the session layout consistent with:

- training_type (e.g. upper/lower):
  - Upper days focusing on upper body (push + pull).
  - Lower days focusing on lower body (quads, hamstrings, glutes).
- constraints:
  - Shoulders and lower back must be protected.
- availability:
  - 45 minutes per session → avoid too many exercises or excessive volume.


====================
5. SAFETY AND INJURY RULES
====================

1) Shoulder issues = \"yes\"
- NO overhead pressing (no strict press, no push press).
- NO deep dips or extreme shoulder extension.
- Prefer:
  - Machine presses.
  - Neutral grip pressing.
  - Supported rowing.
- Avoid positions that cause pain or extreme stretch in the shoulder.

2) Lumbar disc issues = \"yes\"
- NO heavy axial loading:
  - No barbell back squat.
  - No conventional deadlift from the floor.
- Prefer:
  - Machine-based lower body (leg press, hack squat, etc.) with controlled range of motion.
  - Supported hip hinge patterns (e.g. machine RDL, back extension with strict technique, glute bridge machines).
- Core work: focus on anti-rotation and stability, not loaded spinal flexion.

3) General:
- Use moderate volume per muscle group per session.
- Use RPE targets that are challenging but safe (e.g. 7–8 for compound lifts, 8–9 for isolation if the client tolerates it).
- Always assume the client should STOP if any sharp or joint pain appears.


====================
6. HOW MANY SESSIONS AND HOW TO LAYOUT
====================

For a 4-day upper/lower split:

- D1: Upper 1 (push emphasis, but always including some row).
- D2: Lower 1 (quad emphasis, plus hamstrings/glutes).
- D3: Rest or other day (not defined here).
- D4: Upper 2 (pull emphasis, plus secondary push).
- D5: Lower 2 (posterior chain emphasis).
- You do NOT need to model rest days in this agent, only the 4 training days (D1, D2, D3, D4).

Each upper day:
- 2–3 blocks:
  - Block A: compound press + row pattern (horizontal press/row).
  - Block B: accessory chest/back/shoulders, shoulder-safe.
  - Block C: arms (biceps/triceps) or extra upper back.

Each lower day:
- 2–3 blocks:
  - Block A: main quad-dominant machine (e.g. leg press vs squats).
  - Block B: hamstring-focused machine (e.g. leg curl, RDL machine).
  - Block C: glute/hip work and/or calves.

You MUST keep the total time realistic for 45 minutes:
- Typically 2–3 blocks with 1–2 exercises each.


====================
7. GENERAL NOTES (\"general_notes\")
====================

\"general_notes\" MUST be an array of short strings in English.

Include:
- Notes about shoulder protection.
- Notes about lumbar protection.
- Warm-up recommendations.
- Progression guidelines (e.g. add load when all sets are easy at the top of the rep range).
- Auto-regulation suggestions (if extra fatigue, reduce volume slightly).


====================
8. LANGUAGE AND FORMAT RULES
====================

- Output MUST be ONLY valid JSON.
- The ONLY root key MUST be \"training_plan\".
- No markdown, no comments, no extra text.
- All strings MUST be in English.
- Do NOT add any keys that are not present in the schema.
- You MUST respect additionalProperties: false in all objects.


====================
9. SUMMARY OF OUTPUT SHAPE
====================

{
  \"training_plan\": {
    \"training_type\": \"upper_lower\",
    \"days_per_week\": 4,
    \"session_duration_min\": 45,
    \"weeks\": 4,
    \"goal\": \"Short English description of the plan goal\",
    \"sessions\": [
      {
        \"id\": \"D1\",
        \"name\": \"Upper 1 – Push emphasis\",
        \"focus\": [\"upper_body\", \"push_focus\"],
        \"blocks\": [
          {
            \"id\": \"A\",
            \"primary_muscles\": [\"chest\", \"triceps\"],
            \"secondary_muscles\": [\"front_delts\"],
            \"num_exercises\": 2,
            \"exercise_types\": [\"horizontal_press\", \"horizontal_row\"],
            \"series\": 3,
            \"reps\": \"8-12\",
            \"rpe\": \"7-8\",
            \"notes\": \"Controlled tempo, no shoulder pain, keep scapulae stable.\"
          }
          // ... more blocks
        ],
        \"core_mobility_block\": {
          \"include\": true,
          \"details\": \"5-10 minutes of core stability (planks, anti-rotation), lumbar-friendly.\"
        },
        \"session_notes\": [
          \"Warm up shoulders thoroughly.\",
          \"Avoid any overhead pressing.\",
          \"Stop if shoulder or lower back pain appears.\"
        ]
      }
      // ... more sessions (D2, D3, D4)
    ],
    \"general_notes\": [
      \"Progressively increase load when all sets feel comfortable at the top of the rep range.\",
      \"Always prioritize joint safety over load.\",
      \"If fatigue or pain increases, reduce volume or intensity in the next session.\"
    ]
  }
}
`,
  model: "gpt-4.1",
  outputType: E4TrainingPlanGeneratorSchema,
  modelSettings: {
    temperature: 1,
    topP: 1,
    maxTokens: 2048,
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
   - For advanced lifter, 4 days/week:
     - Moderate–high volume, but not excessive.
     - Series per block usually 2–4.
     - RPE around 7–8 (main work), up to 8–9 on isolations if joints are safe.

You should mainly tweak \`series\`, \`reps\`, \`rpe\` and safety notes to hit these constraints.

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
    fileSearch
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
  name: "E7 – Training Plan Assembler",
  instructions: `You are E7 – Training Plan Assembler, the seventh agent in the EDN360 training pipeline.

Your mission is purely technical and non-creative.

You receive TWO inputs via chat history:

1) From E5 (Training Plan Validator):
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
       - exercise_types[] (array of strings)
       - series (number or string, per block)
       - reps (string, e.g. \"8-12\")
       - rpe (string or number)
     - session_notes[] (array of short strings)
   - general_notes[] (array of short strings)

2) From E6 (Exercise Normalizer & DB Mapper):
   mappings[]:
   - session_id
   - block_id
   - exercise_index
   - exercise_type_from_plan
   - db_match.id
   - similar_candidates[] (ignored by this agent)

Your ONLY job:
Assemble a compact, client-ready technical program by MERGING:
- the structure and parameters from final_training_plan (E5)
- the db_ids from mappings (E6)

You MUST:

1. KEEP the same training_type, days_per_week, session_duration_min, weeks and sessions structure from final_training_plan.
2. For each session in final_training_plan.sessions:
   - Copy:
     - id
     - name
     - focus[]
   - For each block in session.blocks:
     - Copy:
       - id
       - primary_muscles[]
       - secondary_muscles[]
     - For each exercise index i (0-based) in block.exercise_types:
       - Find the mapping in E6.mappings where:
         - mapping.session_id == session.id
         - mapping.block_id == block.id
         - mapping.exercise_index == i
       - Create an exercise object with:
         - order = i + 1
         - db_id = mapping.db_match.id
         - series = block.series
         - reps = block.reps
         - rpe = block.rpe
     - Put all these exercise objects in an \"exercises\" array in the same order.
   - session_notes:
     - Copy final_training_plan.sessions[x].session_notes
     - If they are very long, you MAY shorten them into short sentences, but KEEP the meaning.

3. general_notes:
   - Copy from final_training_plan.general_notes
   - If they are very long, you MAY shorten them into short sentences, but KEEP the meaning.

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
    fileSearch1
  ],
  outputType: E75TrainingPlanEnricherSchema,
  modelSettings: {
    temperature: 1,
    topP: 1,
    maxTokens: 2048,
    store: true
  }
});

// Tipo de input flexible: puede venir con input_as_text o con el EDN360Input completo
type WorkflowInput = {
  input_as_text?: string;
  [key: string]: any;
};

// Helper function to safely run agents with detailed error logging
async function runAgentWithLogging(
  runner: any,
  agent: any,
  agentName: string,
  input: any[]
) {
  try {
    console.log(`\n🚀 Ejecutando ${agentName}...`);
    const result = await runner.run(agent, input);
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
  // Si ya viene input_as_text lo usamos; si no, convertimos todo el objeto a texto
  const inputAsText =
    typeof workflow.input_as_text === "string"
      ? workflow.input_as_text
      : JSON.stringify(workflow);

  return await withTrace("EDN360 – Entreno v1", async () => {
    const state = {

    };
    const conversationHistory: AgentInputItem[] = [
      { role: "user", content: [{ type: "input_text", text: inputAsText }] }
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
      ]
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
      ]
    );
    conversationHistory.push(...e2ParseQuestionnaireResultTemp.newItems.map((item: any) => item.rawItem));

    if (!e2ParseQuestionnaireResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }

    const e2ParseQuestionnaireResult = {
      output_text: JSON.stringify(e2ParseQuestionnaireResultTemp.finalOutput),
      output_parsed: e2ParseQuestionnaireResultTemp.finalOutput
    };
    const e3TrainingSummaryResultTemp = await runner.run(
      e3TrainingSummary,
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
      ]
    );
    conversationHistory.push(...e3TrainingSummaryResultTemp.newItems.map((item: any) => item.rawItem));

    if (!e3TrainingSummaryResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }

    const e3TrainingSummaryResult = {
      output_text: JSON.stringify(e3TrainingSummaryResultTemp.finalOutput),
      output_parsed: e3TrainingSummaryResultTemp.finalOutput
    };
    const e4TrainingPlanGeneratorResultTemp = await runner.run(
      e4TrainingPlanGenerator,
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
      ]
    );
    conversationHistory.push(...e4TrainingPlanGeneratorResultTemp.newItems.map((item: any) => item.rawItem));

    if (!e4TrainingPlanGeneratorResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }

    const e4TrainingPlanGeneratorResult = {
      output_text: JSON.stringify(e4TrainingPlanGeneratorResultTemp.finalOutput),
      output_parsed: e4TrainingPlanGeneratorResultTemp.finalOutput
    };
    const e5TrainingPlanValidatorResultTemp = await runner.run(
      e5TrainingPlanValidator,
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
      ]
    );
    conversationHistory.push(...e5TrainingPlanValidatorResultTemp.newItems.map((item: any) => item.rawItem));

    if (!e5TrainingPlanValidatorResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }

    const e5TrainingPlanValidatorResult = {
      output_text: JSON.stringify(e5TrainingPlanValidatorResultTemp.finalOutput),
      output_parsed: e5TrainingPlanValidatorResultTemp.finalOutput
    };
    const e6ExerciseNormalizerDbMapperResultTemp = await runner.run(
      e6ExerciseNormalizerDbMapper,
      [
        ...conversationHistory,
        {
          id: undefined,
          role: "assistant",
          content: [
            { type: "output_text", text: `Final_training_plan_from_E5:
          {{ E5.final_training_plan }}
          ` }
          ]
        }
      ]
    );
    conversationHistory.push(...e6ExerciseNormalizerDbMapperResultTemp.newItems.map((item: any) => item.rawItem));

    if (!e6ExerciseNormalizerDbMapperResultTemp.finalOutput) {
        throw new Error("Agent result is undefined");
    }

    const e6ExerciseNormalizerDbMapperResult = {
      output_text: JSON.stringify(e6ExerciseNormalizerDbMapperResultTemp.finalOutput),
      output_parsed: e6ExerciseNormalizerDbMapperResultTemp.finalOutput
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
      ]
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
      ]
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
