# 🎯 FLUJO DEFINITIVO EDN360 - RESUMEN EJECUTIVO

**Fecha**: Noviembre 2025  
**Propósito**: Contrato claro y estable entre Web ↔ Backend ↔ Agentes EDN360

---

## 🔑 PRINCIPIO FUNDAMENTAL

**La web NO "piensa"**:
- Solo recoge cuestionarios
- Solo muestra planes
- Solo permite edición/envío

**Los agentes EDN360 NO se tocan en el día a día**:
- Viven en backend/OpenAI
- Se llaman por endpoints claros
- Jorge solo los modifica si cambia lógica interna

---

## 📊 ARQUITECTURA EN 3 CAPAS

```
┌────────────────────────────────────────────┐
│         CAPA 1: PANEL ADMIN (WEB)          │
│                                            │
│  • Selecciona cuestionario                │
│  • Pulsa "Generar plan"                   │
│  • Ve plan presentable                    │
│  • Edita/ajusta con IA                    │
│  • Envía (PDF/Email/WhatsApp)             │
│                                            │
│  ❌ NO toca agentes ni prompts            │
└───────────────┬────────────────────────────┘
                │
                │ POST /api/training-plan
                │ { user_id, questionnaire_submission_id }
                ▼
┌────────────────────────────────────────────┐
│      CAPA 2: BACKEND (FastAPI)            │
│                                            │
│  1. Valida user_id + submission_id        │
│  2. Construye EDN360Input desde BD        │
│  3. Llama a workflow E1-E7.5              │
│  4. Guarda snapshot                       │
│  5. Devuelve plan enriched                │
│                                            │
│  ✅ Construye input                       │
│  ✅ Guarda trazabilidad                   │
│  ❌ NO toca lógica de agentes             │
└───────────────┬────────────────────────────┘
                │
                │ EDN360Input
                │ (user_profile + questionnaires + context)
                ▼
┌────────────────────────────────────────────┐
│   CAPA 3: AGENTES EDN360 (OpenAI)         │
│                                            │
│  E1 → E2 → E3 → E4 → E5 → E6 → E7 → E7.5 │
│                                            │
│  • Usa BD ejercicios (file_search)        │
│  • Devuelve plan enriched                 │
│                                            │
│  ✅ Jorge los modifica cuando quiera      │
│  ❌ Web nunca los toca                    │
└────────────────────────────────────────────┘
```

---

## 1️⃣ FLUJO DE ENTRENAMIENTO

### 1.1 UX del Admin (Jorge)

**Ubicación**: `/admin` → Cliente → Tab "Cuestionarios"

**Acciones**:
1. **Veo** lista de cuestionarios (inicial + seguimientos)
2. **Selecciono** el cuestionario a usar
3. **Pulso** "Generar plan de entrenamiento"
4. **Espero** (puede tardar 30-60s)
5. **Veo** plan en tab "Entrenamiento":
   - Estructura legible (días, bloques, ejercicios)
   - Videos incrustados
   - Notas de seguridad
6. **Edito** (manualmente o con IA) si quiero
7. **Envío** cuando esté listo:
   - PDF
   - Email
   - WhatsApp

**NO hago**:
- ❌ Tocar agentes
- ❌ Configurar prompts
- ❌ Mapear ejercicios manualmente

---

### 1.2 Endpoint (Ya Implementado ✅)

```http
POST /api/training-plan
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "user_id": "1764016044644335",
  "questionnaire_submission_id": "1764016775848319"
}
```

**Response**:
```json
{
  "client_training_program_enriched": {
    "title": "Hipertrofia con enfoque articular seguro (4 días)",
    "summary": "Plan de 4 días...",
    "goal": "Ganar músculo...",
    "training_type": "upper_lower",
    "days_per_week": 4,
    "session_duration_min": 45,
    "weeks": 4,
    "sessions": [
      {
        "id": "D1",
        "name": "Upper 1 – Empuje dominante",
        "blocks": [
          {
            "exercises": [
              {
                "db_id": "E049",
                "name": "press banca smith agarre cerrado",
                "video_url": "https://drive.google.com/...",
                "series": 3,
                "reps": "10-12",
                "rpe": "7"
              }
            ]
          }
        ],
        "session_notes": ["No overhead pressing..."]
      }
    ],
    "general_notes": ["Calentar hombros..."]
  }
}
```

