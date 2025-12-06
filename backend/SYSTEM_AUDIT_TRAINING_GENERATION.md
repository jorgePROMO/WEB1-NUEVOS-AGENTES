# 🔍 AUDITORÍA COMPLETA - SISTEMA DE GENERACIÓN DE PLANES EDN360

**Fecha:** 6 de diciembre 2024  
**Plan analizado:** "Rutina Weider 4 días (Hipertrofia avanzada, seguro lumbar/hombros)"  
**Plan ID:** `0be1edd6-2f3f-42da-ae8f-185773cf8fe0`

---

## 📊 RESUMEN EJECUTIVO

### 🚨 Problemas Críticos Identificados

1. **Ejercicios con códigos NO CANÓNICOS**
   - E4 genera códigos inventados: `pec_deck`, `cable_fly`, `horizontal_press_machine`
   - Estos códigos NO EXISTEN en el catálogo de 1243 ejercicios
   - Resultado: Sin videos, sin nombres enriquecidos, experiencia pobre

2. **Mala Adecuación al Perfil de Usuario**
   - Usuario: Culturista profesional avanzado
   - Plan generado: Volumen bajo, ejercicios poco desafiantes
   - Falta de ejercicios básicos pesados

3. **Desalineación Prompt vs Schema**
   - El prompt de E4 pide usar `fileSearchExercises` para validar códigos
   - En la práctica, E4 genera códigos sin validar contra el catálogo
   - El schema no valida que los códigos existan

---

## 1️⃣ ARQUITECTURA DE ALTO NIVEL

### Flujo Completo de Generación

```
┌─────────────────┐
│  Cuestionario   │
│   (Usuario)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  E1 – Analizador de Perfil                              │
│  Input: Texto del cuestionario                          │
│  Output: profile { edad, género, nivel, objetivos... }  │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  E2 – Parse Questionnaire (DEPRECATED?)                 │
│  Parece duplicar E1. Posible código legacy.             │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  E3 – Training Summary                                   │
│  Input: profile (de E1)                                  │
│  Output: training_context {                              │
│    - training_type (full_body, upper_lower, etc.)       │
│    - days_per_week                                       │
│    - session_duration_min                                │
│    - constraints (injuries, equipment)                   │
│  }                                                        │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  E4 – Training Plan Generator V4.0 (K1-Based)           │
│  ⚠️ AQUÍ ESTÁ EL PROBLEMA PRINCIPAL                      │
│  Input: training_context (de E3)                         │
│  Tools: fileSearchTrainingKB, fileSearchExercises        │
│  Output: training_plan {                                 │
│    sessions: [                                           │
│      { blocks: [                                         │
│        { exercise_id: "???" }  ← ❌ CÓDIGOS INVENTADOS  │
│      ]}                                                  │
│    ]                                                     │
│  }                                                       │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  E5 – Training Plan Validator                            │
│  Input: training_plan (de E4)                            │
│  Ajusta: series, reps, rpe, notes (por seguridad)       │
│  Output: final_training_plan                             │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  E6 – Exercise Normalizer (DESACTIVADO)                 │
│  Comentado en código. No se ejecuta.                    │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  E7 – Training Plan Assembler                            │
│  Input: final_training_plan (de E5)                      │
│  Transforma a estructura cliente-friendly                │
│  Output: client_training_program                         │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  E7.5 – Training Plan Enricher                           │
│  Input: client_training_program (de E7)                  │
│  Agrega: name, video_url, primary_group                  │
│  Fuente: exercise_catalog_edn360.json (1243 ejercicios) │
│  ⚠️ PROBLEMA: Si exercise_code no existe, falla         │
│  Output: client_training_program_enriched                │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  BACKEND PYTHON – Templates & Integration               │
│  - Bloque A: Calentamiento (template fijo)              │
│  - Bloque B: De E7.5 (enriched)                         │
│  - Bloque C: Core (template fijo)                       │
│  - Bloque D: Cardio (template fijo)                     │
│  Output: plan completo → training_plans_v2               │
└─────────────────────────────────────────────────────────┘
```

---

## 2️⃣ DESGLOSE DE AGENTES Y PROMPTS

### E1 – Analizador de Perfil

**Responsabilidad:**  
Extraer información estructurada del cuestionario en texto libre.

**Input:**  
Texto del cuestionario (puede estar en español o inglés)

