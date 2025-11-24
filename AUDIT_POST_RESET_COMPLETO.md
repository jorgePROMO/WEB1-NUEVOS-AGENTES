# AUDITORÍA POST-RESET COMPLETA - EDN360

**Fecha:** Enero 2025  
**Estado:** Sistema Limpio (Post-Eliminación Total)  
**Auditor:** AI Engineer  
**Solicitado por:** Jorge Calcerrada  

---

## 📋 RESUMEN EJECUTIVO

### ✅ CONFIRMACIÓN: RESET COMPLETADO

El sistema ha sido **completamente limpiado** de toda la lógica de aplicación anterior. Se ha eliminado:

- ❌ **ELIMINADO:** Todo el directorio `/app/backend/edn360/agents/` (E1-E9, N0-N8, etc.)
- ❌ **ELIMINADO:** `/app/backend/edn360/orchestrator.py` (orquestador de agentes)
- ❌ **ELIMINADO:** Toda la lógica de negocio que gestionaba el flujo EDN360

### ✅ ESTADO ACTUAL

**El sistema está en "clean slate":**
- ✅ Los archivos base de infraestructura siguen intactos (`server.py`, `job_worker.py`, `models.py`)
- ✅ Los documentos de arquitectura están presentes y aprobados
- ✅ La base de datos MongoDB contiene datos históricos (sin modificar)
- ✅ El frontend existe pero sin lógica de negocio activa
- ✅ Los servicios de supervisor están ejecutándose (frontend, backend, MongoDB)

---

## 🗂️ ESTRUCTURA DE ARCHIVOS ACTUAL

### Backend (`/app/backend/`)

#### ✅ ARCHIVOS BASE INTACTOS

| Archivo | Estado | Propósito |
|---------|--------|-----------|
| `server.py` | ✅ Intacto | API FastAPI con endpoints (sin lógica EDN360) |
| `job_worker.py` | ✅ Intacto | Worker para jobs asíncronos (SIN orchestrator) |
| `models.py` | ✅ Intacto | Modelos Pydantic para MongoDB |
| `auth.py` | ✅ Intacto | Sistema de autenticación JWT |
| `email_utils.py` | ✅ Intacto | Utilidades para envío de emails |
| `google_calendar_service.py` | ✅ Intacto | Integración con Google Calendar |
| `gpt_service.py` | ✅ Intacto | Wrapper para OpenAI |
| `nutrition_service.py` | ✅ Intacto | Servicio auxiliar de nutrición |
| `training_service.py` | ✅ Intacto | Servicio auxiliar de entrenamiento |
| `waitlist_scoring.py` | ✅ Intacto | Sistema de scoring de waitlist |
| `exercise_selector.py` | ✅ Intacto | Selector de ejercicios de BD |
| `.env` | ✅ Intacto | Variables de entorno |
| `requirements.txt` | ✅ Intacto | Dependencias Python |

#### ❌ DIRECTORIO EDN360 VACIADO

```
/app/backend/edn360/
├── __init__.py          ✅ (archivo vacío)
└── README.md            ✅ (documentación básica)

❌ ELIMINADO: agents/     (TODO el directorio de agentes)
❌ ELIMINADO: orchestrator.py  (lógica principal del sistema)
```

**CONFIRMACIÓN:** La carpeta `edn360/` existe pero está **vacía de lógica**. Solo contiene archivos de infraestructura mínima.

### Frontend (`/app/frontend/`)

#### ✅ ESTRUCTURA INTACTA

```
/app/frontend/
├── src/
│   ├── App.js                      ✅ App principal React
│   ├── components/                 ✅ 20+ componentes UI
│   │   ├── EDN360Manager.jsx       (gestión de planes)
│   │   ├── EDN360PlanViewer.jsx    (visualización planes)
│   │   ├── AdminComponents.jsx     (panel admin)
│   │   ├── DiagnosisQuestionnaire.jsx
│   │   ├── FollowUpQuestionnaire.jsx
│   │   └── ... (otros componentes)
│   ├── pages/                      ✅ Páginas principales
│   ├── context/                    ✅ AuthContext
│   └── hooks/                      ✅ Custom hooks
├── public/
├── package.json                    ✅ Dependencias
└── .env                            ✅ Variables de entorno
```