---

### 1.3 Backend Construye EDN360Input

**Fuentes de datos**:
- `users` collection → user_profile
- `client_drawers` collection → questionnaires

**Input construido**:
```json
{
  "user_profile": {
    "user_id": "1764016044644335",
    "full_name": "Jorge",
    "email": "jorge@example.com",
    "age": 38,
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
        /* ~100 respuestas crudas */
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

---

### 1.4 Workflow E1-E7.5 (OpenAI)

**Input**: `EDN360Input`

**Proceso Interno** (Jorge lo controla):
1. **E1**: Analiza perfil
2. **E2**: Parsea cuestionario
3. **E3**: Resume contexto training
4. **E4**: Genera plan base
5. **E5**: Valida seguridad
6. **E6**: Mapea ejercicios a BD
7. **E7**: Ensambla plan técnico
8. **E7.5**: Enriquece con nombres/videos (file_search)

**Output**: `client_training_program_enriched`

**Herramientas**:
- BD de ejercicios (file_search)
- Prompts específicos por agente
- Validaciones de seguridad

---

### 1.5 Backend Guarda y Responde

**Acciones**:
1. **Guardar snapshot** en `edn360_snapshots`:
   ```javascript
   {
     user_id: "...",
     workflow_name: "training_plan_v1",
     input: EDN360Input,
     workflow_response: client_training_program_enriched,
     status: "success",
     created_at: ISODate("...")
   }
   ```

2. **Opcional**: Guardar en `training_plans_v2` (nueva collection):
   ```javascript
   {
     _id: "plan_uuid_123",
     user_id: "...",
     questionnaire_submission_id: "...",
     snapshot_id: "...",
     program: client_training_program_enriched,
     status: "draft",  // draft | sent | archived
     created_at: ISODate("..."),
     updated_at: ISODate("...")
   }
   ```

3. **Devolver** al frontend:
   ```json
   {
     "client_training_program_enriched": { ... }
   }
   ```

---

### 1.6 Frontend Muestra Plan

**Tab "Entrenamiento"**:

```jsx
// Renderizado del plan
<TrainingPlanView plan={client_training_program_enriched}>
  
  {/* Header */}
  <PlanHeader
    title={plan.title}
    summary={plan.summary}
    goal={plan.goal}
    metadata={{
      days_per_week: plan.days_per_week,
      session_duration: plan.session_duration_min,
      weeks: plan.weeks
    }}
  />
  
  {/* Sessions */}
  {plan.sessions.map(session => (
    <SessionCard key={session.id}>
      <h3>{session.name}</h3>
      <Tags>{session.focus}</Tags>
      
      {session.blocks.map(block => (
        <BlockSection key={block.id}>
          <MuscleGroups
            primary={block.primary_muscles}
            secondary={block.secondary_muscles}
          />
          
          {block.exercises.map(exercise => (
            <ExerciseCard key={exercise.order}>
              <ExerciseInfo
                name={exercise.name}
                series={exercise.series}
                reps={exercise.reps}
                rpe={exercise.rpe}
              />
              
              {exercise.video_url && (
                <VideoEmbed url={exercise.video_url} />
              )}
            </ExerciseCard>
          ))}
        </BlockSection>
      ))}
      
      <SessionNotes notes={session.session_notes} />
    </SessionCard>
  ))}
  
  {/* General Notes */}
  <GeneralNotes notes={plan.general_notes} />
  
  {/* Actions */}
  <ActionButtons>
    <Button onClick={handleEditWithIA}>Editar con IA</Button>
    <Button onClick={handleGeneratePDF}>Generar PDF</Button>
    <Button onClick={handleSendEmail}>Enviar Email</Button>
    <Button onClick={handleShareWhatsApp}>Compartir WhatsApp</Button>
  </ActionButtons>
  
