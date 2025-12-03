# EDN360 - Guía Rápida de Referencia

**Versión:** 2.0.0  
**Fecha:** 2025-12-03  
**Propósito:** Referencia rápida para operaciones comunes y troubleshooting

---

## Diagrama de Flujo Visual

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USUARIO ADMIN                              │
│                     (AdminDashboard.jsx)                             │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Selecciona:
                                  │ • Cliente
                                  │ • Cuestionario Previo
                                  │ • Cuestionario Nuevo
                                  │ • Plan Anterior
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │  POST /api/training-plan    │
                    │  {                          │
                    │    user_id,                 │
                    │    questionnaire_ids: [],   │
                    │    previous_training_plan_id│
                    │  }                          │
                    └─────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI - server.py)                     │
│                                                                      │
│  ┌────────────────┐     ┌────────────────┐     ┌────────────────┐ │
│  │ 1. Validación  │ ──► │ 2. Lee MongoDB │ ──► │ 3. Construye   │ │
│  │    de Inputs   │     │  - Cuestionarios│     │    STATE       │ │
│  │                │     │  - Planes       │     │                │ │
│  └────────────────┘     └────────────────┘     └────────────────┘ │
│                                                         │            │
│                                                         ▼            │
│                                            ┌────────────────────┐   │
│                                            │ 4. Llama Workflow  │   │
│                                            │    con INPUT+STATE │   │
│                                            └────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ POST /api/edn360/run-training-workflow
                                  │ { input: {...}, state: {...} }
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│         MICROSERVICIO EDN360 (Node.js - edn360_workflow.ts)        │
│                                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│  │  E1      │──►│  E2      │──►│  E3      │──►│  E4      │        │
│  │  Profile │   │  Parse   │   │  Training│   │  Plan    │        │
│  │  Analyzer│   │  Quest   │   │  Summary │   │  Generator│       │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘        │
│                                                         │            │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│  │  E7.5    │◄──│  E7      │◄──│  E6      │◄──│  E5      │        │
│  │  Enricher│   │  Assembler│  │  Exercise│   │  Validator│       │
│  │          │   │          │   │  Mapper  │   │          │        │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘        │
│                                                         │            │
│                                                         ▼            │
│                        ┌─────────────────────────────────────┐      │
│                        │ Response:                           │      │
│                        │ client_training_program_enriched    │      │
│                        └─────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Response JSON
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI - server.py)                     │
│                                                                      │
│  ┌────────────────┐     ┌────────────────┐     ┌────────────────┐ │
│  │ 5. Guarda Plan │ ──► │ 6. Responde al │ ──► │ 7. Frontend    │ │
│  │    en MongoDB  │     │    Frontend    │     │    Muestra Plan│ │
│  │                │     │                │     │                │ │
│  └────────────────┘     └────────────────┘     └────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │ MongoDB:                    │
                    │ edn360_app.training_plans_v2│
                    │ • Plan guardado             │
                    │ • is_evolutionary: true     │
                    └─────────────────────────────┘
```

---

## Archivos Clave por Componente

### Frontend
```
/app/frontend/src/pages/
  └── AdminDashboard.jsx         (UI de generación de planes)

/app/frontend/src/components/
  └── TrainingPlanCard.jsx        (Visualización de planes)
```

### Backend
```
/app/backend/
  ├── server.py                   (Endpoint principal: POST /api/training-plan)
  └── services/
      ├── training_workflow_service.py    (Llamada al microservicio)
      └── edn360_input_builder.py         (Construcción de inputs - legacy)
```

### Microservicio
```
/app/edn360-workflow-service/
  └── src/
      └── edn360_workflow.ts      (Workflow completo con 8 agentes)
```

### Configuración
```
/app/backend/.env                 (Variables de entorno backend)
/app/frontend/.env                (Variables de entorno frontend)
/app/edn360-workflow-service/.env (Variables microservicio)
```

### Documentación
```
/app/docs/
  ├── EDN360_ARCHITECTURE_COMPLETE.md   (Arquitectura completa)
  ├── EDN360_DATABASE_QUERIES.md        (Consultas MongoDB)
  ├── EDN360_QUICK_REFERENCE.md         (Esta guía)
  └── agent_prompts_v2.0.0_evolutionary.md (Prompts de agentes)
```

---

## Comandos Rápidos

### Verificar Estado de Servicios

```bash
# Ver estado de todos los servicios
sudo supervisorctl status

# Backend
sudo supervisorctl status backend

# Frontend
sudo supervisorctl status frontend

# Microservicio EDN360
sudo supervisorctl status edn360-workflow-service
```

### Reiniciar Servicios

```bash
# Reiniciar backend
sudo supervisorctl restart backend

# Reiniciar microservicio
sudo supervisorctl restart edn360-workflow-service

