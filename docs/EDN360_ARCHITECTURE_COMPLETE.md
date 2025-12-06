# EDN360 - Documentación Técnica Completa

**Versión:** 2.0.0 (EVOLUTIONARY)  
**Fecha:** 2025-12-03  
**Autor:** Sistema EDN360  
**Estado:** PRODUCCIÓN

---

## Tabla de Contenidos

1. [Arquitectura General](#1-arquitectura-general)
2. [Esquema de Bases de Datos](#2-esquema-de-bases-de-datos)
3. [Contratos de Endpoints](#3-contratos-de-endpoints)
4. [Contrato con Workflow EDN360](#4-contrato-con-workflow-edn360)
5. [Prompts y Proceso de Cambios](#5-prompts-y-proceso-de-cambios)
6. [Flujos de Datos Completos](#6-flujos-de-datos-completos)

---

## 1. Arquitectura General

### 1.1 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                      PANEL DE ADMIN (React)                      │
│                     http://localhost:3000                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  AdminDashboard.jsx                                     │    │
│  │  - Selecciona cliente                                   │    │
│  │  - Selecciona cuestionarios (Previo + Nuevo)           │    │
│  │  - Selecciona plan anterior                             │    │
│  │  - Botón "Generar Plan EDN360"                         │    │
│  └────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           │ POST /api/training-plan             │
│                           ▼                                      │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP Request
                            │ {
                            │   user_id,
                            │   questionnaire_ids: [],
                            │   previous_training_plan_id
                            │ }
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND PRINCIPAL (FastAPI)                         │
│                 http://0.0.0.0:8001                             │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  server.py                                              │    │
│  │  POST /api/training-plan                               │    │
│  │                                                          │    │
│  │  1. Valida user_id y questionnaire_ids                 │    │
│  │  2. Lee cuestionarios de MongoDB                       │    │
│  │  3. Lee planes previos de MongoDB                      │    │
│  │  4. Construye objeto STATE                             │    │
│  │  5. Construye objeto INPUT                             │    │
│  │  6. Llama al microservicio EDN360                      │    │
│  │  7. Guarda plan en training_plans_v2                   │    │
│  │  8. Retorna plan al frontend                           │    │
│  └────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           │ POST /api/edn360/run-training-workflow
│                           │ {                                    │
│                           │   input: {...},                     │
│                           │   state: {...}                      │
│                           │ }                                    │
│                           ▼                                      │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP Request
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│         MICROSERVICIO EDN360 (Node.js + OpenAI SDK)            │
│                 http://localhost:4000                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  edn360_workflow.ts                                     │    │
│  │                                                          │    │
│  │  1. Detecta tipo de flujo (INICIAL vs EVOLUTIVO)      │    │
│  │  2. Construye contexto con STATE                       │    │
│  │  3. Ejecuta workflow de 8 agentes:                     │    │
│  │     - E1: Analizador de Perfil                         │    │
│  │     - E2: Parse Questionnaire                          │    │
│  │     - E3: Training Summary                             │    │
│  │     - E4: Training Plan Generator                      │    │
│  │     - E5: Training Plan Validator                      │    │
│  │     // - E6: Exercise Normalizer                       │    │  // DISABLED - Using catalog directly in backend
│  │     - E7: Training Plan Assembler                      │    │
│  │     - E7.5: Training Plan Enricher                     │    │
│  │  4. Retorna client_training_program_enriched           │    │
│  └────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           │ OpenAI API Calls                    │
│                           ▼                                      │
│                    OpenAI GPT-4.1                               │
│                  + File Search (BD Ejercicios)                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ Response
                            │ {
                            │   client_training_program_enriched: {
                            │     title, summary, sessions[...]
                            │   }
                            │ }
                            │
                            ▼
                  BACKEND guarda en MongoDB
                  test_database.client_drawers
                  edn360_app.training_plans_v2


┌─────────────────────────────────────────────────────────────────┐
│                    BASES DE DATOS (MongoDB)                      │
│                                                                  │
│  ┌──────────────────────────┐  ┌──────────────────────────┐   │
│  │  test_database           │  │  edn360_app              │   │
│  │  ----------------------  │  │  ----------------------  │   │
│  │  • users                 │  │  • training_plans_v2     │   │
│  │  • client_drawers        │  │  • edn360_snapshots      │   │
│  │    - shared_questionnaires│  │                          │   │
│  └──────────────────────────┘  └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Flujo Detallado: "Generar Plan EDN360"

**Paso a Paso:**

1. **Frontend (AdminDashboard.jsx):**
   - Usuario selecciona cliente
   - Usuario selecciona:
     - Cuestionario Previo (Base)
     - Cuestionario Nuevo (opcional)
     - Plan Anterior (opcional)
   - Click en "Generar Plan EDN360"
   - JavaScript construye payload:
     ```javascript
     {
       user_id: "1764016044644335",
       questionnaire_ids: ["cuest_inicial", "seguimiento_1"],
       previous_training_plan_id: "plan_id_123"
     }
     ```
   - Envía POST a `/api/training-plan`

2. **Backend (server.py):**
   - **Validación:** Verifica user_id y questionnaire_ids
   - **Recuperación de Cuestionarios:**
     - Lee `test_database.client_drawers` para el user_id
     - Obtiene todos los cuestionarios del campo `services.shared_questionnaires`
     - Ordena por `submitted_at` (más antiguo → más reciente)
     - Identifica:
       - `initial_questionnaire`: El más antiguo (siempre)
       - `current_questionnaire`: El último en `questionnaire_ids`
       - `previous_followups`: Cuestionarios entre inicial y actual
   
   - **Recuperación de Planes:**
     - Lee `edn360_app.training_plans_v2` para el user_id
     - Ordena por `created_at` (más antiguo → más reciente)
     - Si hay `previous_training_plan_id`:
       - Filtra planes hasta ese ID (inclusive)
     - Identifica:
       - `previous_plans`: Array de todos los planes hasta el seleccionado
       - `last_plan`: El último del array (o null si no hay)
   
   - **Construcción de STATE:**
     ```python
     state = {
       "initial_questionnaire": {...},
       "previous_followups": [...],
       "previous_plans": [...],
       "last_plan": {...}
     }
     ```
   
   - **Construcción de INPUT:**
     ```python
     workflow_input = {
       "input": {
         "input_as_text": json.dumps({
           "user_profile": user_profile.dict(),
           "current_questionnaire": current_q_data
         })
       },
       "state": state
     }
     ```
   
   - **Llamada al Microservicio:**
     - POST `http://localhost:4000/api/edn360/run-training-workflow`
     - Timeout: 300 segundos (5 minutos)
     - Headers: `Content-Type: application/json`

3. **Microservicio EDN360 (edn360_workflow.ts):**
   - **Detección de Flujo:**
     ```typescript
     if (workflow.input && workflow.state) {
       const hasHistory = Boolean(workflowState.last_plan);
       console.log(`Tipo: ${hasHistory ? 'EVOLUTIVO' : 'INICIAL'}`);
     }
     ```
   
   - **Construcción de Contexto:**
     - Agrega STATE al texto inicial para los agentes
     - Pasa historial a E1, E3, E4 para análisis evolutivo
   
   - **Ejecución de Agentes (secuencial):**
     - E1: Analiza perfil, compara con historial si existe
     - E2: Normaliza cuestionario actual
     - E3: Construye contexto de entrenamiento, usa last_plan si existe
     - E4: Genera plan, aplica progresión si es evolutivo
     - E5: Valida seguridad del plan
     - E6: Mapea exercise_types a IDs de BD de ejercicios
     - E7: Ensambla plan técnico
     - E7.5: Enriquece con nombres, videos, notas
   
   - **Respuesta:**
     ```json
     {
       "client_training_program_enriched": {
         "title": "...",
         "summary": "...",
         "sessions": [...]
       }
     }
     ```

4. **Backend (Guardado):**
   - **Persistencia en `training_plans_v2`:**
     ```python
     training_plan_doc = {
       "user_id": "...",
       "questionnaire_submission_id": "...",
       "created_at": datetime.now(timezone.utc).isoformat(),
       "plan": training_program,  # El JSON completo del plan
       "status": "draft",
       "version": "2.0.0",
       "source": "edn360_workflow_evolutionary_v1",
       "is_evolutionary": bool(last_plan)
     }
     ```
   
   - **Respuesta al Frontend:**
     ```json
     {
       "client_training_program_enriched": {...},
       "is_evolutionary": true
     }
     ```

5. **Frontend (Visualización):**
   - Recibe plan generado
   - Muestra en TrainingPlanCard.jsx
   - Permite editar, eliminar, enviar por email

---

## 2. Esquema de Bases de Datos

### 2.1 Base de Datos: `test_database`

#### Colección: `users`

**Propósito:** Almacena información de usuarios (clientes y admin)

**Campos Principales:**

| Campo | Tipo | Ejemplo | Descripción |
|-------|------|---------|-------------|
| `_id` | String | `"1764016044644335"` | ID único del usuario |
| `name` | String | `"Jorge Calcerrada"` | Nombre completo |
| `email` | String | `"jorge@example.com"` | Email |
| `phone` | String | `"+34600123456"` | Teléfono |
| `role` | String | `"user"` / `"admin"` | Rol del usuario |
| `subscription` | Object | `{plan: "team", status: "active"}` | Datos de suscripción |
| `created_at` | DateTime | `2025-01-15T10:00:00Z` | Fecha de registro |

**Relación con EDN360:**
- Un `user` puede tener múltiples cuestionarios en `client_drawers`
- Un `user` puede tener múltiples planes en `training_plans_v2`

---

#### Colección: `client_drawers`

**Propósito:** Almacena cuestionarios de cada cliente (inicial + seguimientos)

**Estructura del Documento:**

```json
{
  "_id": "drawer_id_123",
  "user_id": "1764016044644335",
  "id": "drawer_id_123",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-25T12:00:00Z",
  "services": {
    "shared_questionnaires": [
      {
        "submission_id": "quest_inicial_001",
        "submitted_at": "2025-01-15T10:30:00Z",
        "source": "edn360",
        "raw_payload": {
          "nombre_completo": "Jorge Calcerrada",
          "edad": 35,
          "peso": 80,
          "altura_cm": 175,
          "objetivo_fisico": "Ganar músculo",
          "dias_semana_entrenar": 4,
          "tiempo_sesion": "45 min",
          "lesiones": "Molestias hombro izquierdo",
          "experiencia": "Avanzado",
          "gimnasio": "Sí, gimnasio completo",
          // ... muchos más campos del cuestionario
        }
      },
      {
        "submission_id": "quest_seguimiento_001",
        "submitted_at": "2025-01-25T11:00:00Z",
        "source": "edn360",
        "raw_payload": {
          "nombre_completo": "Jorge Calcerrada",
          "seguimiento": 1,
          "dolor_hombro": "Mejorado, ya no molesta tanto",
          "progreso": "Bien, quiero más desafío",
          "adherencia": "4 días por semana cumplidos",
          // ... campos del seguimiento
        }
      }
    ]
  }
}
```

**Campos Principales de `shared_questionnaires`:**

| Campo | Tipo | Ejemplo | Descripción |
|-------|------|---------|-------------|
| `submission_id` | String | `"quest_inicial_001"` | ID único del cuestionario |
| `submitted_at` | DateTime | `2025-01-15T10:30:00Z` | Fecha de envío |
| `source` | String | `"edn360"` | Origen del cuestionario |
| `raw_payload` | Object | `{...}` | Respuestas completas del cuestionario |

**Relación con EDN360:**
- Cada `user_id` tiene UN `client_drawer`
- Cada `client_drawer` contiene TODOS los cuestionarios del usuario
- Los cuestionarios se ordenan por `submitted_at` para identificar:
  - **Inicial:** El más antiguo
  - **Seguimientos:** Los posteriores al inicial

**Búsqueda en Backend:**
```python
from repositories.client_drawer_repository import get_drawer_by_user_id
drawer = await get_drawer_by_user_id(user_id)
all_questionnaires = drawer.services.shared_questionnaires
```

---

### 2.2 Base de Datos: `edn360_app`

#### Colección: `training_plans_v2`

**Propósito:** Almacena todos los planes de entrenamiento generados

**Estructura del Documento:**

```json
{
  "_id": ObjectId("674eabcd1234567890abcdef"),
  "user_id": "1764016044644335",
  "questionnaire_submission_id": "quest_inicial_001",
  "created_at": "2025-01-20T12:00:00Z",
  "status": "draft",
  "version": "2.0.0",
  "source": "edn360_workflow_evolutionary_v1",
  "is_evolutionary": false,
  "plan": {
    "title": "Plan Foundational Upper/Lower - 4 días/semana",
    "summary": "Programa de hipertrofia con enfoque en seguridad articular",
    "goal": "Aumentar masa muscular respetando lesión de hombro",
    "training_type": "upper_lower",
    "days_per_week": 4,
    "session_duration_min": 45,
    "weeks": 4,
    "sessions": [
      {
        "id": "D1",
        "name": "Upper 1 – Push Dominante",
        "focus": ["upper_body", "push", "chest"],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["chest", "triceps"],
            "secondary_muscles": ["front_delts"],
            "exercises": [
              {
                "order": 1,
                "db_id": "E321",
                "name": "Press banca con mancuernas",
                "primary_group": "Pecho",
                "secondary_group": "Tríceps",
                "series": 3,
                "reps": "8-12",
                "rpe": "7",
                "notes": "Control en descenso, evitar dolor hombro",
                "video_url": "https://drive.google.com/file/d/xyz123"
              },
              {
                "order": 2,
                "db_id": "E145",
                "name": "Remo en máquina sentado",
                "primary_group": "Espalda",
                "secondary_group": "Bíceps",
                "series": 3,
                "reps": "10-12",
                "rpe": "7",
                "notes": "Escápulas retraídas, sin balanceo",
                "video_url": "https://drive.google.com/file/d/abc456"
              }
            ]
          },
          {
            "id": "B",
            "primary_muscles": ["shoulders"],
            "secondary_muscles": [],
            "exercises": [
              {
                "order": 3,
                "db_id": "E201",
                "name": "Elevaciones laterales con mancuernas",
                "primary_group": "Hombros",
                "secondary_group": "Trapecio",
                "series": 3,
                "reps": "12-15",
                "rpe": "7",
                "notes": "NO overhead press, solo laterales",
                "video_url": "https://drive.google.com/file/d/def789"
              }
            ]
          }
        ],
        "session_notes": [
          "Calentar hombros con rotaciones",
          "Si hay dolor, reducir peso o saltar ejercicio",
          "Finalizar con estiramientos de pecho y hombros"
        ]
      },
      {
        "id": "D2",
        "name": "Lower 1 – Cuádriceps Dominante",
        "focus": ["lower_body", "quads"],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["quads"],
            "secondary_muscles": ["glutes"],
            "exercises": [
              {
                "order": 1,
                "db_id": "E401",
                "name": "Prensa de piernas",
                "primary_group": "Cuádriceps",
                "secondary_group": "Glúteos",
                "series": 4,
                "reps": "8-10",
                "rpe": "8",
                "notes": "Rango completo sin despegar lumbar",
                "video_url": "https://drive.google.com/file/d/ghi012"
              }
            ]
          }
        ],
        "session_notes": [
          "Calentar con movilidad de cadera",
          "Core activado en todos los ejercicios"
        ]
      }
      // ... D3, D4
    ],
    "general_notes": [
      "Progresar aumentando peso cuando todas las series sean fáciles",
      "Priorizar seguridad articular sobre carga",
      "Si aumenta fatiga o dolor, reducir volumen"
    ]
  }
}
```

**Campos Principales del Documento:**

| Campo | Tipo | Ejemplo | Descripción |
|-------|------|---------|-------------|
| `_id` | ObjectId | `ObjectId("...")` | ID único del plan |
| `user_id` | String | `"1764016044644335"` | ID del usuario |
| `questionnaire_submission_id` | String | `"quest_inicial_001"` | ID del cuestionario usado |
| `created_at` | String (ISO) | `"2025-01-20T12:00:00Z"` | Fecha de generación |
| `status` | String | `"draft"` / `"sent"` | Estado del plan |
| `version` | String | `"2.0.0"` | Versión del sistema |
| `source` | String | `"edn360_workflow_evolutionary_v1"` | Origen del plan |
| `is_evolutionary` | Boolean | `false` / `true` | Si es plan evolutivo |
| `plan` | Object | `{...}` | **JSON completo del plan** |

**Campos del `plan` (JSON interno):**

| Campo | Tipo | Ejemplo | Descripción |
|-------|------|---------|-------------|
| `title` | String | `"Plan Upper/Lower..."` | Título del plan |
| `summary` | String | `"Programa de hipertrofia..."` | Resumen |
| `goal` | String | `"Aumentar masa muscular..."` | Objetivo |
| `training_type` | String | `"upper_lower"` | Tipo de split |
| `days_per_week` | Integer | `4` | Días de entrenamiento |
| `session_duration_min` | Integer | `45` | Duración de sesión |
| `weeks` | Integer | `4` | Semanas del bloque |
| `sessions` | Array | `[...]` | **Array de sesiones** |
| `general_notes` | Array | `[...]` | Notas generales |

**Estructura de `sessions[i]`:**

| Campo | Tipo | Ejemplo | Descripción |
|-------|------|---------|-------------|
| `id` | String | `"D1"` | ID de la sesión |
| `name` | String | `"Upper 1 – Push Dominante"` | Nombre de la sesión |
| `focus` | Array | `["upper_body", "push"]` | Foco de la sesión |
| `blocks` | Array | `[...]` | **Array de bloques** |
| `session_notes` | Array | `["Calentar...", "..."]` | Notas de la sesión |

**Estructura de `blocks[i]`:**

| Campo | Tipo | Ejemplo | Descripción |
|-------|------|---------|-------------|
| `id` | String | `"A"` | ID del bloque |
| `primary_muscles` | Array | `["chest", "triceps"]` | Músculos primarios |
| `secondary_muscles` | Array | `["front_delts"]` | Músculos secundarios |
| `exercises` | Array | `[...]` | **Array de ejercicios** |

**Estructura de `exercises[i]`:**

| Campo | Tipo | Ejemplo | Descripción |
|-------|------|---------|-------------|
| `order` | Integer | `1` | Orden del ejercicio |
| `db_id` | String | `"E321"` | ID en BD de ejercicios |
| `name` | String | `"Press banca con mancuernas"` | Nombre del ejercicio |
| `primary_group` | String | `"Pecho"` | Grupo muscular primario |
| `secondary_group` | String | `"Tríceps"` | Grupo muscular secundario |
| `series` | Integer/String | `3` / `"3-4"` | Número de series |
| `reps` | String | `"8-12"` | Rango de repeticiones |
| `rpe` | Integer/String | `7` / `"7-8"` | RPE (esfuerzo percibido) |
| `notes` | String | `"Control en descenso..."` | Notas de ejecución |
| `video_url` | String | `"https://drive.google.com/..."` | URL del video |

**Relación con EDN360:**
- Cada plan está vinculado a un `user_id`
- Cada plan referencia el `questionnaire_submission_id` usado
- Los planes se ordenan por `created_at` para identificar:
  - **Plan más reciente:** `last_plan` en STATE
  - **Planes previos:** `previous_plans` en STATE

**Búsqueda en Backend:**
```python
edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
all_plans = await edn360_db.training_plans_v2.find(
    {"user_id": user_id},
    {"_id": 1, "created_at": 1, "plan": 1}
).sort("created_at", 1).to_list(length=100)
```

---

#### Colección: `edn360_snapshots`

**Propósito:** Almacena snapshots inmutables de cada ejecución del workflow (para auditoría)

**Estructura del Documento:**

```json
{
  "_id": "snapshot_uuid_abc123",
  "snapshot_id": "snapshot_uuid_abc123",
  "user_id": "1764016044644335",
  "created_at": "2025-01-20T12:05:00Z",
  "version": "2.0.0",
  "input": {
    "user_profile": {...},
    "questionnaires": [...]
  },
  "workflow_name": "training_plan_v1",
  "workflow_response": {
    "client_training_program_enriched": {...}
  },
  "status": "success",
  "error_message": null
}
```

**Nota:** Los snapshots son inmutables y se usan para debugging y auditoría, no para lógica de negocio.

---

### 2.3 Relaciones Entre Colecciones

```
users (test_database)
  └─ user_id: "1764016044644335"
      │
      ├─→ client_drawers (test_database)
      │    └─ services.shared_questionnaires[]
      │        ├─ quest_inicial_001 (2025-01-15)
      │        ├─ quest_seguimiento_001 (2025-01-25)
      │        └─ quest_seguimiento_002 (2025-02-05)
      │
      └─→ training_plans_v2 (edn360_app)
           ├─ Plan 1 (2025-01-20, is_evolutionary: false)
           ├─ Plan 2 (2025-01-27, is_evolutionary: true)
           └─ Plan 3 (2025-02-10, is_evolutionary: true)
```

**Flujo de Datos:**
1. Usuario completa cuestionario → se guarda en `client_drawers.shared_questionnaires`
2. Admin genera plan → backend lee `client_drawers` + `training_plans_v2` para construir STATE
3. Workflow genera plan → se guarda en `training_plans_v2`
4. Para el siguiente plan, el plan anterior se usa en STATE como `last_plan`

---

## 3. Contratos de Endpoints

### 3.1 POST /api/training-plan (Endpoint Principal)

**Descripción:** Genera un plan de entrenamiento evolutivo usando el workflow EDN360.

**URL:** `POST /api/training-plan`

**Autenticación:** Bearer Token (Admin only)

**Request Body:**

```json
{
  "user_id": "1764016044644335",
  "questionnaire_ids": [
    "quest_inicial_001",
    "quest_seguimiento_001"
  ],
  "previous_training_plan_id": "674eabcd1234567890abcdef"
}
```

**Campos del Request:**

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `user_id` | String | ✅ Sí | ID del usuario/cliente |
| `questionnaire_ids` | Array[String] | ✅ Sí | IDs de cuestionarios (1 o 2) |
| `previous_training_plan_id` | String | ❌ No | ID del plan anterior (opcional) |

**Lógica:**
- **`questionnaire_ids[0]`:** Cuestionario Previo (Base) seleccionado en UI
- **`questionnaire_ids[1]`:** Cuestionario Nuevo (si existe)
- **`current_questionnaire_id`:** Se toma como el ÚLTIMO del array
- **`initial_questionnaire`:** SIEMPRE se busca como el más antiguo en BD
- **`previous_training_plan_id`:** Si se proporciona, filtra planes hasta ese ID

**Response (Éxito - 200 OK):**

```json
{
  "client_training_program_enriched": {
    "title": "Plan Evolutivo Upper/Lower - Fase 2",
    "summary": "Programa progresivo basado en Plan 1 con incremento de volumen",
    "goal": "Hipertrofia muscular con progresión controlada",
    "training_type": "upper_lower",
    "days_per_week": 4,
    "session_duration_min": 45,
    "weeks": 4,
    "sessions": [
      {
        "id": "D1",
        "name": "Upper 1 – Push Dominante",
        "focus": ["upper_body", "push"],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["chest", "triceps"],
            "secondary_muscles": ["front_delts"],
            "exercises": [
              {
                "order": 1,
                "db_id": "E321",
                "name": "Press banca con mancuernas",
                "primary_group": "Pecho",
                "secondary_group": "Tríceps",
                "series": 4,
                "reps": "6-10",
                "rpe": "8",
                "notes": "Progresión desde Plan 1",
                "video_url": "https://drive.google.com/..."
              }
            ]
          }
        ],
        "session_notes": ["Calentar hombros..."]
      }
    ],
    "general_notes": ["Progresar cuando sea fácil..."]
  },
  "is_evolutionary": true
}
```

**Response (Error - 400 Bad Request):**

```json
{
  "detail": {
    "error": "missing_fields",
    "message": "Se requiere user_id y al menos un cuestionario"
  }
}
```

**Response (Error - 404 Not Found):**

```json
{
  "detail": {
    "error": "user_not_found",
    "message": "Usuario 1764016044644335 no encontrado"
  }
}
```

**Response (Error - 500 Internal Server Error):**

```json
{
  "detail": {
    "error": "workflow_error",
    "message": "Error generando plan de entrenamiento: OpenAI API timeout"
  }
}
```

---

### 3.2 POST /api/training-plan/mock (Endpoint de Testing)

**Descripción:** Genera un plan de entrenamiento MOCK (hardcoded) para testing sin llamar a OpenAI.

**URL:** `POST /api/training-plan/mock`

**Autenticación:** Bearer Token (Admin only)

**Request Body:**

```json
{
  "user_id": "1764016044644335"
}
```

**Campos del Request:**

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `user_id` | String | ✅ Sí | ID del usuario/cliente |

**Response (Éxito - 200 OK):**

```json
{
  "client_training_program_enriched": {
    "title": "Plan de Hipertrofia Upper/Lower - 4 días/semana",
    "summary": "Programa MOCK para testing",
    "goal": "Aumentar masa muscular",
    "training_type": "upper_lower",
    "days_per_week": 4,
    "session_duration_min": 60,
    "weeks": 8,
    "sessions": [
      // ... estructura completa igual que el endpoint real
    ]
  }
}
```

**Uso:**
- Para testing de frontend sin consumir créditos de OpenAI
- Para validar la estructura del plan sin workflow
- Para desarrollo local

---

### 3.3 GET /api/admin/users/{user_id}/training-plans/latest

**Descripción:** Obtiene el plan de entrenamiento más reciente de un usuario.

**URL:** `GET /api/admin/users/{user_id}/training-plans/latest`

**Autenticación:** Bearer Token (Admin only)

**Path Parameters:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `user_id` | String | ID del usuario |

**Response (Éxito - 200 OK):**

```json
{
  "plan_id": "674eabcd1234567890abcdef",
  "created_at": "2025-01-20T12:00:00Z",
  "is_evolutionary": true,
  "plan": {
    "title": "Plan Evolutivo Upper/Lower - Fase 2",
    "sessions": [...]
  }
}
```

**Response (Error - 404 Not Found):**

```json
{
  "detail": {
    "error": "no_plans_found",
    "message": "Usuario no tiene planes de entrenamiento"
  }
}
```

---

## 4. Contrato con Workflow EDN360

### 4.1 Estructura Completa del Request

**Endpoint del Microservicio:**
```
POST http://localhost:4000/api/edn360/run-training-workflow
Content-Type: application/json
Timeout: 300 segundos
```

#### CASO 1: Plan Inicial (Sin Historial)

**Request Body:**

```json
{
  "input": {
    "input_as_text": "{\"user_profile\": {\"user_id\": \"1764016044644335\", \"name\": \"Jorge Calcerrada\", \"email\": \"jorge@example.com\", \"age\": 35, \"height_cm\": 175, \"weight_kg\": 80}, \"current_questionnaire\": {\"submission_id\": \"quest_inicial_001\", \"submitted_at\": \"2025-01-15T10:30:00Z\", \"source\": \"edn360\", \"payload\": {\"nombre_completo\": \"Jorge Calcerrada\", \"edad\": 35, \"peso\": 80, \"altura_cm\": 175, \"objetivo_fisico\": \"Ganar músculo\", \"dias_semana_entrenar\": 4, \"tiempo_sesion\": \"45 min\", \"lesiones\": \"Molestias hombro izquierdo\", \"experiencia\": \"Avanzado\", \"gimnasio\": \"Sí, gimnasio completo\"}}}"
  },
  "state": {
    "initial_questionnaire": {
      "submission_id": "quest_inicial_001",
      "submitted_at": "2025-01-15T10:30:00Z",
      "source": "edn360",
      "payload": {
        "nombre_completo": "Jorge Calcerrada",
        "edad": 35,
        "peso": 80,
        "altura_cm": 175,
        "objetivo_fisico": "Ganar músculo",
        "dias_semana_entrenar": 4,
        "tiempo_sesion": "45 min",
        "lesiones": "Molestias hombro izquierdo",
        "experiencia": "Avanzado",
        "gimnasio": "Sí, gimnasio completo"
      }
    },
    "previous_followups": [],
    "previous_plans": [],
    "last_plan": null
  }
}
```

**Logs del Microservicio:**
```
🔄 Detectado flujo EVOLUTIVO con STATE
📊 Tipo de generación: INICIAL
📋 Previous plans: 0
📋 Previous followups: 0
🚀 Ejecutando E1 – Analizador de Perfil...
✅ E1 – Analizador de Perfil completado
🚀 Ejecutando E2 – Parse Questionnaire...
✅ E2 – Parse Questionnaire completado
...
```

#### CASO 2: Plan Evolutivo (Con Historial)

**Request Body:**

```json
{
  "input": {
    "input_as_text": "{\"user_profile\": {\"user_id\": \"1764016044644335\", \"name\": \"Jorge Calcerrada\", \"email\": \"jorge@example.com\", \"age\": 35, \"height_cm\": 175, \"weight_kg\": 82}, \"current_questionnaire\": {\"submission_id\": \"quest_seguimiento_001\", \"submitted_at\": \"2025-01-25T11:00:00Z\", \"source\": \"edn360\", \"payload\": {\"nombre_completo\": \"Jorge Calcerrada\", \"seguimiento\": 1, \"dolor_hombro\": \"Mejorado, ya no molesta tanto\", \"progreso\": \"Bien, quiero más desafío\", \"adherencia\": \"4 días por semana cumplidos\"}}}"
  },
  "state": {
    "initial_questionnaire": {
      "submission_id": "quest_inicial_001",
      "submitted_at": "2025-01-15T10:30:00Z",
      "source": "edn360",
      "payload": {
        "nombre_completo": "Jorge Calcerrada",
        "edad": 35,
        "peso": 80,
        "altura_cm": 175,
        "objetivo_fisico": "Ganar músculo",
        "lesiones": "Molestias hombro izquierdo"
      }
    },
    "previous_followups": [],
    "previous_plans": [
      {
        "_id": "674eabcd1234567890abcdef",
        "created_at": "2025-01-20T12:00:00Z",
        "plan": {
          "title": "Plan Foundational Upper/Lower",
          "training_type": "upper_lower",
          "days_per_week": 4,
          "sessions": [
            {
              "id": "D1",
              "blocks": [
                {
                  "id": "A",
                  "exercises": [
                    {
                      "order": 1,
                      "series": 3,
                      "reps": "8-12",
                      "rpe": "7"
                    }
                  ]
                }
              ]
            }
          ]
        }
      }
    ],
    "last_plan": {
      "_id": "674eabcd1234567890abcdef",
      "created_at": "2025-01-20T12:00:00Z",
      "plan": {
        "title": "Plan Foundational Upper/Lower",
        "training_type": "upper_lower",
        "days_per_week": 4,
        "sessions": [
          {
            "id": "D1",
            "blocks": [
              {
                "id": "A",
                "exercises": [
                  {
                    "order": 1,
                    "series": 3,
                    "reps": "8-12",
                    "rpe": "7"
                  }
                ]
              }
            ]
          }
        ]
      }
    }
  }
}
```

**Logs del Microservicio:**
```
🔄 Detectado flujo EVOLUTIVO con STATE
📊 Tipo de generación: EVOLUTIVO
📋 Previous plans: 1
📋 Previous followups: 0
🚀 Ejecutando E1 – Analizador de Perfil...
✅ E1 – Analizador de Perfil completado
...
```

---

### 4.2 Estructura Completa de la Response

**Response del Workflow (Success):**

```json
{
  "client_training_program_enriched": {
    "title": "Plan Evolutivo Upper/Lower - Fase 2",
    "summary": "Programa progresivo con incremento de volumen del 15%",
    "goal": "Hipertrofia muscular con progresión controlada",
    "training_type": "upper_lower",
    "days_per_week": 4,
    "session_duration_min": 45,
    "weeks": 4,
    "sessions": [
      {
        "id": "D1",
        "name": "Upper 1 – Push Dominante",
        "focus": ["upper_body", "push", "chest"],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["chest", "triceps"],
            "secondary_muscles": ["front_delts"],
            "exercises": [
              {
                "order": 1,
                "db_id": "E321",
                "name": "Press banca con mancuernas",
                "primary_group": "Pecho",
                "secondary_group": "Tríceps",
                "series": 4,
                "reps": "6-10",
                "rpe": "8",
                "notes": "Progresión desde Plan 1: +1 serie, reps más bajas",
                "video_url": "https://drive.google.com/file/d/xyz123"
              },
              {
                "order": 2,
                "db_id": "E145",
                "name": "Remo en máquina sentado",
                "primary_group": "Espalda",
                "secondary_group": "Bíceps",
                "series": 4,
                "reps": "8-10",
                "rpe": "8",
                "notes": "Progresión: +1 serie vs Plan 1",
                "video_url": "https://drive.google.com/file/d/abc456"
              }
            ]
          },
          {
            "id": "B",
            "primary_muscles": ["shoulders"],
            "secondary_muscles": [],
            "exercises": [
              {
                "order": 3,
                "db_id": "E202",
                "name": "Elevaciones laterales en máquina",
                "primary_group": "Hombros",
                "secondary_group": "Trapecio",
                "series": 3,
                "reps": "12-15",
                "rpe": "8",
                "notes": "Variación vs Plan 1: cambio de mancuernas a máquina",
                "video_url": "https://drive.google.com/file/d/def789"
              }
            ]
          }
        ],
        "session_notes": [
          "Calentar hombros, dolor ha mejorado según seguimiento",
          "Si hay dolor, reducir peso",
          "Finalizar con estiramientos"
        ]
      },
      {
        "id": "D2",
        "name": "Lower 1 – Cuádriceps Dominante",
        "focus": ["lower_body", "quads"],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["quads"],
            "secondary_muscles": ["glutes"],
            "exercises": [
              {
                "order": 1,
                "db_id": "E401",
                "name": "Prensa de piernas",
                "primary_group": "Cuádriceps",
                "secondary_group": "Glúteos",
                "series": 4,
                "reps": "6-8",
                "rpe": "8",
                "notes": "Progresión: reps más bajas, RPE más alto",
                "video_url": "https://drive.google.com/file/d/ghi012"
              }
            ]
          }
        ],
        "session_notes": [
          "Movilidad de cadera antes de empezar"
        ]
      }
    ],
    "general_notes": [
      "Plan progresado desde Plan 1: +15% volumen",
      "Hombro ha mejorado según seguimiento, mantener precaución",
      "Progresar peso cuando series sean fáciles",
      "Si fatiga aumenta, reducir volumen próxima sesión"
    ]
  }
}
```

**Diferencias vs Plan 1 (Evolutivo):**
- ✅ **Series:** 3 → 4 (incremento de volumen)
- ✅ **Reps:** "8-12" → "6-10" (intensidad aumentada)
- ✅ **RPE:** 7 → 8 (esfuerzo aumentado)
- ✅ **Ejercicios variados:** Elevaciones laterales: mancuernas → máquina
- ✅ **Notas contextuales:** "Hombro ha mejorado según seguimiento"

---

## 5. Prompts y Proceso de Cambios

### 5.1 Ubicación de Prompts

**Archivo Principal:**
```
/app/edn360-workflow-service/src/edn360_workflow.ts
```

**Prompts de Agentes:**

| Agente | Líneas Aprox | Función |
|--------|--------------|---------|
| E1 – Profile Analyzer | 20-220 | Analiza perfil, compara con historial |
| E2 – Parse Questionnaire | 220-420 | Normaliza cuestionario |
| E3 – Training Summary | 440-620 | Construye contexto, usa last_plan |
| E4 – Training Plan Generator | 640-950 | Genera plan, aplica progresión |
| E5 – Training Plan Validator | 970-1020 | Valida seguridad |
| E6 – Exercise Normalizer | 1040-1230 | Mapea ejercicios a BD |
| E7 – Training Plan Assembler | 1250-1430 | Ensambla plan técnico |
| E7.5 – Training Plan Enricher | 1450-1620 | Enriquece con nombres y videos |

**Documentación de Prompts:**
```
/app/docs/agent_prompts_v2.0.0_evolutionary.md
```
- Contiene los prompts completos de E1, E3, E4
- Versionado y documentado para referencia

---

### 5.2 Estructura del Código del Workflow

**Organización:**

```typescript
// 1. Imports y Schemas
import { Agent, Runner } from "@openai/agents";
import { z } from "zod";

// 2. Definición de Schemas Zod
const E1AnalizadorDePerfilSchema = z.object({...});
// ... schemas para cada agente

// 3. Definición de Agentes
const e1AnalizadorDePerfil = new Agent({
  name: "E1 – Analizador de Perfil",
  instructions: `Prompt completo del agente...`,
  model: "gpt-4.1",
  outputType: E1AnalizadorDePerfilSchema,
  modelSettings: {
    temperature: 0.2,
    maxTokens: 2048
  }
});

// 4. Función Principal: runWorkflow
export const runWorkflow = async (workflow: WorkflowInput) => {
  // Detecta tipo de flujo
  // Construye contexto con STATE
  // Ejecuta agentes secuencialmente
  // Retorna respuesta
};

// 5. Servidor Express
const app = express();
app.post('/api/edn360/run-training-workflow', async (req, res) => {
  const result = await runWorkflow(req.body);
  res.json(result);
});
```

---

### 5.3 Proceso para Cambios en Prompts

#### Paso 1: Identificar Necesidad de Cambio

**Casos comunes:**
- Agente no está detectando cambios en el historial
- Plan generado no tiene suficiente progresión
- Seguridad articular insuficiente
- Ejercicios inadecuados

**Ejemplo:**
> "E4 no está aumentando el volumen lo suficiente cuando hay progresión"

#### Paso 2: Proponer Cambio

**Ubicación:**
- Archivo: `/app/edn360-workflow-service/src/edn360_workflow.ts`
- Buscar el agente específico (e.g., `const e4TrainingPlanGenerator`)

**Modificación:**
```typescript
// ANTES:
"1. PROGRESSION LOGIC:
   - If user has been training for 4+ weeks → increase volume by 10-15%"

// DESPUÉS:
"1. PROGRESSION LOGIC:
   - If user has been training for 4+ weeks → increase volume by 15-20%
   - If user reports 'want more challenge' → increase intensity (lower reps, higher RPE)"
```

#### Paso 3: Validación Local

**Reiniciar Microservicio:**
```bash
sudo supervisorctl restart edn360-workflow-service
```

**Monitorear Logs:**
```bash
tail -f /var/log/supervisor/edn360-workflow-service.out.log
```

**Probar con Caso Real:**
```bash
curl -X POST http://localhost:8001/api/training-plan \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_ID",
    "questionnaire_ids": ["quest_id_1", "quest_id_2"],
    "previous_training_plan_id": "plan_id"
  }'
```

**Verificar:**
- ✅ ¿El plan generado refleja el cambio?
- ✅ ¿Los logs muestran el comportamiento esperado?
- ✅ ¿No hay errores en el workflow?

#### Paso 4: Documentar Cambio

**Actualizar Documentación:**
```
/app/docs/agent_prompts_v2.0.0_evolutionary.md
```

**Agregar al Changelog:**
```markdown
### v2.0.1 (2025-12-04)
- ✅ E4: Aumentado rango de progresión de volumen de 10-15% a 15-20%
- ✅ E4: Agregada detección de "want more challenge" para ajustar intensidad
```

#### Paso 5: Testing E2E

**Casos de Prueba:**
1. Plan inicial (sin historial) → Verificar que sigue siendo conservador
2. Primer seguimiento con "quiero más desafío" → Verificar incremento de volumen/intensidad
3. Segundo seguimiento normal → Verificar progresión estándar

**Usar Testing Agent:**
```bash
# (Desde el agente principal)
# Llamar al testing agent para validar los 3 casos
```

#### Paso 6: Commit y Deploy

**Git Commit:**
```bash
git add /app/edn360-workflow-service/src/edn360_workflow.ts
git add /app/docs/agent_prompts_v2.0.0_evolutionary.md
git commit -m "feat(E4): Increase progression range and detect challenge requests"
```

**Deploy:**
- Si usas entorno de staging → deploy allí primero
- Si es producción directa → el supervisor ya está corriendo la versión actualizada

---

### 5.4 Mejores Prácticas

**DO:**
- ✅ Siempre documentar cambios en `/app/docs/agent_prompts_v2.0.0_evolutionary.md`
- ✅ Probar con casos reales antes de considerar completo
- ✅ Mantener changelog actualizado
- ✅ Usar ejemplos concretos en los prompts
- ✅ Especificar límites numéricos (e.g., "15-20%" no "más volumen")

**DON'T:**
- ❌ Cambiar múltiples agentes a la vez sin testing
- ❌ Usar lenguaje ambiguo ("un poco más", "mejor")
- ❌ Olvidar actualizar `modelSettings.maxTokens` si el prompt crece mucho
- ❌ Modificar schemas Zod sin actualizar el output del agente

---

## 6. Flujos de Datos Completos

### 6.1 Flujo Caso A: Primer Plan

**Entrada UI:**
```
Usuario selecciona:
- Cliente: Jorge (user_id: "1764016044644335")
- Cuestionario Previo: Inicial (quest_inicial_001)
- Cuestionario Nuevo: (ninguno)
- Plan Anterior: (ninguno)
Click "Generar Plan"
```

**Request Frontend → Backend:**
```json
POST /api/training-plan
{
  "user_id": "1764016044644335",
  "questionnaire_ids": ["quest_inicial_001"],
  "previous_training_plan_id": null
}
```

**Backend: Construcción de STATE:**
```python
# 1. Lee client_drawers
drawer = await get_drawer_by_user_id("1764016044644335")
all_questionnaires = drawer.services.shared_questionnaires
# Resultado: [quest_inicial_001]

# 2. Identifica
initial_questionnaire = all_questionnaires[0]  # quest_inicial_001
current_q = all_questionnaires[0]  # quest_inicial_001
previous_followups = []

# 3. Lee training_plans_v2
all_plans = await edn360_db.training_plans_v2.find(...)
# Resultado: []

# 4. Construye STATE
state = {
  "initial_questionnaire": {...},
  "previous_followups": [],
  "previous_plans": [],
  "last_plan": null
}
```

**Request Backend → Microservicio:**
```json
POST http://localhost:4000/api/edn360/run-training-workflow
{
  "input": {
    "input_as_text": "{\"user_profile\": {...}, \"current_questionnaire\": {...}}"
  },
  "state": {
    "initial_questionnaire": {...},
    "previous_followups": [],
    "previous_plans": [],
    "last_plan": null
  }
}
```

**Microservicio: Ejecución:**
```
🔄 Detectado flujo EVOLUTIVO con STATE
📊 Tipo de generación: INICIAL
🚀 E1 → E2 → E3 → E4 → E5 → E6 → E7 → E7.5
✅ Plan generado
```

**Response Microservicio → Backend:**
```json
{
  "client_training_program_enriched": {
    "title": "Plan Foundational Upper/Lower",
    "sessions": [...],
    "general_notes": [...]
  }
}
```

**Backend: Guardado:**
```python
# Guarda en training_plans_v2
training_plan_doc = {
  "user_id": "1764016044644335",
  "questionnaire_submission_id": "quest_inicial_001",
  "created_at": "2025-01-20T12:00:00Z",
  "plan": {...},
  "status": "draft",
  "is_evolutionary": False  # ← Primer plan
}
await edn360_db.training_plans_v2.insert_one(training_plan_doc)
```

**Response Backend → Frontend:**
```json
{
  "client_training_program_enriched": {...},
  "is_evolutionary": false
}
```

**Frontend: Visualización:**
```
TrainingPlanCard muestra el plan
Usuario puede:
- Editar
- Enviar por email
- Exportar PDF
```

---

### 6.2 Flujo Caso B: Primer Seguimiento

**Entrada UI:**
```
Usuario selecciona:
- Cliente: Jorge (user_id: "1764016044644335")
- Cuestionario Previo: Inicial (quest_inicial_001)
- Cuestionario Nuevo: Seguimiento 1 (quest_seguimiento_001)
- Plan Anterior: Plan 1 (plan_id_123)
Click "Generar Plan"
```

**Request Frontend → Backend:**
```json
POST /api/training-plan
{
  "user_id": "1764016044644335",
  "questionnaire_ids": ["quest_inicial_001", "quest_seguimiento_001"],
  "previous_training_plan_id": "plan_id_123"
}
```

**Backend: Construcción de STATE:**
```python
# 1. Lee client_drawers
all_questionnaires = [quest_inicial_001, quest_seguimiento_001]
# Ordenados por submitted_at

# 2. Identifica
initial_questionnaire = all_questionnaires[0]  # quest_inicial_001
current_q = all_questionnaires[1]  # quest_seguimiento_001
previous_followups = []  # No hay cuestionarios entre inicial y seguimiento_001

# 3. Lee training_plans_v2
all_plans = [plan_1]

# 4. Filtra por previous_training_plan_id
previous_plans = [plan_1]
last_plan = plan_1

# 5. Construye STATE
state = {
  "initial_questionnaire": {...},
  "previous_followups": [],
  "previous_plans": [plan_1],
  "last_plan": plan_1
}
```

**Request Backend → Microservicio:**
```json
POST http://localhost:4000/api/edn360/run-training-workflow
{
  "input": {
    "input_as_text": "{\"user_profile\": {...}, \"current_questionnaire\": {\"submission_id\": \"quest_seguimiento_001\", ...}}"
  },
  "state": {
    "initial_questionnaire": {...},
    "previous_followups": [],
    "previous_plans": [
      {
        "_id": "plan_id_123",
        "created_at": "2025-01-20T12:00:00Z",
        "plan": {
          "sessions": [
            {
              "blocks": [
                {
                  "exercises": [
                    {"series": 3, "reps": "8-12", "rpe": "7"}
                  ]
                }
              ]
            }
          ]
        }
      }
    ],
    "last_plan": {...}
  }
}
```

**Microservicio: Ejecución:**
```
🔄 Detectado flujo EVOLUTIVO con STATE
📊 Tipo de generación: EVOLUTIVO
📋 Previous plans: 1
🚀 E1 (compara inicial vs seguimiento)
🚀 E3 (usa last_plan para contexto)
🚀 E4 (genera plan evolutivo: series 3→4, reps 8-12→6-10, rpe 7→8)
✅ Plan generado con progresión
```

**Response Microservicio → Backend:**
```json
{
  "client_training_program_enriched": {
    "title": "Plan Evolutivo Upper/Lower - Fase 2",
    "sessions": [
      {
        "blocks": [
          {
            "exercises": [
              {
                "series": 4,  // ← Progresión
                "reps": "6-10",
                "rpe": "8",
                "notes": "Progresión desde Plan 1"
              }
            ]
          }
        ]
      }
    ],
    "general_notes": [
      "Plan progresado desde Plan 1: +15% volumen",
      "Hombro ha mejorado según seguimiento"
    ]
  }
}
```

**Backend: Guardado:**
```python
training_plan_doc = {
  "user_id": "1764016044644335",
  "questionnaire_submission_id": "quest_seguimiento_001",
  "created_at": "2025-01-27T14:00:00Z",
  "plan": {...},
  "status": "draft",
  "is_evolutionary": True  # ← Plan evolutivo
}
```

**Response Backend → Frontend:**
```json
{
  "client_training_program_enriched": {...},
  "is_evolutionary": true  // ← Indica evolución
}
```

---

## Resumen Ejecutivo

### ¿Qué tienes ahora?

1. **✅ Arquitectura Clara:**
   - Frontend (React) → Backend (FastAPI) → Microservicio (Node.js + OpenAI)
   - Flujo documentado paso a paso

2. **✅ Esquema de BD Completo:**
   - `users`: Clientes
   - `client_drawers`: Cuestionarios
   - `training_plans_v2`: Planes de entrenamiento
   - Relaciones claras y ejemplos reales

3. **✅ Contratos de Endpoints:**
   - Request/Response de todos los endpoints
   - Ejemplos JSON reales
   - Campos obligatorios vs opcionales

4. **✅ Contrato con Workflow:**
   - Estructura completa de STATE
   - Ejemplos de planes inicial y evolutivo
   - Diferencias visibles entre progresiones

5. **✅ Proceso de Cambios:**
   - Dónde están los prompts
   - Cómo modificarlos
   - Cómo validar y desplegar

### ¿Qué puedes hacer con esto?

- **Control Total:** Sabes exactamente dónde se guardan los datos y cómo se relacionan
- **Iteración Rápida:** Puedes modificar prompts y probar cambios en minutos
- **Decisiones Informadas:** Tienes la información para decidir sobre arquitectura y features
- **Apertura a Terceros:** Documentación lista para compartir si decides abrir parte del sistema

---

**Próximos Pasos Sugeridos:**
1. Revisar este documento completo
2. Hacer preguntas sobre cualquier parte que no esté clara
3. Probar flujo completo con datos reales
4. Iterar sobre prompts según necesidades de negocio