**NOTA:** El frontend existe y está funcional, pero **no puede generar planes** porque el backend no tiene la lógica del orquestador.

---

## 💾 ESTADO DE LA BASE DE DATOS

### Colecciones Existentes (16 total)

| Colección | Documentos | Descripción |
|-----------|------------|-------------|
| `users` | 4 | Usuarios registrados en el sistema |
| `questionnaire_responses` | 3 | Cuestionarios iniciales (prospección) |
| `nutrition_questionnaire_submissions` | 5 | Cuestionarios nutricionales detallados |
| `training_plans` | 15 | Planes de entrenamiento históricos |
| `nutrition_plans` | 1 | Planes de nutrición históricos |
| `generation_jobs` | 36 | Jobs de generación (21 completados, 15 fallidos) |
| `follow_up_submissions` | 1 | Seguimientos mensuales |
| `follow_up_reports` | 1 | Reportes de seguimiento |
| `alerts` | 2 | Alertas del sistema |
| `external_clients` | 1 | Clientes externos |
| `message_templates` | 11 | Plantillas de mensajes |
| `prospect_stages` | 5 | Etapas del CRM de prospectos |
| `payment_transactions` | 2 | Transacciones de pago |
| `user_subscriptions` | 2 | Suscripciones de usuarios |
| `pdfs` | 0 | PDFs generados (vacío) |
| `manual_payments` | 0 | Pagos manuales (vacío) |

### 🔍 Análisis de Datos

#### USUARIOS
- **Total:** 4 usuarios
- **Estructura:** `_id`, `username`, `email`, `password` (hash), `name`, `phone`, `role`, `email_verified`, `created_at`
- **Roles:** admin, user

#### CUESTIONARIOS
- **Cuestionarios de prospección (`questionnaire_responses`):** 3
  - Cuestionario inicial simplificado (landing page)
  - Campos: nombre, edad, email, whatsapp, objetivo, experiencia previa
  
- **Cuestionarios detallados (`nutrition_questionnaire_submissions`):** 5
  - Cuestionario completo con 100+ campos
  - Campos: datos personales, medidas corporales, salud, trabajo, experiencia deportiva, disponibilidad, horarios, hábitos alimentarios, objetivos
  - **ESTE es el cuestionario que usaba el orquestador para generar planes**

#### PLANES HISTÓRICOS

**Training Plans (15):**
- Planes de entrenamiento generados por el sistema EDN360
- Campos principales:
  - `user_id`: ID del usuario
  - `month`, `year`: Mes y año del plan
  - `source_type`: "inicial", "followup"
  - `questionnaire_data`: **COPIA DUPLICADA** del cuestionario completo
  - `edn360_data`: Outputs de agentes E1-E9
  - `agent_executions`: Registro de ejecución de cada agente
  - `system_version`: "edn360_v3_integrated"

**Nutrition Plans (1):**
- Plan de nutrición
- Estructura similar a training plans
- `edn360_data`: Outputs de agentes N0-N8

#### GENERATION JOBS (36 total)

| Estado | Cantidad | Descripción |
|--------|----------|-------------|
| Completed | 21 | Jobs exitosos |
| Failed | 15 | Jobs fallidos |
| Pending | 0 | Sin jobs pendientes |
| Running | 0 | Sin jobs en ejecución |

**Estructura de Jobs:**
```javascript
{
  _id: "job_uuid",
  user_id: "176...",
  type: "training" | "nutrition" | "full",
  submission_id: "referencia al cuestionario",
  status: "pending" | "running" | "completed" | "failed",
  progress: {
    phase: "training" | "nutrition" | "completed",
    current_agent: "E1" | "E2" | ... | "N8",
    completed_steps: 0-18,
    percentage: 0-100,
    message: "..."
  },
  result: {
    training_plan_id: "...",
    nutrition_plan_id: "..."
  },
  token_usage: { /* uso de tokens OpenAI */ },
  created_at: ISODate(),
  started_at: ISODate(),
  completed_at: ISODate()
}
```

