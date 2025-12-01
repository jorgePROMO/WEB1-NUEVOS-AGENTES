# ✅ Fix: Serialización de Datetime

**Fecha:** 1 Diciembre 2025  
**Problema:** `TypeError: Object of type datetime is not JSON serializable`

---

## 🔴 PROBLEMA

El backend Python intentaba enviar objetos `datetime` al microservicio Node.js usando `json=payload` en `requests.post()`, pero Python no puede serializar automáticamente objetos datetime a JSON.

**Error:**
```python
TypeError: Object of type datetime is not JSON serializable
```

---

## ✅ SOLUCIÓN APLICADA

**Archivo:** `/app/backend/services/training_workflow_service.py`

**Cambio:**

### ANTES (incorrecto):
```python
workflow_response_raw = requests.post(
    EDN360_WORKFLOW_SERVICE_URL,
    json=edn360_input,  # ❌ No puede serializar datetime
    headers={"Content-Type": "application/json"},
    timeout=120
)
```

### AHORA (correcto):
```python
# Función para serializar datetime a ISO string
def default_serializer(obj):
    """Serializa objetos datetime a ISO string"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

# Serializar payload con manejo de datetime
payload_json = json.dumps(edn360_input, default=default_serializer)

# Enviar como data (string) en lugar de json (dict)
workflow_response_raw = requests.post(
    EDN360_WORKFLOW_SERVICE_URL,
    data=payload_json,  # ✅ Ya serializado a string
    headers={"Content-Type": "application/json"},
    timeout=120
)
```

---

## 📊 CÓMO FUNCIONA

1. **`default_serializer`**: Función personalizada que convierte `datetime` a ISO string
   ```python
   datetime(2025, 12, 1, 18, 30, 0) → "2025-12-01T18:30:00"
   ```

2. **`json.dumps()`**: Serializa el dict completo usando `default=default_serializer`
   - Cuando encuentra un datetime, llama a `default_serializer`
   - Convierte el datetime a string ISO
   - Resultado: JSON string válido

3. **`data=payload_json`**: Envía el string JSON directamente
   - No `json=` (que intenta serializar de nuevo)
   - Usa `data=` con el string ya serializado

---

## 🎯 EJEMPLO

### EDN360Input antes de serializar:
```python
{
    "user_profile": {...},
    "questionnaires": [{
        "submitted_at": datetime(2025, 11, 26, 15, 3, 52)  # objeto datetime
    }],
    "context": {
        "timestamp": datetime(2025, 12, 1, 18, 30, 0)  # objeto datetime
    }
}
```

### Después de `json.dumps(edn360_input, default=default_serializer)`:
```json
{
    "user_profile": {...},
    "questionnaires": [{
        "submitted_at": "2025-11-26T15:03:52"
    }],
    "context": {
        "timestamp": "2025-12-01T18:30:00"
    }
}
```

---

## ✅ VERIFICACIÓN

Backend reiniciado correctamente:
```bash
$ sudo supervisorctl status backend
backend    RUNNING   pid 849, uptime 0:00:07
```

Sin errores en logs:
```
✅ Successfully connected to database
✅ Application startup complete
```

---

## 🧪 PRUEBA AHORA

Ahora que el problema de serialización está resuelto:

1. **Asegúrate de que el microservicio Node.js esté corriendo:**
   ```bash
   cd /app/edn360-workflow-service
   yarn start
   ```

2. **Prueba desde el admin panel:**
   - Refresca (Ctrl+R)
   - Abre Jorge2
   - Tab "Entrenamiento"
   - Click "Generar plan (EDN360)"

El backend ahora podrá enviar correctamente el EDN360Input al microservicio. 🚀
