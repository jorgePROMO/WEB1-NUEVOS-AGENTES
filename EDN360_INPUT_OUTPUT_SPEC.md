# 📋 EDN360 - INPUT y OUTPUT Exactos para Agentes

---

## 🔵 INPUT ENVIADO A TUS AGENTES

El backend construye y envía este JSON al Assistant:

```json
{
  "user_profile": {
    "user_id": "1764168881795908",
    "name": "Jorge2",
    "email": "jorge31011987@gmail.com",
    "age": 38,
    "gender": "male",
    "height": 175,
    "weight": 78,
    "subscription": {
      "plan": "premium",
      "status": "active"
    }
  },
  "questionnaires": [
    {
      "submission_id": "1764169432140799",
      "type": "initial",
      "submitted_at": "2025-11-26T15:03:52.140000",
      "answers": {
        "fitness_goal": "hipertrofia",
        "training_experience": "intermedio",
        "days_per_week": 4,
        "session_duration": 60,
        "available_equipment": ["mancuernas", "barra", "banco", "máquinas"],
        "injuries": "ninguna",
        "health_conditions": "ninguna",
        "preferred_training_style": "upper_lower",
        "training_location": "gimnasio"
      }
    }
  ],
  "context": {
    "request_type": "training_plan_generation",
    "timestamp": "2025-11-28T13:45:30.123456",
    "version": "1.0.0"
  }
}
```

**Notas sobre el INPUT:**
- El `user_profile` contiene datos básicos del cliente
- `questionnaires` es un array (puede tener inicial + seguimientos)
- `answers` contiene TODAS las respuestas del cuestionario
- Este JSON se envía tal cual al thread del Assistant

---

## 🟢 OUTPUT ESPERADO DE TUS AGENTES

Tus agentes (E1-E7.5) deben devolver EXACTAMENTE este formato JSON:

