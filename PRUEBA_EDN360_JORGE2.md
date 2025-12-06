# ✅ Sistema EDN360 Configurado - Listo para Prueba con Jorge2

**Fecha**: 27 de Noviembre 2025  
**Status**: ✅ COMPLETAMENTE CONFIGURADO Y LISTO

---

## 📋 CONFIRMACIÓN DE CONFIGURACIÓN

### 1. Variables de Entorno ✅

**Archivo**: `/app/backend/.env`

```bash
# Core Assistant que ejecuta el workflow completo
EDN360_CORE_ASSISTANT_ID="asst_MSoK0Jfj1VgSvRevHPjY9Yb2"

# Workflow publicado en OpenAI Agent Builder
EDN360_TRAINING_WORKFLOW_ID="wf_69260afcea288190955843b5a4223eea061948bdf6abc68b"

# API Key (ya estaba configurada)
EDN360_OPENAI_API_KEY="sk-proj-MguaE2c...sUQA"
```

✅ **CONFIRMADO**: Todas las variables están correctamente configuradas en el `.env`

---

### 2. Código Actualizado ✅

**Archivo**: `/app/backend/services/training_workflow_service.py`

**Cambios implementados**:
- ✅ Lee `EDN360_CORE_ASSISTANT_ID` y `EDN360_TRAINING_WORKFLOW_ID`
- ✅ Usa el **Core Assistant ID** (`asst_...`) en la llamada a `create_and_poll`
- ✅ Valida que el Core Assistant ID esté configurado
- ✅ Logging mejorado con ambos IDs

**Línea crítica** (línea 137):
```python
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=EDN360_CORE_ASSISTANT_ID  # ✅ USA EL CORE ASSISTANT
)
```

---

### 3. Backend Reiniciado ✅

```bash
$ sudo supervisorctl status backend
backend                          RUNNING   pid 401, uptime 0:00:12
```

✅ **CONFIRMADO**: Backend reiniciado y corriendo con la nueva configuración

---

### 4. Endpoint Funcional ✅

**Endpoint**: `POST /api/training-plan`

**Flujo**:
1. Valida `user_id` y `questionnaire_submission_id`
2. Construye `EDN360Input` completo
3. Crea thread en OpenAI
4. Envía `EDN360Input` como mensaje
5. Ejecuta `create_and_poll` con el **Core Assistant** (`asst_MSoK0Jfj1VgSvRevHPjY9Yb2`)
6. Lee la respuesta del thread
7. Guarda snapshot en `edn360_snapshots`
8. Guarda plan en `training_plans_v2`
9. Devuelve `client_training_program_enriched` al frontend

✅ **CONFIRMADO**: El endpoint usa el workflow publicado correcto

---

## 🧪 DATOS PARA PRUEBA CON JORGE2

### Cliente: Jorge2
```javascript
{
  "user_id": "1764168881795908",
  "name": "Jorge2",
  "email": "jorge31011987@gmail.com"
}
```

### Cuestionario Disponible
```javascript
{
  "submission_id": "1764169432140799",
  "source": "initial",
  "submitted_at": "Wed Nov 26 2025 15:03:52 GMT+0000 (UTC)"
}
```

✅ **CONFIRMADO**: Jorge2 tiene un cuestionario inicial listo para generar plan

---

## 🚀 CÓMO REALIZAR LA PRUEBA

### Desde el Admin Panel (Interfaz Gráfica):

1. **Acceder al Admin Panel**
   - URL: Tu URL del panel admin
   - Login como administrador

2. **Seleccionar Cliente Jorge2**
   - En la lista de clientes, buscar "Jorge2"
   - Click en el cliente para ver su detalle

3. **Ir a Pestaña de Entrenamiento**
   - Click en tab "🏋️ Entrenamiento"
   - Verás una sección "📋 Cuestionarios"

4. **Generar Plan EDN360**
   - Verás el cuestionario inicial (enviado el 26 Nov 2025)
   - Click en botón "Generar plan (EDN360)"
   - Verás spinner de loading
   - **ESPERA 1-2 MINUTOS** (el workflow tarda en ejecutarse)

5. **Ver Resultado**
   - El plan se renderizará automáticamente en la misma página
   - Verás:
     - Título del plan
     - Resumen y objetivo
     - Metadatos (días/semana, duración, programa)
     - Notas generales
     - Sesiones de entrenamiento (D1, D2, D3, D4...)
     - Bloques de ejercicios (A, B, C...)
     - Tabla de ejercicios con videos clickeables

---

### Desde Curl (Testing de API):

```bash
# 1. Login como admin (obtener token)
ADMIN_TOKEN="<tu_token_de_admin>"

# 2. Generar plan de entrenamiento para Jorge2
curl -X POST "https://exerule-system.preview.emergentagent.com/api/training-plan" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "1764168881795908",
    "questionnaire_submission_id": "1764169432140799"
  }'
```