**Output (Profile):**
```json
{
  "name": "string",
  "age": number,
  "gender": "male|female|other",
  "height_cm": number,
  "weight_kg": number,
  "experience_level": "beginner|intermediate|advanced|professional",
  "primary_goal": "muscle_gain|fat_loss|strength|performance|health",
  "injuries_or_limitations": ["string"],
  "available_equipment": ["gym"|"home"|"bodyweight"],
  "training_days_per_week": number,
  "session_duration_min": number
}
```

**Prompt clave:**
- Extraer edad, género, peso, altura
- Mapear nivel de experiencia: "culturista profesional" → `professional`
- Detectar lesiones: "molestias hombro" → `shoulder_issues`
- Identificar preferencias: "no ejercicios raros" → ¿dónde se captura esto? ❌

**PROBLEMA IDENTIFICADO:**  
El cuestionario dice "culturista profesional", "no ejercicios raros", pero esto **NO se refleja** adecuadamente en las decisiones del plan.

---

### E3 – Training Summary

**Responsabilidad:**  
Decidir el tipo de rutina y estructura semanal.

**Input:** profile (de E1)

**Output (training_context):**
```json
{
  "training_type": "full_body|upper_lower|push_pull_legs|bro_split|other",
  "training_type_reason": "string",
  "days_per_week": number,
  "session_duration_min": number,
  "availability": {...},
  "constraints": {
    "shoulder_issues": boolean,
    "lower_back_issues": boolean,
    "other": ["string"]
  }
}
```

**Prompt clave:**
- Si `experience_level === "professional"` → rutinas avanzadas (PPL, Weider)
- Si `injuries_or_limitations` incluye "hombro" → `shoulder_issues: true`

**PROBLEMA IDENTIFICADO:**  
E3 correctamente identifica `shoulder_issues` y `lower_back_issues`, pero estas constraints **sobrepisan** el objetivo de hipertrofia avanzada en agentes posteriores.

---

### E4 – Training Plan Generator V4.0 (K1-Based)

**Responsabilidad:** ⚠️ **AQUÍ ESTÁ EL NÚCLEO DEL PROBLEMA**  
Generar el plan de entrenamiento (solo Bloque B - fuerza principal).

**Input:** training_context (de E3)

**Tools disponibles:**
1. `fileSearchTrainingKB`: Query K1_ENTRENAMIENTO_ABSTRACTO.json (reglas abstractas)
2. `fileSearchExercises`: Query exercise_catalog_edn360.json (1243 ejercicios canónicos)

**Prompt (resumido):**
```
You are E4 – Training Plan Generator.

⚠️ CRITICAL: Generate ONLY BLOCK B (Main Strength Training).
❌ Do NOT generate: Warm-up (Block A), Core (Block C), or Cardio (Block D).

WORKFLOW:
1. CONSULT K1 via fileSearchTrainingKB
2. CREATE SESSIONS (one per training day)
3. SELECT EXERCISES via fileSearchExercises:
   - Filter by movement_pattern
   - Filter by difficulty_clean matching user level
   - Check health_flags for injuries
   - Use exercise_code from catalog (e.g. "press_banca_barra")

OUTPUT STRUCTURE:
{
  "training_plan": {
    "sessions": [{
      "blocks": [{
        "exercises": [{
          "exercise_id": "<from catalog>",  ← ⚠️ DEBE SER CANÓNICO
          "patron": "...",
          "tipo": "...",
          ...
        }]
      }]
    }]
  }
}

⚠️ CRITICAL JSON FORMAT:
- Do NOT include k1_justification
- Keep output concise
- Ensure all brackets and commas are properly closed
```

**Output (E4TrainingPlanGeneratorSchema):**
```typescript
{
  training_plan: {
    sessions: [{
      blocks: [{
        exercises: [{
          order: number,
          exercise_id: string,  // ⚠️ DEBE ser código del catálogo
          patron: enum[...],
          tipo: enum[...],
          volumen_abstracto: enum[...],
          series_abstracto: enum[...],
          reps_abstracto: enum[...],
          intensidad_abstracta: enum[...],
          proximidad_fallo_abstracta: enum[...],
          notas_tecnicas: string
        }]
      }]
    }]
  }
}
```

**🚨 PROBLEMA CRÍTICO IDENTIFICADO:**

El agente E4 está generando códigos **INVENTADOS** que NO están en el catálogo:

**Códigos generados por E4:**
- `horizontal_press_machine` ❌ NO EXISTE
- `pec_deck` ❌ NO EXISTE
- `cable_fly` ❌ NO EXISTE