</TrainingPlanView>
```

**Funcionalidades adicionales**:
- **Edición manual**: Cambiar textos, series, reps, etc.
- **Edición con IA**: "Sube 1 serie a todos los ejercicios de pierna"
- **Histórico**: Ver planes anteriores del mismo cliente
- **Comparación**: Ver diferencias entre planes

---

## 2️⃣ FLUJO FUTURO DE NUTRICIÓN

### 2.1 UX del Admin (Cuando esté listo)

**Ubicación**: `/admin` → Cliente → Tabs "Cuestionarios" + "Entrenamiento"

**Acciones**:
1. **Selecciono** cuestionario (inicial o seguimiento)
2. **Selecciono** plan de entrenamiento actual
3. **Pulso** "Generar plan de nutrición"
4. **Espero**
5. **Veo** plan en tab "Nutrición":
   - Macros diarios
   - Menús por día
   - Días altos/bajos carbos
   - Ajustes según entrenamientos
6. **Edito** si quiero
7. **Envío**

---

### 2.2 Endpoint Futuro

```http
POST /api/nutrition-plan
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "user_id": "1764016044644335",
  "questionnaire_submission_id": "1764016775848319",
  "training_plan_id": "plan_uuid_123"  // Opcional
}
```

**Response**:
```json
{
  "client_nutrition_program_enriched": {
    "title": "Plan Nutricional Personalizado",
    "summary": "...",
    "macros": {
      "calories_avg": 2500,
      "protein_g": 180,
      "carbs_g_high": 300,
      "carbs_g_low": 150,
      "fats_g": 70
    },
    "meals": [...],
    "notes": [...]
  }
}
```

---

### 2.3 Input para Agentes de Nutrición (Idea)

```json
{
  "user_profile": { ... },
  "questionnaires": [ ... ],
  "training_program": {
    // Resumen del plan de entrenamiento
    "days_per_week": 4,
    "session_duration_min": 45,
    "intensity": "high",
    "volume": "moderate"
  },
  "context": {
    "service_type": "full",
    "goal_primary": "muscle_gain"
  }
}
```

**Nota**: El workflow de nutrición puede leer el plan de entrenamiento completo desde el snapshot o desde `training_plans_v2`.

---

## 3️⃣ GESTIÓN DE PLANES (Nueva Collection Sugerida)

### ¿Por qué `training_plans_v2`?

**Problema con solo snapshots**:
- Los snapshots son inmutables (correcto para trazabilidad)
- Pero si Jorge quiere **editar** un plan después, necesita una copia mutable

**Solución**: `training_plans_v2` collection

```javascript
{
  _id: "plan_uuid_123",
  user_id: "1764016044644335",
  type: "training",  // "training" | "nutrition"
  questionnaire_submission_id: "1764016775848319",
  snapshot_id: "snapshot_uuid_456",  // Referencia al snapshot original
  
  // El plan actual (puede ser editado)
  program: {
    /* client_training_program_enriched */
  },
  
  // Metadata
  status: "draft",  // "draft" | "sent" | "active" | "archived"
  version: 1,  // Incrementa si se edita
  created_at: ISODate("..."),
  updated_at: ISODate("..."),
  sent_at: null,
  
  // Ediciones
  edit_history: [
    {
      edited_at: ISODate("..."),
      edited_by: "admin_id",
      changes: "Aumentó 1 serie en ejercicios de pierna"
    }
  ]
}
```

**Ventajas**:
- Jorge puede editar sin perder el original (snapshot)
- Histórico de versiones
- Estado del plan (borrador, enviado, activo)
- Facilita endpoints de edición/envío

---

## 4️⃣ ENDPOINTS ADICIONALES SUGERIDOS

### GET `/api/admin/users/{user_id}/training-plans`

**Propósito**: Listar todos los planes de entrenamiento del usuario

**Response**:
```json
{
  "training_plans": [
    {
      "plan_id": "plan_uuid_123",
      "title": "Hipertrofia...",
      "created_at": "2025-11-26T...",
      "status": "sent",
      "version": 2
    }
  ]
}
```

---

### PUT `/api/admin/training-plans/{plan_id}`

**Propósito**: Editar un plan existente

**Body**:
```json
{
  "program": {
    /* client_training_program_enriched modificado */
  },
  "changes_description": "Aumentó 1 serie en todos los ejercicios de pierna"
}
```

---

### POST `/api/admin/training-plans/{plan_id}/send`

**Propósito**: Enviar plan al cliente

**Body**:
```json
{
  "method": "email",  // "email" | "whatsapp" | "pdf"
  "message": "Aquí está tu plan personalizado..."
}
```

**Acción**:
- Genera PDF si es necesario
- Envía email o genera link WhatsApp
- Actualiza `status: "sent"` y `sent_at`

---

## 5️⃣ RESTRICCIONES Y GARANTÍAS

### ✅ LO QUE JORGE PUEDE HACER SIN TOCAR AGENTES

1. **Editar planes manualmente** (texto, series, reps)
2. **Usar IA para ajustes** ("Sube 1 serie", "Cambia RPE a 8")
3. **Cambiar formato de presentación** (CSS, PDF layout)
4. **Agregar/quitar ejercicios** (desde interfaz admin)
5. **Cambiar workflows** (sustituir E1-E7.5 por otra versión)

### ❌ LO QUE JORGE NUNCA DEBE HACER

1. Modificar `EDN360Input` (contrato estable)
2. Modificar `client_training_program_enriched` (contrato estable)
3. Tocar el endpoint `/api/training-plan` (ya funciona)
4. Cambiar cómo se construye el input desde BD

### ✅ LO QUE JORGE PUEDE MODIFICAR EN AGENTES

1. **Prompts de cada agente** (E1, E2, ... E7.5)
2. **Lógica de mapeo de ejercicios** (E6)
3. **Base de datos de ejercicios** (agregar/modificar)
4. **Validaciones de seguridad** (E5)
5. **Tools y funciones** (file_search, custom functions)

**Sin romper nada** porque el contrato Input/Output se mantiene.

---

## 6️⃣ VERSIONADO DEL SISTEMA

### Versiones de Workflows

```
training_plan_v1 → Versión actual (E1-E7.5)
training_plan_v2 → Futura mejora (E1-E7.5 optimizado)
training_plan_v3 → Nueva arquitectura (E1-E10)
```

**Cada versión**:
- Mismo contrato: `EDN360Input` → `client_training_program_enriched`
- Puede tener lógica interna diferente
- Se identifica por `workflow_name` en snapshot

**Ventaja**: Jorge puede A/B test workflows sin tocar la web.

---

### Versiones de Formato de Output

Si en el futuro necesitas cambiar el formato de `client_training_program_enriched`:

**Opción 1**: Mantener retrocompatibilidad
```json
{
  "client_training_program_enriched": {
    "version": "2.0",
    "title": "...",
    /* nuevos campos */
  }
}
```

**Opción 2**: Crear nuevo contrato
```json
{
  "client_training_program_v2": {
    /* nueva estructura */
  }
}
```

Y actualizar frontend para soportar ambos.

---

## 7️⃣ DIAGRAMA DE DATOS

```
┌─────────────────────────────────────────────────────┐
│              BD WEB (test_database)                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  users                                              │
│  └─ full_name, email, age, etc.                    │
│                                                     │
│  nutrition_questionnaire_submissions                │
│  └─ submission_id, responses, submitted_at          │
│                                                     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│         BD TÉCNICA (edn360_app)                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  client_drawers                                     │
│  └─ services.shared_questionnaires[]                │
│     └─ submission_id, source, raw_payload           │
│                                                     │
│  edn360_snapshots  (INMUTABLES)                     │
│  └─ input, workflow_response, status                │
│                                                     │
│  training_plans_v2  (EDITABLES) [NUEVA]            │
│  └─ program, status, version, edit_history          │
│                                                     │
│  nutrition_plans_v2  (FUTURO)                       │
│  └─ similar a training_plans_v2                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Flujo de datos**:
1. Usuario envía cuestionario → `nutrition_questionnaire_submissions` (BD Web)
2. Dual-write → `client_drawers` (BD Técnica)
3. Admin genera plan → Crea snapshot en `edn360_snapshots`
4. Plan se copia a `training_plans_v2` (editable)
5. Admin edita/envía desde `training_plans_v2`

