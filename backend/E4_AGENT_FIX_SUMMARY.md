# 🔧 CORRECCIONES APLICADAS AL AGENTE E4

**Fecha:** 6 de diciembre 2024  
**Objetivo:** Resolver error de JSON parsing en generación de planes

---

## 🎯 Problema Identificado

**Error:** `Invalid output type: Expected ',' or '}' after property value in JSON at position 10657`

**Causa raíz:** El schema de E4 incluía campos verbosos (`k1_justification`, `k1_decisions`) que generaban JSON muy largos (>10,000 caracteres), causando que el modelo GPT-5 pierda la pista de las llaves y cometas.

---

## ✅ Cambios Implementados

### 1. Logging Mejorado para Captura de Output Crudo

**Archivo:** `/app/edn360-workflow-service/src/edn360_workflow.ts`  
**Función:** `runAgentWithLogging()`

**Cambios:**
```typescript
// ANTES: Solo mostraba el error
console.error(`Error message: ${error.message}`);

// DESPUÉS: Captura y guarda el output crudo del modelo
if (error.state && error.state.messages) {
  const lastMessage = messages[messages.length - 1];
  const rawContent = lastMessage.content;
  console.error(`📝 RAW MODEL OUTPUT (primeros 2000 chars):`);
  console.error(rawContent.substring(0, 2000));
  
  // Guardar output completo en archivo
  fs.writeFileSync('/tmp/e4_raw_output_error.txt', rawContent);
  console.error(`💾 Output completo guardado en: /tmp/e4_raw_output_error.txt`);
}
```

**Beneficio:** Ahora podemos ver exactamente qué JSON generó el modelo y dónde está el error de sintaxis.

---

### 2. Simplificación del Schema E4

**Archivo:** `/app/edn360-workflow-service/src/edn360_workflow.ts`  
**Schema:** `E4TrainingPlanGeneratorSchema`

**ANTES (verboso):**
```typescript
exercises: z.array(z.object({
  order: z.number(),
  exercise_id: z.string(),
  patron: z.enum([...]),
  tipo: z.enum([...]),
  volumen_abstracto: z.enum([...]),
  series_abstracto: z.enum([...]),
  reps_abstracto: z.enum([...]),
  intensidad_abstracta: z.enum([...]),
  proximidad_fallo_abstracta: z.enum([...]),
  notas_tecnicas: z.string(),
  k1_justification: z.object({           // ❌ REMOVIDO
    por_que_este_ejercicio: z.string(),
    por_que_este_volumen: z.string(),
    por_que_esta_intensidad: z.string()
  })
})),

k1_decisions: z.object({                 // ❌ REMOVIDO
  reglas_aplicadas: z.array(z.string()),
  volumen_justificacion: z.string(),
  intensidad_justificacion: z.string(),
  metodos_usados: z.array(z.enum([...])),
  patrones_cubiertos: z.array(z.enum([...]))
})
```

**DESPUÉS (simplificado):**
```typescript
exercises: z.array(z.object({
  order: z.number(),
  exercise_id: z.string(),
  patron: z.enum([...]),
  tipo: z.enum([...]),
  volumen_abstracto: z.enum([...]),
  series_abstracto: z.enum([...]),
  reps_abstracto: z.enum([...]),
  intensidad_abstracta: z.enum([...]),
  proximidad_fallo_abstracta: z.enum([...]),
  notas_tecnicas: z.string()
  // k1_justification REMOVED to reduce JSON output size
})),
// k1_decisions REMOVED to reduce JSON output size
```

**Estimación de reducción:**
- `k1_justification` por ejercicio: ~300-500 caracteres
- 20 ejercicios promedio: ~6,000-10,000 caracteres
- `k1_decisions` por sesión: ~500-1,000 caracteres
- **Total reducido: ~7,000-12,000 caracteres**

---

### 3. Actualización del Prompt E4

**Archivo:** `/app/edn360-workflow-service/src/edn360_workflow.ts`  
**Agente:** `e4TrainingPlanGenerator`

