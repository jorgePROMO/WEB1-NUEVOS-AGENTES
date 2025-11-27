# 🎯 DISEÑO TO-BE: INTEGRACIÓN EDN360 TRAINING WORKFLOW

**Fecha**: Noviembre 2025  
**Versión**: 1.0  
**Propósito**: Especificación completa del flujo de generación de planes de entrenamiento usando EDN360 (E1-E7.5)

---

## 📑 ÍNDICE

1. [Visión General](#1-visión-general)
2. [Flujo Completo End-to-End](#2-flujo-completo-end-to-end)
3. [Especificación del Endpoint](#3-especificación-del-endpoint)
4. [Especificación EDN360Input](#4-especificación-edn360input)
5. [Especificación del Workflow](#5-especificación-del-workflow)
6. [Especificación del Output](#6-especificación-del-output)
7. [Configuración del Workflow en OpenAI](#7-configuración-del-workflow-en-openai)
8. [Gestión de Errores](#8-gestión-de-errores)
9. [Testing y Validación](#9-testing-y-validación)
10. [Riesgos y Mitigaciones](#10-riesgos-y-mitigaciones)

---

## 1️⃣ VISIÓN GENERAL

### Principio Fundamental

**La web NO ejecuta IA. Solo recoge datos y muestra resultados.**

```
┌─────────────┐
│   FRONTEND  │  Recoge cuestionario
│    (React)  │  Muestra plan
└──────┬──────┘
       │
       │ POST /api/training-plan
       │ { user_id, questionnaire_submission_id }
       ▼
┌─────────────────────────────┐
│    BACKEND (FastAPI)        │
│                             │
│  1. Lee user + cuestionario │
│  2. Construye EDN360Input   │
│  3. Llama a EDN360 Workflow │◄─────┐
│  4. Guarda snapshot         │      │
│  5. Devuelve plan           │      │
└──────┬──────────────────────┘      │
       │                             │
       │ client_training_program_    │
       │ enriched                    │
       ▼                             │
┌─────────────┐                      │
│   FRONTEND  │                      │
│             │                      │
│  • Renderiza plan                  │
│  • Genera PDF                      │
│  • Envía email                     │
│  • Link WhatsApp                   │
└─────────────┘                      │
                                     │
                    ┌────────────────┘
                    │
                    │ EDN360Input
                    ▼
        ┌───────────────────────────┐
        │ EDN360 WORKFLOW (E1-E7.5) │
        │ (OpenAI Platform)         │
        │                           │
        │  E1 → Profile Analyzer    │
        │  E2 → Questionnaire Parser│
        │  E3 → Training Summary    │
        │  E4 → Plan Generator      │
        │  E5 → Plan Validator      │
        │  E6 → Exercise DB Mapper  │◄──┐
        │  E7 → Plan Assembler      │   │
        │  E7.5 → Plan Enricher     │◄──┤
        │                           │   │
        └───────────┬───────────────┘   │
                    │                   │
                    │ client_training_  │
                    │ program_enriched  │
                    │                   │
                    └───────────────────┘
                            ▲
                            │
                    ┌───────┴────────┐
                    │  BD EJERCICIOS │
                    │  EDN360        │
                    │  (file_search) │
                    └────────────────┘
```

---

## 2️⃣ FLUJO COMPLETO END-TO-END

### 2.1 Registro y Cuestionario (Estado Actual - No Cambia)

1. **Usuario se registra** → `POST /api/auth/register`
2. **Usuario paga** → Stripe checkout
3. **Admin verifica pago** → `POST /api/admin/verify-payment/{user_id}`
4. **Usuario accede a dashboard** → `/dashboard`
5. **Usuario rellena cuestionario** → Modal `NutritionQuestionnaire`
6. **Cuestionario se envía** → `POST /api/nutrition/questionnaire/submit`
7. **Backend guarda**:
   - En `nutrition_questionnaire_submissions` (BD Web)
   - **Dual-write** a `client_drawers.services.shared_questionnaires` (BD Técnica)

**Resultado**: El cuestionario está guardado y listo para usarse.

---

### 2.2 Generación de Plan (Nuevo Sistema EDN360)

**Trigger**: Admin hace click en "Generar Plan de Entrenamiento"

**Paso 1: Frontend llama al backend**

```javascript
// AdminDashboard.jsx
const handleGenerateTrainingPlan = async (userId, submissionId) => {
  try {
    const response = await axios.post(
      `${API}/training-plan`,
      {
        user_id: userId,
        questionnaire_submission_id: submissionId
      },
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    
    const plan = response.data.client_training_program_enriched;
    
    // Mostrar plan en UI
    displayTrainingPlan(plan);
    
  } catch (error) {
    console.error('Error generando plan:', error);
    alert('Error al generar el plan');
  }
};
```

**Paso 2: Backend procesa**

```python
# /app/backend/server.py
@api_router.post("/training-plan")
async def generate_training_plan(request: TrainingPlanRequest, admin=Depends(require_admin)):
    """
    Genera un plan de entrenamiento usando EDN360 Workflow.
    
    1. Valida user_id y questionnaire_submission_id
    2. Construye EDN360Input desde BD
    3. Llama a EDN360_TRAINING_WORKFLOW_V1
    4. Guarda snapshot
    5. Devuelve client_training_program_enriched
    """
    
    # 1. Validar
    user = await db.users.find_one({"_id": request.user_id})
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    
    # 2. Construir EDN360Input
    edn360_input = await build_edn360_input_from_ids(
        user_id=request.user_id,
        submission_id=request.questionnaire_submission_id
    )
    
    # 3. Llamar a EDN360 Workflow
    workflow_result = await call_training_workflow(edn360_input)
    
    # 4. Guardar snapshot
    await create_snapshot(
        user_id=request.user_id,
        workflow_name="training_plan_v1",
        input=edn360_input,
        workflow_response=workflow_result,
        status="success"
    )
    
    # 5. Devolver plan
    return workflow_result  # { "client_training_program_enriched": {...} }
```

**Paso 3: Workflow EDN360 ejecuta**

Internamente (en OpenAI Platform):
- E1 analiza perfil
- E2 parsea cuestionario
- E3 genera contexto training
- E4 crea plan base
- E5 valida seguridad
- E6 mapea ejercicios a BD
- E7 ensambla plan técnico
- E7.5 enriquece con nombres y URLs

**Paso 4: Frontend recibe plan listo**

```javascript
{
  "client_training_program_enriched": {
    "title": "Hipertrofia...",
    "sessions": [
      {
        "exercises": [
          {
            "db_id": "E049",
            "name": "press banca smith...",
            "video_url": "https://drive.google.com/..."
          }
        ]
      }
    ]
  }
}
```

---

## 3️⃣ ESPECIFICACIÓN DEL ENDPOINT

### Endpoint: `POST /api/training-plan`

**Auth**: Admin only (Bearer token)

**Request Body**:

```json
{
  "user_id": "1764016044644335",
  "questionnaire_submission_id": "1764016775848319"
}
```

**Request Model (Pydantic)**:

```python
class TrainingPlanRequest(BaseModel):
    user_id: str = Field(..., description="ID del usuario")
    questionnaire_submission_id: str = Field(
        ..., 
        description="ID del cuestionario a usar para generar el plan"
    )
```

**Response (Success - 200 OK)**:

```json
{
  "client_training_program_enriched": {
    "title": "Hipertrofia con enfoque articular seguro (4 días)",
    "summary": "Plan 4 días, máquinas y rangos controlados...",
    "goal": "Ganar músculo sin agravar lesiones",
    "training_type": "upper_lower",
    "days_per_week": 4,
    "session_duration_min": 45,
    "weeks": 4,
    "sessions": [...],
    "general_notes": [...]
  }
}
```

**Error Responses**:

| Code | Description | Body |
|------|-------------|------|
| 401 | No autenticado | `{ "detail": "Token requerido" }` |
| 403 | No es admin | `{ "detail": "Admin only" }` |
| 404 | Usuario no encontrado | `{ "detail": "Usuario {user_id} no encontrado" }` |
| 404 | Cuestionario no encontrado | `{ "detail": "Cuestionario {submission_id} no encontrado" }` |
| 500 | Error en workflow | `{ "detail": "Error ejecutando workflow EDN360" }` |

---

## 4️⃣ ESPECIFICACIÓN EDN360INPUT

### Estructura Completa

```typescript
interface EDN360Input {
  user_profile: {
    user_id: string;
    full_name: string;
    email: string;
    age: number;
    gender: "male" | "female" | "other";
    height_cm: number;
    weight_kg: number;
  };
  
  questionnaires: Array<{
    submission_id: string;
    source: "initial" | "followup";
    submitted_at: string;  // ISO8601
    payload: Record<string, any>;  // ~100 respuestas crudas
  }>;
  
  context: {
    service_type: "training_only" | "nutrition_only" | "full";
    training_days_per_week: number;
    session_duration_min: number;
  };
}
```

### Ejemplo Real

```json
{
  "user_profile": {
    "user_id": "1764016044644335",
    "full_name": "Jorge",
    "email": "jorge@example.com",
    "age": 37,
    "gender": "male",
    "height_cm": 172,
    "weight_kg": 85
  },
  "questionnaires": [
    {
      "submission_id": "1764016775848319",
      "source": "initial",
      "submitted_at": "2025-11-24T20:39:35.848Z",
      "payload": {
        "full_name": "Jorge",
        "email": "jorge@example.com",
        "birth_date": "1987-01-31",
        "gender": "male",
        "height_cm": 172,
        "weight_kg": 85,
        "bodyfat_percent": 23,
        "chronic_conditions": ["hypothyroidism"],
        "injuries_limitations": [
          "rotator_cuff_issues_both_shoulders",
          "lumbar_disc_hernias_L5_L6"
        ],
        "training_experience_level": "advanced",
        "training_days_per_week": 4,
        "session_duration_min": 45,
        "equipment_available": ["full_gym"],
        "goal_primary": "muscle_gain",
        "goal_secondary": "return_to_competition",
        "sleep_hours": 6.5,
        "daily_activity": "high",
        "motivation_reason": "Wants to return to bodybuilding stage competition",
        "preferred_training_environment": "gym",
        "pain_current_level": "moderate",
        "stress_level": "medium",
        "has_personal_trainer_before": true,
        "alcohol_frequency": "weekly",
        "smoking_status": "non_smoker",
        "food_allergies_intolerances": ["gluten"],
        "schedule_constraints": "Works long shifts, limited time evenings",
        "adherence_challenges": [
          "long_work_hours",
          "social_events_with_alcohol"
        ]
      }
    }
  ],
  "context": {
    "service_type": "training_only",
    "training_days_per_week": 4,
    "session_duration_min": 45
  }
}
```

### Cómo se Construye

**Función**: `build_edn360_input_from_ids(user_id, submission_id)`

**Paso 1**: Leer `users` collection

```python
user = await db.users.find_one({"_id": user_id})
```

**Paso 2**: Leer `client_drawers` collection

```python
drawer = await db_edn360.client_drawers.find_one({"user_id": user_id})
questionnaire = next(
    (q for q in drawer["services"]["shared_questionnaires"]
     if q["submission_id"] == submission_id),
    None
)
```

**Paso 3**: Extraer datos relevantes

```python
# De user
age = calculate_age(user["birth_date"])  # si existe en user
# O calcular de questionnaire.payload.birth_date

# De questionnaire.payload
height_cm = questionnaire["raw_payload"]["payload"]["height_cm"]
weight_kg = questionnaire["raw_payload"]["payload"]["weight_kg"]
training_days = questionnaire["raw_payload"]["payload"]["training_days_per_week"]
session_duration = questionnaire["raw_payload"]["payload"]["session_duration_min"]
```

**Paso 4**: Montar EDN360Input

```python
edn360_input = {
    "user_profile": {
        "user_id": user_id,
        "full_name": user["full_name"],
        "email": user["email"],
        "age": age,
        "gender": extract_gender(questionnaire),
        "height_cm": height_cm,
        "weight_kg": weight_kg
    },
    "questionnaires": [
        {
            "submission_id": submission_id,
            "source": questionnaire["source"],
            "submitted_at": questionnaire["submitted_at"].isoformat(),
            "payload": questionnaire["raw_payload"]["payload"]
        }
    ],
    "context": {
        "service_type": "training_only",
        "training_days_per_week": training_days,
        "session_duration_min": session_duration
    }
}
```

---

## 5️⃣ ESPECIFICACIÓN DEL WORKFLOW

### Contrato del Workflow

**Nombre**: `EDN360_TRAINING_WORKFLOW_V1`

**Input**: `EDN360Input` (ver sección 4)

**Output**: `client_training_program_enriched` (ver sección 6)

---

### Agentes Internos (E1-E7.5)

#### **E1: Profile Analyzer**

**Input**: `EDN360Input`

**Output**:
```json
{
  "profile": {
    "age": 37,
    "gender": "male",
    "experience_level": "advanced",
    "limitations": ["shoulders", "lumbar"],
    "goals": ["muscle_gain", "return_competition"]
  }
}
```

---

#### **E2: Questionnaire Parser**

**Input**: `questionnaires[0].payload` (respuestas crudas)

**Output**:
```json
{
  "questionnaire_normalized": {
    "training_days_per_week": 4,
    "session_duration_min": 45,
    "equipment": ["full_gym"],
    "injuries": ["rotator_cuff", "lumbar_hernias"],
    "chronic_conditions": ["hypothyroidism"],
    "limitations": ["no_overhead_press", "controlled_ranges"]
  }
}
```

---

#### **E3: Training Summary**

**Input**: Profile + Questionnaire Normalized

**Output**:
```json
{
  "training_context": {
    "recommended_split": "upper_lower",
    "sessions_per_week": 4,
    "session_duration": 45,
    "focus": "hypertrophy",
    "constraints": [
      "avoid_overhead",
      "protect_shoulders",
      "protect_lumbar"
    ],
    "equipment_priority": "machines_over_free_weights"
  }
}
```

---

#### **E4: Training Plan Generator**

**Input**: Training Context

**Output**:
```json
{
  "training_plan": {
    "title": "Upper/Lower 4 Days Hypertrophy",
    "training_type": "upper_lower",
    "weeks": 4,
    "days_per_week": 4,
    "sessions": [
      {
        "id": "D1",
        "name": "Upper 1 - Push Emphasis",
        "focus": ["upper_body", "push_focus"],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["chest", "front_delts", "triceps"],
            "secondary_muscles": ["upper_back"],
            "exercise_types": [
              "horizontal_press_machine",
              "horizontal_row_machine"
            ],
            "series": 3,
            "reps": "10-12",
            "rpe": "7"
          }
        ],
        "session_notes": ["No overhead pressing"]
      }
    ]
  }
}
```

**Nota**: Aquí NO hay `db_id`, `name`, ni `video_url` todavía. Solo tipos abstractos de ejercicios.

---

#### **E5: Training Plan Validator**

**Input**: Training Plan

**Output**: Training Plan validado (mismo formato, con posibles ajustes)

**Validaciones**:
- Seguridad (no ejercicios contraindicados)
- Balance muscular
- Volumen apropiado
- Progresión lógica

---

#### **E6: Exercise Normalizer & DB Mapper**

**Input**: Training Plan validado

**Herramienta**: Acceso a BD de ejercicios EDN360 (file_search o function calling)

**Output**:
```json
{
  "mappings": [
    {
      "session_id": "D1",
      "block_id": "A",
      "exercise_index": 0,
      "exercise_type_from_plan": "horizontal_press_machine",
      "db_match": {
        "id": "E049",
        "confidence": "high"
      },
      "similar_candidates": []
    },
    {
      "session_id": "D1",
      "block_id": "A",
      "exercise_index": 1,
      "exercise_type_from_plan": "horizontal_row_machine",
      "db_match": {
        "id": "E0665",
        "confidence": "high"
      },
      "similar_candidates": []
    }
  ]
}
```

**Lógica de Mapeo**:

1. Para cada `exercise_type` en el plan:
2. Buscar en BD de ejercicios por:
   - Movimiento (horizontal press, row, etc.)
   - Equipo (machine, barbell, dumbbell)
   - Grupo muscular
3. Devolver mejor match con `db_id`

**Manejo de errores**:
- Si no hay match → `{ "id": "UNKNOWN", "confidence": "none" }`
- Si hay múltiples matches → Escoger el más seguro/común

---

#### **E7: Training Plan Assembler**

**Input**: Training Plan + Mappings

**Output**:
```json
{
  "client_training_program": {
    "title": "...",
    "sessions": [
      {
        "exercises": [
          {
            "order": 1,
            "db_id": "E049",
            "series": 3,
            "reps": "10-12",
            "rpe": "7"
          }
        ]
      }
    ]
  }
}
```

**Nota**: Aquí ya tenemos `db_id`, pero todavía NO tenemos `name`, `primary_group`, `secondary_group`, `video_url`.

---

#### **E7.5: Training Plan Enricher** ⭐

**Input**: Client Training Program (con db_ids)

**Herramienta**: Acceso a BD de ejercicios EDN360 (file_search o function calling)

**Output**: `client_training_program_enriched` (completo, ver sección 6)

**Lógica**:

Para cada ejercicio con `db_id`:

1. Buscar en BD de ejercicios: `ejercicios.find({ id: db_id })`
2. Extraer:
   - `name`: Nombre legible
   - `primary_group`: Grupo muscular primario
   - `secondary_group`: Grupo muscular secundario
   - `video_url`: URL del video (Google Drive, etc.)
3. Agregar al ejercicio

**Ejemplo de Enrichment**:

**Antes** (de E7):
```json
{
  "order": 1,
  "db_id": "E049",
  "series": 3,
  "reps": "10-12",
  "rpe": "7"
}
```

**Después** (de E7.5):
```json
{
  "order": 1,
  "db_id": "E049",
  "name": "press banca smith agarre cerrado",
  "primary_group": "tríceps",
  "secondary_group": "pectorales",
  "series": 3,
  "reps": "10-12",
  "rpe": "7",
  "video_url": "https://drive.google.com/file/d/1DJpGDOn_u4oi28QpCjWcxZwRtEEWi4gh/view?usp=drivesdk"
}
```

**Manejo de errores**:
- Si `db_id` = "UNKNOWN" → Dejar con valores por defecto:
  ```json
  {
    "db_id": "UNKNOWN",
    "name": "Ejercicio no mapeado",
    "primary_group": "unknown",
    "secondary_group": "unknown",
    "video_url": null
  }
  ```

---

## 6️⃣ ESPECIFICACIÓN DEL OUTPUT

### Estructura TypeScript

```typescript
interface ClientTrainingProgramEnriched {
  title: string;
  summary: string;
  goal: string;
  training_type: string;
  days_per_week: number;
  session_duration_min: number;
  weeks: number;
  sessions: Session[];
  general_notes: string[];
}

interface Session {
  id: string;
  name: string;
  focus: string[];
  blocks: Block[];
  session_notes: string[];
}

interface Block {
  id: string;
  primary_muscles: string[];
  secondary_muscles: string[];
  exercises: Exercise[];
}

interface Exercise {
  order: number;
  db_id: string;
  name: string;
  primary_group: string;
  secondary_group: string;
  series: number | string;
  reps: string;
  rpe: number | string;
  video_url: string | null;
}
```

### Ejemplo Completo

```json
{
  "client_training_program_enriched": {
    "title": "Hipertrofia con enfoque articular seguro (4 días)",
    "summary": "Plan de 4 días centrado en máquinas, rangos controlados y protección de hombros y zona lumbar.",
    "goal": "Ganar músculo sin agravar las lesiones previas.",
    "training_type": "upper_lower",
    "days_per_week": 4,
    "session_duration_min": 45,
    "weeks": 4,

    "sessions": [
      {
        "id": "D1",
        "name": "Upper 1 – Empuje dominante",
        "focus": ["upper_body", "push_focus"],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["chest", "front_delts", "triceps"],
            "secondary_muscles": ["upper_back"],
            "exercises": [
              {
                "order": 1,
                "db_id": "E049",
                "name": "press banca smith agarre cerrado",
                "primary_group": "tríceps",
                "secondary_group": "pectorales",
                "series": 3,
                "reps": "10-12",
                "rpe": "7",
                "video_url": "https://drive.google.com/file/d/1DJpGDOn_u4oi28QpCjWcxZwRtEEWi4gh/view?usp=drivesdk"
              },
              {
                "order": 2,
                "db_id": "E0665",
                "name": "remo bajo máquina hammer",
                "primary_group": "dorsal",
                "secondary_group": "bíceps",
                "series": 3,
                "reps": "10-12",
                "rpe": "7",
                "video_url": "https://drive.google.com/file/d/19Qd9TISCfa0PAF7vvFiwUSmwOhFCgZZh/view?usp=drivesdk"
              },
              {
                "order": 3,
                "db_id": "E0234",
                "name": "press inclinado máquina hammer",
                "primary_group": "pectorales",
                "secondary_group": "tríceps",
                "series": 3,
                "reps": "10-12",
                "rpe": "8",
                "video_url": "https://drive.google.com/file/d/1abc..."
              }
            ]
          },
          {
            "id": "B",
            "primary_muscles": ["biceps", "rear_delts"],
            "secondary_muscles": [],
            "exercises": [
              {
                "order": 1,
                "db_id": "E0555",
                "name": "curl predicador máquina",
                "primary_group": "bíceps",
                "secondary_group": "antebrazo",
                "series": 3,
                "reps": "12-15",
                "rpe": "8",
                "video_url": "https://drive.google.com/file/d/1xyz..."
              }
            ]
          }
        ],
        "session_notes": [
          "No realizar press por encima de la cabeza.",
          "Respetar siempre rango sin dolor.",
          "Detener la serie si aparece molestia en hombro o zona lumbar."
        ]
      },
      {
        "id": "D2",
        "name": "Lower 1 – Cuádriceps énfasis",
        "focus": ["lower_body", "quad_focus"],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["quads", "glutes"],
            "secondary_muscles": ["hamstrings"],
            "exercises": [
              {
                "order": 1,
                "db_id": "E0789",
                "name": "leg press 45 grados",
                "primary_group": "cuádriceps",
                "secondary_group": "glúteos",
                "series": 4,
                "reps": "10-12",
                "rpe": "8",
                "video_url": "https://drive.google.com/file/d/1leg..."
              }
            ]
          }
        ],
        "session_notes": [
          "Posición de pies neutral o ligeramente abierta.",
          "No descender más allá de donde aparezca molestia lumbar."
        ]
      },
      {
        "id": "D3",
        "name": "Upper 2 – Tracción dominante",
        "focus": ["upper_body", "pull_focus"],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["back", "biceps"],
            "secondary_muscles": ["rear_delts"],
            "exercises": [
              {
                "order": 1,
                "db_id": "E0665",
                "name": "remo bajo máquina hammer",
                "primary_group": "dorsal",
                "secondary_group": "bíceps",
                "series": 4,
                "reps": "10-12",
                "rpe": "8",
                "video_url": "https://drive.google.com/file/d/19Qd9..."
              }
            ]
          }
        ],
        "session_notes": [
          "Enfocar en retracción escapular.",
          "Evitar hiperextensión lumbar."
        ]
      },
      {
        "id": "D4",
        "name": "Lower 2 – Femorales énfasis",
        "focus": ["lower_body", "hamstring_focus"],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["hamstrings", "glutes"],
            "secondary_muscles": ["calves"],
            "exercises": [
              {
                "order": 1,
                "db_id": "E0912",
                "name": "curl femoral tumbado máquina",
                "primary_group": "femorales",
                "secondary_group": "gemelos",
                "series": 3,
                "reps": "12-15",
                "rpe": "8",
                "video_url": "https://drive.google.com/file/d/1ham..."
              }
            ]
          }
        ],
        "session_notes": [
          "Control excéntrico en cada repetición.",
          "No forzar rango si hay molestia en rodilla."
        ]
      }
    ],

    "general_notes": [
      "Calienta de forma específica hombros y zona lumbar al inicio de cada sesión.",
      "Priorizar máquinas y agarres neutros siempre que sea posible.",
      "Evitar rangos extremos que comprometan el manguito rotador.",
      "Reducir la carga de trabajo si hay dolor o fatiga articular excesiva.",
      "Mantener hidratación adecuada y descanso entre series de 90-120 segundos."
    ]
  }
}
```

### Validaciones del Output

**Campos obligatorios** (no pueden ser null/undefined):
- `title`
- `summary`
- `goal`
- `training_type`
- `days_per_week`
- `session_duration_min`
- `weeks`
- `sessions[]`
- `general_notes[]`

**Para cada ejercicio**:
- `db_id` es obligatorio (puede ser "UNKNOWN")
- `name` es obligatorio
- `video_url` puede ser `null` si no disponible

---

## 7️⃣ CONFIGURACIÓN DEL WORKFLOW EN OPENAI

### Opción A: Assistants API (Recomendada)

**Paso 1: Crear Assistant en OpenAI Platform**

```python
# Crear assistant con file_search para BD ejercicios
import openai

client = openai.OpenAI(api_key="sk-...")

# 1. Subir BD de ejercicios
file = client.files.create(
    file=open("ejercicios_edn360.json", "rb"),
    purpose="assistants"
)

# 2. Crear vector store
vector_store = client.beta.vector_stores.create(
    name="BD Ejercicios EDN360",
    file_ids=[file.id]
)

# 3. Crear assistant
assistant = client.beta.assistants.create(
    name="EDN360 Training Workflow V1",
    instructions="""
    Eres el orquestador de generación de planes de entrenamiento EDN360.
    
    Recibirás un EDN360Input con perfil de usuario y cuestionarios.
    
    Debes ejecutar internamente los agentes E1-E7.5 y devolver un 
    client_training_program_enriched completo.
    
    Usa file_search para mapear ejercicios desde la BD.
    """,
    model="gpt-4o",
    tools=[{"type": "file_search"}],
    tool_resources={
        "file_search": {
            "vector_store_ids": [vector_store.id]
        }
    }
)

print(f"Assistant ID: {assistant.id}")
# Guardar este ID en .env como EDN360_TRAINING_WORKFLOW_ID
```

**Paso 2: Configurar en Backend**

```bash
# /app/backend/.env
EDN360_TRAINING_WORKFLOW_ID="asst_abc123..."
```

**Paso 3: Actualizar `training_workflow_service.py`**

```python
async def call_training_workflow(edn360_input: Dict[str, Any]) -> Dict[str, Any]:
    client = openai.OpenAI(api_key=EDN360_OPENAI_API_KEY)
    
    # Crear thread
    thread = client.beta.threads.create()
    
    # Enviar input
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=json.dumps(edn360_input, default=datetime_handler)
    )
    
    # Ejecutar y esperar
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=EDN360_TRAINING_WORKFLOW_ID
    )
    
    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response_text = messages.data[0].content[0].text.value
        return json.loads(response_text)
    else:
        raise Exception(f"Workflow failed: {run.status}")
```

---

### Opción B: Chat Completions con Function Calling

Si prefieres NO usar Assistants API:

**Paso 1: Definir tools**

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_exercise_by_id",
            "description": "Buscar ejercicio por db_id en BD EDN360",
            "parameters": {
                "type": "object",
                "properties": {
                    "db_id": {"type": "string"}
                },
                "required": ["db_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_exercises_by_type",
            "description": "Buscar ejercicios por tipo/movimiento",
            "parameters": {
                "type": "object",
                "properties": {
                    "movement_type": {"type": "string"},
                    "equipment": {"type": "string"}
                }
            }
        }
    }
]
```

**Paso 2: Implementar handlers**

```python
def search_exercise_by_id(db_id: str) -> dict:
    # Buscar en BD local o archivo JSON
    exercises = load_exercise_database()
    return next((ex for ex in exercises if ex["id"] == db_id), None)

def search_exercises_by_type(movement_type: str, equipment: str) -> list:
    exercises = load_exercise_database()
    return [
        ex for ex in exercises
        if ex["movement_type"] == movement_type
        and ex["equipment"] == equipment
    ]
```

**Paso 3: Llamada con manejo de tool calls**

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT_E1_E7_5},
        {"role": "user", "content": json.dumps(edn360_input)}
    ],
    tools=tools,
    response_format={"type": "json_object"}
)

# Manejar tool calls si el modelo los solicita
while response.choices[0].finish_reason == "tool_calls":
    tool_calls = response.choices[0].message.tool_calls
    
    for tool_call in tool_calls:
        if tool_call.function.name == "search_exercise_by_id":
            args = json.loads(tool_call.function.arguments)
            result = search_exercise_by_id(args["db_id"])
            # Agregar resultado a messages y continuar
            # ...
    
    # Nueva llamada con resultados de tools
    # ...

# Al final, obtener JSON final
workflow_response = json.loads(response.choices[0].message.content)
```

---

## 8️⃣ GESTIÓN DE ERRORES

### Errores Posibles y Manejo

| Error | Causa | Manejo |
|-------|-------|--------|
| Usuario no encontrado | `user_id` inválido | 404 Not Found |
| Cuestionario no encontrado | `submission_id` inválido | 404 Not Found |
| EDN360Input inválido | Falta datos críticos | 400 Bad Request |
| Timeout del workflow | Workflow tarda >60s | 504 Gateway Timeout, reintentar |
| Error de OpenAI API | Rate limit, API down | 503 Service Unavailable, reintentar |
| Ejercicio no mapeado | No match en BD | Continuar con `db_id: "UNKNOWN"` |
| JSON inválido del workflow | Formato incorrecto | 500 Internal Error, logear y notificar |

### Estrategia de Reintentos

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_training_workflow_with_retry(edn360_input):
    return await call_training_workflow(edn360_input)
```

### Snapshot en Caso de Error

Incluso si el workflow falla, guardar snapshot:

```python
try:
    workflow_result = await call_training_workflow(edn360_input)
    status = "success"
except Exception as e:
    workflow_result = {"error": str(e)}
    status = "failed"
finally:
    await create_snapshot(
        user_id=user_id,
        workflow_name="training_plan_v1",
        input=edn360_input,
        workflow_response=workflow_result,
        status=status,
        error_message=str(e) if status == "failed" else None
    )
```

---

## 9️⃣ TESTING Y VALIDACIÓN

### Test Case 1: Flujo Completo Happy Path

```python
# Datos de prueba
user_id = "1764016044644335"
submission_id = "1764016775848319"

# 1. Llamar endpoint
response = await client.post(
    "/api/training-plan",
    json={
        "user_id": user_id,
        "questionnaire_submission_id": submission_id
    },
    headers={"Authorization": f"Bearer {admin_token}"}
)

# 2. Validar response
assert response.status_code == 200
data = response.json()

# 3. Validar estructura
assert "client_training_program_enriched" in data
plan = data["client_training_program_enriched"]

assert "title" in plan
assert "sessions" in plan
assert len(plan["sessions"]) == 4  # 4 días/semana

# 4. Validar ejercicios enriquecidos
first_exercise = plan["sessions"][0]["blocks"][0]["exercises"][0]
assert "db_id" in first_exercise
assert "name" in first_exercise
assert "video_url" in first_exercise
assert first_exercise["db_id"] != "UNKNOWN"  # Mapeado correctamente

# 5. Verificar snapshot guardado
snapshot = await db_edn360.edn360_snapshots.find_one(
    {"user_id": user_id},
    sort=[("created_at", -1)]
)
assert snapshot is not None
assert snapshot["status"] == "success"
assert snapshot["workflow_name"] == "training_plan_v1"
```

### Test Case 2: Usuario Sin Cuestionario

```python
response = await client.post(
    "/api/training-plan",
    json={
        "user_id": "user_sin_cuestionario",
        "questionnaire_submission_id": "inexistente"
    },
    headers={"Authorization": f"Bearer {admin_token}"}
)

assert response.status_code == 404
assert "Cuestionario" in response.json()["detail"]
```

### Test Case 3: Ejercicio No Mapeado

```python
# Simular workflow que devuelve UNKNOWN
mock_workflow_response = {
    "client_training_program_enriched": {
        "sessions": [{
            "blocks": [{
                "exercises": [{
                    "db_id": "UNKNOWN",
                    "name": "Ejercicio no mapeado",
                    "video_url": null
                }]
            }]
        }]
    }
}

# Verificar que el plan se crea igual
assert response.status_code == 200
```

---

## 🔟 RIESGOS Y MITIGACIONES

### Riesgo 1: Cambio en Formato de Output

**Impacto**: Frontend y PDFs se rompen

**Mitigación**:
- Versionar el formato: `training_plan_v1`, `training_plan_v2`
- Mantener retrocompatibilidad
- Tests de integración que validen estructura

---

### Riesgo 2: Latencia Alta del Workflow

**Impacto**: Timeout, mala UX

**Mitigación**:
- Aumentar timeout a 120s
- Optimizar prompts de agentes
- Considerar respuesta async con webhook (futura iteración)

---

### Riesgo 3: Ejercicios No Mapeables

**Impacto**: Plan incompleto o con "UNKNOWN"

**Mitigación**:
- Enriquecer BD de ejercicios
- Tener fallbacks por tipo de ejercicio
- Permitir que plan siga funcionando con UNKNOWN

---

### Riesgo 4: BD de Ejercicios Desactualizada

**Impacto**: IDs cambian, mapeos fallan

**Mitigación**:
- Mantener IDs estables (nunca cambiar IDs existentes)
- Si se agregan nuevos ejercicios, solo agregar IDs nuevos
- Migración de datos si es absolutamente necesario

---

### Riesgo 5: Costo de Tokens

**Impacto**: Alto costo por llamada (E1-E7.5 + file_search)

**Mitigación**:
- Limitar longitud de `questionnaire.payload` (truncar si >10k tokens)
- Usar modelos más eficientes donde sea posible (gpt-4o-mini)
- Cachear resultados si usuario regenera múltiples veces

---

## 📌 RESUMEN EJECUTIVO

### Estado Actual

✅ **Implementado**:
- Endpoint `POST /api/training-plan`
- Sincronización con `client_drawers`
- Guardado de snapshots en `edn360_snapshots`
- Modelos Pydantic para request/response

⚠️ **Pendiente de Configuración (Jorge)**:
- Crear workflow E1-E7.5 en OpenAI Platform
- Subir BD de ejercicios como file_search
- Configurar `EDN360_TRAINING_WORKFLOW_ID` en .env
- Ajustar `training_workflow_service.py` según método elegido

---

### Contrato Estable

**Input**: `EDN360Input`
```json
{
  "user_profile": {...},
  "questionnaires": [...],
  "context": {...}
}
```

**Output**: `client_training_program_enriched`
```json
{
  "client_training_program_enriched": {
    "title": "...",
    "sessions": [
      {
        "exercises": [
          {
            "db_id": "E049",
            "name": "...",
            "video_url": "..."
          }
        ]
      }
    ]
  }
}
```

---

### Next Steps

1. **Jorge**: Configurar workflow E1-E7.5 en OpenAI Platform
2. **Jorge**: Proporcionar `EDN360_TRAINING_WORKFLOW_ID`
3. **Emergent**: Ajustar `training_workflow_service.py` según método
4. **Testing**: Validar flujo completo end-to-end
5. **Migrar Frontend**: Eliminar polling legacy, usar nuevo endpoint

---

**FIN DEL DOCUMENTO** 🚀
