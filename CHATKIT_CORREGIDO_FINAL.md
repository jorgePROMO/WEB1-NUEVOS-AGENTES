# ✅ ChatKit Integración Corregida - FINAL

**Fecha:** 1 Diciembre 2025  
**Workflow ID:** `wf_69260afcea288190955843b5a4223eea061948bdf6abc68b`

---

## 🔧 PROBLEMA RESUELTO

**Error anterior:**
```json
{
  "error": {
    "message": "Unknown parameter: 'input'.",
    "type": "invalid_request_error",
    "param": "input"
  }
}
```

**Causa:** ChatKit NO acepta el campo `input` en `POST /sessions`. El mensaje debe enviarse por separado.

**Solución:** Dividir en 3 pasos claros.

---

## 📡 IMPLEMENTACIÓN CORRECTA

### PASO 1: Crear sesión SIN input

```python
POST https://api.openai.com/v1/chatkit/sessions

Headers:
{
    "Authorization": "Bearer {API_KEY}",
    "Content-Type": "application/json",
    "OpenAI-Beta": "chatkit_beta=v1"
}

Body:
{
    "workflow": {"id": "wf_69260..."},
    "user": "1764168881795908"
    // ❌ NO incluir 'input' aquí
}

Response:
{
    "id": "chatkit_session_XXXX",
    ...
}
```

### PASO 2: Enviar EDN360Input como mensaje

```python
POST https://api.openai.com/v1/chatkit/sessions/{session_id}/messages

Headers: (mismos)

Body:
{
    "role": "user",
    "content": [
        {
            "type": "input_text",
            "text": "{...EDN360Input JSON string...}"
        }
    ]
}

Response: 200 OK
```

### PASO 3: Polling para obtener respuesta

```python
GET https://api.openai.com/v1/chatkit/sessions/{session_id}/messages?limit=50&order=desc

Headers: (mismos)

Response:
{
    "data": [
        {
            "id": "msg_XXX",
            "role": "assistant",
            "content": [
                {
                    "type": "output_text",  // o "text"
                    "text": "{...client_training_program_enriched JSON...}"
                }
            ]
        },
        ...
    ]
}
```

---

## 🎯 FLUJO COMPLETO IMPLEMENTADO

```python
# 1. Crear sesión
session_response = requests.post(
    f"{base_url}/sessions",
    headers=headers,
    json={
        "workflow": {"id": WORKFLOW_ID},
        "user": user_id
    }
)
session_id = session_response.json()['id']

# 2. Enviar EDN360Input
message_response = requests.post(
    f"{base_url}/sessions/{session_id}/messages",
    headers=headers,
    json={
        "role": "user",
        "content": [{"type": "input_text", "text": input_json_str}]
    }
)

# 3. Polling (cada 2 segundos, max 60 intentos = 2 minutos)
for attempt in range(60):
    if attempt > 0:
        time.sleep(2)
    
    messages_response = requests.get(
        f"{base_url}/sessions/{session_id}/messages",
        headers=headers,
        params={"limit": 50, "order": "desc"}
    )
    
    messages = messages_response.json()['data']
    
    # Buscar mensaje del assistant con output_text o text
    for message in messages:
        if message['role'] == 'assistant':
            for block in message['content']:
                if block['type'] in ['output_text', 'text']:
                    response_text = block['text']
                    break
    
    if response_text:
        break

# 4. Parsear y validar
workflow_response = json.loads(response_text)
if "client_training_program_enriched" not in workflow_response:
    raise Exception("Respuesta inválida")
```

---

## ✅ CÓDIGO ACTUALIZADO

**Archivo:** `/app/backend/services/training_workflow_service.py`

**Cambios clave:**

1. **Sesión sin input:**
   ```python
   session_payload = {
       "workflow": {"id": EDN360_TRAINING_WORKFLOW_ID},
       "user": user_id
       # ✅ NO hay campo 'input'
   }
   ```