**Códigos correctos en el catálogo:**
- `press_horizontal_maquina_palanca` ✅
- `aperturas_medias_poleas` ✅

**¿Por qué pasa esto?**

1. **El prompt NO es suficientemente explícito:**
   - Dice "use exercise_code from catalog" pero no valida
   - No hay ejemplos concretos de códigos válidos

2. **El tool `fileSearchExercises` no se está usando correctamente:**
   - E4 debería buscar en el catálogo antes de generar
   - Pero parece que genera códigos "de memoria" sin consultar

3. **El schema NO valida contra el catálogo:**
   - `exercise_id: string` acepta cualquier string
   - No hay validación de que el código exista

4. **GPT-5 está "inventando" códigos lógicos pero incorrectos:**
   - `pec_deck` suena razonable → pero el código real es diferente
   - `horizontal_press_machine` es descriptivo → pero no es el código canónico

---

### E5 – Training Plan Validator

**Responsabilidad:**  
Ajustes de seguridad (series, reps, RPE, notas).

**Input:** training_plan (de E4)

**Output:** final_training_plan (mismo formato, con ajustes)

**Prompt clave (resumido):**
```
Your ONLY job is:
1. Read training_plan from E4
2. Make SMALL, TARGETED safety adjustments:
   - Focus on shoulder safety and lumbar safety
   - Adjust only: series, reps, rpe, notes
   - Do NOT change structure or exercise_types

VALIDATION RULES:
1. Shoulder safety:
   - NO overhead pressing patterns
   - NO deep dips or extreme shoulder extension
   - Prefer machines, neutral grips

2. Lumbar safety:
   - NO heavy axial loading (no barbell squats, no deadlifts from floor)
   - Use machine-based patterns

3. Volume & intensity:
   - Beginner: 2-3 series, RPE 6-7
   - Intermediate: 3-4 series, RPE 7-8
   - Advanced/Professional: 4-5 series, RPE 8-9
   - DO NOT reduce intensity just because user has injuries
```

**🚨 PROBLEMA IDENTIFICADO:**

E5 está siendo **DEMASIADO CONSERVADOR** con usuarios avanzados:

**Usuario del plan analizado:**
- `experience_level: "professional"` (ex culturista)
- `primary_goal: "muscle_gain"` (hipertrofia)

**Plan generado:**
- Series: 4 (correcto para avanzado según prompt)
- RPE: 8 (correcto)
- **PERO:** Ejercicios seleccionados son demasiado "seguros"
  - "sentadilla y press landmine" como ejercicio principal de pecho
  - Falta de básicos pesados (press banca barra, sentadilla barra, peso muerto)

**¿Por qué?**

Las reglas de seguridad están **sobrepasando** las reglas de nivel avanzado:

```
"NO heavy axial loading (no barbell squats, no deadlifts)"
"NO overhead pressing patterns"
```

Para un usuario `professional` sin dolor agudo, esto es **DEMASIADO RESTRICTIVO**.

**Sugerencia de fix:**
- E5 debe diferenciar entre:
  - `shoulder_issues: "mild_discomfort"` → ejercicios seguros pero desafiantes
  - `shoulder_issues: "chronic_pain"` → evitar overhead completamente
- Para `professional` level → permitir básicos con carga alta si no hay dolor agudo

---

### E7 – Training Plan Assembler

**Responsabilidad:**  
Transformar el plan abstracto de E5 a estructura cliente-friendly.

**Input:** final_training_plan (de E5)

**Output:** client_training_program

**Transformaciones:**
- `series_abstracto: "altas"` → `series: 4`
- `reps_abstracto: "medias"` → `reps: "8-12"`
- `proximidad_fallo_abstracta: "cerca_del_fallo"` → `rpe: "8"`

---

### E7.5 – Training Plan Enricher

**Responsabilidad:** ⚠️ **CRÍTICO PARA VIDEOS/NOMBRES**  
Agregar datos enriquecidos (nombre, video, grupos musculares).

**Input:** client_training_program (de E7)

**Output:** client_training_program_enriched

**Lógica:**
```typescript
for each exercise in plan:
  exercise_code = exercise.exercise_types[0]  // ⚠️ ASUME QUE ES CANÓNICO
  
  // Buscar en catálogo
  catalog_exercise = findInCatalog(exercise_code)
  
  if (catalog_exercise):
    exercise.name = catalog_exercise.name_es
    exercise.video_url = catalog_exercise.video_url
    exercise.primary_group = catalog_exercise.primary_muscles_clean
  else:
    // ⚠️ AQUÍ ESTÁ EL PROBLEMA
    exercise.name = "" // ❌ VACÍO
    exercise.video_url = "" // ❌ VACÍO
```

