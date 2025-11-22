# Flujo de Ejecución Asíncrona - E.D.N.360

## Arquitectura General

El sistema E.D.N.360 utiliza una arquitectura asíncrona basada en jobs para generar planes de entrenamiento y nutrición sin causar timeouts. La arquitectura consta de 3 componentes principales:

```
┌─────────────┐        ┌──────────────┐        ┌────────────────┐
│   Frontend  │───────>│   Backend    │───────>│    MongoDB     │
│   (React)   │<───────│   (FastAPI)  │<───────│  (Jobs Queue)  │
└─────────────┘        └──────────────┘        └────────────────┘
      │                                                 │
      │                                                 ▼
      │                                         ┌────────────────┐
      └─────────────────────────────────────────│  Job Worker    │
              (polling cada 3s)                 │   (Python)     │
                                                └────────────────┘
                                                        │
                                                        ▼
                                                ┌────────────────┐
                                                │ Orquestador    │
                                                │   E1-E9 /      │
                                                │   N0-N8        │
                                                └────────────────┘
```

## Componentes del Sistema

### 1. Backend FastAPI (`server.py`)

**Responsabilidades:**
- Recibe solicitudes de generación de planes
- Crea jobs en MongoDB con status `pending`
- **NO** ejecuta el orquestador directamente (evita timeouts)
- Provee endpoint para consultar estado de jobs

**Endpoints Clave:**

#### `POST /admin/users/{user_id}/plans/generate_async`
Crea un job de generación asíncrono.

**Request Body:**
```json
{
  "type": "training" | "nutrition" | "full",
  "submission_id": "string",
  "previous_training_plan_id": "string (opcional)"
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "job_1732270123456789",
  "message": "Job de generación creado. Consulta el estado en /jobs/{job_id}"
}
```

**Duración:** ~100-200ms (respuesta inmediata)

#### `GET /jobs/{job_id}`
Consulta el estado de un job (endpoint público, sin autenticación).

**Response:**
```json
{
  "_id": "job_1732270123456789",
  "user_id": "user_123",
  "submission_id": "submission_456",
  "type": "training",
  "status": "pending" | "running" | "completed" | "failed",
  "progress": {
    "phase": "training",
    "current_agent": "E5",
    "completed_steps": 5,
    "total_steps": 9,
    "percentage": 55.6,
    "message": "Agente E5 completado"
  },
  "result": {
    "training_plan_id": "plan_789",
    "nutrition_plan_id": null
  },
  "error_message": null,
  "token_usage": {
    "total_tokens": 45000,
    "total_prompt_tokens": 30000,
    "total_completion_tokens": 15000,
    "by_agent": {
      "E1": { "prompt_tokens": 3000, "completion_tokens": 1500, "total_tokens": 4500 },
      "E2": { "prompt_tokens": 3500, "completion_tokens": 1800, "total_tokens": 5300 }
    }
  },
  "created_at": "2024-11-22T10:00:00Z",
  "started_at": "2024-11-22T10:00:05Z",
  "completed_at": "2024-11-22T10:08:30Z"
}
```

### 2. Job Worker (`job_worker.py`)

**Responsabilidades:**
- Proceso separado e independiente de FastAPI
- Polling cada 5 segundos a MongoDB buscando jobs con `status="pending"`
- Control de concurrencia: máximo 2 jobs simultáneos
- Ejecuta `process_generation_job()` para cada job
- Watchdog que marca jobs stuck como `failed` después de 30 minutos

**Gestión con Supervisor:**

```bash
# Ver estado
sudo supervisorctl status job_worker

# Iniciar
sudo supervisorctl start job_worker

# Detener
sudo supervisorctl stop job_worker

# Reiniciar
sudo supervisorctl restart job_worker

# Ver logs
tail -f /var/log/supervisor/job_worker.out.log
tail -f /var/log/supervisor/job_worker.err.log
```