```json
{
  "client_training_program_enriched": {
    "title": "Programa de Hipertrofia Upper/Lower",
    "summary": "Plan de entrenamiento diseñado para maximizar la hipertrofia muscular mediante un split upper/lower de 4 días semanales, con énfasis en ejercicios compuestos y aislamiento estratégico.",
    "goal": "hipertrofia",
    "training_type": "upper_lower",
    "days_per_week": 4,
    "session_duration_min": 60,
    "weeks": 4,
    "general_notes": [
      "Calentar 5-10 minutos antes de cada sesión",
      "Descansar 2-3 minutos entre series de ejercicios compuestos",
      "Progresar carga semanalmente cuando sea posible",
      "Mantener RPE entre 7-9 para estimular hipertrofia"
    ],
    "sessions": [
      {
        "id": "D1",
        "name": "Upper Body Push",
        "focus": ["upper_body", "push_focus"],
        "session_notes": [
          "Enfocarse en control excéntrico de 3 segundos",
          "Priorizar conexión mente-músculo en ejercicios de aislamiento"
        ],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["pecho", "hombros"],
            "secondary_muscles": ["tríceps"],
            "exercises": [
              {
                "order": 1,
                "name": "Press Banca con Barra",
                "primary_group": "pecho",
                "secondary_group": "tríceps",
                "series": 4,
                "reps": "8-10",
                "rpe": 8,
                "video_url": "https://www.youtube.com/watch?v=example1",
                "notes": "Bajar barra hasta el pecho, pausa de 1 segundo"
              },
              {
                "order": 2,
                "name": "Press Militar con Barra",
                "primary_group": "hombros",
                "secondary_group": "tríceps",
                "series": 4,
                "reps": "10-12",
                "rpe": 8,
                "video_url": "https://www.youtube.com/watch?v=example2",
                "notes": "Mantener core activo, evitar hiperextensión lumbar"
              }
            ]
          },
          {
            "id": "B",
            "primary_muscles": ["pecho", "hombros"],
            "secondary_muscles": [],
            "exercises": [
              {
                "order": 3,
                "name": "Press Inclinado con Mancuernas",
                "primary_group": "pecho",
                "secondary_group": "hombros",
                "series": 3,
                "reps": "10-12",
                "rpe": 8,
                "video_url": "https://www.youtube.com/watch?v=example3",
                "notes": "Banco a 30-45 grados"
              },
              {
                "order": 4,
                "name": "Elevaciones Laterales",
                "primary_group": "hombros",
                "secondary_group": "",
                "series": 3,
                "reps": "12-15",
                "rpe": 7,
                "video_url": "https://www.youtube.com/watch?v=example4",
                "notes": "Control total del movimiento, sin balanceo"
              }
            ]
          },
          {
            "id": "C",
            "primary_muscles": ["tríceps"],
            "secondary_muscles": [],
            "exercises": [
              {
                "order": 5,
                "name": "Extensiones de Tríceps en Polea",
                "primary_group": "tríceps",
                "secondary_group": "",
                "series": 3,
                "reps": "12-15",
                "rpe": 7,
                "video_url": "https://www.youtube.com/watch?v=example5",
                "notes": "Mantener codos fijos, rango completo"
              }
            ]
          }
        ]
      },
      {
        "id": "D2",
        "name": "Lower Body",
        "focus": ["lower_body"],
        "session_notes": [
          "Activar glúteos con ejercicio de activación previo",
          "Mantener técnica impecable en sentadillas y peso muerto"
        ],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["cuádriceps", "glúteos"],
            "secondary_muscles": ["isquiotibiales"],
            "exercises": [
              {
                "order": 1,
                "name": "Sentadilla con Barra",
                "primary_group": "cuádriceps",
                "secondary_group": "glúteos",
                "series": 4,
                "reps": "6-8",
                "rpe": 9,
                "video_url": "https://www.youtube.com/watch?v=example6",
                "notes": "Profundidad completa, rodillas alineadas con pies"
              },
              {
                "order": 2,
                "name": "Prensa de Piernas",
                "primary_group": "cuádriceps",
                "secondary_group": "glúteos",
                "series": 3,
                "reps": "10-12",
                "rpe": 8,
                "video_url": "https://www.youtube.com/watch?v=example7",
                "notes": "Rango completo sin levantar glúteos"
              }
            ]
          },
          {
            "id": "B",
            "primary_muscles": ["isquiotibiales", "glúteos"],
            "secondary_muscles": [],
            "exercises": [
              {
                "order": 3,
                "name": "Peso Muerto Rumano",
                "primary_group": "isquiotibiales",
                "secondary_group": "glúteos",
                "series": 3,
                "reps": "8-10",
                "rpe": 8,
                "video_url": "https://www.youtube.com/watch?v=example8",
                "notes": "Mantener espalda neutra, sentir estiramiento"
              },
              {
                "order": 4,
                "name": "Curl Femoral Tumbado",
                "primary_group": "isquiotibiales",
                "secondary_group": "",
                "series": 3,
                "reps": "12-15",
                "rpe": 7,
                "video_url": "https://www.youtube.com/watch?v=example9",
                "notes": "Contracción máxima en la parte superior"
              }
            ]
          },
          {
            "id": "C",
            "primary_muscles": ["gemelos"],
            "secondary_muscles": [],
            "exercises": [
              {
                "order": 5,
                "name": "Elevaciones de Gemelos de Pie",
                "primary_group": "gemelos",
                "secondary_group": "",
                "series": 4,
                "reps": "15-20",
                "rpe": 8,
                "video_url": "https://www.youtube.com/watch?v=example10",
                "notes": "Rango completo, pausa en contracción"
              }
            ]
          }
        ]
      },
      {
        "id": "D3",
        "name": "Upper Body Pull",
        "focus": ["upper_body", "pull_focus"],
        "session_notes": [
          "Concentrarse en tirar con la espalda, no con los brazos",
          "Retracción escapular activa en todos los ejercicios de tirón"
        ],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["espalda"],
            "secondary_muscles": ["bíceps"],
            "exercises": [
              {
                "order": 1,
                "name": "Peso Muerto Convencional",
                "primary_group": "espalda",
                "secondary_group": "isquiotibiales",
                "series": 4,
                "reps": "6-8",
                "rpe": 9,
                "video_url": "https://www.youtube.com/watch?v=example11",
                "notes": "Espalda neutra todo el movimiento"
              },
              {
                "order": 2,
                "name": "Dominadas",
                "primary_group": "espalda",
                "secondary_group": "bíceps",
                "series": 4,
                "reps": "8-10",
                "rpe": 8,
                "video_url": "https://www.youtube.com/watch?v=example12",
                "notes": "Si es necesario, usar banda de asistencia"
              }
            ]
          },
          {
            "id": "B",
            "primary_muscles": ["espalda"],
            "secondary_muscles": ["bíceps"],
            "exercises": [
              {
                "order": 3,
                "name": "Remo con Barra",
                "primary_group": "espalda",
                "secondary_group": "bíceps",
                "series": 3,
                "reps": "10-12",
                "rpe": 8,
                "video_url": "https://www.youtube.com/watch?v=example13",
                "notes": "Torso a 45 grados, tirar hacia abdomen bajo"
              },
              {
                "order": 4,
                "name": "Face Pulls",
                "primary_group": "hombros",
                "secondary_group": "trapecio",
                "series": 3,
                "reps": "15-20",
                "rpe": 7,
                "video_url": "https://www.youtube.com/watch?v=example14",
                "notes": "Rotación externa activa, apuntar a las orejas"
              }
            ]
          },
          {
            "id": "C",
            "primary_muscles": ["bíceps"],
            "secondary_muscles": [],
            "exercises": [
              {
                "order": 5,
                "name": "Curl con Barra",
                "primary_group": "bíceps",
                "secondary_group": "",
                "series": 3,
                "reps": "10-12",
                "rpe": 8,
                "video_url": "https://www.youtube.com/watch?v=example15",
                "notes": "Codos fijos, sin balanceo"
              },
              {
                "order": 6,
                "name": "Curl Martillo",
                "primary_group": "bíceps",
                "secondary_group": "antebrazos",
                "series": 3,
                "reps": "12-15",
                "rpe": 7,
                "video_url": "https://www.youtube.com/watch?v=example16",
                "notes": "Alternar brazos o simultáneo"
              }
            ]
          }
        ]
      },
      {
        "id": "D4",
        "name": "Lower Body + Core",
        "focus": ["lower_body", "core"],
        "session_notes": [
          "Última sesión de la semana, mantener intensidad alta",
          "Core al final para no comprometer estabilidad en ejercicios principales"
        ],
        "blocks": [
          {
            "id": "A",
            "primary_muscles": ["cuádriceps", "glúteos"],
            "secondary_muscles": [],
            "exercises": [
              {
                "order": 1,
                "name": "Sentadilla Búlgara",
                "primary_group": "cuádriceps",
                "secondary_group": "glúteos",
                "series": 3,
                "reps": "10-12",
                "rpe": 8,
                "video_url": "https://www.youtube.com/watch?v=example17",
                "notes": "Por pierna, mantener equilibrio"
              },
              {
                "order": 2,
                "name": "Zancadas con Mancuernas",
                "primary_group": "cuádriceps",
                "secondary_group": "glúteos",
                "series": 3,
                "reps": "12-15",
                "rpe": 7,
                "video_url": "https://www.youtube.com/watch?v=example18",
                "notes": "Por pierna, rodilla no pasa la punta del pie"
              }
            ]
          },
          {
            "id": "B",
            "primary_muscles": ["glúteos", "isquiotibiales"],
            "secondary_muscles": [],
            "exercises": [
              {
                "order": 3,
                "name": "Hip Thrust con Barra",
                "primary_group": "glúteos",
                "secondary_group": "isquiotibiales",
                "series": 4,
                "reps": "10-12",
                "rpe": 8,
                "video_url": "https://www.youtube.com/watch?v=example19",
                "notes": "Contracción máxima arriba, barbilla neutra"
              },
              {
                "order": 4,
                "name": "Curl Femoral Sentado",
                "primary_group": "isquiotibiales",
                "secondary_group": "",
                "series": 3,
                "reps": "12-15",
                "rpe": 7,
                "video_url": "https://www.youtube.com/watch?v=example20",
                "notes": "Control en fase excéntrica"
              }
            ]
          },
          {
            "id": "C",
            "primary_muscles": ["core"],
            "secondary_muscles": [],
            "exercises": [
              {
                "order": 5,
                "name": "Plancha Abdominal",
                "primary_group": "core",
                "secondary_group": "",
                "series": 3,
                "reps": "45-60s",
                "rpe": 8,
                "video_url": "https://www.youtube.com/watch?v=example21",
                "notes": "Cuerpo alineado, glúteos activos"
              },
              {
                "order": 6,
                "name": "Russian Twists",
                "primary_group": "core",
                "secondary_group": "oblicuos",
                "series": 3,
                "reps": "20-30",
                "rpe": 7,
                "video_url": "https://www.youtube.com/watch?v=example22",
                "notes": "Con peso ligero, rotación controlada"
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

## ✅ VALIDACIÓN DE LA ESTRUCTURA

**Campos OBLIGATORIOS en la raíz:**
- ✅ `client_training_program_enriched` (objeto)

**Campos OBLIGATORIOS en client_training_program_enriched:**
- ✅ `title` (string)
- ✅ `summary` (string)
- ✅ `goal` (string)
- ✅ `training_type` (string)
- ✅ `days_per_week` (number)
- ✅ `session_duration_min` (number)
- ✅ `weeks` (number)
- ✅ `sessions` (array)

**Campos OPCIONALES:**
- `general_notes` (array de strings)

**Campos OBLIGATORIOS en cada session:**
- ✅ `id` (string: D1, D2, D3, D4...)
- ✅ `name` (string)
- ✅ `focus` (array de strings)
- ✅ `blocks` (array)

**Campos OPCIONALES en session:**
- `session_notes` (array de strings)

**Campos OBLIGATORIOS en cada block:**
- ✅ `id` (string: A, B, C...)
- ✅ `primary_muscles` (array de strings)
- ✅ `exercises` (array)

**Campos OPCIONALES en block:**
- `secondary_muscles` (array de strings)

**Campos OBLIGATORIOS en cada exercise:**
- ✅ `order` (number)
- ✅ `name` (string)
- ✅ `primary_group` (string)
- ✅ `series` (number)
- ✅ `reps` (string o number)
- ✅ `rpe` (number)
- ✅ `video_url` (string)

**Campos OPCIONALES en exercise:**
- `secondary_group` (string)
- `notes` (string)

---

## 🔴 ERRORES COMUNES A EVITAR

### ❌ ERROR 1: Respuesta sin el wrapper
```json
{
  "title": "...",
  "sessions": [...]
}
```
**INCORRECTO** - Falta el wrapper `client_training_program_enriched`

### ❌ ERROR 2: Responder con error
```json
{
  "error": "Invalid EDN360Input"
}
```
**INCORRECTO** - No debe devolver errores, debe generar el plan

### ❌ ERROR 3: Responder con texto
```
Aquí está el plan de entrenamiento...
```
**INCORRECTO** - Debe ser JSON puro, sin texto ni markdown

### ✅ CORRECTO:
```json
{
  "client_training_program_enriched": {
    ...todo el plan aquí...
  }
}
```

---

## 🎯 RESUMEN

**INPUT:** JSON con `user_profile`, `questionnaires`, `context`  
**OUTPUT:** JSON con `client_training_program_enriched` conteniendo el plan completo

**Clave:** Tus agentes deben recibir el INPUT, procesarlo, consultar tu BD de ejercicios, y devolver el OUTPUT en el formato exacto especificado.