**🚨 PROBLEMA IDENTIFICADO:**

Si E4 genera un `exercise_code` que NO existe en el catálogo:
- `pec_deck` → NO en catálogo → `name: ""`, `video_url: ""`
- El usuario ve ejercicios sin datos

**Solución necesaria:**

1. **Prevenir en E4:** Validar que todos los códigos existan antes de generar
2. **Fallback en E7.5:** Si el código no existe, usar fuzzy matching para encontrar el más cercano
3. **Alertar:** Loggear códigos no encontrados para corrección

---

## 3️⃣ BACKEND PYTHON – TEMPLATES & INTEGRATION

### Bloque A – Calentamiento

**Fuente:** Template fijo en `/app/backend/templates/block_a_warmup.py`

**Ejercicios:**
- Rotaciones de cuello
- Círculos de hombros
- Rotaciones de tronco
- Dislocaciones de hombro con banda
- Círculos de cadera
- Balanceos de pierna
- Bird dog
- Cardio ligero

**Nota:** Este bloque es **idéntico** para todos los usuarios y todas las sesiones.

**Sugerencia de mejora:**  
Adaptar el calentamiento según el enfoque de la sesión (ej: más movilidad de hombro para día de pecho).

---

### Bloque B – Entrenamiento Principal

**Fuente:** E7.5 (enriched)

**Problema ya identificado:** Ejercicios con códigos NO canónicos.

---

### Bloque C – Core

**Fuente:** Template fijo en `/app/backend/templates/block_c_core.py`

**Ejercicios (ejemplo):**
- Anti-rotación: Plancha lateral, Pallof press
- Anti-extensión: Plancha frontal, Dead bug
- Anti-flexión: Superman, Bird dog

**Nota:** Template adaptado según disponibilidad de equipo y lesiones.

---

### Bloque D – Cardio

**Fuente:** Template fijo en `/app/backend/templates/block_d_cardio.py`

**Estructura nueva (desde E4 v2):**
```json
{
  "recomendaciones": [
    {
      "type": "Cardio LISS / MISS",
      "frequency": "2-3x/semana",
      "duration": "20-30 min",
      "intensity": "Zona 2",
      "modalities": ["Bici", "Caminata", "Natación"],
      "notes": "Separar 6h del entrenamiento"
    }
  ]
}
```

**Nota:** Este bloque **ya está corregido** y funciona correctamente con PDF/Email.

---

## 4️⃣ CATÁLOGOS Y DATOS

### Exercise Catalog (Canónico)

**Ubicación:**
- Workflow: `/app/edn360-workflow-service/exercise_catalog_edn360.json`
- Backend: `/app/backend/exercise_catalog_edn360.json`

**Contenido:**
- **1243 ejercicios** (ambos catálogos son idénticos)
- Cada ejercicio tiene:
  ```json
  {
    "exercise_code": "press_banca_barra",
    "name_es": "Press banca barra",
    "video_url": "https://...",
    "primary_muscles_clean": "pecho",
    "secondary_muscles_clean": "triceps, hombro",
    "difficulty_clean": "intermediate",
    "movement_pattern": "empuje_horizontal",
    ...
  }
  ```

**Verificación:**
```bash
$ wc -l exercise_catalog_edn360.json
38927 /app/edn360-workflow-service/exercise_catalog_edn360.json
41413 /app/backend/exercise_catalog_edn360.json
```

**Códigos totales:** 1243 (verificado: 0 diferencias entre ambos)

---

### K1 Knowledge Base (Reglas Abstractas)

**Ubicación:** `/app/edn360-workflow-service/K1_ENTRENAMIENTO_ABSTRACTO.json`

**Contenido:**  
Reglas de entrenamiento por nivel y objetivo:
- `nivel_principiante` → volumen bajo, intensidad moderada
- `nivel_intermedio` → volumen medio, intensidad moderada-alta
- `nivel_avanzado` → volumen alto, intensidad alta

**Ejemplo:**
```json
{
  "nivel_experiencia": "avanzado",
  "objetivo_principal": "hipertrofia",
  "volumen_semanal": "muy_alto (20-28 series por grupo muscular)",
  "intensidad": "alta (RPE 8-9)",
  "metodos_permitidos": [
    "basico",
    "intensificacion_local",
    "avanzado_carga"
  ]
}
```

