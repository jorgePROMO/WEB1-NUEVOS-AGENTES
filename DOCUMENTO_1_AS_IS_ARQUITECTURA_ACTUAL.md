# DOCUMENTO 1: ARQUITECTURA AS IS (Estado Actual)

**Sistema:** E.D.N.360 - Generación de Planes de Entrenamiento y Nutrición  
**Fecha:** Enero 2025  
**Versión:** 1.0  
**Cliente Referencia:** Jorge1  

---

## 📋 TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Diagrama de Flujo Actual](#diagrama-de-flujo-actual)
3. [Inventario de Colecciones MongoDB](#inventario-de-colecciones-mongodb)
4. [Flujo Detallado: Cuestionario → Contexto → Planes](#flujo-detallado)
5. [Puntos de Lectura Dispersos](#puntos-de-lectura-dispersos)
6. [Duplicidades y Contradicciones](#duplicidades-y-contradicciones)
7. [Lógicas Legacy Identificadas](#lógicas-legacy-identificadas)

---

## RESUMEN EJECUTIVO

### 🎯 Núcleo Actual del Sistema EDN360

El sistema E.D.N.360 es una plataforma de generación de planes de entrenamiento y nutrición basada en IA, que utiliza:
- **Backend:** FastAPI + Python
- **Base de datos:** MongoDB
- **Arquitectura de agentes:** Pipeline de 26 agentes especializados (E1-E9 para entrenamiento, N0-N8 para nutrición, ES1-ES4 y NS1-NS4 para seguimientos)

### 🔍 Estado Actual del Flujo de Datos

**El flujo actual es DISPERSO y tiene MÚLTIPLES fuentes de verdad:**

1. **Datos del cliente** se almacenan en **múltiples colecciones** sin un punto centralizado:
   - `questionnaire_responses` (cuestionario inicial de prospección)
   - `nutrition_questionnaire_submissions` (cuestionario nutricional detallado)
   - `users` (datos de usuario autenticado)
   - `generation_jobs` (jobs de generación de planes con contexto temporal)

2. **Los planes generados** se guardan en colecciones separadas:
   - `training_plans` (planes de entrenamiento históricos)
   - `nutrition_plans` (planes de nutrición históricos)
   - Cada plan contiene **datos duplicados** del cuestionario

3. **El contexto del cliente se reconstruye EN CADA EJECUCIÓN:**
   - Los agentes NO leen de una fuente unificada
   - El orquestador (`orchestrator.py`) construye el `ClientContext` desde el cuestionario cada vez
   - No existe persistencia del `ClientContext` entre ejecuciones

### ⚠️ Problemas Identificados

1. **Duplicación de datos:** El mismo cuestionario se copia en cada plan generado
2. **Falta de trazabilidad:** No hay historial unificado de evolución del cliente
3. **Reconstrucción repetida:** Cada job debe re-parsear el cuestionario completo
4. **Versionado inconsistente:** Los planes históricos no están vinculados entre sí
5. **Sin punto único de verdad:** Los datos del cliente están fragmentados en múltiples colecciones

---

## DIAGRAMA DE FLUJO ACTUAL

```
┌──────────────────────────────────────────────────────────────────────┐
│                         USUARIO CLIENTE                               │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                    Completa Cuestionario
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    COLECCIONES DE ENTRADA                             │
├──────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐        ┌────────────────────────────┐      │
│  │ questionnaire_      │        │ nutrition_questionnaire_   │      │
│  │ responses           │        │ submissions                │      │
│  │                     │        │                            │      │
│  │ - Cuestionario      │        │ - Cuestionario nutricional │      │
│  │   inicial           │        │   detallado                │      │
│  │ - Datos prospecto   │        │ - user_id                  │      │
│  │ - stage_name        │        │ - responses (dict)         │      │
│  └─────────────────────┘        │ - submitted_at             │      │
│                                 │ - plan_generated (bool)    │      │
│                                 │ - plan_id (ref)            │      │
│                                 └────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────┘
                                │
                    Admin crea Generation Job
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    GENERATION JOB CREADO                              │
├──────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ generation_jobs                                                │  │
│  │                                                                │  │
│  │ {                                                              │  │
│  │   job_id: "uuid",                                             │  │
│  │   user_id: "1762...",                                         │  │
│  │   type: "training" | "nutrition" | "full",                    │  │
│  │   submission_id: "ref al cuestionario",                       │  │
│  │   status: "pending" → "running" → "completed",                │  │
│  │   progress: { phase, current_agent, percentage }              │  │
│  │ }                                                              │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
                                │
                    Job Worker lo detecta
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    JOB WORKER (Proceso Separado)                      │
├──────────────────────────────────────────────────────────────────────┤
│  1. Lee job pendiente de generation_jobs                             │
│  2. Lee cuestionario de nutrition_questionnaire_submissions          │
│  3. CONSTRUYE ClientContext en memoria (NO persiste)                 │
│  4. Llama al Orquestador con el ClientContext construido             │
└──────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    ORQUESTADOR (orchestrator.py)                      │
├──────────────────────────────────────────────────────────────────────┤
│  Función: initialize_client_context()                                │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ ClientContext (Objeto Pydantic en Memoria)                     │  │
│  │                                                                │  │
│  │ {                                                              │  │
│  │   meta: { client_id, snapshot_id, version },                  │  │
│  │   raw_inputs: { cuestionario_inicial, ... },                  │  │
│  │   training: { profile, capacity, ..., formatted_plan },       │  │
│  │   nutrition: { profile, metabolism, ..., menu_plan }          │  │
│  │ }                                                              │  │
│  │                                                                │  │
│  │ ⚠️ ESTE OBJETO SE DESTRUYE AL TERMINAR EL JOB                  │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  Ejecuta Pipeline:                                                   │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ E1 → E2 → E3 → E4 → E5 → E6 → E7 → E8 → E9                      │  │
│  │ (Agentes de Entrenamiento)                                     │  │
│  │                                                                │  │
│  │ ↓ training.bridge_for_nutrition                                │  │
│  │                                                                │  │
│  │ N0 → N1 → N2 → N3 → N4 → N5 → N6 → N7 → N8                      │  │
│  │ (Agentes de Nutrición)                                         │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
                                │
                    Plan Completo Generado
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    GUARDAR RESULTADO EN BD                            │
├──────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────┐     ┌──────────────────────────────┐   │
│  │ training_plans          │     │ nutrition_plans              │   │
│  │                         │     │                              │   │
│  │ {                       │     │ {                            │   │
│  │   _id: "plan_id",       │     │   _id: "plan_id",            │   │
│  │   user_id,              │     │   user_id,                   │   │
│  │   questionnaire_data,   │     │   questionnaire_data,        │   │
│  │   formatted_plan,       │     │   menu_plan,                 │   │
│  │   generated_at,         │     │   generated_at,              │   │
│  │   month, year           │     │   month, year                │   │
│  │ }                       │     │ }                            │   │
│  │                         │     │                              │   │
│  │ ⚠️ COPIA DUPLICADA       │     │ ⚠️ COPIA DUPLICADA            │   │
│  │ del cuestionario        │     │ del cuestionario             │   │
│  └─────────────────────────┘     └──────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    ACTUALIZAR REFERENCIAS                             │
├──────────────────────────────────────────────────────────────────────┤
│  nutrition_questionnaire_submissions:                                │
│  {                                                                   │
│    plan_generated: true,                                             │
│    plan_id: "ref al plan generado"                                   │
│  }                                                                   │
│                                                                       │
│  generation_jobs:                                                    │
│  {                                                                   │
│    status: "completed",                                              │
│    result: { training_plan_id, nutrition_plan_id }                  │
│  }                                                                   │
└──────────────────────────────────────────────────────────────────────┘
```

### 🔄 Flujo de Seguimiento Mensual

```
┌──────────────────────────────────────────────────────────────────────┐
│  SEGUIMIENTO (30 días después)                                       │
├──────────────────────────────────────────────────────────────────────┤
│  Cliente completa cuestionario de seguimiento                        │
│  ↓                                                                   │
│  Se guarda en: followup_submissions                                  │
│  {                                                                   │
│    user_id,                                                          │
│    previous_plan_id: "ref al plan anterior",                         │
│    responses: { mediciones, adherencia, cambios }                    │
│  }                                                                   │
│  ↓                                                                   │
│  SE REPITE TODO EL FLUJO                                             │
│  ↓                                                                   │
│  PROBLEMA: No hay vínculo claro entre planes sucesivos               │
└──────────────────────────────────────────────────────────────────────┘
```

---

## INVENTARIO DE COLECCIONES MONGODB

### 📦 Colecciones Relacionadas con el Cliente

#### 1. `users`
**Propósito:** Almacenar usuarios autenticados del sistema  
**Uso en EDN360:** Referencia principal del cliente, pero NO contiene cuestionarios

```javascript
{
  _id: "1762094831193507",  // Timestamp-based ID
  username: "jorge1",
  email: "jorge@example.com",
  name: "Jorge Calcerrada",
  role: "user",  // "user" | "admin"
  subscription: {
    status: "active",
    plan: "team",
    payment_status: "verified"
  },
  followup_activated: true,  // Indica si tiene cuestionario de seguimiento activo
  created_at: ISODate("2025-01-05T10:00:00Z"),
  updated_at: ISODate("2025-01-10T12:30:00Z")
}
```

**Problemas:**
- ❌ No contiene datos del cuestionario inicial
- ❌ No tiene historial de planes generados (solo referencias dispersas)
- ❌ No tiene versionado de progresión del cliente

---

#### 2. `questionnaire_responses`
**Propósito:** Almacenar cuestionarios iniciales de prospección (landing page)  
**Uso en EDN360:** Primera captura de datos, pero **NO se usa en generación de planes**

```javascript
{
  _id: "1736950123456789",
  // Datos personales
  nombre: "Jorge Calcerrada",
  edad: "35",
  email: "jorge@example.com",
  whatsapp: "+34612345678",
  
  // Contexto
  objetivo: "Perder grasa y ganar músculo",
  intentos_previos: "Sí, varios",
  dificultades: ["Falta de constancia", "No sé qué comer"],
  tiempo_semanal: "3-4 horas",
  entrena: "Sí, en casa",
  
  // CRM
  stage_name: "Nuevo",
  stage_id: null,
  converted_to_client: false,
  submitted_at: ISODate("2025-01-01T08:00:00Z")
}
```

**Problemas:**
- ❌ Datos básicos, no suficientes para generar plan
- ❌ Queda huérfano cuando el prospecto se convierte en cliente
- ❌ No hay vínculo con `nutrition_questionnaire_submissions`

---

#### 3. `nutrition_questionnaire_submissions` ⭐ **FUENTE ACTUAL DE VERDAD**
**Propósito:** Cuestionario detallado que **SÍ se usa** para generar planes  
**Uso en EDN360:** **ESTE es el cuestionario que lee el orquestador**

```javascript
{
  _id: "1736950234567890",
  user_id: "1762094831193507",  // Referencia a users
  responses: {
    // Datos personales
    nombre_completo: "Jorge Calcerrada",
    email: "jorge@example.com",
    fecha_nacimiento: "1989-05-15",
    sexo: "Hombre",
    profesion: "Ingeniero",
    telefono: "+34612345678",
    
    // Medidas corporales
    peso: "85",
    altura_cm: "178",
    grasa_porcentaje: "22",
    cintura_cm: "92",
    
    // Salud
    medicamentos: "Ninguno",
    enfermedad_cronica: "Ninguna",
    alergias_intolerancias: "Lactosa (leve)",
    hernias_protusiones: "Hernia discal L4-L5 controlada",
    
    // Trabajo y estrés
    estres_profesion: "Moderado-Alto",
    movimiento_trabajo: "Sedentario",
    horas_trabajo: "9-10 horas",
    actividad_fisica_diaria: "Poca",
    
    // Experiencia deportiva
    practicado_deporte: "Sí, natación",
    entrenado_gimnasio: "Sí, hace 2 años",
    resistencia_cardiorespiratoria: "Media",
    fuerza: "Baja",
    flexibilidad: "Baja",
    
    // Disponibilidad
    dias_semana_entrenar: "4",
    tiempo_sesion: "45-60 min",
    entrena_manana_tarde: "Tarde (19:00-21:00)",
    gimnasio: "No, entreno en casa",
    material_casa: "Mancuernas, esterilla, banda elástica",
    
    // Horarios
    hora_levanta: "07:00",
    hora_desayuno: "07:30",
    hora_comida: "14:00",
    hora_cena: "21:00",
    hora_acuesta: "23:30",
    horas_duerme: "7-8",
    
    // Hábitos alimentarios
    comidas_dia: "4",
    alimento_no_soporta: "Pescado azul",
    comida_favorita: "Pasta, arroz",
    dietas_anteriores: "Sí, varias sin éxito",
    come_fuera_casa: "Sí, 2-3 días/semana",
    azucar_dulces_bolleria: "A veces",
    
    // Objetivos
    objetivo_fisico: "Perder grasa",  // ⭐ CRÍTICO
    experiencia_ejercicio_constante: "Intermitente",
    nivel_energia_dia: "Media-Baja",
    motiva_ejercicio: "Verme mejor, tener más energía"
  },
  submitted_at: ISODate("2025-01-02T09:00:00Z"),
  plan_generated: true,
  plan_id: "1736960000000001"  // Referencia al training_plan generado
}
```

**Problemas:**
- ❌ **Toda la información está en un dict sin estructura** (`responses`)
- ❌ No hay versionado: si el cliente actualiza algo, se pierde el histórico
- ❌ `plan_id` solo apunta al último plan generado
- ❌ No hay vínculo con planes de nutrición (solo training)

---

#### 4. `generation_jobs` (Sistema Asíncrono)
**Propósito:** Cola de jobs para generación asíncrona de planes  
**Uso en EDN360:** Gestión de jobs, progreso y control de concurrencia

```javascript
{
  _id: "job_1736960100000000",
  job_id: "job_1736960100000000",
  user_id: "1762094831193507",
  type: "full",  // "training" | "nutrition" | "full"
  submission_id: "1736950234567890",  // Ref a nutrition_questionnaire_submissions
  status: "completed",  // "pending" | "queued" | "running" | "completed" | "failed"
  progress: {
    phase: "completed",
    current_agent: "N8",
    completed_steps: 18,
    total_steps: 18,
    percentage: 100,
    message: "Plan completo generado"
  },
  result: {
    training_plan_id: "1736960200000001",
    nutrition_plan_id: "1736960200000002"
  },
  token_usage: {
    total_prompt_tokens: 45000,
    total_completion_tokens: 12000,
    total_tokens: 57000
  },
  created_at: ISODate("2025-01-03T10:00:00Z"),
  started_at: ISODate("2025-01-03T10:00:05Z"),
  completed_at: ISODate("2025-01-03T10:15:30Z")
}
```

**Problemas:**
- ❌ Los jobs se mantienen indefinidamente (no hay limpieza)
- ❌ No hay vínculo entre jobs sucesivos (seguimientos)
- ❌ El ClientContext construido **NO se guarda**

---

### 📦 Colecciones de Planes Generados

#### 5. `training_plans`
**Propósito:** Almacenar planes de entrenamiento históricos  
**Estructura:**

```javascript
{
  _id: "1736960200000001",
  user_id: "1762094831193507",
  
  // ⚠️ DUPLICACIÓN: Copia completa del cuestionario
  questionnaire_data: { /* Copia de responses */ },
  
  // Outputs de agentes E1-E9
  e1_output: { profile, constraints, prehab },
  e2_output: { capacity },
  e3_output: { adaptation },
  e4_output: { mesocycle },
  e5_output: { sessions },
  e6_output: { safe_sessions },
  e7_output: { formatted_plan },  // ⚠️ LEGACY
  e8_output: { audit },
  e9_output: { bridge_for_nutrition },
  
  // Plan final formateado (POST-PROCESADO)
  formatted_plan: "# PLAN DE ENTRENAMIENTO...",  // ⭐ Markdown generado
  
  // Metadatos
  generated_at: ISODate("2025-01-03T10:15:00Z"),
  month: 1,
  year: 2025,
  edited: false,
  pdf_id: null,
  sent_email: false
}
```

**Problemas:**
- ❌ **Duplicación masiva:** `questionnaire_data` repite todo el cuestionario
- ❌ `formatted_plan` se guarda 2 veces (legacy E7 + post-procesado)
- ❌ No hay vínculo con el plan previo (progresión)
- ❌ `month` y `year` son manuales, no calculados

---

#### 6. `nutrition_plans`
**Propósito:** Almacenar planes de nutrición históricos  
**Estructura:** Similar a `training_plans`

```javascript
{
  _id: "1736960200000002",
  user_id: "1762094831193507",
  
  // ⚠️ DUPLICACIÓN: Copia completa del cuestionario
  questionnaire_data: { /* Copia de responses */ },
  
  // Outputs de agentes N0-N8
  n0_output: { profile },
  n1_output: { metabolism },
  n2_output: { energy_strategy },
  n3_output: { macro_design },
  n4_output: { weekly_structure },
  n5_output: { timing_plan },
  n6_output: { menu_plan },
  n7_output: { adherence_report },
  n8_output: { audit },
  
  // Plan final
  final_menu: "...",
  
  // Metadatos
  generated_at: ISODate("2025-01-03T10:15:20Z"),
  month: 1,
  year: 2025,
  edited: false,
  pdf_id: null
}
```

**Problemas:** Idénticos a `training_plans`

---

#### 7. `followup_submissions` (Seguimientos)
**Propósito:** Almacenar cuestionarios de seguimiento mensual

```javascript
{
  _id: "1739550000000000",
  user_id: "1762094831193507",
  submission_date: ISODate("2025-02-03T10:00:00Z"),
  days_since_last_plan: 30,
  previous_plan_id: "1736960200000001",  // Ref al training_plan previo
  previous_questionnaire_id: "1736950234567890",
  
  // Tipo de medición elegido
  measurement_type: "smart_scale",  // "smart_scale" | "tape_measure" | "none"
  
  // Mediciones
  measurements: {
    peso: "83",
    grasa_corporal: "20",
    masa_muscular: "42",
    satisfecho_cambios: "SI"
  },
  
  // Adherencia
  adherence: {
    constancia_entrenamiento: "80%",
    seguimiento_alimentacion: "70%"
  },
  
  // Bienestar
  wellbeing: {
    factores_externos: "Trabajo estresante esta semana",
    energia_animo_motivacion: "Bien",
    sueno_estres: "Regular"
  },
  
  // Cambios percibidos
  changes_perceived: {
    molestias_dolor_lesion: "Ninguna nueva",
    cambios_corporales: "Más definición abdominal",
    fuerza_rendimiento: "Mejorando"
  },
  
  // Feedback
  feedback: {
    objetivo_proximo_mes: "Seguir perdiendo grasa",
    cambios_deseados: "Aumentar intensidad",
    comentarios_adicionales: "Me siento bien"
  },
  
  // Estado
  status: "analyzed",  // "pending_analysis" | "analyzed" | "plan_generated"
  ai_analysis: "...",  // Análisis IA generado
  new_plan_id: "1739560000000001"  // Ref al nuevo plan
}
```

**Problemas:**
- ❌ Vínculo solo con `previous_plan_id`, no con el cuestionario original
- ❌ No se actualiza el `nutrition_questionnaire_submissions` original
- ❌ Crear nuevo plan requiere RE-generar desde cero

---

## FLUJO DETALLADO: CUESTIONARIO → CONTEXTO → PLANES

### 🔄 Fase 1: Captura de Datos del Cliente

```
Usuario registrado (users)
    ↓
Completa cuestionario detallado
    ↓
Se guarda en: nutrition_questionnaire_submissions
    {
      user_id: "1762...",
      responses: { /* 100+ campos */ },
      submitted_at: "2025-01-02",
      plan_generated: false,
      plan_id: null
    }
```

**Problemas en esta fase:**
1. ❌ No hay validación de datos completos
2. ❌ `responses` es un dict plano sin estructura Pydantic
3. ❌ Si el cliente completa varios cuestionarios, se crean múltiples registros sin vínculo

---

### 🔄 Fase 2: Creación del Job de Generación

**Endpoint:** `POST /admin/users/{user_id}/plans/generate_async`

**Input:**
```json
{
  "submission_id": "1736950234567890",
  "mode": "full"
}
```

**Proceso:**
1. Validar que el `submission_id` existe en `nutrition_questionnaire_submissions`
2. Crear job en `generation_jobs` con `status: "pending"`
3. Responder inmediatamente con `job_id`

```javascript
// Se crea en generation_jobs:
{
  job_id: "job_xyz",
  user_id: "1762...",
  type: "full",
  submission_id: "1736950234567890",
  status: "pending",
  created_at: "2025-01-03T10:00:00Z"
}
```

**Problemas en esta fase:**
1. ❌ No se valida que el cuestionario tiene todos los campos necesarios
2. ❌ No se verifica si ya existe un plan reciente

---

### 🔄 Fase 3: Ejecución del Job (Job Worker)

**Proceso actual:**

```python
# /app/backend/job_worker.py (línea 53-86)
async def process_pending_jobs():
    # 1. Buscar jobs pendientes
    pending_jobs = await db.generation_jobs.find(
        {"status": "pending"}
    ).sort("created_at", 1).to_list(10)
    
    for job in pending_jobs:
        job_id = job["_id"]
        
        # 2. Ejecutar job
        await process_generation_job(job_id)
```

```python
# /app/backend/server.py (proceso simplificado)
async def process_generation_job(job_id: str):
    # 1. Leer job de BD
    job = await db.generation_jobs.find_one({"_id": job_id})
    
    # 2. Leer cuestionario
    submission = await db.nutrition_questionnaire_submissions.find_one(
        {"_id": job["submission_id"]}
    )
    
    # 3. ⚠️ CONSTRUIR ClientContext EN MEMORIA (NO SE PERSISTE)
    from edn360.orchestrator import EDN360Orchestrator
    orchestrator = EDN360Orchestrator()
    
    questionnaire_data = submission["responses"]
    
    # 4. Ejecutar pipeline
    result = await orchestrator.generate_initial_plan(
        questionnaire_data=questionnaire_data,
        client_data={"client_id": job["user_id"]},
        plan_id=job_id
    )
    
    # 5. Si exitoso, guardar planes
    if result["success"]:
        # Extraer client_context del resultado
        client_context = result["client_context"]
        
        # ⚠️ DUPLICACIÓN: Guardar training_plan CON COPIA del cuestionario
        training_plan = {
            "_id": f"training_{job_id}",
            "user_id": job["user_id"],
            "questionnaire_data": questionnaire_data,  # ⚠️ DUPLICADO
            "formatted_plan": client_context["training"]["formatted_plan"],
            # ... todos los outputs de E1-E9
            "generated_at": datetime.now(timezone.utc),
            "month": datetime.now().month,
            "year": datetime.now().year
        }
        await db.training_plans.insert_one(training_plan)
        
        # ⚠️ DUPLICACIÓN: Guardar nutrition_plan CON COPIA del cuestionario
        nutrition_plan = {
            "_id": f"nutrition_{job_id}",
            "user_id": job["user_id"],
            "questionnaire_data": questionnaire_data,  # ⚠️ DUPLICADO
            "menu_plan": client_context["nutrition"]["menu_plan"],
            # ... todos los outputs de N0-N8
            "generated_at": datetime.now(timezone.utc)
        }
        await db.nutrition_plans.insert_one(nutrition_plan)
        
        # 6. Actualizar references
        await db.nutrition_questionnaire_submissions.update_one(
            {"_id": job["submission_id"]},
            {"$set": {
                "plan_generated": True,
                "plan_id": training_plan["_id"]
            }}
        )
        
        # 7. Marcar job como completado
        await db.generation_jobs.update_one(
            {"_id": job_id},
            {"$set": {
                "status": "completed",
                "result": {
                    "training_plan_id": training_plan["_id"],
                    "nutrition_plan_id": nutrition_plan["_id"]
                }
            }}
        )
```

**⚠️ ClientContext NO SE PERSISTE:**

El `ClientContext` construido por el orquestador:
```python
# /app/backend/edn360/orchestrator.py (línea 597-621)
client_context = initialize_client_context(
    client_id=questionnaire_data.get("client_id", "unknown"),
    version=version,
    cuestionario_data=questionnaire_data,
    previous_training=previous_training,
    is_followup=is_followup
)
# Este objeto SOLO existe en memoria durante el job
# Al terminar, se destruye
# Solo se guardan los outputs finales en training_plans y nutrition_plans
```

**Problemas en esta fase:**
1. ❌ **ClientContext no se persiste:** Se destruye después de cada ejecución
2. ❌ **Duplicación masiva:** El cuestionario se copia en 2 colecciones (training + nutrition)
3. ❌ **Sin trazabilidad:** No hay registro del ClientContext intermedio
4. ❌ **Reconstrucción costosa:** Cada seguimiento debe reconstruir desde cero

---

### 🔄 Fase 4: Ejecución del Orquestador

**Proceso interno del orquestador:**

```python
# /app/backend/edn360/orchestrator.py

# PASO 1: Inicializar ClientContext
client_context = ClientContext(
    meta=ClientContextMeta(...),
    raw_inputs=RawInputs(cuestionario_inicial=questionnaire_data),
    training=TrainingData(),
    nutrition=NutritionData()
)

# PASO 2: Pipeline de Entrenamiento (E1-E9)
for agent in [E1, E2, E3, E4, E5, E6, E7, E8, E9]:
    # Construir input reducido (arquitectura de cajones)
    agent_input = build_scoped_input_for_agent(agent.agent_id, client_context)
    
    # Ejecutar agente
    result = await agent.execute(agent_input, knowledge_base=kb)
    
    # Actualizar SOLO el campo del agente en client_context
    client_context.training.<campo> = result["output"]["client_context"]["training"]["<campo>"]
    
    # Validar contrato (que no tocó otros campos)
    validate_agent_contract(agent.agent_id, before, client_context)

# PASO 3: Post-procesamiento (Determinístico Python)
from format_premium_plan import format_plan_for_client
markdown_plan = format_plan_for_client(client_context.training.model_dump())
client_context.training.formatted_plan = markdown_plan

# PASO 4: Pipeline de Nutrición (N0-N8)
for agent in [N0, N1, N2, N3, N4, N5, N6, N7, N8]:
    agent_input = build_nutrition_llm_context(client_context)
    result = await agent.execute(agent_input, knowledge_base=kb)
    client_context.nutrition.<campo> = result["output"]["client_context"]["nutrition"]["<campo>"]

# PASO 5: Retornar resultado
return {
    "success": True,
    "client_context": client_context.model_dump(),  # ⚠️ Se serializa pero NO se guarda
    "training_executions": [...],
    "nutrition_executions": [...]
}
```

**⚠️ El ClientContext completo NO se guarda en BD:**
- Solo se extraen los campos finales (`formatted_plan`, `menu_plan`, etc.)
- Los campos intermedios (`capacity`, `mesocycle`, `weekly_structure`) se guardan individualmente en `training_plans` y `nutrition_plans`
- NO hay snapshot del `ClientContext` completo

---

## PUNTOS DE LECTURA DISPERSOS

### 🔍 ¿De dónde leen los agentes actualmente?

#### E1 - Analyst (Primer Agente)
**Lee de:**
- `raw_inputs.cuestionario_inicial` (construido desde `nutrition_questionnaire_submissions.responses`)

**Código:**
```python
# /app/backend/edn360/orchestrator.py (línea 100-107)
if agent_id == "E1":
    return {
        "meta": client_context.meta.model_dump(),
        "raw_inputs": client_context.raw_inputs.model_dump(),  # ← ÚNICO QUE RECIBE ESTO
        "training": TrainingData().model_dump()  # Vacío
    }
```

**Problema:**
- ❌ E1 debe parsear manualmente el cuestionario cada vez
- ❌ No hay caché del análisis de E1

---

#### E2-E9 (Agentes Subsecuentes)
**Leen de:**
- `training.client_summary` (generado por E1)
- Campos específicos de agentes anteriores

**Código:**
```python
# E2 lee:
{
    "training": {
        "client_summary": client_context.training.client_summary,  # De E1
        "profile": client_context.training.profile,  # De E1
        "constraints": client_context.training.constraints,  # De E1
        "capacity": None  # Lo que él va a llenar
    }
}

# E3 lee:
{
    "training": {
        "client_summary": client_context.training.client_summary,
        "capacity": client_context.training.capacity,  # De E2
        "adaptation": None
    }
}
```

**Problema:**
- ❌ Cada agente recibe input reducido, pero esto se reconstruye EN MEMORIA
- ❌ No hay persistencia de los inputs intermedios

---

#### N0-N8 (Agentes de Nutrición)
**Leen de:**
- `training.bridge_for_nutrition` (generado por E9)
- `raw_inputs` (para datos del cuestionario nutricional)

**Código:**
```python
# /app/backend/edn360/orchestrator.py (línea 1028)
agent_input = build_nutrition_llm_context(client_context)
# Esta función construye una VISTA REDUCIDA:
# - NO incluye training.sessions (muy pesado)
# - SÍ incluye training.bridge_for_nutrition
# - SÍ incluye raw_inputs para N0
```

**Problema:**
- ❌ `build_nutrition_llm_context()` hace filtraje manual cada vez
- ❌ No hay vista persistida

---

### 🗄️ Resumen de Fuentes de Verdad Actuales

| **Dato** | **Colección Primaria** | **Duplicado en** | **Problema** |
|---|---|---|---|
| Cuestionario inicial prospecto | `questionnaire_responses` | `nutrition_questionnaire_submissions` | ❌ Dos cuestionarios diferentes, sin vínculo |
| Cuestionario detallado | `nutrition_questionnaire_submissions.responses` | `training_plans`, `nutrition_plans` | ❌ Copiado en cada plan |
| Plan de entrenamiento | `training_plans` | `generation_jobs.result` | ❌ Referencia inconsistente |
| Plan de nutrición | `nutrition_plans` | `generation_jobs.result`, `nutrition_questionnaire_submissions.plan_id` | ❌ Múltiples referencias |
| Seguimientos | `followup_submissions` | Ninguno | ⚠️ No vinculado con cuestionario original |
| ClientContext completo | **NINGUNO** | **No se persiste** | ❌ Se reconstruye cada vez |

---

## DUPLICIDADES Y CONTRADICCIONES

### ❌ Duplicidad 1: Cuestionario Completo en Cada Plan

**Magnitud:**
- Cuestionario: ~100 campos, ~5-10KB por cliente
- Se duplica en:
  1. `nutrition_questionnaire_submissions` (original)
  2. `training_plans.questionnaire_data` (copia 1)
  3. `nutrition_plans.questionnaire_data` (copia 2)

**Impacto:**
- Para 1 cliente con 1 plan: **3 copias** del mismo cuestionario
- Para 1 cliente con 12 meses (seguimientos): **25 copias** (1 original + 12 training + 12 nutrition)

**Ejemplo Real (Cliente Jorge1):**
```javascript
// nutrition_questionnaire_submissions
{
  _id: "1736950234567890",
  responses: { peso: "85", altura_cm: "178", ... }  // ⚠️ ORIGINAL
}

// training_plans (Plan Enero)
{
  _id: "1736960200000001",
  questionnaire_data: { peso: "85", altura_cm: "178", ... }  // ⚠️ COPIA 1
}

// nutrition_plans (Plan Enero)
{
  _id: "1736960200000002",
  questionnaire_data: { peso: "85", altura_cm: "178", ... }  // ⚠️ COPIA 2
}

// training_plans (Plan Febrero - Seguimiento)
{
  _id: "1739560000000001",
  questionnaire_data: { peso: "85", altura_cm: "178", ... }  // ⚠️ COPIA 3 (¡Ya obsoleto!)
}
```

**Contradicción:**
- Si el cliente actualiza su peso en un seguimiento, el campo `peso` queda **inconsistente** entre copias
- No hay "fuente de verdad" clara

---

### ❌ Duplicidad 2: `formatted_plan` (Doble Guardado)

**Problema:**
- E7 genera un `formatted_plan` (legacy, texto plano)
- El post-procesador genera otro `formatted_plan` (Markdown premium)
- Ambos se guardan en `training_plans`:

```javascript
{
  _id: "1736960200000001",
  e7_output: {
    formatted_plan: "PLAN GENERADO POR E7..."  // ⚠️ LEGACY
  },
  formatted_plan: "# PLAN PREMIUM EN MARKDOWN..."  // ⚠️ POST-PROCESADO
}
```

**Impacto:**
- Confusión sobre cuál es el "correcto"
- Desperdicio de espacio

---

### ❌ Duplicidad 3: Referencias Cruzadas Inconsistentes

**Problema:**
- `nutrition_questionnaire_submissions.plan_id` → Apunta **solo** al `training_plan`
- No hay referencia al `nutrition_plan`
- `generation_jobs.result` tiene ambas, pero el job puede ser eliminado

```javascript
// nutrition_questionnaire_submissions
{
  _id: "1736950234567890",
  plan_generated: true,
  plan_id: "1736960200000001"  // ⚠️ Solo training_plan
}

// generation_jobs (si existe todavía)
{
  _id: "job_xyz",
  result: {
    training_plan_id: "1736960200000001",
    nutrition_plan_id: "1736960200000002"  // ⚠️ Aquí sí está
  }
}

// ¿Cómo encontrar el nutrition_plan desde el cuestionario?
// Respuesta: NO SE PUEDE directamente
```

---

### ❌ Contradicción 1: Versionado Manual vs Temporal

**Problema:**
- `training_plans` tiene `month` y `year` (manual)
- `ClientContext.meta` tiene `version` (incremental)
- No están sincronizados

```javascript
// Plan generado el 3 de enero
{
  _id: "1736960200000001",
  month: 1,  // ← Manual
  year: 2025,  // ← Manual
  generated_at: ISODate("2025-01-03T10:15:00Z")  // ← Automático
}

// ClientContext.meta (durante ejecución)
{
  version: 1,  // ← Incremental
  snapshot_id: "1736960200000001_v1"
}

// ¿Cuál es la fuente de verdad del versionado?
```

---

### ❌ Contradicción 2: Progresión de Planes Sin Vínculo

**Problema:**
- `followup_submissions.previous_plan_id` apunta al plan previo
- `training_plans` NO tiene campo `next_plan_id` ni `previous_plan_id`
- Imposible navegar la cadena de planes de un cliente

```javascript
// Plan Enero (Inicial)
{
  _id: "plan_enero_2025",
  user_id: "1762...",
  // ⚠️ NO HAY CAMPO: next_plan_id
}

// Seguimiento Febrero
{
  _id: "followup_feb_2025",
  previous_plan_id: "plan_enero_2025"  // ← Vínculo unidireccional
}

// Plan Febrero (Generado)
{
  _id: "plan_febrero_2025",
  user_id: "1762...",
  // ⚠️ NO HAY CAMPO: previous_plan_id
}

// ¿Cómo obtener todos los planes de un cliente en orden?
// Respuesta: Buscar por user_id y ordenar por generated_at (frágil)
```

---

## LÓGICAS LEGACY IDENTIFICADAS

### 🔧 Legacy 1: Formato de Output de Agentes (E2, E3, E6, E7, E9)

**Problema:**
- Algunos agentes todavía NO devuelven `client_context` completo
- Devuelven formato legacy: `{"success": True, "output": {...}}`

**Código afectado:**
```python
# /app/backend/edn360/orchestrator.py (línea 811-841)
else:
    # Compatibilidad: agente legacy (E2, E3, E4, E6, E7, E9)
    logger.warning(f"  ⚠️ {agent.agent_id} es legacy, simulando output con datos dummy")
    
    # Llenar el campo del agente legacy con datos dummy
    legacy_output = result.get("output", {})
    
    agent_fields = {
        "E2": "capacity",
        "E3": "adaptation",
        "E4": "mesocycle",
        "E6": "safe_sessions",
        "E7": "formatted_plan",
        "E9": "bridge_for_nutrition"
    }
    
    field_to_fill = agent_fields.get(agent.agent_id)
    if field_to_fill:
        dummy_data = {
            "_legacy": True,
            "_agent_id": agent.agent_id,
            "data": legacy_output
        }
        setattr(client_context.training, field_to_fill, dummy_data)
```

**Impacto:**
- Código condicional en el orquestador
- Dificulta validación de contratos
- Algunos agentes funcionan, otros necesitan "simulación"

---

### 🔧 Legacy 2: Arquitectura de Cajones Incompleta

**Problema:**
- Solo E1-E4 usan la arquitectura de cajones (inputs reducidos)
- E5-E9 todavía reciben formato legacy

**Código:**
```python
# /app/backend/edn360/orchestrator.py (línea 629-631)
agents_with_scoped_input = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9"]

if agent.agent_id in agents_with_scoped_input:
    # Arquitectura de cajones
    agent_input = build_scoped_input_for_agent(agent.agent_id, client_context)
else:
    # Agente legacy: pasar formato antiguo
    # ...construir outputs en formato legacy
```

**Impacto:**
- Dos flujos diferentes coexistiendo
- E5-E9 reciben más datos de los que necesitan

---

### 🔧 Legacy 3: Validación Manual de Contratos

**Problema:**
- La validación de que cada agente modifica SOLO su campo se hace manualmente en el orquestador
- No hay validación automática en los agentes

**Código:**
```python
# /app/backend/edn360/orchestrator.py (línea 843-859)
# VALIDACIÓN POST-EJECUCIÓN: ¿Llenó sus campos? ¿No modificó otros?
logger.info(f"    🔍 Validando contrato de {agent.agent_id}...")
valid_contract, errors = validate_agent_contract(
    agent.agent_id,
    client_context_before,
    client_context
)

if not valid_contract:
    logger.error(f"  ❌ {agent.agent_id} - Violación de contrato:")
    for error in errors:
        logger.error(f"      • {error}")
    return {"success": False, "error": f"{agent.agent_id} violó su contrato"}
```

**Impacto:**
- Los agentes pueden "romper" el sistema si no respetan contratos
- Debugging difícil cuando hay violación

---

### 🔧 Legacy 4: Reconstrucción de `ClientContext` en Cada Job

**Problema:**
- No hay persistencia del `ClientContext`
- Cada job debe reconstruirlo desde el cuestionario

**Código:**
```python
# /app/backend/server.py (en process_generation_job)
# 1. Leer cuestionario de BD
submission = await db.nutrition_questionnaire_submissions.find_one({"_id": submission_id})
questionnaire_data = submission["responses"]

# 2. Construir ClientContext desde cero (CADA VEZ)
client_context = initialize_client_context(
    client_id=user_id,
    version=1,
    cuestionario_data=questionnaire_data,  # ← Parseo manual
    previous_training=None,
    is_followup=False
)
```

**Impacto:**
- Procesamiento redundante
- No se aprovecha caché
- Seguimientos deben re-parsear el cuestionario original

---

### 🔧 Legacy 5: Sistema Híbrido (Legacy + V2 Reasoning)

**Problema:**
- Existen agentes "V2" para razonamiento (E2, E4, E5, E6)
- Se ejecutan en paralelo a los legacy
- NO son críticos, solo capturan `_rationale`

**Código:**
```python
# /app/backend/edn360/orchestrator.py (línea 866-918)
# RAZONAMIENTO V2: Si existe agente v2, ejecutar en paralelo (NO crítico)
agent_class_name = agent.__class__.__name__
if agent_class_name in self.reasoning_agents:
    try:
        logger.info(f"  🧠 Ejecutando {agent.agent_id} V2 (razonamiento)...")
        reasoning_agent = self.reasoning_agents[agent_class_name]
        reasoning_result = await reasoning_agent.execute(...)
        
        # Guardar razonamiento en campo adicional (capacity_rationale, etc.)
        training_dict["capacity_rationale"] = rationale
        
    except Exception as e:
        logger.error(f"  ⚠️ {agent.agent_id} V2 falló (NO crítico): {e}")
        logger.info(f"    → Continuando con datos de {agent.agent_id} legacy")
```

**Impacto:**
- Complejidad adicional
- Dos sistemas de agentes coexistiendo
- El sistema "V2" no está completamente implementado

---

## CONCLUSIONES DEL DOCUMENTO AS IS

### ✅ Fortalezas del Sistema Actual

1. **Pipeline de agentes funcional:** E1-E9 y N0-N8 generan planes correctamente
2. **Sistema asíncrono estable:** Jobs en background evitan timeouts
3. **Validación de contratos:** El orquestador verifica que agentes no se pisen
4. **Post-procesador determinístico:** `format_premium_plan.py` genera Markdown consistente
5. **Arquitectura de cajones (parcial):** E1-E4 usan inputs reducidos (menos contexto)

---

### ❌ Debilidades Críticas

| **Problema** | **Impacto** | **Severidad** |
|---|---|---|
| **ClientContext NO se persiste** | Se reconstruye cada vez, sin caché | 🔴 Alta |
| **Duplicación masiva de cuestionarios** | 3+ copias por cliente, inconsistencia | 🔴 Alta |
| **Sin fuente única de verdad** | Datos dispersos en 6+ colecciones | 🔴 Alta |
| **Sin versionado claro** | Planes históricos sin vinculación | 🟡 Media |
| **Referencias cruzadas inconsistentes** | Difícil navegar historial del cliente | 🟡 Media |
| **Lógicas legacy coexistiendo** | Complejidad, dos flujos diferentes | 🟡 Media |
| **Seguimientos sin vínculo al original** | Reconstrucción desde cero cada vez | 🔴 Alta |

---

### 🎯 Próximos Pasos

Este documento AS IS establece la línea base del sistema actual. El próximo paso es diseñar la arquitectura TO BE con `client_drawer` como fuente única de verdad.

**Enfoque del TO BE:**
1. Crear `client_drawer` como colección unificada
2. Eliminar duplicaciones de cuestionarios
3. Persistir `ClientContext` completo en cada snapshot
4. Establecer versionado explícito con vínculos entre planes
5. Migrar lógicas legacy a arquitectura unificada

---

**Fin del Documento AS IS**
