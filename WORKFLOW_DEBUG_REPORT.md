# 🔍 REPORTE DE DEBUG - Workflow EDN360

**Fecha:** 2 de Diciembre, 2025  
**Status:** PROBLEMA IDENTIFICADO ✅

---

## 📊 PROBLEMA IDENTIFICADO

### **Agente que falla:** E7 – Training Plan Assembler

### **Error exacto:**
```
Invalid output type: Unterminated string in JSON at position 9018
```

### **Causa raíz:**
El agente E7 tiene configurado `maxTokens: 2048`, lo cual es **insuficiente** para generar un plan de entrenamiento completo.

**Análisis:**
- Un plan de entrenamiento típico con 4 sesiones, múltiples bloques y ejercicios puede fácilmente superar los 2048 tokens
- El JSON se corta exactamente en la posición 9018 caracteres (~2000 tokens aprox)
- Esto deja strings sin cerrar, causando el error de JSON malformado

---

## 🔧 SOLUCIÓN PROPUESTA

### **Opción 1: Aumentar maxTokens en E7** (RECOMENDADO)

**Cambiar en `/app/edn360-workflow-service/src/edn360_workflow.ts`:**

```typescript
// Línea 1425 (E7)
modelSettings: {
  temperature: 1,
  topP: 1,
  maxTokens: 4096,  // ⬅️ CAMBIAR DE 2048 a 4096
  store: true
}
```

**Y también en E7.5:**

```typescript
// Línea ~1616 (E7.5)
modelSettings: {
  temperature: 1,
  topP: 1,
  maxTokens: 4096,  // ⬅️ CAMBIAR DE 2048 a 4096
  store: true
}
```

**Justificación:**
- 4096 tokens permite ~8000-10000 caracteres de JSON
- Suficiente para planes de 4-6 sesiones con múltiples ejercicios
- No afecta el costo significativamente si el contenido real es menor

---

### **Opción 2: Optimizar los prompts para generar menos texto**

**Instrucciones más restrictivas:**
- Limitar `session_notes` a máximo 2 items por sesión (actualmente 3)
- Limitar `general_notes` a máximo 3 items (actualmente 5)
- Acortar las descripciones de `title` y `summary`

**Inconveniente:**
- Reduce la calidad y riqueza de la información del plan
- No es la solución ideal

---

### **Opción 3: Dividir E7 en dos agentes**

**E7a:** Genera estructura básica (sessions, blocks, ids)  
**E7b:** Completa con notas y detalles

**Inconveniente:**
- Mayor complejidad
- Más tiempo de ejecución
- Más llamadas a OpenAI = más costo

---

## ✅ RECOMENDACIÓN FINAL

**Aumentar `maxTokens` de 2048 a 4096 en E7 y E7.5**

**Pasos:**
1. Editar `/app/edn360-workflow-service/src/edn360_workflow.ts`
2. Cambiar `maxTokens: 2048` → `maxTokens: 4096` en líneas 1425 y ~1616
3. Recompilar: `cd /app/edn360-workflow-service && yarn build`
4. Reiniciar servicio: `supervisorctl restart edn360-workflow-service`
5. Probar workflow completo

---

## 📝 LOGS CAPTURADOS

### **Ejecución del workflow:**
```
🚀 Ejecutando E1 – Analizador de Perfil...
✅ E1 – Analizador de Perfil completado

🚀 Ejecutando E2 – Parse Questionnaire...
✅ E2 – Parse Questionnaire completado

🚀 Ejecutando E7 – Training Plan Assembler...
❌ ERROR: Unterminated string in JSON at position 9018
```

### **Error stack trace:**
```
Error: Invalid output type: Unterminated string in JSON at position 9018
    at resolveTurnAfterModelResponse
    at runAgentWithLogging
```

---

## 🎯 PRÓXIMOS PASOS

1. **Aplicar fix de maxTokens** (5 minutos)
2. **Probar workflow completo** con input real
3. **Verificar que el JSON generado es válido**
4. **Comparar con estructura del mock** para confirmar compatibilidad

---

## 📊 ESTADO ACTUAL DEL SISTEMA

✅ Microservicio Node.js corriendo  
✅ Endpoints mock funcionando  
✅ Backend Python persistiendo correctamente  
✅ Estructura `sessions[].blocks[].exercises[]` validada  
⚠️ Workflow real bloqueado por límite de tokens en E7  
🔄 Fix identificado y listo para aplicar  