**🚨 HIPÓTESIS:**  
E4 está consultando K1 correctamente, **PERO** las reglas de seguridad de E5 están reduciendo el volumen/intensidad que K1 recomienda para usuarios avanzados.

---

## 5️⃣ ANÁLISIS DEL PLAN ESPECÍFICO

### Plan ID: `0be1edd6-2f3f-42da-ae8f-185773cf8fe0`

**Título:** "Rutina Weider 4 días (Hipertrofia avanzada, seguro lumbar/hombros)"

**Usuario:**
- Nivel: `professional` (ex culturista profesional)
- Objetivo: `muscle_gain` (hipertrofia)
- Lesiones: Molestias hombro, zona lumbar
- Preferencias: "No ejercicios raros, básicos"

### Cuestionario (inferido del plan)

**Datos estructurados generados por E1:**
```json
{
  "experience_level": "professional",
  "primary_goal": "muscle_gain",
  "injuries_or_limitations": [
    "molestias_hombro",
    "molestias_lumbar"
  ],
  "training_days_per_week": 4,
  "session_duration_min": 45,
  "available_equipment": ["gym"]
}
```

**Contexto generado por E3:**
```json
{
  "training_type": "Rutina Weider",  // ✅ Correcto para avanzado
  "days_per_week": 4,                 // ✅ Correcto
  "session_duration_min": 45,         // ✅ Correcto
  "constraints": {
    "shoulder_issues": true,          // ⚠️ Activa reglas restrictivas
    "lower_back_issues": true         // ⚠️ Activa reglas restrictivas
  }
}
```

### Sesión 1: Pecho y Tríceps

**Ejercicios en Bloque B (Fuerza):**

| Orden | exercise_types | exercise_code | name | video | Problema |
|-------|----------------|---------------|------|-------|----------|
| 1 | `horizontal_press_machine` | `sentadilla_press_landmine` | sentadilla y press landmine | ✅ | ❌ **CÓDIGO DESALINEADO** (pecho → piernas+hombros) |
| 2 | `pec_deck` | `pec_deck` | Pec Deck | ❌ | ❌ **CÓDIGO NO EXISTE** (sin video, sin datos) |
| 3 | `cable_fly` | `cable_fly` | Cable Fly | ❌ | ❌ **CÓDIGO NO EXISTE** (sin video, sin datos) |

**Series:** 4  
**Reps:** 8-12  
**RPE:** 8  

**🚨 PROBLEMAS IDENTIFICADOS:**

1. **Ejercicio 1 - Desalineación total:**
   - E4 pidió `horizontal_press_machine` (press pecho horizontal)
   - E7.5 mapeó a `sentadilla_press_landmine` (piernas + hombros)
   - **Causa:** `horizontal_press_machine` NO existe en catálogo
   - **Código correcto:** `press_horizontal_maquina_palanca`

2. **Ejercicio 2 - Código inventado:**
   - `pec_deck` NO existe en catálogo
   - **Código correcto:** ¿`aperturas_contractor`? (no encontrado en grep)
   - **Alternativa:** `aperturas_medias_poleas`

3. **Ejercicio 3 - Código inventado:**
   - `cable_fly` NO existe en catálogo
   - **Código correcto:** `aperturas_medias_poleas` o `aperturas_poleas_tumbado`

4. **Falta de ejercicios básicos pesados:**
   - Usuario es `professional`, pide básicos
   - **Esperado:** `press_banca_barra`, `press_inclinado_barra`
   - **Generado:** Solo máquinas y poleas

---

### ¿Por qué el plan es tan "mediocre"?

**Hipótesis 1: Reglas de Seguridad Sobrepasan Nivel Avanzado**

E5 tiene estas reglas:
```
"NO overhead pressing patterns"
"NO deep dips"
"NO heavy axial loading (no barbell squats, no deadlifts)"
"Prefer machines"
```

Para un usuario `professional` con molestias **leves**, esto es **EXCESIVO**.

**Sugerencia:**
- Diferenciar severidad de lesión:
  - Molestias leves → ejercicios desafiantes con buena técnica
  - Dolor crónico → evitar patrones problemáticos
- Para `professional` → permitir básicos con barra si no hay dolor agudo

---

**Hipótesis 2: E4 No Consulta fileSearchExercises Correctamente**

