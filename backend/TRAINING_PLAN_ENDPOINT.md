# Endpoint: POST /api/training-plan

## 📋 Descripción

Endpoint para generar planes de entrenamiento personalizados usando el workflow de Platform (E1-E7.5).

**Flujo interno:**
1. Valida el `questionnaire_submission`
2. Sincroniza con `client_drawers` (dual-write, idempotente)
3. Llama al workflow de Platform (E1-E7.5)
4. Guarda snapshot en `edn360_snapshots`
5. Devuelve solo `client_training_program_enriched`

---

## 🔐 Autenticación

**Requerido**: Usuario autenticado

```
Authorization: Bearer <token>
```

---

## 📤 Request

### URL
```
POST /api/training-plan
```

### Headers
```
Content-Type: application/json
Authorization: Bearer <token>
```

### Body
```json
{
  "questionnaire_submission": {
    "submission_id": "1764016775848319",
    "source": "initial",
    "submitted_at": "2025-11-24T20:39:35.848Z",
    "payload": {
      "full_name": "Jorge",
      "email": "jorge31011987promo@gmail.com",
      "birth_date": "1987-01-31",
      "gender": "male",
      "height_cm": 172,
      "weight_kg": 85,
      "bodyfat_percent": 23,
      "chronic_conditions": ["hypothyroidism"],
      "injuries_limitations": [
        "rotator_cuff_issues_both_shoulders",
        "lumbar_disc_hernias_L5_L6"
      ],
      "training_experience_level": "advanced",
      "training_days_per_week": 4,
      "session_duration_min": 45,
      "equipment_available": ["full_gym"],
      "goal_primary": "muscle_gain",
      "goal_secondary": "return_to_competition",
      "sleep_hours": 6.5,
      "daily_activity": "high",
      "motivation_reason": "Wants to return to bodybuilding stage competition.",
      "preferred_training_environment": "gym",
      "pain_current_level": "moderate",
      "stress_level": "medium",
      "has_personal_trainer_before": true,
      "alcohol_frequency": "weekly",
      "smoking_status": "non_smoker",
      "food_allergies_intolerances": ["gluten"],
      "schedule_constraints": "Works long shifts, limited time evenings",
      "adherence_challenges": [
        "long_work_hours",
        "social_events_with_alcohol"
      ]
    }
  }
}
```

### Validaciones

- `source`: debe ser `"initial"` o `"follow_up"`
- `submitted_at`: formato ISO8601 válido
- `submission_id`: no puede estar vacío
- `payload`: debe ser un objeto no vacío

---

## 📥 Response

### Success (200 OK)
```json
{
  "client_training_program_enriched": {
    "title": "Hipertrofia con enfoque articular seguro (4 días)",
    "summary": "Plan de 4 días centrado en máquinas, rangos controlados y protección de hombros y zona lumbar.",
    "goal": "Ganar músculo sin agravar las lesiones previas.",
    "training_type": "upper_lower",
    "days_per_week": 4,
    "session_duration_min": 45,
    "weeks": 4,
    "sessions": [
      {
        "id": "D1",
        "name": "Upper 1 – Empuje dominante",
        "focus": ["upper_body", "push_focus"],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["chest", "front_delts", "triceps"],
            "secondary_muscles": ["upper_back"],
            "exercises": [
              {
                "order": 1,
                "db_id": "E049",
                "name": "press banca smith agarre cerrado",
                "primary_group": "tríceps",
                "secondary_group": "pectorales",
                "series": 3,
                "reps": "10-12",
                "rpe": "7",
                "video_url": "https://drive.google.com/file/d/1DJpGDOn_u4oi28QpCjWcxZwRtEEWi4gh/view?usp=drivesdk"
              }
            ]
          }
        ],
        "session_notes": [
          "No realizar press por encima de la cabeza.",
          "Respetar siempre rango sin dolor."
        ]
      }
    ],
    "general_notes": [
      "Calienta de forma específica hombros y zona lumbar al inicio de cada sesión.",
      "Priorizar máquinas y agarres neutros siempre que sea posible."
    ]
  }
}
```

### Error Responses

**401 Unauthorized**
```json
{
  "detail": "Token de autenticación requerido"
}
```

**400 Bad Request**
```json
{
  "detail": {
    "error": "invalid_questionnaire",
    "message": "El cuestionario no es válido",
    "errors": ["source debe ser 'initial' o 'follow_up'"]
  }
}
```

**404 Not Found**
```json
{
  "detail": "Usuario no encontrado"
}
```

**500 Internal Server Error**
```json
{
  "detail": {
    "error": "workflow_error",
    "message": "Error generando plan de entrenamiento: ..."
  }
}
```

---

## 🏗️ Arquitectura Interna

### 1. Sincronización con `client_drawers`

El cuestionario se guarda en `edn360_app.client_drawers`:

```javascript
{
  user_id: "1764016044644335",
  services: {
    shared_questionnaires: [
      {
        submission_id: "1764016775848319",
        submitted_at: ISODate("2025-11-24T20:39:35.848Z"),
        source: "initial",
        raw_payload: { ... }
      }
    ]
  }
}
```

**Nota**: La sincronización es **idempotente** (no duplica si ya existe).

### 2. Llamada al Workflow de Platform

**Configuración** (`.env`):
```env
EDN360_OPENAI_API_KEY="sk-proj-..."
EDN360_TRAINING_WORKFLOW_ID="TU_WORKFLOW_ID_AQUI"
```

**Input enviado**:
```json
{
  "questionnaire_submission": { ... }
}
```

**Output esperado**:
```json
{
  "client_training_program_enriched": { ... },
  "_metadata": {
    "workflow_id": "...",
    "tokens_used": 5000
  }
}
```

### 3. Snapshot en `edn360_snapshots`

Cada ejecución crea un snapshot:

```javascript
{
  _id: "uuid-...",
  user_id: "1764016044644335",
  created_at: ISODate("2025-11-27T..."),
  version: "1.0.0",
  input: { questionnaire_submission: {...} },
  workflow_name: "training_plan_v1",
  workflow_response: { ... },
  status: "success",
  error_message: null
}
```

---

## 🧪 Testing

### Ejemplo con cURL

```bash
curl -X POST http://localhost:8001/api/training-plan \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "questionnaire_submission": {
      "submission_id": "test_123",
      "source": "initial",
      "submitted_at": "2025-11-27T10:00:00.000Z",
      "payload": {
        "full_name": "Test User",
        "goal_primary": "muscle_gain",
        "training_days_per_week": 4
      }
    }
  }'
```

---

## 📝 Notas Importantes

1. **No exponer internals**: El frontend solo recibe `client_training_program_enriched`, no metadatos ni snapshots.

2. **Dual-write coherente**: Reutiliza la misma lógica de `add_questionnaire_to_drawer` que el resto del sistema.

3. **Idempotencia**: Si el mismo `submission_id` se envía múltiples veces, no se duplica en `client_drawers`.

4. **Snapshots para trazabilidad**: Todas las ejecuciones se guardan en `edn360_snapshots` para auditoría.

5. **Errors no bloquean flujo**: Si falla el dual-write o el snapshot, se logea pero no se bloquea la respuesta al usuario.

---

## 🔧 Configuración Requerida

Antes de usar este endpoint, Jorge debe configurar:

```env
EDN360_TRAINING_WORKFLOW_ID="<workflow_id_real>"
```

Sin este ID configurado, el endpoint devolverá error 500.