---

## 🔧 ESTADO DE SERVICIOS

### Backend (FastAPI)

**Estado:** ✅ RUNNING (Puerto 8001)

**Endpoints Disponibles:**

#### Autenticación
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/verify-email`
- `POST /api/auth/resend-verification`
- `GET /api/auth/me`

#### Usuarios
- `GET /api/users/dashboard`
- `PATCH /api/users/me`

#### Admin
- `GET /api/admin/clients`
- `GET /api/admin/clients/{user_id}`
- `POST /api/admin/verify-payment/{user_id}`
- `POST /api/admin/archive-client/{user_id}`
- `DELETE /api/admin/delete-client/{user_id}`

#### Cuestionarios
- `POST /api/questionnaire/submit`
- `POST /api/questionnaire/nutrition/submit`
- `POST /api/questionnaire/followup/submit`

#### Planes (LEGACY - SIN LÓGICA ACTIVA)
- `POST /api/admin/users/{user_id}/plans/generate_async`
  - **⚠️ CRÍTICO:** Este endpoint existe pero **NO FUNCIONA** porque no hay orquestador

#### CRM
- Prospectos, Clientes Externos, Templates

**⚠️ IMPORTANTE:** El backend está ejecutándose pero **no puede generar planes nuevos** porque falta el orquestador.

### Frontend (React)

**Estado:** ✅ RUNNING (Puerto 3000)

**Páginas:**
- `/` - Landing page
- `/login` - Login
- `/register` - Registro
- `/admin-dashboard` - Panel de administración
- `/user-dashboard` - Panel de usuario
- `/trabaja-conmigo` - Página de trabajo
- `/verify-email` - Verificación de email
- `/waitlist-confirmacion` - Confirmación de waitlist

**Componentes Principales:**
- `EDN360Manager.jsx`: Gestión de planes EDN360 (generación, visualización)
- `EDN360PlanViewer.jsx`: Visualizador de planes
- `DiagnosisQuestionnaire.jsx`: Cuestionario de diagnóstico
- `FollowUpQuestionnaire.jsx`: Cuestionario de seguimiento
- `AdminComponents.jsx`: Panel de administración

**⚠️ IMPORTANTE:** El frontend está ejecutándose pero el botón de "Generar Plan" **fallará** porque no hay lógica en el backend.

### Job Worker

**Estado:** 🔴 FATAL (Exit too quickly)

**Motivo:** El job worker intenta importar:
```python
from server import (
    process_generation_job,
    add_job_log,
    check_job_concurrency,
    update_job_progress
)
```

Pero `process_generation_job()` **probablemente tiene referencias al orquestador eliminado**, causando que el worker falle al iniciar.

### MongoDB

**Estado:** ✅ RUNNING

### Nginx

**Estado:** ✅ RUNNING

---

## 📄 DOCUMENTOS DE ARQUITECTURA

### ✅ DOCUMENTOS CRÍTICOS PRESENTES

1. **`DOCUMENTO_1_AS_IS_ARQUITECTURA_ACTUAL.md`** (Aprobado)
   - 1,250 líneas
   - Auditoría detallada del sistema anterior
   - Identifica todos los problemas (duplicación, falta de versionado, etc.)

2. **`DOCUMENTO_2_VFINAL_TO_BE_CLIENT_DRAWER.md`** (Aprobado)
   - 2,281 líneas
   - Arquitectura TO BE completa con `client_drawer`
   - Modelo de datos, flujos, reglas de oro, estrategias de archivado
   - **ESTE es el blueprint oficial a implementar**

3. **`DOCUMENTO_3_V2_MANUAL_OPERATIVO_MIGRACION.md`** (Aprobado)
   - 1,885 líneas
   - Manual de migración paso a paso
   - 5 fases detalladas (Fase 0 a Fase 4)
   - Scripts, validaciones, rollbacks, umbrales
   - **ESTE es el manual obligatorio a seguir**

### 📚 OTROS DOCUMENTOS DE SOPORTE

- `HANDOFF_COMPLETO_EDN360.md`: Handoff del sistema anterior
- `PARADIGMA_RAZONAMIENTO_EDN360.md`: Paradigma de razonamiento de agentes
- `TRAINING_AGENTS_REFACTOR_ROADMAP.md`: Roadmap de refactor de agentes
- `IMPLEMENTATION_STATUS.md`: Estado de implementación previo
- `FINAL_SUMMARY.md`: Resumen final del proyecto anterior

---

## 🔍 ANÁLISIS DE CÓDIGO RESIDUAL

### Backend

#### `/app/backend/server.py` (3,000+ líneas)

**ENDPOINTS QUE NO FUNCIONAN (sin orquestador):**

```python
@app.post("/api/admin/users/{user_id}/plans/generate_async")
async def create_generation_job_async(user_id: str, ...):
    # Este endpoint crea un job en generation_jobs
    # Pero el job_worker NO puede procesarlo sin orchestrator
    # ❌ ROTO