El prompt dice:
```
"SELECT EXERCISES via fileSearchExercises:
 - Use exercise_code from catalog"
```

Pero E4 genera códigos inventados → **NO está consultando el catálogo**.

**Posibles causas:**
1. El tool `fileSearchExercises` no está configurado correctamente
2. E4 prefiere "inventar" códigos lógicos sin consultar
3. El prompt no es suficientemente explícito sobre **CUÁNDO** consultar

**Sugerencia:**
- Modificar el prompt para REQUERIR consulta:
  ```
  "MANDATORY: For EACH exercise, you MUST:
   1. Use fileSearchExercises to find valid exercise_code
   2. Do NOT invent codes
   3. If no exact match, use the closest valid code from search results"
  ```

---

**Hipótesis 3: Prompt de E4 No Tiene Ejemplos Concretos**

El prompt actual es abstracto:
```
"Use exercise_code from catalog (e.g. 'press_banca_barra')"
```

Un solo ejemplo no es suficiente. GPT-5 puede "inventar" códigos razonables.

**Sugerencia:**
- Agregar 10-15 ejemplos concretos en el prompt:
  ```
  "Valid exercise_code examples from catalog:
   - Pecho: press_banca_barra, press_inclinado_mancuernas, aperturas_medias_poleas
   - Espalda: dominadas_agarre_prono, remo_barra_inclinado, jalon_al_pecho_barra_ancha
   - Piernas: sentadilla_barra, peso_muerto_rumano, prensa_pierna_45_maquina
   - Hombros: press_militar_barra, elevaciones_laterales_mancuernas
   
   NEVER use: pec_deck, cable_fly, horizontal_press_machine (these are NOT valid codes)"
  ```

---

**Hipótesis 4: Falta Validación en Runtime**

Incluso si E4 genera códigos incorrectos, el sistema debería detectarlo.

**Puntos de validación faltantes:**

1. **En E4 (schema Zod):**
   ```typescript
   // ACTUAL (no valida):
   exercise_id: z.string()
   
   // MEJORADO:
   exercise_id: z.string().refine(
     (code) => VALID_EXERCISE_CODES.includes(code),
     { message: "Invalid exercise_code. Must be from catalog." }
   )
   ```

2. **En E7.5 (enricher):**
   ```typescript
   // ACTUAL (falla silenciosamente):
   if (!catalog_exercise) {
     exercise.name = ""
     exercise.video_url = ""
   }
   
   // MEJORADO (con fallback y logging):
   if (!catalog_exercise) {
     logger.error(`❌ exercise_code not found: ${exercise_code}`)
     
     // Fuzzy match
     const closest = findClosestMatch(exercise_code, catalog)
     if (closest) {
       exercise.exercise_code = closest.exercise_code
       exercise.name = closest.name_es
       exercise.video_url = closest.video_url
       logger.warn(`🔄 Using fuzzy match: ${exercise_code} → ${closest.exercise_code}`)
     }
   }
   ```

---

## 6️⃣ CHECKLIST DE PUNTOS DE RUPTURA

### ¿Dónde se pierde el exercise_code canónico?

✅ **Backend catalog:** Tiene 1243 ejercicios correctos  
✅ **Workflow catalog:** Tiene 1243 ejercicios correctos (mismo contenido)  
❌ **E4 generation:** Genera códigos **inventados** que NO están en catálogo  
⚠️ **E7.5 enrichment:** Intenta buscar el código → no lo encuentra → datos vacíos  
❌ **Frontend display:** Muestra ejercicios sin nombre/video  

**Punto crítico de ruptura:** E4 NO está usando `fileSearchExercises` correctamente.

---

### ¿Dónde podría estar entrando lógica antigua?

**E2 – Parse Questionnaire:**
- Código comentado: "DEPRECATED?"
- Parece duplicar E1
- **Recomendación:** Eliminar completamente si no se usa

**E6 – Exercise Normalizer:**
- Código comentado: "DESACTIVADO"
- Su función era mapear códigos legacy → canónicos
- **¿Por qué está desactivado?** Si E4 ya genera canónicos, no se necesita.
- **PERO:** E4 NO está generando canónicos → tal vez E6 debería reactivarse como failsafe

---

### ¿Qué catálogo usan los diferentes componentes?

