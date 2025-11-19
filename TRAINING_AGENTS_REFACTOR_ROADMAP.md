# 🗺️ HOJA DE RUTA: REFACTOR ARQUITECTURAL DE AGENTES DE ENTRENAMIENTO

## 📋 RESUMEN EJECUTIVO

Este documento define el plan de implementación para **refactorizar completamente** la arquitectura de agentes de entrenamiento (E1-E9) según las especificaciones del documento "EMERGENT – SISTEMA DE AGENTES DE ENTRENAMIENTO".

### 🎯 Objetivo del Refactor
Transformar el sistema actual donde cada agente recibe estructuras de datos diferentes, a un sistema unificado donde **TODOS los agentes trabajan con el mismo objeto `client_context`**, garantizando:
- ✅ Consistencia de información entre agentes
- ✅ Trazabilidad completa del estado del cliente
- ✅ Escalabilidad para versiones futuras
- ✅ Eliminación de pérdidas de datos
- ✅ Reglas claras de responsabilidad por agente

---

## 🔍 ANÁLISIS DE LA SITUACIÓN ACTUAL

### Problemas Detectados en el Sistema Actual

❌ **1. Estructura de datos inconsistente entre agentes**
- E1 recibe: cuestionario directo
- E2 recibe: `{"e1_output": ..., **questionnaire}`
- E3 recibe: `{"e1_output": ..., "e2_output": ...}`
- E4-E9 reciben: outputs acumulados con claves diferentes

❌ **2. No hay objeto unificado `client_context`**
- La información no está estructurada de forma estándar
- Cada agente interpreta y estructura los datos a su manera

❌ **3. Posible pérdida de información**
- Si un agente no "reenvía" correctamente el output anterior, se pierde
- No hay garantía de que toda la información llegue a los agentes finales

❌ **4. Difícil trazabilidad**
- No hay un "snapshot" claro del estado del cliente en cada versión
- Difícil auditar qué datos específicos se usaron para generar un plan

### Lo que FUNCIONA y se MANTIENE

✅ **1. Arquitectura de Knowledge Bases (recién implementada)**
- El sistema de KB está correcto según el documento
- NO se debe incluir K1 dentro de client_context
- K1 es referencia global, client_context tiene prioridad

✅ **2. Secuencia de agentes**
- El orden E1→E2→E3→E4→E5→E6→E7→E8→E9 es correcto
- Los roles de cada agente están bien definidos

✅ **3. BaseAgent y método execute()**
- La estructura base con `execute(input_data, knowledge_base)` es correcta
- Solo necesitamos ajustar cómo se usa

---

## 🏗️ ARQUITECTURA OBJETIVO

### Objeto `client_context` (Estructura Completa)

```json
{
  "client_context": {
    "meta": {
      "client_id": "string",
      "snapshot_id": "string",
      "version": 1,
      "selected_inputs": {
        "cuestionario": "id",
        "entrenamiento_base": "id"
      }
    },
    "raw_inputs": {
      "cuestionario_inicial": "string|null",
      "cuestionario_seguimiento": "string|null",
      "entrenamiento_base": {},
      "notas_entrenador": "string|null"
    },
    "training": {
      "profile": null,           // E1
      "constraints": null,       // E1
      "prehab": null,           // E1
      "progress": null,         // E1 (solo seguimientos)
      "capacity": null,         // E2
      "adaptation": null,       // E3
      "mesocycle": null,        // E4
      "sessions": null,         // E5
      "safe_sessions": null,    // E6
      "formatted_plan": null,   // E7
      "audit": null,            // E8
      "bridge_for_nutrition": null  // E9
    }
  }
}
```

### Reglas del Nuevo Sistema

1. **Todos los agentes reciben `client_context` completo**
2. **Cada agente modifica SOLO su campo asignado**
3. **Los agentes devuelven `client_context` completo actualizado**
4. **NO se pueden eliminar o sobrescribir campos de agentes anteriores**
5. **Validación estricta**: error si faltan campos requeridos

---

## 📅 PLAN DE IMPLEMENTACIÓN POR FASES

### ⚙️ FASE 0: PREPARACIÓN (30 min)
**Objetivo**: Entender y documentar la arquitectura actual antes de modificar

**Tareas**:
1. [ ] Revisar estructura actual de cada agente E1-E9
2. [ ] Documentar inputs/outputs actuales de cada agente
3. [ ] Identificar dependencias entre agentes
4. [ ] Crear backup mental de la arquitectura actual

**Entregable**: Documento de análisis de arquitectura actual

---

### 🏗️ FASE 1: DEFINICIÓN DE CONTRATOS (1-2 horas)
**Objetivo**: Definir con precisión la estructura de cada campo del `client_context`

**Tareas**:
1. [ ] Crear archivo `contracts.py` o actualizar el existente con:
   - Estructura completa de `client_context`
   - Estructura de cada campo: `profile`, `constraints`, `prehab`, etc.
   - Tipos de datos, campos requeridos y opcionales
   - Validaciones por campo

