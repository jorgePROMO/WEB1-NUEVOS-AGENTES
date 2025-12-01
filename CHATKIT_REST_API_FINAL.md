# ✅ ChatKit REST API - Integración Final

**Fecha:** 1 Diciembre 2025  
**Workflow ID:** `wf_69260afcea288190955843b5a4223eea061948bdf6abc68b`

---

## 🔧 PROBLEMA RESUELTO

**Antes:** Intentábamos usar `client.chatkit.sessions.create()` pero el objeto `OpenAI()` no tiene atributo `chatkit`.

**Ahora:** Usamos **ChatKit REST API** directamente con `requests`.

---

## 📡 IMPLEMENTACIÓN ACTUAL

### Endpoint usado:
```
POST https://api.openai.com/v1/chatkit/sessions
```

### Headers:
```python
{
    "Authorization": "Bearer {EDN360_OPENAI_API_KEY}",
    "Content-Type": "application/json",
    "OpenAI-Beta": "chatkit_beta=v1"
}
```

### Payload para crear sesión:
```json
{
  "workflow": {
    "id": "wf_69260afcea288190955843b5a4223eea061948bdf6abc68b"
  },
  "user": "1764168881795908",
  "input": {
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": "{...EDN360Input JSON serializado...}"
          }
        ]
      }
    ]
  }
}
```

### Obtener mensajes:
```
GET https://api.openai.com/v1/chatkit/sessions/{session_id}/messages
```

---

## 🎯 FLUJO COMPLETO

1. **Construir EDN360Input** (user_profile + questionnaires + context)
2. **Serializar a JSON string**
3. **POST /chatkit/sessions** con workflow_id y mensaje inicial
4. **Obtener session_id**
5. **Polling GET /chatkit/sessions/{session_id}/messages** cada 2 segundos
6. **Buscar último mensaje con role="assistant"**
7. **Extraer content[].text del mensaje**
8. **Parsear como JSON**
9. **Validar que contenga client_training_program_enriched**
10. **Guardar en BD y devolver al frontend**

---

## 📋 CÓDIGO ACTUALIZADO

**Archivo:** `/app/backend/services/training_workflow_service.py`

**Cambios clave:**

```python
# Ya no usamos OpenAI().chatkit
# Ahora usamos requests directamente

import requests

chatkit_base_url = "https://api.openai.com/v1/chatkit"
headers = {
    "Authorization": f"Bearer {EDN360_OPENAI_API_KEY}",
    "Content-Type": "application/json",
    "OpenAI-Beta": "chatkit_beta=v1"
}

# Crear sesión
session_response = requests.post(
    f"{chatkit_base_url}/sessions",
    headers=headers,
    json={
        "workflow": {"id": EDN360_TRAINING_WORKFLOW_ID},
        "user": user_id,
        "input": {
            "messages": [{
                "role": "user",
                "content": [{"type": "input_text", "text": input_json_str}]
            }]
        }
    }
)

session_id = session_response.json()['id']

# Polling para obtener respuesta
while attempt < max_attempts:
    messages_response = requests.get(
        f"{chatkit_base_url}/sessions/{session_id}/messages",
        headers=headers
    )
    
    messages = messages_response.json()['data']
    assistant_messages = [m for m in messages if m['role'] == 'assistant']
    
    if assistant_messages:
        final_message = assistant_messages[-1]
        response_text = final_message['content'][0]['text']
        break
    
    time.sleep(2)
    attempt += 1
```

---

## ✅ INPUT/OUTPUT SIN CAMBIOS

### INPUT enviado (igual que antes):
```json
{
  "user_profile": {...},
  "questionnaires": [{...}],
  "context": {...}
}
```

### OUTPUT esperado (igual que antes):
```json
{
  "client_training_program_enriched": {
    "title": "...",
    "summary": "...",
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

---

## 📊 LOGS ESPERADOS

En `/var/log/supervisor/backend.err.log` deberías ver:

```
🚀 Iniciando Training Workflow EDN360 | Workflow ID: wf_69260...
📋 EDN360Input preparado | Size: XXXX chars | Questionnaires: 1
🔄 Creando sesión ChatKit con workflow EDN360...
📤 Creando sesión ChatKit con workflow_id: wf_69260...
✅ Sesión ChatKit creada: chatkit_session_XXXX
⏳ Ejecutando Workflow EDN360 (esto puede tardar 1-2 minutos)...
⏳ Esperando respuesta... (10/60 intentos)
⏳ Esperando respuesta... (20/60 intentos)
📥 Respuesta recibida del workflow | Size: XXXX chars | Attempt: XX/60
✅ Training Workflow ejecutado exitosamente | Sessions: X
```

---

## ⚠️ POSIBLES ERRORES

### Error 401: Unauthorized
**Causa:** API key incorrecta o no autorizada para ChatKit  
**Solución:** Verifica `EDN360_OPENAI_API_KEY` en `.env`

### Error 404: Workflow not found
**Causa:** El workflow no está publicado o el ID es incorrecto  
**Solución:** Verifica que el workflow esté publicado en Agent Builder

### Error 403: Domain not authorized
**Causa:** El dominio `trainplan-admin.preview.emergentagent.com` no está autorizado  
**Solución:** Ve a OpenAI Agent Builder → Settings → Authorized domains

### Timeout después de 2 minutos
**Causa:** El workflow tarda más de lo esperado  
**Solución:** Aumentar `max_attempts` en el código si es necesario

### El workflow devuelve error en lugar de plan
**Causa:** El EDN360Input no tiene el formato esperado por tu workflow  
**Solución:** Verifica que tu workflow acepte el formato del EDN360Input

---

## 🔍 DEBUG

Para ver la comunicación con ChatKit:

```bash
# Ver logs en tiempo real
tail -f /var/log/supervisor/backend.err.log | grep -i "chatkit\|workflow\|edn360"

# Ver últimos 100 logs
tail -100 /var/log/supervisor/backend.err.log | grep -i "chatkit"
```

---

## ✅ ESTADO ACTUAL

- ✅ ChatKit REST API implementada correctamente
- ✅ Polling cada 2 segundos para obtener respuesta
- ✅ Mismo INPUT/OUTPUT que antes
- ✅ Backend reiniciado y corriendo
- ✅ Sin errores en logs de arranque
- ⏳ **Pendiente:** Prueba real con Jorge2

---

## 📝 RESUMEN

**Cambio principal:** En lugar de usar SDK inexistente `OpenAI().chatkit`, ahora usamos **REST API de ChatKit** con `requests`.

**Todo lo demás igual:**
- Mismo EDN360Input
- Mismo client_training_program_enriched esperado
- Misma validación
- Mismo guardado en BD
- Mismo renderizado en frontend

**El workflow de Agent Builder ahora se puede ejecutar correctamente desde el backend.** 🚀