# Reiniciar todos
sudo supervisorctl restart all
```

### Ver Logs

```bash
# Backend (errores)
tail -f /var/log/supervisor/backend.err.log

# Backend (output)
tail -f /var/log/supervisor/backend.out.log

# Microservicio
tail -f /var/log/supervisor/edn360-workflow-service.out.log

# Frontend
tail -f /var/log/supervisor/frontend.err.log
```

### Buscar en Logs

```bash
# Buscar errores recientes en backend
tail -n 200 /var/log/supervisor/backend.err.log | grep -i "error\|❌"

# Buscar generaciones de planes
tail -n 200 /var/log/supervisor/backend.err.log | grep "Generando plan"

# Ver tipo de flujo (inicial vs evolutivo)
tail -n 100 /var/log/supervisor/edn360-workflow-service.out.log | grep "Tipo de generación"
```

---

## Operaciones Comunes

### 1. Probar Generación de Plan (curl)

```bash
# Obtener token de admin
TOKEN="YOUR_ADMIN_TOKEN_HERE"

# URL del backend
API_URL="http://localhost:8001"

# Caso A: Primer plan (sin historial)
curl -X POST "$API_URL/api/training-plan" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "1764016044644335",
    "questionnaire_ids": ["quest_inicial_001"]
  }' | jq .

# Caso B: Plan evolutivo (con historial)
curl -X POST "$API_URL/api/training-plan" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "1764016044644335",
    "questionnaire_ids": ["quest_inicial_001", "quest_seguimiento_001"],
    "previous_training_plan_id": "674eabcd1234567890abcdef"
  }' | jq .
```

### 2. Probar Endpoint Mock (sin OpenAI)

```bash
curl -X POST "$API_URL/api/training-plan/mock" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "1764016044644335"
  }' | jq .
```

### 3. Obtener Plan Más Reciente

```bash
USER_ID="1764016044644335"

curl -X GET "$API_URL/api/admin/users/$USER_ID/training-plans/latest" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### 4. Ver Cuestionarios en MongoDB

```bash
mongosh test_database --eval "
  db.client_drawers.findOne(
    { user_id: '1764016044644335' },
    { 'services.shared_questionnaires.submission_id': 1 }
  )
"
```

### 5. Ver Planes en MongoDB

```bash
mongosh edn360_app --eval "
  db.training_plans_v2.find(
    { user_id: '1764016044644335' },
    { _id: 1, created_at: 1, is_evolutionary: 1, 'plan.title': 1 }
  ).sort({ created_at: 1 })
"
```

---

## Troubleshooting Rápido

### Problema: "Error 500 al generar plan"

**Diagnóstico:**
```bash
# 1. Verificar que el microservicio está corriendo
sudo supervisorctl status edn360-workflow-service
# Debe estar: RUNNING

# 2. Ver logs del microservicio
tail -n 50 /var/log/supervisor/edn360-workflow-service.out.log
# Buscar errores de OpenAI API

# 3. Ver logs del backend
tail -n 50 /var/log/supervisor/backend.err.log
# Buscar "Error ejecutando training workflow"
```

**Soluciones:**
- Si microservicio está STOPPED → `sudo supervisorctl restart edn360-workflow-service`
- Si hay "OpenAI API timeout" → Verificar API key en `/app/edn360-workflow-service/.env`
- Si hay "Timeout: El microservicio no respondió" → Aumentar timeout en `training_workflow_service.py`

---

### Problema: "Usuario no tiene cuestionarios"

**Diagnóstico:**
```bash
# Verificar que el usuario tiene cuestionarios
mongosh test_database --eval "
  db.client_drawers.findOne({ user_id: 'USER_ID' })
"
```

**Soluciones:**
- Si `client_drawer` no existe → Crear uno usando el endpoint de cuestionarios
- Si `shared_questionnaires` está vacío → Usuario necesita completar un cuestionario

---

### Problema: "Plan no está progresando (volumen igual)"

**Diagnóstico:**
```bash
# Ver logs del microservicio para verificar tipo de flujo
tail -n 100 /var/log/supervisor/edn360-workflow-service.out.log | grep "Tipo de generación"

# Si dice "INICIAL" en vez de "EVOLUTIVO", verificar STATE
tail -n 50 /var/log/supervisor/backend.err.log | grep "Planes previos recuperados"
```

**Soluciones:**
- Si STATE tiene `last_plan: null` pero debería tener planes → Verificar `previous_training_plan_id` en el request
- Si hay planes en BD pero no en STATE → Verificar filtrado de planes en `server.py`
- Si es EVOLUTIVO pero no progresa → Revisar prompt de E4 en `edn360_workflow.ts`

---

### Problema: "Frontend no muestra planes"