**Configuración en `/etc/supervisor/conf.d/job_worker.conf`:**
```ini
[program:job_worker]
command=python /app/backend/job_worker.py
directory=/app/backend
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/job_worker.out.log
stderr_logfile=/var/log/supervisor/job_worker.err.log
environment=MONGO_URL="mongodb://localhost:27017",DB_NAME="test_database"
```

### 3. Procesador de Jobs (`process_generation_job()` en `server.py`)

**Responsabilidades:**
- Valida el formato del cuestionario robustamente
- Ejecuta el orquestador E1-E9 (training) y/o N0-N8 (nutrition)
- Actualiza progreso en MongoDB después de cada agente
- Captura métricas de tokens y costos por agente
- Maneja errores y retry automático (2 reintentos)
- Guarda resultados en `training_plans` o `nutrition_plans`

**Flujo Interno:**

1. **Validación del Cuestionario**
   ```python
   is_valid, errors, data = _validate_questionnaire_format(submission)
   ```
   
   - Verifica estructura del documento MongoDB
   - Valida campo `responses` (CRÍTICO)
   - Verifica campos requeridos mínimos
   - Valida formatos (fecha, sexo, campos numéricos)

2. **Ejecución del Pipeline**
   ```python
   training_result = await orchestrator._execute_training_initial(
       adapted_questionnaire,
       previous_plan=previous_training_plan
   )
   ```

3. **Actualización de Progreso**
   ```python
   for execution in training_result["executions"]:
       await update_job_progress(
           job_id,
           "training",
           execution["agent_id"],
           completed,
           total_steps,
           message
       )
   ```

4. **Captura de Métricas**
   ```python
   await db.generation_jobs.update_one(
       {"_id": job_id},
       {
           "$inc": {
               "token_usage.total_tokens": tokens,
               ...
           },
           "$set": {
               f"token_usage.by_agent.{agent_id}": token_usage
           }
       }
   )
   ```

5. **Guardado de Resultados**
   ```python
   plan_id = await save_training_plan(...)
   await db.generation_jobs.update_one(
       {"_id": job_id},
       {
           "$set": {
               "status": "completed",
               "result.training_plan_id": plan_id,
               "completed_at": datetime.now(timezone.utc)
           }
       }
   )
   ```

### 4. Frontend React (`GenerationProgressModal.jsx`)

**Responsabilidades:**
- Muestra modal con progreso en tiempo real
- Polling cada 3 segundos al endpoint `/jobs/{job_id}`
- Barra de progreso animada
- Muestra agente actual y porcentaje
- Callbacks al completar o fallar

**Uso:**
```jsx
const [jobId, setJobId] = useState(null);

const generateTrainingPlan = async () => {
  const response = await api.post(
    `/admin/users/${userId}/plans/generate_async`,
    { type: "training", submission_id: "..." }
  );
  setJobId(response.data.job_id);
};

<GenerationProgressModal
  isOpen={!!jobId}
  jobId={jobId}
  onComplete={(result) => {
    console.log("Plan generado:", result.training_plan_id);
    reloadData();
  }}
  onError={(error) => {
    console.error("Error:", error);
  }}
  onClose={() => setJobId(null)}
/>
```

## Formato del Cuestionario en MongoDB

### Schema Esperado

```javascript
{
  "_id": "1732270123456789",  // Timestamp único
  "user_id": "user_123",
  "responses": {  // ⚠️ CAMPO CRÍTICO - DEBE EXISTIR
    // Campos requeridos mínimos
    "nombre_completo": "Carlos Fernández",
    "email": "carlos@example.com",
    "fecha_nacimiento": "1990-05-15",  // Formato: YYYY-MM-DD
    "sexo": "Hombre",  // Valores: Hombre, Mujer
    "peso": "78",      // String con número
    "altura_cm": "178", // String con número
    "objetivo_fisico": "Ganar músculo y definir",
    
    // Campos opcionales (150+ campos posibles)
    "profesion": "Ingeniero",
    "telefono": "+34 612 345 678",
    "entrenado_gimnasio": "Sí, 3 años",
    "dias_semana_entrenar": "4-5 días",
    // ... más campos
  },
  "submitted_at": ISODate("2024-11-22T10:00:00Z"),
  "plan_generated": false,
  "plan_id": null
}
```