---

## 8️⃣ ESTADO ACTUAL DE IMPLEMENTACIÓN

### ✅ COMPLETADO

1. **Endpoint `POST /api/training-plan`**
   - Acepta `user_id` + `questionnaire_submission_id`
   - Construye `EDN360Input` desde BD
   - Llama a workflow
   - Guarda snapshot
   - Devuelve `client_training_program_enriched`

2. **Dual-write a `client_drawers`**
   - Cuestionarios se guardan automáticamente
   - Sincronización idempotente

3. **Modelos y Repositories**
   - `EDN360Input` (Pydantic)
   - `EDN360Snapshot` (Pydantic)
   - `client_training_program_enriched` (Pydantic)
   - Repositories para drawers y snapshots

4. **Documentación**
   - `/app/DISEÑO_TO_BE_EDN360_TRAINING.md` (completo)
   - `/app/INFORME_TECNICO_SISTEMA_ACTUAL.md` (AS-IS)

---

### ⚠️ PENDIENTE (Requiere Jorge)

1. **Configurar workflow E1-E7.5 en OpenAI**
   - Crear assistant o cadena de agents
   - Subir BD de ejercicios (file_search)
   - Configurar prompts
   - Obtener `EDN360_TRAINING_WORKFLOW_ID`

2. **Actualizar `.env`**
   ```bash
   EDN360_TRAINING_WORKFLOW_ID="asst_..."
   ```

