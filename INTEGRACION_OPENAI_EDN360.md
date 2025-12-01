# 🔌 INTEGRACIÓN OPENAI - EDN360 TRAINPLAN

**Última actualización:** 28 Noviembre 2025  
**Versión:** 1.0.0

---

## 📋 ÍNDICE

1. [Configuración del ID](#configuración-del-id)
2. [Cómo llamamos a OpenAI](#cómo-llamamos-a-openai)
3. [INPUT enviado a OpenAI](#input-enviado-a-openai)
4. [OUTPUT esperado de OpenAI](#output-esperado-de-openai)
5. [Flujo completo](#flujo-completo)
6. [Cómo actualizar el ID](#cómo-actualizar-el-id)

---

## 1️⃣ CONFIGURACIÓN DEL ID

### Ubicación
El ID del Assistant/Workflow se configura en:

```
Archivo: /app/backend/.env
Línea: 58
Variable: EDN360_CORE_ASSISTANT_ID
```

**Contenido actual:**
```bash
EDN360_CORE_ASSISTANT_ID="asst_MSoK0Jfj1VgSvRevHPjY9Yb2"
```

### Formato esperado
- Si usas **Assistants API**: `asst_XXXXXXXXXXXXX` (formato antiguo)
- Si usas **Workflows API**: `wf_XXXXXXXXXXXXX` (nuevo Agent Builder)

**NOTA:** Si cambias de Assistants a Workflows, también hay que modificar el código del servicio (ver sección 6).

---

## 2️⃣ CÓMO LLAMAMOS A OPENAI

### Endpoint actual: **Assistants API**

**Archivo:** `/app/backend/services/training_workflow_service.py`

**Método:** `call_training_workflow()`

**Pasos:**

1. **Crear Thread**
   ```python
   thread = client.beta.threads.create()
   ```

2. **Enviar mensaje con el EDN360Input**
   ```python
   client.beta.threads.messages.create(
       thread_id=thread.id,
       role="user",
       content=input_json  # JSON como string
   )
   ```

3. **Ejecutar Assistant con create_and_poll**
   ```python
   run = client.beta.threads.runs.create_and_poll(
       thread_id=thread.id,
       assistant_id=EDN360_CORE_ASSISTANT_ID
   )
   ```

4. **Obtener respuesta del thread**
   ```python
   messages = client.beta.threads.messages.list(
       thread_id=thread.id,
       order="desc"
   )
   final_message = messages.data[0].content[0].text.value
   ```

5. **Parsear JSON y validar**
   ```python
   workflow_response = json.loads(final_message)
   # Debe contener: client_training_program_enriched
   ```

### Configuración
- **API Key:** `EDN360_OPENAI_API_KEY` (variable de entorno)
- **Assistant ID:** `EDN360_CORE_ASSISTANT_ID` (variable de entorno)
- **Timeout:** Sin timeout explícito (usa polling hasta que complete)

---

## 3️⃣ INPUT ENVIADO A OPENAI

### Formato exacto

Cuando el usuario pulsa "Generar plan de entrenamiento", el backend:

1. **Construye el EDN360Input** (archivo: `services/edn360_input_builder.py`)
2. **Lo serializa a JSON string**
3. **Lo envía tal cual al thread**

### Estructura del JSON enviado:

```json
{
  "user_profile": {
    "user_id": "1764168881795908",
    "name": "Jorge2",
    "email": "jorge31011987@gmail.com",
    "age": 38,
    "gender": "male",
    "height": 175,
    "weight": 78,
    "subscription": {
      "plan": "premium",
      "status": "active"
    }
  },
  "questionnaires": [
    {
      "submission_id": "1764169432140799",
      "type": "initial",
      "submitted_at": "2025-11-26T15:03:52.140000",
      "source": "initial",
      "answers": {
        "fitness_goal": "hipertrofia",
        "training_experience": "intermedio",
        "days_per_week": 4,
        "session_duration": 60,
        "available_equipment": ["mancuernas", "barra", "banco", "máquinas"],
        "injuries": "ninguna",
        "health_conditions": "ninguna",
        "preferred_training_style": "upper_lower",
        "training_location": "gimnasio",
        ...todas las demás respuestas del cuestionario...
      }
    }
  ],
  "context": {
    "request_type": "training_plan_generation",
    "timestamp": "2025-11-28T13:45:30.123456",
    "version": "1.0.0"
  }
}
```

### Campos importantes del INPUT:

| Campo | Descripción | Origen |
|-------|-------------|--------|
| `user_profile` | Datos básicos del cliente | Colección `users` |
| `questionnaires` | Array de cuestionarios (inicial + seguimientos) | Colección `client_drawers.services.shared_questionnaires` |
| `questionnaires[].answers` | Todas las respuestas del cuestionario | Del payload del cuestionario |
| `context` | Metadata de la petición | Generado por el backend |

### NO modificamos el input

**IMPORTANTE:** El backend **NO añade instrucciones extra** ni modifica el prompt. El JSON se envía tal cual. Las instrucciones deben estar en el **System Prompt** de tu Assistant/Workflow.

---

## 4️⃣ OUTPUT ESPERADO DE OPENAI

### Formato requerido

Tu Assistant/Workflow **DEBE** devolver un JSON con esta estructura exacta:

```json
{
  "client_training_program_enriched": {
    "title": "Programa de Hipertrofia Upper/Lower",
    "summary": "Descripción del plan...",
    "goal": "hipertrofia",
    "training_type": "upper_lower",
    "days_per_week": 4,
    "session_duration_min": 60,
    "weeks": 4,
    "general_notes": [
      "Nota 1",
      "Nota 2"
    ],
    "sessions": [
      {
        "id": "D1",
        "name": "Upper Body Push",
        "focus": ["upper_body", "push_focus"],
        "session_notes": ["Nota de la sesión"],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["pecho", "hombros"],
            "secondary_muscles": ["tríceps"],
            "exercises": [
              {
                "order": 1,
                "name": "Press Banca con Barra",
                "primary_group": "pecho",
                "secondary_group": "tríceps",
                "series": 4,
                "reps": "8-10",
                "rpe": 8,
                "video_url": "https://www.youtube.com/watch?v=ejemplo",
                "notes": "Notas del ejercicio"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### ⚠️ CLAVE RAÍZ OBLIGATORIA

**MUY IMPORTANTE:** El JSON **DEBE tener** como clave raíz:

```json
{
  "client_training_program_enriched": { ... }
}
```

**NO debe ser:**
- `client_training_program` ❌
- `training_plan` ❌
- `plan` ❌
- Sin wrapper (directamente el plan) ❌

### Validación en el backend

El backend valida (archivo: `training_workflow_service.py`, línea ~204):

```python
if "client_training_program_enriched" not in workflow_response:
    raise Exception(
        f"La respuesta no contiene 'client_training_program_enriched'. "
        f"Claves recibidas: {list(workflow_response.keys())}"
    )
```

---

## 5️⃣ FLUJO COMPLETO

### Diagrama del proceso

```
USUARIO PULSA BOTÓN
     ↓
Frontend: POST /api/training-plan
{
  "user_id": "1764168881795908",
  "questionnaire_submission_id": "1764169432140799"
}
     ↓
Backend valida user y questionnaire
     ↓
Backend construye EDN360Input
(user_profile + questionnaires + context)
     ↓
Backend serializa a JSON string
     ↓
Backend crea Thread en OpenAI
     ↓
Backend envía mensaje al Thread
(contenido = EDN360Input JSON)
     ↓
Backend ejecuta Assistant/Workflow
con create_and_poll()
     ↓
OpenAI procesa (1-2 minutos)
Agentes E1-E7.5 generan plan
Consultan BD de ejercicios
     ↓
OpenAI devuelve mensaje en Thread
(contenido = JSON del plan)
     ↓
Backend lee último mensaje
     ↓
Backend parsea JSON
     ↓
Backend valida que tenga
"client_training_program_enriched"
     ↓
Backend guarda snapshot en
edn360_snapshots
     ↓
Backend guarda plan en
training_plans_v2
     ↓
Backend devuelve al Frontend:
{
  "client_training_program_enriched": { ... }
}
     ↓
Frontend renderiza plan en UI
(sesiones, bloques, ejercicios, videos)
```

### Persistencia de datos

**1. Snapshot inmutable** (`edn360_snapshots`):
```javascript
{
  snapshot_id: "uuid",
  user_id: "1764168881795908",
  created_at: "2025-11-28T...",
  version: "1.0.0",
  type: "training_plan_v1",
  input: { ...EDN360Input completo... },
  workflow_name: "training_plan_v1",
  workflow_response: { ...respuesta completa de OpenAI... },
  status: "success",
  error_message: null
}
```

**2. Plan editable** (`training_plans_v2`):
```javascript
{
  _id: ObjectId,
  user_id: "1764168881795908",
  questionnaire_submission_id: "1764169432140799",
  created_at: "2025-11-28T...",
  plan: { ...client_training_program_enriched... },
  status: "draft",
  version: "1.0.0",
  source: "edn360_workflow_v1"
}
```

### Frontend: Renderizado del plan

El frontend recibe `client_training_program_enriched` y renderiza:

**Metadata:**
- Title (título del plan)
- Summary (resumen)
- Goal, days_per_week, session_duration_min, weeks
- General notes (notas generales)

**Por cada session:**
- ID y Name (D1, D2, D3...)
- Focus tags (upper_body, push_focus, etc.)
- Session notes

**Por cada block:**
- ID (A, B, C...)
- Primary y secondary muscles (badges)

**Por cada exercise:**
- Order (número de orden)
- Name (nombre del ejercicio)
- Primary/secondary group
- Series, Reps, RPE
- **Video URL** (enlace clickeable que abre en nueva pestaña)
- Notes (notas del ejercicio)

---

## 6️⃣ CÓMO ACTUALIZAR EL ID

### Caso A: Nuevo Assistant ID (formato `asst_`)

Si tu workflow publica un **nuevo Assistant**, solo necesitas:

1. **Editar el archivo `.env`:**
   ```bash
   # Línea 58
   EDN360_CORE_ASSISTANT_ID="asst_TU_NUEVO_ID_AQUI"
   ```

2. **Reiniciar el backend:**
   ```bash
   sudo supervisorctl restart backend
   ```

3. **Listo** ✅ - No hay que cambiar código

---

### Caso B: Workflow ID (formato `wf_`)

Si tu workflow usa **Workflows API**, necesitas:

1. **Editar el archivo `.env`:**
   ```bash
   EDN360_CORE_ASSISTANT_ID="wf_TU_WORKFLOW_ID_AQUI"
   ```

2. **Modificar el código** en `training_workflow_service.py`:

   El código actual usa Assistants API:
   ```python
   run = client.beta.threads.runs.create_and_poll(
       thread_id=thread.id,
       assistant_id=EDN360_CORE_ASSISTANT_ID
   )
   ```

   Habría que cambiarlo a Workflows API (si existe ese endpoint).

   **NOTA:** A fecha de noviembre 2025, OpenAI Workflows API puede tener diferencias. Necesitaríamos:
   - Documentación oficial de OpenAI sobre Workflows API
   - Verificar si `create_and_poll` funciona con workflow IDs
   - O usar un endpoint diferente

3. **Reiniciar el backend**

---

## 📊 RESUMEN PARA TU WORKFLOW

Para que tu workflow funcione con Trainplan, debe:

### ✅ INPUT que recibirá:
```json
{
  "user_profile": {...},
  "questionnaires": [{
    "submission_id": "...",
    "type": "initial",
    "answers": {
      "fitness_goal": "...",
      "training_experience": "...",
      ...
    }
  }],
  "context": {...}
}
```

### ✅ OUTPUT que debe devolver:
```json
{
  "client_training_program_enriched": {
    "title": "...",
    "summary": "...",
    "goal": "...",
    "training_type": "...",
    "days_per_week": 4,
    "session_duration_min": 60,
    "weeks": 4,
    "general_notes": [...],
    "sessions": [
      {
        "id": "D1",
        "name": "...",
        "focus": [...],
        "session_notes": [...],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": [...],
            "secondary_muscles": [...],
            "exercises": [
              {
                "order": 1,
                "name": "...",
                "primary_group": "...",
                "secondary_group": "...",
                "series": 4,
                "reps": "8-10",
                "rpe": 8,
                "video_url": "https://...",
                "notes": "..."
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### ⚠️ Requisitos críticos:
1. La clave raíz DEBE ser `client_training_program_enriched`
2. El JSON debe ser válido (sin texto, sin markdown)
3. Cada ejercicio DEBE tener `video_url` válido
4. Los campos obligatorios (ver spec) no pueden faltar

---

## 🔗 ARCHIVOS DE REFERENCIA

- **Especificación completa:** `/app/EDN360_INPUT_OUTPUT_SPEC.md`
- **Código del servicio:** `/app/backend/services/training_workflow_service.py`
- **Constructor del input:** `/app/backend/services/edn360_input_builder.py`
- **Endpoint:** `/app/backend/server.py` (línea 1035-1265)
- **Configuración:** `/app/backend/.env` (línea 58)

---

## 📞 SOPORTE

Si tu workflow devuelve un formato diferente o necesitas ayuda para adaptarlo, comparte:
1. El JSON de ejemplo que devuelve tu workflow
2. El tipo de ID que tienes (asst_ o wf_)
3. Capturas de pantalla de errores

Y ajustaremos la integración según sea necesario.