2. [ ] Definir Pydantic models para:
   - `ClientContextMeta`
   - `RawInputs`
   - `TrainingProfile`
   - `TrainingConstraints`
   - `TrainingPrehab`
   - `TrainingProgress`
   - `TrainingCapacity`
   - `TrainingAdaptation`
   - `TrainingMesocycle`
   - `TrainingSessions`
   - `TrainingSafeSessions`
   - `TrainingFormattedPlan`
   - `TrainingAudit`
   - `TrainingBridgeForNutrition`
   - `TrainingData` (contiene todos los anteriores)
   - `ClientContext` (modelo principal)

**Entregable**: 
- `/app/backend/edn360/contracts.py` actualizado
- Documentación de cada estructura

---

### 🔧 FASE 2: REFACTOR DEL ORCHESTRATOR (1-2 horas)
**Objetivo**: Modificar `orchestrator.py` para pasar `client_context` unificado

**Tareas**:
1. [ ] Crear método `_initialize_client_context()` que construye el objeto inicial desde el cuestionario
2. [ ] Modificar `_execute_training_initial()` para:
   - Inicializar `client_context` al principio
   - Pasar el mismo objeto a TODOS los agentes
   - Recibir el objeto actualizado de cada agente
   - Validar que cada agente devolvió el objeto completo
3. [ ] Añadir validación entre agentes:
   - Verificar que E2 recibió `training.profile` de E1
   - Verificar que E3 recibió `training.capacity` de E2
   - etc.

**Cambios clave**:
```python
# ANTES (actual)
for agent in self.training_initial_agents:
    if agent.agent_id == "E1":
        agent_input = current_data
    elif agent.agent_id == "E2":
        agent_input = {"e1_output": outputs.get("E1"), **questionnaire_data}
    # ... diferentes estructuras por agente

# DESPUÉS (nuevo)
client_context = self._initialize_client_context(questionnaire_data, previous_plan)
for agent in self.training_initial_agents:
    # TODOS reciben el mismo objeto
    client_context = await agent.execute(client_context, knowledge_base=kb)
    # Validar que el campo esperado fue llenado
    self._validate_agent_output(agent.agent_id, client_context)
```

**Entregable**: 
- `orchestrator.py` refactorizado
- Método `_initialize_client_context()`
- Método `_validate_agent_output()`

---

### 🤖 FASE 3: REFACTOR DE AGENTES (4-6 horas)
**Objetivo**: Reescribir cada agente E1-E9 para trabajar con `client_context`

**Enfoque**: Un agente a la vez, en orden secuencial

#### 3.1 - Agente E1 (Analista)
**Input**: `client_context` con `raw_inputs` llenos
**Output**: `client_context` con `training.profile`, `training.constraints`, `training.prehab`, `training.progress` llenos

**Tareas**:
1. [ ] Modificar `e1_analyst.py`:
   - `validate_input()`: verificar que `raw_inputs` existen
   - `get_system_prompt()`: actualizar para trabajar con client_context
   - `process_output()`: parsear y llenar solo los campos de E1
2. [ ] Crear tests unitarios para E1
3. [ ] Verificar funcionamiento aislado

#### 3.2 - Agente E2 (Evaluador de Capacidad)
**Input**: `client_context` con `training.profile` y `training.progress` (si existe)
**Output**: `client_context` con `training.capacity` lleno

**Tareas**:
1. [ ] Modificar `e2_capacity.py`:
   - `validate_input()`: verificar que `training.profile` existe
   - `get_system_prompt()`: actualizar para leer profile y generar capacity
   - `process_output()`: parsear y llenar solo `training.capacity`
2. [ ] Tests unitarios
3. [ ] Verificar funcionamiento

#### 3.3 - Agente E3 (Adaptador)
**Input**: `client_context` con `training.capacity`, `training.profile`, `training.progress`
**Output**: `client_context` con `training.adaptation` lleno

**Tareas**: (similar patrón)

#### 3.4 - Agente E4 (Arquitecto del Mesociclo)
**Input**: `client_context` con `training.capacity`, `training.adaptation`, `training.profile`
**Output**: `client_context` con `training.mesocycle` lleno

**Tareas**: (similar patrón)

#### 3.5 - Agente E5 (Ingeniero de Sesiones)
**Input**: `client_context` con `training.mesocycle`, `training.profile`
**Output**: `client_context` con `training.sessions` lleno

**Tareas**: (similar patrón)

#### 3.6 - Agente E6 (Técnico Clínico)
**Input**: `client_context` con `training.sessions`, `training.constraints`, `training.prehab`
**Output**: `client_context` con `training.safe_sessions` lleno

**Tareas**: (similar patrón)

#### 3.7 - Agente E7 (Visualizador)
**Input**: `client_context` con `training.safe_sessions`, `training.mesocycle`
**Output**: `client_context` con `training.formatted_plan` lleno