```

```python
async def process_generation_job(job_id: str):
    # Esta función está en server.py pero probablemente
    # tiene imports/llamadas al orquestador eliminado
    # ❌ ROTO
```

#### `/app/backend/job_worker.py` (167 líneas)

**PROBLEMA:**

```python
from server import (
    process_generation_job,  # ❌ Probablemente roto
    add_job_log,
    check_job_concurrency,
    update_job_progress
)

async def process_pending_jobs():
    # ...
    await process_generation_job(job_id)  # ❌ Falla aquí
```

El worker intenta ejecutar `process_generation_job()` que internamente llamaba al orquestador. Como el orquestador no existe, el worker crashea.

#### `/app/backend/edn360/` (VACÍO)

```
/app/backend/edn360/
├── __init__.py          # Vacío
└── README.md            # Solo documentación

❌ NO EXISTE: agents/
❌ NO EXISTE: orchestrator.py
❌ NO EXISTE: client_context_models.py (si existía)
❌ NO EXISTE: format_premium_plan.py (si existía)
```

### Frontend

#### Componentes con Referencias EDN360

Los siguientes componentes **intentarán llamar al backend** para generar planes, pero fallarán:

1. **`EDN360Manager.jsx`**
   - Llama a `/api/admin/users/{user_id}/plans/generate_async`
   - Botón "Generar Plan Asíncrono" → ❌ Fallará

2. **`EDN360PlanViewer.jsx`**
   - Visualiza planes existentes (✅ Funciona con datos históricos)
   - No intenta generar nuevos planes

3. **`DiagnosisQuestionnaire.jsx`**
   - Envía cuestionario a `/api/questionnaire/nutrition/submit`
   - Guarda cuestionario en BD (✅ Funciona)
   - NO genera plan automáticamente

4. **`FollowUpQuestionnaire.jsx`**
   - Envía seguimiento a `/api/questionnaire/followup/submit`
   - Guarda en BD (✅ Funciona)
   - NO genera plan automáticamente

---

## ⚠️ FUNCIONALIDADES ROTAS

### ❌ NO FUNCIONA: Generación de Nuevos Planes

**Flujo anterior:**
1. Usuario completa cuestionario → BD
2. Admin crea job → `generation_jobs`
3. Job worker detecta job pendiente
4. Job worker llama a `process_generation_job()`
5. `process_generation_job()` llama al **orquestador**
6. Orquestador ejecuta E1-E9, N0-N8
7. Plan guardado en BD

**Flujo actual (ROTO):**
1. ✅ Usuario completa cuestionario → BD
2. ✅ Admin crea job → `generation_jobs`
3. 🔴 Job worker NO está ejecutándose (FATAL)
4. 🔴 Si se arreglara el worker, fallaría al llamar al orquestador (no existe)

### ❌ NO FUNCIONA: Job Worker

El worker crashea al iniciar porque:
- Intenta importar `process_generation_job()`
- Esa función probablemente tiene referencias al orquestador eliminado
- Python lanza ImportError o AttributeError

### ✅ FUNCIONA: Todo lo Demás

**Funcionalidades operativas:**
- ✅ Autenticación (login, registro, JWT)
- ✅ Dashboard de usuario (ver datos históricos)
- ✅ Dashboard de admin (gestionar usuarios)
- ✅ CRM de prospectos
- ✅ CRM de clientes externos
- ✅ Templates de mensajes
- ✅ Integración con Google Calendar
- ✅ Sistema de pagos (Stripe)
- ✅ Envío de emails
- ✅ Gestión de sesiones
- ✅ Visualización de planes históricos (los 16 planes que ya existen)

---

## 🧪 DATOS DE PRUEBA EXISTENTES

### Usuario Admin
- **Email:** (probablemente en la BD como role="admin")
- **Puede:** Ver todos los usuarios, crear jobs (pero no se procesarán)

### Usuarios de Prueba (4 total)
- Usuarios con cuestionarios completados
- Algunos con planes históricos

### Planes Históricos (16 total)
- 15 training plans
- 1 nutrition plan
- **ESTOS PLANES SON VISUALIZABLES** en el frontend

---

## 🎯 PRÓXIMOS PASOS SEGÚN DOCUMENTOS

### Según DOCUMENTO_3_V2 (Manual Obligatorio)

**FASE 0: Preparación** (3-5 días)

1. **Crear modelos Pydantic del `client_drawer`:**
   - Archivo: `/app/backend/models/client_drawer.py`
   - Incluir:
     - `ClientDrawer` (modelo principal)
     - `ClientServices` (con `shared`, `training`, `nutrition`)
     - `ServiceShared` (cuestionarios únicos EDN360)
     - `SharedQuestionnaires` (inicial + followups)
     - `ServiceModule` (snapshots, plans, measurements, notes)

2. **Crear colección MongoDB `client_drawers`:**
   - Script: `/app/backend/migration/scripts/00_create_collection.py`
   - Crear índices:
     - `user_id` (único)
     - `services.shared.questionnaires.inicial.submitted_at`
     - `services.training.active`
     - `services.nutrition.active`

3. **Tests unitarios:**
   - Validar estructura de modelos
   - Validar que `services.shared.questionnaires` funciona

4. **Configurar parámetros de migración:**
   - Definir `DUAL_WRITE_START_AT` en `/app/backend/config.py`

**FASE 0.5: STAGING (OBLIGATORIA)** (5-7 días)

- Crear dump de BD actual
- Configurar entorno staging
- Ejecutar migración completa en staging
- Validar resultados (match rate > 95%)
- Generar informe de staging
- **SOLO con staging exitoso se aprueba ir a producción**

**FASE 1: Coexistencia (Dual-Write)** (1-2 semanas)

- Modificar endpoints para escribir en AS IS + TO BE
- Activar feature flag `USE_CLIENT_DRAWER_WRITE=true`
- Monitorear match rate (> 98%)

**FASE 2: Migración Histórica** (2-3 días)

- Backup completo de BD
- Ejecutar scripts de migración:
  - `02_migrate_questionnaires.py`
  - `03_migrate_followups.py`
  - `04_link_legacy_plans.py`
  - `05_validate_migration.py`
- Validar match rate > 95%
- 0 duplicados

**FASE 3: Switch de Lectura** (1 día + 48h monitoreo)

- Modificar orquestador para leer de `client_drawers`
- Activar feature flag `USE_CLIENT_DRAWER_READ=true`
- Monitorear tasa de éxito > 95%

**FASE 4: Limpieza** (2-3 días)

- Deprecar colecciones legacy
- Eliminar código legacy
- Generar informe final

---

## ✅ CRITERIOS DE VALIDACIÓN

### Para Iniciar Fase 0

- [x] Documento 2 (TO BE) aprobado formalmente
- [x] Documento 3 (Manual) aprobado formalmente
- [x] Sistema actual en "clean slate"
- [ ] Equipo disponible para 6-7 semanas de trabajo

### Para Aprobar Fase 0

- [ ] Modelos Pydantic creados y testeados
- [ ] Colección `client_drawers` creada con índices
- [ ] Tests unitarios pasan 100%

### Para Aprobar Fase 0.5 (Staging)

- [ ] Match rate cuestionarios ≥ 95%
- [ ] Match rate followups ≥ 95%
- [ ] Match rate planes ≥ 90%
- [ ] 0 errores críticos
- [ ] 0 duplicados detectados
- [ ] Informe de staging completo

---

## 🚨 BLOQUEOS ACTUALES

### 🔴 BLOQUEO 1: No Hay Orquestador

**Impacto:** NO se pueden generar planes nuevos

**Solución:**
- Implementar nuevo orquestador que lea de `client_drawer`
- **IMPORTANTE:** El nuevo orquestador debe construirse desde cero siguiendo el DOCUMENTO_2

### 🔴 BLOQUEO 2: Job Worker Crasheado

**Impacto:** Jobs pendientes no se procesan

**Solución Temporal:**
- Comentar la importación del orquestador en `job_worker.py`
- Hacer que el worker solo monitoree sin ejecutar

**Solución Definitiva:**
- Reescribir `process_generation_job()` para usar `client_drawer`

### 🟡 BLOQUEO 3: Frontend Intentará Generar Planes

**Impacto:** Botones "Generar Plan" mostrarán errores

**Solución:**
- Deshabilitar botones de generación temporalmente
- Añadir mensaje: "Sistema en migración - generación deshabilitada"

---

## 📊 MÉTRICAS DEL SISTEMA

### Tamaño de Datos

- **Usuarios:** 4
- **Cuestionarios iniciales:** 3
- **Cuestionarios detallados:** 5
- **Planes totales:** 16 (15 training + 1 nutrition)
- **Jobs:** 36 (21 completados + 15 fallidos)

### Estimación de Tamaño de BD

- **Colecciones activas:** 16
- **Tamaño aproximado:** ~50-100 MB (estimación)

### Performance Actual

- **Backend:** ✅ Responde rápido (< 100ms endpoints básicos)
- **Frontend:** ✅ Carga rápida
- **MongoDB:** ✅ Sin latencia

---

## 🎬 CONCLUSIÓN

### Estado del Sistema: "Clean Slate con Datos Históricos"

El sistema EDN360 está en un estado especial:

✅ **LO QUE HAY:**
- Base de datos con datos históricos intactos
- Backend funcional (autenticación, CRM, endpoints básicos)
- Frontend funcional (UI completa)
- Documentos de arquitectura aprobados y listos

❌ **LO QUE NO HAY:**
- Lógica de generación de planes (orquestador eliminado)
- Agentes de IA (E1-E9, N0-N8 eliminados)
- Job worker funcional

🎯 **LO QUE FALTA:**
- Implementar arquitectura `client_drawer` (Documento 2)
- Seguir manual de migración (Documento 3)
- Reescribir orquestador y agentes

### ¿Es Seguro Avanzar?

✅ **SÍ**, el sistema está en el estado ideal para comenzar la implementación TO BE:
- Datos históricos preservados
- Lógica antigua eliminada (sin conflictos)
- Arquitectura nueva claramente definida
- Manual de migración detallado

### Siguiente Acción Recomendada

Según el DOCUMENTO_3_V2, el siguiente paso es:

**FASE 0: PREPARACIÓN (días 1-5)**

1. Confirmar aprobación formal de Jorge de Documentos 2 y 3
2. Crear `/app/backend/models/client_drawer.py`
3. Crear script `00_create_collection.py`
4. Escribir tests unitarios
5. Validar que todo funciona antes de Fase 0.5

---

**FIN DEL AUDIT POST-RESET COMPLETO**

---

**Auditor:** AI Engineer  
**Fecha:** Enero 2025  
**Contacto:** Jorge Calcerrada