| Componente | Catálogo | ¿Correcto? |
|------------|----------|------------|
| E4 (tool fileSearchExercises) | `exercise_catalog_edn360.json` (workflow) | ✅ 1243 ejercicios |
| E7.5 (enricher) | `exercise_catalog_edn360.json` (workflow) | ✅ 1243 ejercicios |
| Backend (templates) | `exercise_catalog_edn360.json` (backend) | ✅ 1243 ejercicios |
| Frontend (display) | Recibe del backend | ✅ (si backend tiene datos) |

**Conclusión:** Todos usan el mismo catálogo canónico. El problema NO es el catálogo, es que **E4 no lo consulta correctamente**.

---

## 7️⃣ ANÁLISIS DE VIDEOS FALTANTES

### Ejercicios sin video en el plan

Del análisis del plan actual:

| exercise_code | name | video_url | ¿Por qué? |
|---------------|------|-----------|-----------|
| `pec_deck` | Pec Deck | ❌ Vacío | Código NO existe en catálogo |
| `cable_fly` | Cable Fly | ❌ Vacío | Código NO existe en catálogo |
| `sentadilla_press_landmine` | sentadilla y press landmine | ✅ Sí tiene | Código existe pero es mal match |

### Verificación del catálogo completo

**¿Todos los ejercicios del catálogo tienen video?**

```bash
$ jq '[.[] | select(.video_url == "")] | length' /app/backend/exercise_catalog_edn360.json
```

*Necesita ejecutarse para determinar cuántos ejercicios NO tienen video_url*

**Hipótesis:**  
Algunos ejercicios del catálogo pueden tener `video_url: ""`, pero la mayoría debería tener.

**El problema NO es el catálogo**, es que E4 genera códigos que ni siquiera están en el catálogo.

---

## 8️⃣ RECOMENDACIONES DE FIX

### Fix Crítico 1: Forzar E4 a Usar Catálogo

**Problema:** E4 genera códigos inventados.

**Solución:**

1. **Prompt más explícito con ejemplos:**
   ```
   CRITICAL: You MUST use ONLY exercise_code values from the catalog.
   
   Valid examples:
   - Pecho: press_banca_barra, press_inclinado_mancuernas, aperturas_medias_poleas
   - Espalda: dominadas_agarre_prono, remo_barra_inclinado
   - Piernas: sentadilla_barra, peso_muerto_rumano, prensa_pierna_45_maquina
   
   INVALID (do NOT use):
   - pec_deck (use: aperturas_medias_poleas or specific chest fly)
   - cable_fly (use: aperturas_medias_poleas or aperturas_poleas_tumbado)
   - horizontal_press_machine (use: press_horizontal_maquina_palanca)
   
   WORKFLOW FOR EACH EXERCISE:
   1. Use fileSearchExercises with movement_pattern filter
   2. From results, pick ONE valid exercise_code
   3. Do NOT modify or invent codes
   ```

2. **Schema con validación:**
   ```typescript
   // Cargar códigos válidos en memoria
   const VALID_CODES = loadExerciseCatalog().map(ex => ex.exercise_code);
   
   const E4Schema = z.object({
     training_plan: z.object({
       sessions: z.array(z.object({
         blocks: z.array(z.object({
           exercises: z.array(z.object({
             exercise_id: z.string().refine(
               (code) => VALID_CODES.includes(code),
               (code) => ({ 
                 message: `Invalid exercise_code: "${code}". Must be from catalog. Use fileSearchExercises.`
               })
             )
           }))
         }))
       }))
     })
   });
   ```

3. **Logging en E4:**
   ```typescript
   console.log(`🔍 E4 searching exercises for pattern: ${pattern}`);
   const results = await fileSearchExercises(query);
   console.log(`✅ Found ${results.length} exercises`);
   console.log(`📋 Using exercise_code: ${selectedCode}`);
   ```

---

### Fix Crítico 2: Balancear Seguridad vs Nivel Avanzado

**Problema:** Reglas de seguridad muy restrictivas para usuarios profesionales.

**Solución:**

1. **Agregar severidad de lesión al contexto:**
   ```json
   "constraints": {
     "shoulder_issues": {
       "severity": "mild|moderate|severe",
       "notes": "Molestias ocasionales al hacer overhead press"
     }
   }
   ```

2. **Modificar reglas de E5 según severidad:**
   ```
   IF experience_level === "professional" AND injury_severity === "mild":
     - ALLOW basic barbell exercises with good form
     - ALLOW overhead press with controlled ROM
     - Focus on: proper warm-up, progressive loading, RPE 8-9
   
   IF injury_severity === "severe":
     - AVOID overhead completely
     - AVOID heavy axial loading
     - Use machines and controlled patterns
   ```