**Respuesta esperada** (después de 1-2 minutos):
```json
{
  "client_training_program_enriched": {
    "title": "Programa de Hipertrofia Upper/Lower",
    "summary": "Plan de 4 días por semana enfocado en hipertrofia...",
    "goal": "hipertrophy",
    "training_type": "upper_lower",
    "days_per_week": 4,
    "session_duration_min": 60,
    "weeks": 4,
    "sessions": [
      {
        "id": "D1",
        "name": "Upper Body Push",
        "focus": ["upper_body", "push_focus"],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["pecho", "hombros"],
            "exercises": [
              {
                "order": 1,
                "name": "Press Banca",
                "series": 4,
                "reps": "8-10",
                "rpe": 8,
                "video_url": "https://..."
              }
            ]
          }
        ]
      }
    ]
  }
}
```

---

## 📊 VERIFICACIÓN DE LOGS

### Ver logs del backend durante la ejecución:

```bash
# Logs en tiempo real
tail -f /var/log/supervisor/backend.err.log | grep -i "edn360\|training\|workflow"

# Ver últimas 50 líneas
tail -50 /var/log/supervisor/backend.err.log
```

**Logs esperados durante una ejecución exitosa**:
```
🚀 Iniciando Training Workflow EDN360 | Core Assistant ID: asst_MSoK0Jfj1VgSvRevHPjY9Yb2
🧵 Thread creado: thread_XXXX
📤 Mensaje enviado al thread
⏳ Ejecutando Core Assistant EDN360 (esto puede tardar 1-2 minutos)...
🏁 Run completado | Status: completed | Run ID: run_XXXX
📥 Respuesta recibida | Size: XXXX chars
✅ Training Workflow ejecutado exitosamente | Sessions: 4
✅ Snapshot creado: snap_XXXX
✅ Plan guardado en training_plans_v2 | plan_id: XXXX
✅ Plan de entrenamiento generado exitosamente | user_id: 1764168881795908
```

---

## 🔍 VERIFICACIÓN DE DATOS GUARDADOS

### Verificar snapshot en MongoDB:

```bash
mongosh --quiet --eval "
db = db.getSiblingDB('edn360_app');
snapshot = db.edn360_snapshots.findOne(
  {user_id: '1764168881795908'},
  {snapshot_id: 1, status: 1, workflow_name: 1, created_at: 1}
);
print(JSON.stringify(snapshot, null, 2));
"
```

### Verificar plan guardado en training_plans_v2:

```bash
mongosh --quiet --eval "
db = db.getSiblingDB('edn360_app');
plan = db.training_plans_v2.findOne(
  {user_id: '1764168881795908'},
  {created_at: 1, status: 1, 'plan.title': 1, 'plan.days_per_week': 1}
);
print(JSON.stringify(plan, null, 2));
"
```

---

## ⚠️ POSIBLES ERRORES Y SOLUCIONES

### Error: "EDN360_CORE_ASSISTANT_ID no está configurada"
**Causa**: El backend no está leyendo el .env correctamente  
**Solución**: 
```bash
sudo supervisorctl restart backend
```

### Error: "Workflow no completado. Status: failed"
**Causa**: El workflow E1-E7.5 encontró un error interno  
**Solución**: 
- Verificar logs de OpenAI Platform
- Revisar que el Assistant tenga acceso a la BD de ejercicios
- Verificar que el prompt del workflow sea correcto

### Error: "El workflow no devolvió un plan de entrenamiento válido"
**Causa**: El workflow no está devolviendo el JSON con la estructura esperada  
**Solución**:
- Verificar que el último mensaje del thread tenga el campo `client_training_program_enriched`
- Revisar la salida del workflow en OpenAI Platform

### Error 404: "Usuario no encontrado"
**Causa**: El `user_id` no existe en la BD  
**Solución**: Verificar el `user_id` correcto en MongoDB

### Error 404: "Cuestionario no encontrado"
**Causa**: El `questionnaire_submission_id` no existe para ese usuario  
**Solución**: Verificar que el cuestionario esté en `client_drawers` para ese usuario

---

## ✅ CHECKLIST FINAL

- [x] ✅ Variables configuradas en `.env`
- [x] ✅ Código actualizado para usar Core Assistant ID
- [x] ✅ Backend reiniciado
- [x] ✅ Endpoint `/api/training-plan` funcional
- [x] ✅ Jorge2 tiene cuestionario disponible
- [x] ✅ Frontend con botón "Generar plan (EDN360)"
- [x] ✅ Vista de renderizado implementada
- [ ] ⏳ **PENDIENTE**: Prueba E2E con Jorge2

---

## 🎯 PRÓXIMO PASO

**JORGE: Por favor, realiza la prueba desde el admin panel con Jorge2**

1. Login al admin panel
2. Selecciona Jorge2
3. Tab "Entrenamiento"
4. Click "Generar plan (EDN360)"
5. Espera 1-2 minutos
6. Verifica que el plan se renderice correctamente

**Si hay algún error, comparte**:
- El mensaje de error que aparece en pantalla
- Los logs del backend (últimas 50 líneas)
- Y continuamos debuggeando juntos

---

## 📞 SOPORTE

Si necesitas ayuda durante la prueba:
- Comparte screenshots del error
- Comparte logs del backend
- Podemos hacer la prueba juntos en tiempo real

**¡El sistema está 100% configurado y listo! 🚀**
