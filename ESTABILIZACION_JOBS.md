# 🔧 ESTABILIZACIÓN SISTEMA DE JOBS ASÍNCRONOS E.D.N.360

## ✅ IMPLEMENTACIÓN COMPLETADA

### 1️⃣ TIMEOUT DE SEGURIDAD BÁSICO (30 minutos)

**Implementación:**
- Función `job_timeout_watchdog()` que se ejecuta cada 5 minutos
- Busca jobs en estado "running" con `started_at` > 30 minutos
- Los marca como "failed" con `error_reason: "timeout"`

**Ejemplo de Job con Timeout:**
```json
{
  "_id": "job_123456",
  "status": "failed",
  "error_reason": "timeout",
  "error_message": "Job excedió timeout de 30 minutos",
  "started_at": "2025-11-20T20:00:00Z",
  "completed_at": "2025-11-20T20:30:05Z"
}
```

**Cómo se gestiona:**
- ✅ Watchdog se ejecuta automáticamente al iniciar el servidor
- ✅ Revisa cada 5 minutos
- ✅ Marca job como failed
- ✅ Añade evento al `execution_log`

---

### 2️⃣ PROGRESO REAL POR AGENTE (No Simulado)

**Implementación:**
- Función `update_job_progress()` actualiza DESPUÉS de cada agente real
- Lee `executions` del resultado del orquestador
- Actualiza BD con progreso preciso

**Ejemplo de Progreso durante Ejecución:**
```json
{
  "_id": "job_789",
  "status": "running",
  "progress": {
    "phase": "training",
    "current_agent": "E5",
    "completed_steps": 5,
    "total_steps": 9,
    "percentage": 55,
    "message": "Agente E5 completado"
  }
}
```

**Cómo se actualiza:**
- ✅ El orquestador ejecuta E1 → actualiza BD inmediatamente
- ✅ El orquestador ejecuta E2 → actualiza BD inmediatamente
- ✅ ... continúa hasta E9 o N8
- ✅ Cada actualización incluye timestamp en `execution_log`

**Fallback:**
- Si `executions` no está disponible, usa índice de agente
- Siempre refleja ejecución REAL, no simulación

---

### 3️⃣ REINTENTO AUTOMÁTICO SIMPLE (OpenAI Errors)

**Implementación:**
- Función `execute_with_retry(func, max_retries=2)`
- Detecta errores recuperables: "rate limit", "timeout", "429", "503"
- Delays: 10s (primer reintento), 30s (segundo reintento)

**Ejemplo de Job con Retry Exitoso:**
```json
{
  "_id": "job_456",
  "status": "completed",
  "retry_count": 1,
  "execution_log": [
    {
      "timestamp": "2025-11-20T20:00:00Z",
      "event": "started",
      "details": "Iniciando generación (mode: training)"
    },
    {
      "timestamp": "2025-11-20T20:05:00Z",
      "event": "training_started",
      "details": "Iniciando pipeline E1-E9"
    },
    {
      "timestamp": "2025-11-20T20:08:00Z",
      "event": "retry_success",
      "details": "Pipeline completado después de 1 reintento(s)"
    },
    {
      "timestamp": "2025-11-20T20:10:00Z",
      "event": "completed",
      "details": "Job finalizado exitosamente"
    }
  ]
}
```

**Qué ocurre si falla OpenAI:**
- ✅ **Intento 1:** Error → Espera 10s → Reintenta
- ✅ **Intento 2:** Error → Espera 30s → Reintenta
- ❌ **Intento 3:** Error → Marca job como failed

**Ejemplo de Job Fallido después de Reintentos:**
```json
{
  "_id": "job_999",
  "status": "failed",
  "error_reason": "error",
  "error_message": "OpenAI API rate limit exceeded",
  "retry_count": 2,
  "execution_log": [
    {
      "timestamp": "2025-11-20T20:00:00Z",
      "event": "started",
      "details": "Iniciando generación"
    },
    {
      "timestamp": "2025-11-20T20:05:00Z",
      "event": "failed",
      "details": "Error: OpenAI API rate limit exceeded"
    }
  ]
}
```

---

### 4️⃣ LÍMITE BÁSICO DE CONCURRENCIA (2 jobs simultáneos)

**Implementación:**
- Función `check_job_concurrency()` verifica jobs en "running"
- Si hay 2 o más, marca nuevo job como "queued"
- Función `process_queued_jobs()` revisa cola cada 30s

**Cómo se controla la cola:**

**Escenario 1: Espacio disponible (< 2 jobs running)**
```json
// Job creado directamente en "running"
{
  "_id": "job_A",
  "status": "running",
  "execution_log": [
    {
      "event": "started",
      "details": "Iniciando generación (mode: training)"
    }
  ]
}
```

**Escenario 2: Sin espacio (>= 2 jobs running)**
```json
// Job marcado como "queued"
{
  "_id": "job_B",
  "status": "queued",
  "execution_log": [
    {
      "event": "queued",
      "details": "2 jobs en ejecución"
    }
  ]
}
```

**Procesamiento de Cola:**
- ✅ Watchdog revisa cada 30 segundos
- ✅ Si hay espacio (running < 2), procesa próximo job en cola
- ✅ Jobs procesados en orden FIFO (First In, First Out)