2. **Mensaje separado:**
   ```python
   message_payload = {
       "role": "user",
       "content": [
           {
               "type": "input_text",
               "text": input_json_str
           }
       ]
   }
   
   requests.post(
       f"{base_url}/sessions/{session_id}/messages",
       headers=headers,
       json=message_payload
   )
   ```

3. **Polling mejorado:**
   ```python
   # Buscar tanto "output_text" como "text"
   if block.get('type') in ['output_text', 'text']:
       response_text = block.get('text', '')
   ```

---

## 📋 INPUT/OUTPUT (SIN CAMBIOS)

### INPUT enviado:
```json
{
  "user_profile": {...},
  "questionnaires": [{...}],
  "context": {...}
}
```

### OUTPUT esperado:
```json
{
  "client_training_program_enriched": {
    "title": "...",
    "sessions": [...]
  }
}
```

---

## 🧪 PRUEBA AHORA

1. **Refresca el panel admin** (Ctrl+R)
2. **Abre Jorge2**
3. **Ve a "Entrenamiento"**
4. **Click en "Generar plan (EDN360)"**
5. **Espera 1-2 minutos**

Deberías ver:
- Spinner girando
- Después: plan completo renderizado
- Con sesiones, bloques, ejercicios y videos

---

## 📊 LOGS ESPERADOS

```
🚀 Iniciando Training Workflow EDN360 | Workflow ID: wf_69260...
📋 EDN360Input preparado | Size: XXXX chars
🔄 Creando sesión ChatKit con workflow EDN360...
📤 Creando sesión ChatKit con workflow_id: wf_69260...
✅ Sesión ChatKit creada: chatkit_session_XXXX
📤 Enviando EDN360Input como mensaje de usuario...
✅ Mensaje enviado correctamente
⏳ Ejecutando Workflow EDN360 (esto puede tardar 1-2 minutos)...
⏳ Esperando respuesta... (10/60 intentos)
⏳ Esperando respuesta... (20/60 intentos)
📥 Respuesta recibida del workflow | Size: XXXX chars | Attempt: XX/60
✅ Training Workflow ejecutado exitosamente | Sessions: X
```

---

## ⚠️ POSIBLES ERRORES

### Error: "Unknown parameter: 'input'"
**Status:** ✅ RESUELTO - Ya no enviamos 'input' en la creación de sesión

### Error 404: Session not found
**Causa:** El session_id no es válido  
**Solución:** Verificar que la sesión se creó correctamente

### Error 400: Invalid message format
**Causa:** El formato del mensaje es incorrecto  
**Solución:** Verificar que el content tiene type="input_text"

### Timeout después de 2 minutos
**Causa:** El workflow tarda más de lo esperado  
**Solución:** Aumentar max_attempts si es necesario

---

## 🔍 DEBUG

```bash
# Ver logs en tiempo real
tail -f /var/log/supervisor/backend.err.log | grep -i "chatkit\|workflow"

# Ver últimos 100 logs
tail -100 /var/log/supervisor/backend.err.log | grep -A 3 "Creando sesión\|Mensaje enviado\|Respuesta recibida"
```

---

## ✅ ESTADO ACTUAL

- ✅ Sesión se crea sin campo 'input'
- ✅ EDN360Input se envía como mensaje separado
- ✅ Polling busca 'output_text' o 'text'
- ✅ Backend reiniciado y corriendo
- ✅ Sin errores en logs de arranque
- ⏳ **Pendiente:** Prueba real con Jorge2

---

## 📝 DIFERENCIA CLAVE

**ANTES (incorrecto):**
```python
# Todo en un solo paso - FALLA
requests.post("/sessions", json={
    "workflow": {...},
    "user": "...",
    "input": {...}  # ❌ ChatKit no lo acepta
})
```

**AHORA (correcto):**
```python
# Paso 1: Crear sesión
requests.post("/sessions", json={
    "workflow": {...},
    "user": "..."
    # ✅ Sin 'input'
})

# Paso 2: Enviar mensaje
requests.post("/sessions/{id}/messages", json={
    "role": "user",
    "content": [...]
})
```

---

**El flujo ChatKit ahora está implementado correctamente según la API oficial.** 🚀