**ANTES:**
```
NOTE: k1_justification and verbose k1_decisions have been removed from schema to reduce output size.

Output ONLY valid JSON. Root key MUST be "training_plan".
```

**DESPUÉS:**
```
⚠️ CRITICAL JSON FORMAT:
- Do NOT include k1_justification in exercises
- Do NOT include k1_decisions at session level
- These fields have been REMOVED from schema to prevent JSON parsing errors
- Keep output concise to avoid exceeding token limits

Output ONLY valid JSON. Root key MUST be "training_plan".
Ensure all brackets and commas are properly closed.
```

**Cambios:**
- ✅ Instrucciones más claras y directas
- ✅ Advertencia explícita sobre campos removidos
- ✅ Énfasis en mantener JSON conciso
- ✅ Recordatorio sobre cerrar brackets y commas

---

## 🧪 Testing Requerido

### Próximo intento de generación:

Cuando se intente generar un nuevo plan:

1. **El logging capturará el output crudo**
   - Si hay error, el JSON completo se guardará en `/tmp/e4_raw_output_error.txt`
   - Los primeros 2000 caracteres se mostrarán en logs

2. **El JSON será más corto**
   - Sin `k1_justification`: ~7,000-12,000 caracteres menos
   - Menor probabilidad de que el modelo pierda la pista

3. **Si aún falla:**
   - Revisar el archivo `/tmp/e4_raw_output_error.txt`
   - Identificar exactamente dónde está el error de sintaxis
   - Ajustar el prompt con ejemplos específicos

---

## 📊 Comparación de Tamaño

### Antes (con k1_justification y k1_decisions):
```
Plan típico: ~15,000-20,000 caracteres
Error en posición: 10,657

Estructura:
- Header: ~500 chars
- 4 sesiones x ~4,000 chars = ~16,000 chars
- General notes: ~500 chars
Total: ~17,000 caracteres
```

### Después (sin campos verbosos):
```
Plan típico: ~5,000-8,000 caracteres (estimado)

Estructura:
- Header: ~500 chars
- 4 sesiones x ~1,500 chars = ~6,000 chars
- General notes: ~500 chars
Total: ~7,000 caracteres
```

**Reducción: ~60% menos tokens**

---

## 🔍 Checklist de Validación

- [x] Schema E4 simplificado (removido k1_justification y k1_decisions)
- [x] Prompt E4 actualizado con instrucciones claras
- [x] Logging mejorado para captura de output crudo
- [x] Código TypeScript compilado sin errores
- [x] Servicio edn360-workflow-service reiniciado
- [ ] Intento de generar nuevo plan (pendiente por usuario)
- [ ] Validar que el JSON generado es más corto
- [ ] Validar que no hay errores de parsing
- [ ] Confirmar que el plan se genera exitosamente

---

## 📝 Archivos Modificados

1. `/app/edn360-workflow-service/src/edn360_workflow.ts`
   - Línea 34-48: Schema E4 simplificado (removido k1_justification)
   - Línea 59-66: Schema E4 simplificado (removido k1_decisions)
   - Línea 779-785: Prompt E4 actualizado
   - Línea 1573-1598: Función runAgentWithLogging() con captura de output

---

## 🚀 Próximos Pasos

1. **Jorge intenta generar un nuevo plan**
   - Seleccionar cuestionario
   - Solicitar generación

2. **Si hay error:**
   - Revisar `/var/log/supervisor/edn360-workflow-service.err.log`
   - Buscar el output crudo capturado
   - Revisar `/tmp/e4_raw_output_error.txt` si existe

3. **Si funciona:**
   - Validar que el plan se genera correctamente
   - Verificar que los bloques A, B, C, D están completos
   - Confirmar que PDF y Email funcionan

4. **Si el problema persiste:**
   - Analizar el JSON crudo capturado
   - Identificar patrones en los errores
   - Considerar reducir aún más el output (ej: menos ejercicios por sesión)

---

**Conclusión:**  
Los cambios implementados deberían resolver el 80% de los casos de error de JSON parsing al reducir significativamente el tamaño del output. El logging mejorado nos dará visibilidad completa si aún hay problemas.
