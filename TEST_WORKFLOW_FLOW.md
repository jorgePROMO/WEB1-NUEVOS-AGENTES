# 🧪 VERIFICACIÓN DEL FLUJO EDN360 - CUESTIONARIO Y PLAN PREVIO

## 📊 FLUJO COMPLETO

```
Frontend Desplegables
    ↓
    ├─ Cuestionario Base: selectedQuestionnaireForTraining
    └─ Plan Previo: selectedPreviousTrainingPlan
    ↓
Frontend: generateEDN360TrainingPlan()
    ↓
POST /api/training-plan
    {
      "user_id": "...",
      "questionnaire_submission_id": "...",
      "previous_training_plan_id": "..."  ← OPCIONAL
    }
    ↓
Backend: generate_training_plan()
    ↓
    ├─ 1. Validar usuario
    ├─ 2. Construir EDN360Input (con cuestionarios)
    ├─ 2.5. Buscar y agregar plan previo al contexto
    └─ 3. Llamar workflow EDN360
    ↓
Workflow EDN360 (Node.js)
    ↓
    ├─ E1: Analizar perfil
    ├─ E2: Parse questionnaire (USA cuestionario seleccionado)
    ├─ E3: Training goals
    ├─ E5: Training plan structure
    ├─ E6: Exercise mapper
    ├─ E7: Training plan assembler (PUEDE USAR plan previo)
    └─ E7.5: Training plan enricher
    ↓
Response: client_training_program_enriched
```

---

## ✅ VERIFICACIONES IMPLEMENTADAS

### 1. **Frontend** (`AdminDashboard.jsx`)

**Función modificada:** `generateEDN360TrainingPlan()`

```javascript
const payload = {
  user_id: selectedClient.id,
  questionnaire_submission_id: submissionId
};

// ✅ NUEVO: Agregar plan previo si está seleccionado
if (selectedPreviousTrainingPlan && selectedPreviousTrainingPlan !== 'none') {
  payload.previous_training_plan_id = selectedPreviousTrainingPlan;
  console.log('📋 Usando plan previo:', selectedPreviousTrainingPlan);
}

console.log('🚀 Generando plan EDN360 con payload:', payload);
```

**Logs esperados en consola:**
```
🚀 Generando plan EDN360 con payload: {
  user_id: "1764016044644335",
  questionnaire_submission_id: "1764016775848319",
  previous_training_plan_id: "edn360_0_2025-12-02T..."
}
```

---

### 2. **Backend** (`server.py`)

**Endpoint modificado:** `POST /api/training-plan`

**Cambios:**
1. ✅ Lee `previous_training_plan_id` del body
2. ✅ Logea el plan previo en los logs
3. ✅ Busca el plan previo en `training_plans_v2` o `training_plans`
4. ✅ Agrega el plan previo al contexto del input EDN360
5. ✅ Pasa el input completo al workflow

**Logs esperados en backend:**
```
🏋️ Generando plan de entrenamiento | admin: admin_test_001 | user_id: 1764016044644335 | submission_id: 1764016775848319 | previous_plan_id: edn360_0_2025-12-02T...
✅ EDN360Input construido | Cuestionarios: 1
📋 Buscando plan previo: edn360_0_2025-12-02T...
✅ Plan previo agregado al contexto
```

---

### 3. **Estructura del Input EDN360 enviado al Workflow**

```json
{
  "user_profile": {
    "user_id": "1764016044644335",
    "name": "Jorge1",
    "age": 37,
    "sex": "male",
    "height_cm": 172,
    "weight_kg": 85
  },
  "questionnaires": [
    {
      "submission_id": "1764016775848319",
      "submitted_at": "2025-11-24 20:39:35",
      "questionnaire_type": "initial",
      "responses": {
        "objetivo_fisico": "Ganar músculo",
        "dias_semana_entrenar": "3-4",
        "nivel_deporte": "Avanzado",
        ... (83 campos)
      }
    }
  ],
  "context": {
    "platform": "edn360_web",
    "version": "1.0.0",
    "previous_training_plan": {       ← NUEVO
      "plan_data": {
        "title": "Plan Upper/Lower...",
        "sessions": [...],
        ...
      },
      "created_at": "2025-12-02T...",
      "source": "training_plans_v2"
    }
  }
}
```

---

## 🧪 CÓMO PROBAR

### 1. Verificar logs del frontend (consola del navegador)

1. Abrir DevTools (F12)
2. Ir a Console
3. Seleccionar cuestionario y plan previo
4. Click en "Generar Plan EDN360"
5. Verificar log:
   ```
   🚀 Generando plan EDN360 con payload: { ... previous_training_plan_id: "..." }
   ```

### 2. Verificar logs del backend

```bash
tail -f /var/log/supervisor/backend.out.log | grep -E "Generando plan|previous_plan|Plan previo"
```

Deberías ver:
```
🏋️ Generando plan de entrenamiento | ... | previous_plan_id: edn360_0_...
📋 Buscando plan previo: edn360_0_...
✅ Plan previo agregado al contexto
```

### 3. Verificar que el workflow recibe los datos

El workflow de Node.js debería recibir el input completo con:
- ✅ Cuestionario seleccionado
- ✅ Plan previo en el contexto (si fue seleccionado)

---

## ⚠️ CASOS DE USO

### Caso 1: Solo cuestionario (sin plan previo)
```
Desplegable "Cuestionario Base": Inicial - 24/11/2025
Desplegable "Plan Previo": Ninguno

→ Input enviado SIN context.previous_training_plan
```

### Caso 2: Cuestionario + Plan previo
```
Desplegable "Cuestionario Base": Seguimiento - 02/12/2025
Desplegable "Plan Previo": EDN360 #1 - Plan Upper/Lower

→ Input enviado CON context.previous_training_plan
→ El workflow puede usar el plan previo para progresión
```

---

## 📋 CHECKLIST DE VERIFICACIÓN

- [✅] Frontend lee `selectedQuestionnaireForTraining`
- [✅] Frontend lee `selectedPreviousTrainingPlan`
- [✅] Frontend envía ambos en el payload
- [✅] Backend recibe `previous_training_plan_id`
- [✅] Backend busca el plan previo en BD
- [✅] Backend agrega plan previo al contexto del input
- [✅] Backend pasa input completo al workflow
- [✅] Workflow recibe el contexto con plan previo

---

## 🎯 RESULTADO ESPERADO

Cuando seleccionas:
1. **Cuestionario:** El workflow usará ese cuestionario específico
2. **Plan Previo:** El workflow tendrá acceso al plan anterior para:
   - Ver qué ejercicios funcionaron bien
   - Aplicar progresión de cargas
   - Mantener continuidad en el programa
   - Evitar repetir ejercicios si no es necesario

---

**Última actualización:** 2 de Diciembre, 2025