### Validaciones Aplicadas

1. **Estructura del documento:**
   - Debe tener campos `_id`, `user_id`, `responses`
   
2. **Campo `responses`:**
   - Debe existir (no opcional)
   - Debe ser un objeto/dict no vacío
   - Contiene TODOS los datos del cuestionario
   
3. **Campos requeridos mínimos:**
   - `nombre_completo`
   - `email`
   - `fecha_nacimiento` (formato YYYY-MM-DD)
   - `sexo` (Hombre/Mujer)
   - `peso` (número como string)
   - `altura_cm` (número como string)
   - `objetivo_fisico`

4. **Validaciones de formato:**
   - Fecha en formato ISO (YYYY-MM-DD)
   - Sexo normalizado
   - Campos numéricos parseables y positivos

### Mensajes de Error Claros

Si la validación falla, el job se marca como `failed` con un mensaje detallado:

```json
{
  "status": "failed",
  "error_message": "❌ FORMATO DE CUESTIONARIO INVÁLIDO:\n  • Campo 'responses' ausente en submission\n  • Campos requeridos ausentes: nombre_completo, peso\n\n📋 FORMATO ESPERADO: El cuestionario debe guardarse en MongoDB con estructura: {...}",
  "error_reason": "validation_error"
}
```

## Ciclo de Vida Completo de un Job

```
1. Usuario llena cuestionario
   └─> Frontend envía POST /submit-nutrition-questionnaire
       └─> Backend guarda en nutrition_questionnaire_submissions
           └─> Response inmediata con submission_id

2. Usuario/Admin solicita generación de plan
   └─> Frontend envía POST /admin/users/{id}/plans/generate_async
       └─> Backend crea job con status="pending"
           └─> Response inmediata con job_id (100-200ms)

3. Job Worker detecta job pendiente (polling cada 5s)
   └─> Worker ejecuta process_generation_job(job_id)
       ├─> Cambia status a "running"
       ├─> Valida cuestionario (formato robusto)
       ├─> Ejecuta orquestador E1-E9
       │   ├─> Actualiza progreso después de E1
       │   ├─> Actualiza progreso después de E2
       │   ├─> ...
       │   └─> Actualiza progreso después de E9
       ├─> Guarda plan en training_plans
       ├─> Actualiza job con result.training_plan_id
       └─> Cambia status a "completed" (6-10 minutos después)

4. Frontend detecta completion (polling cada 3s)
   └─> Callback onComplete(result)
       └─> Recarga datos del usuario
           └─> Muestra plan generado
```

## Tiempos Esperados

| Operación | Duración | Notas |
|-----------|----------|-------|
| Crear job | ~100-200ms | Respuesta inmediata |
| Pipeline E1-E9 | 6-10 min | Depende de tokens y complejidad |
| Pipeline N0-N8 | 4-8 min | Depende de tokens |
| Pipeline completo (E+N) | 12-18 min | Secuencial |
| Polling job worker | 5s | Intervalo fijo |
| Polling frontend | 3s | Intervalo fijo |

## Métricas Capturadas

Por cada job completado, se capturan:

1. **Tokens:**
   - Total de tokens (input + output)
   - Tokens de input (prompt)
   - Tokens de output (completion)
   - Desglose por agente (E1, E2, ..., E9)

2. **Tiempos:**
   - `created_at`: Momento de creación del job
   - `started_at`: Momento de inicio de ejecución
   - `completed_at`: Momento de finalización
   - Duración total calculada

3. **Costos (calculables):**
   - Basado en tokens y pricing de GPT-5-mini:
     - Input: $0.075 por 1M tokens
     - Output: $0.30 por 1M tokens

4. **Logs de ejecución:**
   - Array `execution_log` con eventos timestamped
   - Ejemplos: "started", "agent_completed", "retry", "timeout"