3. **Ajustar `training_workflow_service.py`**
   - Según método elegido (Assistants API o Function Calling)
   - Manejo de file_search o custom functions

4. **Testing end-to-end**
   - Validar que el workflow devuelve el formato correcto
   - Verificar mapeo de ejercicios
   - Probar con casos edge (ejercicios desconocidos, etc.)

---

### 🔜 PRÓXIMAS MEJORAS

1. **Collection `training_plans_v2`**
   - Para gestión editable de planes
   - Endpoints de edición/envío

2. **Frontend actualizado**
   - Eliminar sistema legacy (polling, generation_jobs)
   - Tab "Entrenamiento" con renderizado del plan
   - Botones de edición/envío

3. **Workflow de Nutrición**
   - Similar a training
   - Endpoint `POST /api/nutrition-plan`
   - Integración con plan de entrenamiento

---

## 9️⃣ RESUMEN EJECUTIVO PARA JORGE

### Lo que tienes ahora

✅ **Backend listo** para recibir llamadas  
✅ **Contrato estable** Input/Output definido  
✅ **Snapshots** para trazabilidad completa  
✅ **Documentación** exhaustiva  

### Lo que necesitas hacer

1. **Configurar workflow E1-E7.5** en OpenAI
2. **Proporcionar ID** del workflow
3. **Probar** flujo end-to-end
4. **Ajustar prompts** si es necesario (sin tocar endpoint)

### Lo que puedes hacer sin tocar la web

- ✅ Cambiar lógica de agentes
- ✅ Mejorar prompts
- ✅ Actualizar BD de ejercicios
- ✅ Crear nuevas versiones de workflows
- ✅ A/B test diferentes configuraciones

### Lo que NO necesitas cambiar nunca

- ❌ Endpoint `/api/training-plan`
- ❌ Formato de `EDN360Input`
- ❌ Formato de `client_training_program_enriched`
- ❌ Cómo la web llama al backend

---

## 🎯 NEXT STEPS

1. **Jorge**: Configurar workflow E1-E7.5 en OpenAI
2. **Jorge**: Proporcionar `EDN360_TRAINING_WORKFLOW_ID`
3. **Emergent**: Ajustar `training_workflow_service.py` si es necesario
4. **Testing conjunto**: Validar flujo completo
5. **Frontend**: Migrar de sistema legacy a nuevo endpoint
6. **Producción**: Deprecar endpoints antiguos

---

**¿Todo claro? ¿Alguna pregunta o ajuste antes de proceder?** 🚀