**Tareas**: (similar patrón)

#### 3.8 - Agente E8 (Auditor)
**Input**: `client_context` con `training.safe_sessions`, `training.mesocycle`, `training.capacity`, `training.constraints`
**Output**: `client_context` con `training.audit` lleno

**Tareas**: (similar patrón)

#### 3.9 - Agente E9 (Bridge para Nutrición)
**Input**: `client_context` con `training.safe_sessions`, `training.mesocycle`, `training.profile`
**Output**: `client_context` con `training.bridge_for_nutrition` lleno

**Tareas**: (similar patrón)

**Entregable por agente**: 
- Archivo `.py` refactorizado
- Tests unitarios pasando
- Documentación del campo que llena

---

### 🔗 FASE 4: INTEGRACIÓN Y VALIDACIÓN (2-3 horas)
**Objetivo**: Probar el flujo completo E1→E9 con el nuevo sistema

**Tareas**:
1. [ ] Crear cuestionario de prueba realista
2. [ ] Ejecutar flujo completo con logs detallados
3. [ ] Verificar que:
   - `client_context` viaja correctamente entre agentes
   - Cada agente llena SOLO su campo
   - No hay pérdida de información
   - El objeto final tiene todos los campos llenos
4. [ ] Crear tests de integración:
   - Test con cuestionario inicial (versión 1)
   - Test con cuestionario de seguimiento (versión 2)
5. [ ] Verificar output de E9 es compatible con agentes de nutrición

**Entregable**: 
- Suite de tests de integración
- Logs de ejecución exitosa
- Documentación de casos edge

---

### 📊 FASE 5: DOCUMENTACIÓN Y LIMPIEZA (1 hora)
**Objetivo**: Documentar el nuevo sistema y limpiar código obsoleto

**Tareas**:
1. [ ] Actualizar README con nueva arquitectura
2. [ ] Crear diagramas de flujo de datos
3. [ ] Documentar estructura de `client_context`
4. [ ] Crear guía de troubleshooting
5. [ ] Eliminar código obsoleto/comentado
6. [ ] Actualizar docstrings de todos los métodos

**Entregable**: 
- Documentación completa del sistema refactorizado
- Diagramas de arquitectura
- Guía de desarrollo para futuros agentes

---

## 📊 ESTIMACIÓN DE ESFUERZO

| Fase | Descripción | Tiempo Estimado |
|------|-------------|-----------------|
| 0 | Preparación | 30 min |
| 1 | Definición de Contratos | 1-2 horas |
| 2 | Refactor Orchestrator | 1-2 horas |
| 3 | Refactor 9 Agentes | 4-6 horas |
| 4 | Integración y Validación | 2-3 horas |
| 5 | Documentación | 1 hora |
| **TOTAL** | **10-14 horas** |

---

## ⚠️ RIESGOS Y CONSIDERACIONES

### Riesgos Técnicos
1. **Tamaño del contexto**: El objeto `client_context` completo puede ser grande para el LLM
   - **Mitigación**: Usar GPT-4o que soporta 128k tokens de contexto
2. **Compatibilidad con nutrición**: E9 debe generar output compatible con N0-N8
   - **Mitigación**: Validar estructura de `bridge_for_nutrition` antes de continuar
3. **Tiempo de ejecución**: Pasar objeto completo entre agentes puede ser lento
   - **Mitigación**: Medir performance y optimizar si es necesario

### Decisiones Críticas Pendientes
1. **¿Cómo manejamos cuestionarios muy largos en `raw_inputs`?**
   - Opción A: Incluir texto completo
   - Opción B: Incluir solo campos extraídos/estructurados
2. **¿Validación estricta o permisiva?**
   - Opción A: Error si falta cualquier campo
   - Opción B: Warning y continuar
3. **¿Versionado de contracts?**
   - ¿Cómo manejamos cambios futuros en la estructura?

---

## 🎯 CRITERIOS DE ÉXITO

El refactor será considerado exitoso cuando:

1. ✅ Todos los agentes E1-E9 reciben y devuelven `client_context`
2. ✅ Cada agente modifica SOLO su campo asignado
3. ✅ No hay pérdida de información entre agentes
4. ✅ Tests de integración pasan con cuestionarios reales
5. ✅ E9 genera output compatible con N0
6. ✅ El sistema es más fácil de debuggear y mantener
7. ✅ La documentación está actualizada

---

## 📝 PRÓXIMOS PASOS

**ANTES DE EMPEZAR LA IMPLEMENTACIÓN, NECESITO TU APROBACIÓN SOBRE**:

1. ¿Estás de acuerdo con esta hoja de ruta por fases?
2. ¿Quieres que proceda con todas las fases o prefieres verlas una por una?
3. ¿Hay alguna decisión crítica que necesitas tomar antes de que empiece?
4. ¿Prefieres algún orden diferente en las fases?

**ESPERANDO TU CONFIRMACIÓN PARA PROCEDER** 🚦
