# 🚨 ANÁLISIS DE ERROR - GENERACIÓN DE PLAN FALLIDA

**Fecha:** 6 de diciembre 2024, 19:52:28 UTC  
**Plan ID:** `3ea66f66-cfc9-4466-956f-5923a058c405`  
**User ID:** `1764168881795908`

---

## 📊 Resumen del Problema

**Status del Plan:** `error`  
**Plan Data:** `null` (no se generó nada)  
**Error Message:** `Error HTTP 500: 500 Server Error: Internal Server Error for url: http://localhost:4000/api/edn360/run-training-workflow`

---

## 🔍 Causa Raíz Identificada

### Error en E4 Agent (Training Plan Generator)

**Archivo:** `/var/log/supervisor/edn360-workflow-service.err.log`

**Error type:** `ModelBehaviorError`  
**Error message:** `Invalid output type: Expected ',' or '}' after property value in JSON at position 10657`

**Traducción:** El agente E4 (GPT-5) generó un JSON **mal formado** (sintaxis inválida).

---

## 📝 Detalles Técnicos

### Timeline del Error:
```
19:52:19 - Usuario selecciona cuestionario y solicita generación
19:52:28 - Backend inicia Training Workflow (POST a http://localhost:4000)
19:52:28 - Plan creado en DB con status "generating"
19:53:30 - Workflow service devuelve error 500 (después de ~62 segundos)
19:53:30 - Backend actualiza plan con status "error"
```

### Stack Trace del Error:
```javascript
Error: Invalid output type: Expected ',' or '}' after property value in JSON at position 10657
    at resolveTurnAfterModelResponse (.../runImplementation.js:668:23)
    at executeRun (.../run.js:280:31)
    at runAgentWithLogging (.../edn360_workflow.js:1535:24)
    at runWorkflow (.../edn360_workflow.js:1589:12)
```

**Interpretación:**
- El agente E4 estaba generando el JSON del plan de entrenamiento
- Aproximadamente en el carácter 10,657 del JSON generado, hay un error de sintaxis
- Probablemente una coma faltante o una llave mal cerrada
- El parser de JSON falló al intentar validar la salida del modelo

---

## 🔬 Análisis de Patrones

### Intentos Fallidos Recientes:
```
1. Plan ID: 3ea66f66-cfc9-4466-956f-5923a058c405 (19:52:28) - Status: error
2. Plan ID: 9ca7d5fb-50f9-456a-872a-7aad09e52696 (18:58:52) - Status: error
3. Plan ID: 9bef3f1e-18e1-4b3a-b2ce-594d15d01835 (08:13:57) - Status: error
```

**Conclusión:** Los últimos 3 intentos de generación de planes han fallado con el **mismo tipo de error**.

**Posibles causas:**
1. Cambio reciente en el prompt del agente E4
2. Respuesta inconsistente del modelo GPT-5
3. Schema de validación muy estricto
4. JSON demasiado largo/complejo que confunde al modelo

---

## 🔧 Posibles Soluciones

### 1. Revisar Prompt del Agente E4
**Archivo:** `/app/edn360-workflow-service/src/edn360_workflow.ts`

**Acciones:**
- Verificar que el prompt incluya instrucciones claras sobre formato JSON
- Agregar ejemplos de JSON válido
- Simplificar la estructura si es demasiado compleja

### 2. Agregar Validación Más Tolerante
**Opción:** Intentar reparar JSON automáticamente antes de fallar

```javascript
try {
  const plan = JSON.parse(rawOutput);
} catch (error) {
  // Intentar reparar JSON común (comas faltantes, etc.)
  const repaired = repairJSON(rawOutput);
  const plan = JSON.parse(repaired);
}
```

### 3. Reducir Complejidad del Output
**Consideración:** Si el JSON es muy largo (>10,000 caracteres), el modelo puede tener dificultad

**Opciones:**
- Dividir la generación en pasos más pequeños
- Simplificar la estructura de datos
- Usar schema más permisivo

### 4. Aumentar Temperature/Top-P
**Si el problema es variabilidad del modelo:**
- Temperature más baja = output más determinístico
- Puede ayudar a evitar errores de sintaxis

### 5. Agregar Retry Logic
**Implementar:**
```javascript
async function generatePlanWithRetry(input, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await generatePlan(input);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      logger.warn(`Retry ${i + 1}/${maxRetries} due to: ${error.message}`);
    }
  }
}
```

---

## 🧪 Testing Requerido

Para identificar la solución correcta:

1. **Capturar el JSON generado antes de fallar:**
   - Modificar el código para loggear el output crudo del modelo
   - Ver exactamente qué está generando en la posición 10,657

2. **Verificar el prompt actual:**
   - ¿Ha cambiado recientemente?
   - ¿Es demasiado complejo?

3. **Probar con diferentes parámetros:**
   - Temperature: 0.7 → 0.3
   - Max tokens: Incrementar si se está cortando

4. **Validar el Schema:**
   - ¿El schema Zod es demasiado estricto?
   - ¿Permite todos los campos que E4 genera?

---

## 📌 Próximos Pasos Inmediatos

### Paso 1: Capturar Output Crudo (CRÍTICO)
```typescript
// En edn360_workflow.ts, línea ~1535
logger.info("🔍 RAW MODEL OUTPUT:", rawModelOutput);
```

### Paso 2: Revisar Prompt de E4
```typescript
// Verificar si el prompt tiene instrucciones claras sobre JSON
// Agregar ejemplo de JSON válido si no existe
```

### Paso 3: Agregar Retry Logic
```typescript
// Implementar 2-3 reintentos automáticos antes de fallar
```

### Paso 4: Notificar al Usuario
```typescript
// En lugar de solo guardar error en DB
// Enviar notificación al admin de que la generación falló
```

---

## 🚨 Impacto Actual

**Severidad:** 🔴 CRÍTICO

**Usuarios afectados:** Todos los que intenten generar un nuevo plan

**Funcionalidad rota:**
- ✅ Plans existentes funcionan (lectura)
- ❌ Generación de nuevos planes (100% fallo)
- ✅ PDF/Email de planes existentes (funciona)

**Workaround temporal:** Ninguno disponible. Requiere fix en E4 agent.

---

## 📊 Logs Relevantes

### Backend Log (server.py)
```
2025-12-06 19:52:28 - Iniciando Training Workflow EVOLUTIVO EDN360
2025-12-06 19:53:30 - ERROR: Error HTTP 500 del workflow service
```

### Workflow Service Log (edn360-workflow-service.err.log)
```
❌ ERROR EN E4 – Training Plan Generator
Error: Invalid output type: Expected ',' or '}' after property value in JSON at position 10657
```

---

**Conclusión:**  
El problema NO está en el código de backend que acabamos de modificar para PDF/Email.  
El problema está en el **agente E4 (Node.js workflow service)** que genera JSON inválido.

**Acción requerida:**  
Revisar y corregir el prompt/schema del agente E4 en `/app/edn360-workflow-service/src/edn360_workflow.ts`