**Ejemplo de Consulta a BD:**
```javascript
// Jobs actualmente en ejecución
db.generation_jobs.find({ "status": "running" }).count()
// Resultado: 2

// Jobs en cola esperando
db.generation_jobs.find({ "status": "queued" }).sort({ "created_at": 1 })
// Resultado: [job_B, job_C, job_D]

// Después de 30s, un job termina:
// job_B pasa automáticamente de "queued" → "running"
```

---

### 5️⃣ LOG SIMPLE POR JOB

**Implementación:**
- Campo `execution_log` (array de objetos) en cada job
- Función `add_job_log(job_id, event, details)` añade eventos

**Eventos Registrados:**
1. `started`: Job comenzó a procesarse
2. `queued`: Job puesto en cola por concurrencia
3. `training_started`: Inicio del pipeline E1-E9
4. `nutrition_started`: Inicio del pipeline N0-N8
5. `agent_completed`: Un agente específico terminó (E1, E2, N0, etc.)
6. `retry_success`: Pipeline completado después de reintentos
7. `training_completed`: Plan de entrenamiento generado
8. `nutrition_completed`: Plan de nutrición generado (si aplica)
9. `completed`: Job finalizado exitosamente
10. `failed`: Job falló
11. `timeout`: Job marcado como failed por timeout

**Ejemplo de Log Completo de Job Exitoso (mode: "full"):**
```json
{
  "_id": "job_full_123",
  "status": "completed",
  "type": "full",
  "retry_count": 0,
  "execution_log": [
    {
      "timestamp": "2025-11-20T20:00:00.000Z",
      "event": "started",
      "details": "Iniciando generación (mode: full)"
    },
    {
      "timestamp": "2025-11-20T20:00:05.000Z",
      "event": "training_started",
      "details": "Iniciando pipeline E1-E9"
    },
    {
      "timestamp": "2025-11-20T20:01:30.000Z",
      "event": "agent_completed",
      "details": "E1 ejecutado exitosamente"
    },
    {
      "timestamp": "2025-11-20T20:02:45.000Z",
      "event": "agent_completed",
      "details": "E2 ejecutado exitosamente"
    },
    // ... E3-E9 ...
    {
      "timestamp": "2025-11-20T20:08:00.000Z",
      "event": "training_completed",
      "details": "Plan de entrenamiento generado: plan_id_xyz"
    },
    {
      "timestamp": "2025-11-20T20:08:05.000Z",
      "event": "nutrition_started",
      "details": "Iniciando pipeline N0-N8"
    },
    {
      "timestamp": "2025-11-20T20:09:30.000Z",
      "event": "agent_completed",
      "details": "N0 ejecutado exitosamente"
    },
    // ... N1-N8 ...
    {
      "timestamp": "2025-11-20T20:15:00.000Z",
      "event": "nutrition_completed",
      "details": "Plan de nutrición generado: plan_id_abc"
    },
    {
      "timestamp": "2025-11-20T20:15:05.000Z",
      "event": "completed",
      "details": "Job finalizado exitosamente. Planes generados: {training_plan_id: 'plan_id_xyz', nutrition_plan_id: 'plan_id_abc'}"
    }
  ],
  "result": {
    "training_plan_id": "plan_id_xyz",
    "nutrition_plan_id": "plan_id_abc"
  }
}
```

---

## 📊 VERIFICACIÓN DEL SISTEMA

### Consultar Estado de un Job:
```bash
GET /jobs/{job_id}
```

**Respuesta con Job Activo:**
```json
{
  "job_id": "job_123",
  "status": "running",
  "type": "training",
  "progress": {
    "phase": "training",
    "current_agent": "E4",
    "completed_steps": 4,
    "total_steps": 9,
    "percentage": 44,
    "message": "Agente E4 completado"
  },
  "execution_log": [
    {"timestamp": "...", "event": "started", "details": "..."},
    {"timestamp": "...", "event": "agent_completed", "details": "E1 ejecutado"},
    {"timestamp": "...", "event": "agent_completed", "details": "E2 ejecutado"},
    {"timestamp": "...", "event": "agent_completed", "details": "E3 ejecutado"},
    {"timestamp": "...", "event": "agent_completed", "details": "E4 ejecutado"}
  ]
}
```

---

## 🎯 RESUMEN EJECUTIVO

| Punto | Estado | Descripción |
|-------|--------|-------------|
| 1️⃣ **Timeout 30min** | ✅ | Watchdog marca jobs stuck como failed |
| 2️⃣ **Progreso Real** | ✅ | Actualiza después de CADA agente ejecutado |
| 3️⃣ **Retry (2x)** | ✅ | Reintentos automáticos con delays 10s/30s |
| 4️⃣ **Cola (max 2)** | ✅ | Concurrencia limitada, cola FIFO |
| 5️⃣ **Logging** | ✅ | Eventos detallados en `execution_log` |

---

## ⚠️ IMPORTANTE - NO ES SAASAT

**Este sistema está optimizado para:**
- ✅ Operación estable con pocos usuarios
- ✅ Prevenir bloqueos y timeouts
- ✅ Visibilidad clara del progreso
- ✅ Control manual si algo falla

**NO está optimizado para:**
- ❌ Miles de jobs concurrentes
- ❌ Auto-scaling dinámico
- ❌ Alta disponibilidad multi-región
- ❌ Optimización de costos cloud

**Recomendación:**
- Monitorear manualmente la colección `generation_jobs`
- Si algún job falla, revisar `execution_log` y `error_message`
- Límite actual: 2 jobs simultáneos es suficiente para operación actual
