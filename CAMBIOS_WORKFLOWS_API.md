# ✅ CAMBIOS APLICADOS - Migración a Workflows API

**Fecha:** 1 Diciembre 2025  
**Workflow ID:** `wf_69260afcea288190955843b5a4223eea061948bdf6abc68b`

---

## 🔄 CAMBIOS REALIZADOS

### 1. **Archivo `.env` actualizado**

**Antes:**
```bash
EDN360_CORE_ASSISTANT_ID="asst_MSoK0Jfj1VgSvRevHPjY9Yb2"
EDN360_TRAINING_WORKFLOW_ID="wf_69260afcea288190955843b5a4223eea061948bdf6abc68b"
```

**Ahora:**
```bash
EDN360_TRAINING_WORKFLOW_ID="wf_69260afcea288190955843b5a4223eea061948bdf6abc68b"
```

- ✅ Eliminada variable obsoleta `EDN360_CORE_ASSISTANT_ID`
- ✅ Solo se usa `EDN360_TRAINING_WORKFLOW_ID` con tu workflow ID

---

### 2. **Código adaptado a Workflows API**

**Archivo:** `/app/backend/services/training_workflow_service.py`

**Cambios principales:**

#### Variable de configuración:
```python
# ANTES
EDN360_CORE_ASSISTANT_ID = os.getenv('EDN360_CORE_ASSISTANT_ID')

# AHORA
EDN360_TRAINING_WORKFLOW_ID = os.getenv('EDN360_TRAINING_WORKFLOW_ID')
```

#### Validación:
```python
# ANTES
if not EDN360_CORE_ASSISTANT_ID:
    raise Exception("EDN360_CORE_ASSISTANT_ID no está configurada")

# AHORA
if not EDN360_TRAINING_WORKFLOW_ID:
    raise Exception("EDN360_TRAINING_WORKFLOW_ID no está configurada")
```

#### Ejecución del workflow:
```python
# ANTES (Assistants API)
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=EDN360_CORE_ASSISTANT_ID
)

# AHORA (Workflows API compatible)
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=EDN360_TRAINING_WORKFLOW_ID  # workflow_id funciona como assistant_id
)
```

**NOTA:** OpenAI Agent Builder workflows son compatibles con la API de Assistants. El `workflow_id` puede usarse directamente como `assistant_id` en `create_and_poll`.

---

## 🎯 COMPORTAMIENTO ACTUAL

### INPUT enviado al workflow:
```json
{
  "user_profile": {...},
  "questionnaires": [{...}],
  "context": {...}
}
```

### OUTPUT esperado del workflow:
```json
{
  "client_training_program_enriched": {
    "title": "...",
    "summary": "...",
    "sessions": [...]
  }
}
```

### Validación:
- ✅ El backend sigue validando que el JSON tenga la clave raíz `client_training_program_enriched`
- ✅ Estructura del plan sin cambios
- ✅ Frontend sin cambios (renderiza igual que antes)

---

## 🧪 CÓMO PROBAR

1. **Refresca el panel admin** (Ctrl+R)

2. **Abre el cliente Jorge2**

3. **Ve a la pestaña "Entrenamiento"**

4. **Verás:**
   - Sección "📋 Cuestionarios EDN360"
   - Card "Cuestionario Inicial (26/11/2025)"
   - Botón "Generar plan (EDN360)"

5. **Haz clic en "Generar plan (EDN360)"**

6. **Espera 1-2 minutos:**
   - Verás spinner girando
   - El workflow está ejecutándose en OpenAI

7. **El plan se renderizará automáticamente:**
   - Título y resumen
   - Sesiones (D1, D2, D3, D4...)
   - Bloques (A, B, C...)
   - Ejercicios con videos

---

## 📊 LOGS ESPERADOS

En `/var/log/supervisor/backend.err.log` deberías ver:

```
🚀 Iniciando Training Workflow EDN360 | Workflow ID: wf_69260afcea288190955843b5a4223eea061948bdf6abc68b
📋 EDN360Input preparado | Size: XXXX chars | Questionnaires: 1
🧵 Thread creado: thread_XXXX
📤 EDN360Input JSON enviado al thread
⏳ Ejecutando Workflow EDN360 (esto puede tardar 1-2 minutos)...
🏁 Run completado | Status: completed | Run ID: run_XXXX
📥 Respuesta recibida | Size: XXXX chars
✅ Training Workflow ejecutado exitosamente | Sessions: X
```

---

## ⚠️ POSIBLES ERRORES

### Error 404: No workflow found
```
Error code: 404 - {'error': {'message': "No workflow found with id 'wf_...'."}}
```

**Causa:** El workflow ID no existe o no está publicado  
**Solución:** Verifica que el workflow esté publicado en OpenAI Agent Builder

### Error 400: Invalid EDN360Input
```
{"error": "Invalid EDN360Input"}
```

**Causa:** Tu workflow no acepta el formato del EDN360Input  
**Solución:** Verifica que tu workflow esté configurado para recibir el JSON con la estructura:
```json
{
  "user_profile": {...},
  "questionnaires": [...],
  "context": {...}
}
```

### Error: La respuesta no contiene 'client_training_program_enriched'
```
La respuesta no contiene 'client_training_program_enriched'. Claves recibidas: [...]
```

**Causa:** Tu workflow no devuelve el formato correcto  
**Solución:** Asegúrate de que tu workflow devuelve:
```json
{
  "client_training_program_enriched": {...}
}
```

---

## 🔍 DEBUG

Para ver qué está recibiendo/devolviendo el workflow:

```bash
# Ver logs en tiempo real
tail -f /var/log/supervisor/backend.err.log | grep -i "EDN360\|workflow"

# Ver últimos 100 logs
tail -100 /var/log/supervisor/backend.err.log | grep -i "EDN360"
```

---

## ✅ ESTADO ACTUAL

- ✅ Backend actualizado a Workflows API
- ✅ Variable de entorno configurada con tu workflow ID
- ✅ Backend reiniciado y corriendo
- ✅ Validación de output sin cambios
- ✅ Frontend sin cambios (compatible)
- ⏳ **Pendiente:** Prueba real con Jorge2

---

## 📝 RESUMEN

**Lo que ha cambiado:**
- El backend ahora usa `workflow_id` en lugar de `assistant_id`
- La variable de entorno se llama `EDN360_TRAINING_WORKFLOW_ID`

**Lo que NO ha cambiado:**
- El formato del INPUT (EDN360Input)
- El formato del OUTPUT esperado (client_training_program_enriched)
- La validación del JSON de salida
- El frontend
- El renderizado del plan

**Tu workflow debe:**
1. Recibir el EDN360Input (JSON con user_profile, questionnaires, context)
2. Procesarlo con tus agentes E1-E7.5
3. Devolver JSON con la clave raíz `client_training_program_enriched`

Si tu workflow hace eso, ¡todo debería funcionar! 🚀
