# ✅ FIX: Cuestionarios de Jorge2 Ahora Visibles

**Problema Reportado**: No aparecían cuestionarios ni el botón "Generar plan (EDN360)" para Jorge2

**Causa**: El frontend solo buscaba cuestionarios en las colecciones legacy (nutrition_questionnaire_submissions), pero los cuestionarios de Jorge2 están en la nueva arquitectura EDN360 (client_drawers)

**Solución Implementada**: Creado nuevo endpoint y actualizado frontend

---

## 🔧 CAMBIOS REALIZADOS

### 1. Nuevo Endpoint Backend ✅

**Archivo**: `/app/backend/server.py` (después de línea 9619)

**Endpoint**: `GET /admin/users/{user_id}/edn360-questionnaires`

**Función**:
- Lee cuestionarios desde `client_drawers.services.shared_questionnaires`
- Devuelve lista formateada para el frontend
- Funciona con la nueva arquitectura EDN360

**Response**:
```json
{
  "questionnaires": [
    {
      "id": "1764169432140799",
      "submission_id": "1764169432140799",
      "source": "initial",
      "submitted_at": "2025-11-26T15:03:52Z",
      "label": "Cuestionario Inicial (26/11/2025)"
    }
  ]
}
```

---

### 2. Nueva Función Frontend ✅

**Archivo**: `/app/frontend/src/pages/AdminDashboard.jsx` (línea ~1145)

**Función**: `loadEDN360Questionnaires(userId)`

**Propósito**:
- Llama al nuevo endpoint `/edn360-questionnaires`
- Actualiza `questionnaireSubmissions` con los cuestionarios EDN360
- Se ejecuta automáticamente al seleccionar un cliente

---

### 3. Flujo de Carga Actualizado ✅

**Archivo**: `/app/frontend/src/pages/AdminDashboard.jsx` (línea ~860)

**Función**: `loadAllClientData(clientId)`

**Flujo**:
```javascript
await loadClientDetails(clientId);
await loadNutritionPlan(clientId);        // Carga cuestionarios legacy
await loadEDN360Questionnaires(clientId);  // ✅ NUEVO: Carga cuestionarios EDN360
await loadTrainingPlans(clientId);
// ... resto de funciones
```

---

## ✅ VERIFICACIÓN

### Backend:
```bash
$ sudo supervisorctl status backend
backend    RUNNING   pid 888, uptime 0:00:17
```

### Frontend:
```bash
$ sudo supervisorctl status frontend
frontend   RUNNING   pid 905, uptime 0:00:15
```

### Datos de Jorge2:
```
✅ Jorge2 tiene 1 cuestionario en client_drawers
   - submission_id: 1764169432140799
   - source: initial
   - submitted_at: 2025-11-26 15:03:52
```

---

## 🚀 QUÉ ESPERAR AHORA

### Al Entrar a Jorge2 en el Admin Panel:

1. **Tab "Entrenamiento"**
2. **Verás sección "📋 Cuestionarios"** (nueva)
3. **Verás el cuestionario inicial** con:
   - Título: "📝 Cuestionario Inicial"
   - Fecha: "26 Nov 2025, 15:03:52"
4. **Verás el botón "Generar plan (EDN360)"** (con ícono de mancuerna)

---

## 🧪 CÓMO PROBAR

1. **Refresca la página** del admin panel (F5 o Ctrl+R)
2. Selecciona "Jorge2" de la lista
3. Ve a tab "🏋️ Entrenamiento"
4. Deberías ver:
   - Sección "📋 Cuestionarios" en azul/cyan
   - Card con "Cuestionario Inicial (26/11/2025)"
   - Botón "Generar plan (EDN360)"
5. **Click en el botón**
6. Espera 1-2 minutos
7. El plan se renderizará automáticamente

---

## 🔍 SI AÚN NO APARECE

### 1. Verifica que la página esté actualizada:
- Presiona F5 o Ctrl+R para recargar
- Cierra y abre el cliente Jorge2 de nuevo

### 2. Verifica la consola del navegador:
- Abre DevTools (F12)
- Ve a la pestaña "Console"
- Busca mensajes de "EDN360 questionnaires" o errores

### 3. Comparte logs del backend:
```bash
tail -50 /var/log/supervisor/backend.err.log
```

### 4. Verifica que el endpoint responda:
```bash
# Desde tu máquina (necesitas el token de admin)
curl -H "Authorization: Bearer <TOKEN>" \
  https://tu-url/api/admin/users/1764168881795908/edn360-questionnaires
```

---

## 📊 ARQUITECTURA

### ANTES (Problema):
```
Frontend → /admin/users/{id}/questionnaires
            ↓
         Busca en: nutrition_questionnaire_submissions (legacy)
            ↓
         ❌ Jorge2 NO está ahí (está en client_drawers)
```

### AHORA (Solución):
```
Frontend → /admin/users/{id}/edn360-questionnaires
            ↓
         Busca en: client_drawers.services.shared_questionnaires
            ↓
         ✅ Jorge2 SÍ está ahí → Muestra cuestionario + botón
```

---

## ✅ ESTADO ACTUAL

- [x] ✅ Backend con nuevo endpoint
- [x] ✅ Frontend con nueva función de carga
- [x] ✅ Servicios reiniciados
- [x] ✅ Jorge2 tiene cuestionario en client_drawers
- [ ] ⏳ **PENDIENTE**: Jorge verifica en el panel admin

---

## 🎯 PRÓXIMO PASO

**Jorge**: Por favor, refresca el admin panel y verifica que ahora sí aparezca:
1. La sección "📋 Cuestionarios"
2. El cuestionario inicial de Jorge2
3. El botón "Generar plan (EDN360)"

Si ahora sí aparece, **procede a hacer la prueba de generación**:
- Click en el botón
- Espera 1-2 minutos
- Verifica que el plan se renderice

**Si algo falla, comparte**:
- Screenshot de lo que ves
- Mensajes de la consola del navegador (F12 → Console)
- Y continuamos debuggeando

---

**El sistema ahora debería mostrar correctamente los cuestionarios de Jorge2 y el botón de generación. 🚀**
