# EDN360 - Migración de BD de Ejercicios y K1 Entrenamiento

**Fecha:** 2025-12-03
**Solicitado por:** Jorge Calcerrada
**Estado:** COMPLETADO ✅

---

## RESUMEN EJECUTIVO

✅ **BD de Ejercicios reemplazada completamente**
✅ **K1 Entrenamiento integrada como Knowledge Base**
✅ **Prompts actualizados sin hardcoding**
✅ **Sistema listo para tests E2E**

---

## 1. BD DE EJERCICIOS - REEMPLAZO COMPLETO

### Archivos
- **Archivo nuevo:** `BD_EJERCICIOS1_BD_AGENTES_DEFINITIVA_CLEAN.json`
- **Total ejercicios:** 1,477
- **Estructura:** JSON array con objetos de ejercicios

### OpenAI Vector Store
- **ID:** `vs_693049ea21308191a8bdcee667ef9ba9`
- **Nombre:** EDN360 - BD Ejercicios v2.0 Definitiva
- **File ID:** `file-S63UqAwhkMS7QXAvocDkmd`

### Agentes Conectados
- ✅ **E6 - Exercise Normalizer & DB Mapper**
- ✅ **E7.5 - Training Plan Enricher**

### BD Anterior (DESCONECTADA)
- **IDs antiguos eliminados:**
  - `vs_6924b7574b7c8191b6008068aa8a1df0`
  - `vs_692c510043dc81919e4e7887a299d583`

**CONFIRMACIÓN:** La BD antigua ya NO está conectada al workflow. Solo se usa la nueva.

---

## 2. K1 ENTRENAMIENTO - KNOWLEDGE BASE

### Archivos
- **Archivo:** `K1 Entrenamiento.txt`
- **Tamaño:** 91 KB
- **Contenido:** Base de conocimientos completa sobre programación de entrenamiento

### OpenAI Vector Store
- **ID:** `vs_693049eb1144819197bf732246b1c1f6`
- **Nombre:** EDN360 - K1 Entrenamiento KB
- **File ID:** `file-6v3YA3fY4VLAwPYVZ7rxoq`

### Agentes Conectados
- ✅ **E3 - Training Summary** (decisiones de programación)
- ✅ **E4 - Training Plan Generator** (manual de programación)
- ✅ **E5 - Training Plan Validator** (referencia de seguridad)

**USO:** Los agentes consultan la K1 como "manual vivo" para decisiones de:
- Tipo de split (upper/lower, PPL, full body)
- Distribución de volumen
- Rangos de repeticiones
- Progresión
- Seguridad articular

---

## 3. CÓDIGO ACTUALIZADO

### Archivo Modificado
`/app/edn360-workflow-service/src/edn360_workflow.ts`

### Cambios Realizados

**ANTES:**
```typescript
const fileSearch = fileSearchTool([
  "vs_6924b7574b7c8191b6008068aa8a1df0"
])
const fileSearch1 = fileSearchTool([
  "vs_692c510043dc81919e4e7887a299d583"
])
```

**DESPUÉS:**
```typescript
// BD de Ejercicios v2.0 Definitiva (1,477 ejercicios corregidos)
const fileSearchExercises = fileSearchTool([
  "vs_693049ea21308191a8bdcee667ef9ba9"
])

// K1 Entrenamiento - Knowledge Base
const fileSearchTrainingKB = fileSearchTool([
  "vs_693049eb1144819197bf732246b1c1f6"
])
```

---

## 4. ELIMINACIÓN DE HARDCODING

### Cambio en E4 - Training Plan Generator

**ANTES (hardcoded test client):**
```
For the current test client:
- Advanced lifter.
- 4 training days per week.
- 45 min sessions.
- Primary goal: muscle_gain.
- Shoulder issues: yes.
- Lumbar disc issues (L5-L6): yes.
- Gym access: full_gym.
```

**DESPUÉS (sin hardcoding):**
```
CRITICAL: Do NOT use hardcoded profiles or assumptions. Base ALL decisions on:
- The actual training_context provided by E3
- The state (previous_plans, last_plan) if available
- The K1 Entrenamiento knowledge base for programming principles
```

**CONFIRMACIÓN:** El agente E4 ya NO tiene perfiles hardcodeados. Todas las decisiones se basan en datos reales del usuario.

---

## 5. ESTRUCTURA DE FILETOOLS POR AGENTE

| Agente | Tools | Propósito |
|--------|-------|----------|
| E1 | Ninguno | Análisis de perfil |
| E2 | Ninguno | Parse cuestionario |
| E3 | `fileSearchTrainingKB` | Decisiones de programación |
| E4 | `fileSearchTrainingKB` | Manual de programación |
| E5 | `fileSearchTrainingKB` | Referencia de seguridad |
| E6 | `fileSearchExercises` | Mapeo a BD ejercicios |
| E7 | Ninguno | Ensamblaje de plan |
| E7.5 | `fileSearchExercises` | Enriquecimiento con nombres/videos |

---

## 6. VERIFICACIÓN

### Servicios
```bash
sudo supervisorctl status edn360-workflow-service
# Output esperado: RUNNING
```

### Logs
```bash
tail -f /var/log/supervisor/edn360-workflow-service.out.log
# Debe mostrar: "✅ EDN360 Workflow Service corriendo en puerto 4000"
```

### Test Rápido
```bash
curl http://localhost:4000/health
# Output esperado: {"status": "ok"}
```

---

## 7. ARCHIVOS DE REFERENCIA

| Documento | Ubicación |
|-----------|----------|
| Este documento | `/app/docs/EDN360_BD_Y_KB_MIGRATION.md` |
| BD Ejercicios (local) | `/tmp/BD_EJERCICIOS_NUEVA.json` |
| K1 Entrenamiento (local) | `/tmp/K1_Entrenamiento.txt` |
| Código del Workflow | `/app/edn360-workflow-service/src/edn360_workflow.ts` |
| IDs de Vector Stores | `/tmp/vector_store_ids.json` |

---

## 8. PRÓXIMOS PASOS

✅ **COMPLETADO:**
1. BD de Ejercicios reemplazada
2. K1 Entrenamiento integrada
3. Hardcoding eliminado
4. Sistema actualizado y funcionando

⏭️ **SIGUIENTE:**
1. Tests E2E con 3 casos (inicial, evolución 1, evolución 2)
2. Validación de progresión de planes
3. Verificación de uso de K1 en decisiones

---

**Documento actualizado:** 2025-12-03  
**Estado del sistema:** PRODUCCIÓN ACTUALIZADA  
**Listo para:** Tests end-to-end