**Diagnóstico:**
```bash
# 1. Verificar que el plan se guardó en MongoDB
mongosh edn360_app --eval "
  db.training_plans_v2.find({ user_id: 'USER_ID' }).count()
"

# 2. Verificar que el endpoint GET funciona
curl -X GET "http://localhost:8001/api/admin/users/USER_ID/training-plans/latest" \
  -H "Authorization: Bearer $TOKEN"

# 3. Ver logs del frontend
tail -n 50 /var/log/supervisor/frontend.err.log
```

**Soluciones:**
- Si plan no está en MongoDB → Problema en guardado (ver logs backend)
- Si endpoint GET no funciona → Verificar token de autenticación
- Si frontend tiene error → Verificar consola del navegador (F12)

---

### Problema: "Timeout en agente E3, E4, E5 o E6"

**Diagnóstico:**
```bash
# Ver en qué agente se detiene
tail -n 200 /var/log/supervisor/edn360-workflow-service.out.log | grep "Ejecutando\|completado"
```

**Soluciones:**
- Si se detiene en E3 o E4 → Posible problema de `maxTokens` insuficiente
- Aumentar `maxTokens` en `edn360_workflow.ts`:
  ```typescript
  modelSettings: {
    temperature: 0.2,
    maxTokens: 4096  // ← Aumentar de 2048 a 4096
  }
  ```
- Reiniciar microservicio: `sudo supervisorctl restart edn360-workflow-service`

---

## Variables de Entorno Importantes

### Backend (.env)
```bash
# MongoDB
MONGO_URL=mongodb://localhost:27017
MONGO_DB_NAME=test_database
MONGO_EDN360_APP_DB_NAME=edn360_app

# Microservicio EDN360
EDN360_WORKFLOW_SERVICE_URL=http://localhost:4000/api/edn360/run-training-workflow
```

### Microservicio (.env)
```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Puerto
PORT=4000
```

### Frontend (.env)
```bash
# Backend URL
REACT_APP_BACKEND_URL=http://your-app-url.com
```

---

## Checklist de Salud del Sistema

```bash
# Ejecutar este script para verificar salud completa
cat << 'EOF' > /tmp/health_check.sh
#!/bin/bash

echo "========================================="
echo "EDN360 HEALTH CHECK"
echo "========================================="

# 1. Servicios
echo "1. Servicios:"
sudo supervisorctl status backend frontend edn360-workflow-service

# 2. MongoDB
echo ""
echo "2. MongoDB:"
mongosh --eval "db.runCommand({ ping: 1 })" --quiet

# 3. Backend endpoint
echo ""
echo "3. Backend API:"
curl -s http://localhost:8001/health | head -n 5

# 4. Microservicio
echo ""
echo "4. Microservicio EDN360:"
curl -s http://localhost:4000/health | head -n 5

# 5. Logs recientes (últimos 5 min)
echo ""
echo "5. Errores recientes en backend:"
tail -n 100 /var/log/supervisor/backend.err.log | grep -i "error" | tail -n 5

echo ""
echo "6. Errores recientes en microservicio:"
tail -n 100 /var/log/supervisor/edn360-workflow-service.out.log | grep -i "error" | tail -n 5

echo ""
echo "========================================="
echo "FIN HEALTH CHECK"
echo "========================================="
EOF

chmod +x /tmp/health_check.sh
/tmp/health_check.sh
```

---

## Resumen de Endpoints Críticos

| Endpoint | Método | Propósito | Auth |
|----------|--------|-----------|------|
| `/api/training-plan` | POST | Generar plan evolutivo | Admin |
| `/api/training-plan/mock` | POST | Generar plan mock | Admin |
| `/api/admin/users/{user_id}/training-plans/latest` | GET | Obtener último plan | Admin |
| `/api/admin/users/{user_id}/training-plans` | GET | Obtener todos los planes | Admin |
| `/api/admin/users/{user_id}/edn360-questionnaires` | GET | Obtener cuestionarios | Admin |
| `/health` | GET | Health check backend | Público |

---

## Próximos Pasos Recomendados

1. **Revisar Documentación Completa:**
   - Leer `/app/docs/EDN360_ARCHITECTURE_COMPLETE.md`
   - Familiarizarse con esquemas de BD

2. **Probar Flujo Completo:**
   - Generar plan inicial con curl
   - Generar plan evolutivo con curl
   - Verificar planes en MongoDB

3. **Iterar en Prompts:**
   - Identificar áreas de mejora en los agentes
   - Modificar prompts en `edn360_workflow.ts`
   - Probar cambios y documentar

4. **Configurar Monitoreo:**
   - Configurar alertas para errores de OpenAI
   - Monitorear tiempos de respuesta del workflow
   - Revisar logs periódicamente

---

**Documento Actualizado:** 2025-12-03  
**Próxima Revisión:** Cuando se implementen cambios significativos en el sistema