## Extracción de Resultados

Para extraer los outputs del pipeline E1-E9:

```python
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.test_database

# 1. Buscar job completado
job = await db.generation_jobs.find_one({
    "_id": "job_id_aqui",
    "status": "completed"
})

# 2. Obtener training_plan_id
training_plan_id = job["result"]["training_plan_id"]

# 3. Obtener el plan completo
training_plan = await db.training_plans.find_one({"_id": training_plan_id})

# 4. Extraer outputs de cada agente
training_data = training_plan["training"]

outputs = {
    "client_summary": training_data.get("client_summary"),  # E1
    "mesocycle": training_data.get("mesocycle"),           # E4
    "sessions": training_data.get("sessions"),             # E5
    "formatted_plan": training_data.get("formatted_plan"), # E7
    "audit": training_data.get("audit"),                   # E8
    "bridge_for_nutrition": training_data.get("bridge_for_nutrition")  # E9
}

# 5. Métricas
token_usage = job["token_usage"]
execution_time = (job["completed_at"] - job["started_at"]).total_seconds()
```

## Troubleshooting

### Job Worker no está procesando jobs

**Diagnóstico:**
```bash
# Verificar que está corriendo
sudo supervisorctl status job_worker

# Ver logs recientes
tail -50 /var/log/supervisor/job_worker.out.log
```

**Soluciones:**
- Si no está corriendo: `sudo supervisorctl start job_worker`
- Si está crasheando: Revisar logs de error
- Verificar que MongoDB es accesible
- Verificar variables de entorno (MONGO_URL, DB_NAME)

### Job queda stuck en "pending"

**Diagnóstico:**
```bash
# Ver si el worker está procesando
tail -f /var/log/supervisor/job_worker.out.log | grep "procesando job"
```

**Causas comunes:**
- Worker no está corriendo
- Ya hay 2 jobs en `running` (concurrencia máxima)
- Error en el código que crashea el worker silenciosamente

**Solución:**
- Reiniciar worker: `sudo supervisorctl restart job_worker`
- Revisar logs para errores

### Job falla con "KeyError: 'responses'"

**Causa:**
El cuestionario en MongoDB no tiene la estructura correcta. Debe tener:
```json
{
  "_id": "...",
  "user_id": "...",
  "responses": { ... }  // ← Este campo DEBE existir
}
```

**Solución:**
Verificar el endpoint que guarda el cuestionario (`/submit-nutrition-questionnaire`) y asegurarse de que guarda con la estructura correcta.

### Job excede 30 minutos (timeout)

**Causa:**
El pipeline está tardando demasiado o está stuck.

**Comportamiento:**
El watchdog del worker marcará automáticamente el job como `failed` con:
```json
{
  "status": "failed",
  "error_message": "Job excedió timeout de 30 minutos",
  "error_reason": "timeout"
}
```

**Solución:**
- Revisar logs del orquestador para ver dónde se atascó
- Verificar que los agentes no estén en loops infinitos
- Considerar optimizar prompts para reducir tokens

## Comando Rápido para Testing

Para probar el flujo completo:

```bash
cd /app/backend
python test_full_pipeline_validation.py
```

Este script:
1. ✅ Define y documenta el schema del cuestionario
2. ✅ Crea un usuario y cuestionario de ejemplo válido
3. ✅ Crea un job de generación
4. ✅ Monitorea su progreso en tiempo real
5. ✅ Extrae métricas (tokens, costos, tiempos)
6. ✅ Extrae outputs (sessions, formatted_plan, audit, bridge)
7. ✅ Valida coherencia entre outputs
8. ✅ Genera un reporte JSON completo

## Contacto de Soporte

Para issues relacionados con:
- **Jobs stuck o timeouts**: Revisar logs del worker
- **Formato de cuestionario**: Ver sección "Formato del Cuestionario"
- **Timeouts de FastAPI**: Verificar que se usa el endpoint async
- **Errores del orquestador**: Revisar logs de backend