3. **Agregar flag de "preferencias":**
   ```json
   "preferences": {
     "exercise_style": "heavy_basics",  // vs "machines_safe"
     "no_weird_exercises": true
   }
   ```

---

### Fix Medio 3: Reactivar E6 como Failsafe

**Problema:** Si E4 falla en generar códigos correctos, no hay red de seguridad.

**Solución:**

1. **Desactivar comentario de E6:**
   ```typescript
   // ANTES:
   // const e6Result = await runAgentWithLogging(...);
   
   // DESPUÉS:
   const e6Result = await runAgentWithLogging(
     runner,
     e6ExerciseNormalizerDbMapper,
     "E6 – Exercise Normalizer & DB Mapper",
     [e5Result.final_training_plan]
   );
   ```

2. **E6 debe tener lógica de fuzzy matching:**
   ```typescript
   if (!exactMatch) {
     const closest = fuzzyMatch(exercise_type, catalog);
     if (closest.score > 0.8) {
       mapping.db_match = closest;
       logger.warn(`🔄 Fuzzy match: ${exercise_type} → ${closest.exercise_code}`);
     } else {
       logger.error(`❌ No match for: ${exercise_type}`);
       throw new Error(`Invalid exercise_code: ${exercise_type}`);
     }
   }
   ```

---

### Fix Menor 4: Mejorar Logging y Alertas

**Problema:** Errores silenciosos (códigos no encontrados, etc.).

**Solución:**

1. **Log cada paso del pipeline:**
   ```
   🚀 E1 completado → profile.experience_level: professional
   🚀 E3 completado → training_type: Rutina Weider, shoulder_issues: true
   🚀 E4 completado → 4 sessions, 20 exercises generated
   ⚠️  E4 WARNING: Generated non-canonical codes: pec_deck, cable_fly
   🚀 E7.5 completado → 3/20 exercises missing video_url
   ```

2. **Enviar alertas a admin:**
   ```typescript
   if (missing_videos > 0) {
     await sendAdminAlert({
       type: "plan_quality_issue",
       plan_id: plan_id,
       message: `${missing_videos} exercises missing video_url`,
       codes: missing_codes
     });
   }
   ```

---

## 9️⃣ PRÓXIMOS PASOS

### Inmediato (Hoy)

1. ✅ **Auditoría completa** (este documento)
2. ⏳ **Fix E4 prompt con ejemplos explícitos**
3. ⏳ **Agregar validación de códigos en schema**
4. ⏳ **Probar generación con nuevo prompt**

### Corto Plazo (Esta Semana)

1. **Implementar severidad de lesiones**
2. **Ajustar reglas de E5 para usuarios avanzados**
3. **Reactivar E6 como failsafe**
4. **Testing exhaustivo con diferentes perfiles**

### Mediano Plazo (Próximas 2 Semanas)

1. **Crear whitelists de ejercicios por nivel:**
   - Principiante: Máquinas, peso corporal
   - Intermedio: Barras, mancuernas, máquinas
   - Avanzado: Todo incluido, técnicas avanzadas

2. **Implementar "exercise style preferences":**
   - heavy_basics
   - machines_safe
   - functional
   - bodybuilding

3. **Dashboard de calidad de planes:**
   - % de ejercicios con video
   - % de códigos canónicos
   - Alertas automáticas

---

## 🔟 CONCLUSIONES

### Problemas Raíz

1. **E4 no valida códigos contra catálogo** → genera inventados
2. **E5 es demasiado restrictivo para avanzados** → planes mediocres
3. **No hay failsafes** → errores silenciosos

### Impacto

- ❌ Ejercicios sin videos
- ❌ Nombres genéricos (legacy)
- ❌ Planes no adecuados al nivel del usuario
- ⚠️ Experiencia de usuario pobre

### Solución

**3 fixes críticos:**
1. Prompt E4 con ejemplos + validación de schema
2. Reglas E5 diferenciadas por severidad de lesión
3. Reactivar E6 como red de seguridad

**Impacto esperado:**
- ✅ 100% de ejercicios con códigos canónicos
- ✅ Videos y nombres enriquecidos
- ✅ Planes adecuados al nivel del usuario

---

**Documento preparado para:**  
Jorge Calcerrada (Cliente EDN360)

**Próxima acción:**  
Implementar Fix Crítico 1 y probar generación de plan.
