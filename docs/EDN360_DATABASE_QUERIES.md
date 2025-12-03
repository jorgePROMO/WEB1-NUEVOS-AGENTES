# EDN360 - Guía de Consultas y Operaciones de Base de Datos

**Versión:** 2.0.0  
**Fecha:** 2025-12-03  
**Propósito:** Guía práctica para consultar y manipular datos de EDN360

---

## Tabla de Contenidos

1. [Conexión a MongoDB](#1-conexión-a-mongodb)
2. [Consultas de Cuestionarios](#2-consultas-de-cuestionarios)
3. [Consultas de Planes](#3-consultas-de-planes)
4. [Consultas de Usuarios](#4-consultas-de-usuarios)
5. [Operaciones Comunes](#5-operaciones-comunes)
6. [Queries para Debugging](#6-queries-para-debugging)

---

## 1. Conexión a MongoDB

### Desde Terminal (mongosh)

```bash
# Conectar a test_database
mongosh test_database

# Conectar a edn360_app
mongosh edn360_app
```

### Desde Python (Backend)

```python
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Cliente MongoDB
client = AsyncIOMotorClient(os.getenv('MONGO_URL'))

# Base de datos test_database
db = client[os.getenv('MONGO_DB_NAME', 'test_database')]

# Base de datos edn360_app
edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
```

---

## 2. Consultas de Cuestionarios

### 2.1 Ver Todos los Cuestionarios de un Usuario

```javascript
// mongosh test_database
db.client_drawers.findOne(
  { user_id: "1764016044644335" },
  { "services.shared_questionnaires": 1, _id: 0 }
)
```

**Resultado esperado:**
```json
{
  "services": {
    "shared_questionnaires": [
      {
        "submission_id": "quest_inicial_001",
        "submitted_at": ISODate("2025-01-15T10:30:00Z"),
        "source": "edn360",
        "raw_payload": {
          "nombre_completo": "Jorge Calcerrada",
          "edad": 35,
          "objetivo_fisico": "Ganar músculo"
        }
      },
      {
        "submission_id": "quest_seguimiento_001",
        "submitted_at": ISODate("2025-01-25T11:00:00Z"),
        "source": "edn360",
        "raw_payload": {
          "seguimiento": 1,
          "progreso": "Bien, quiero más desafío"
        }
      }
    ]
  }
}
```

### 2.2 Contar Cuestionarios de un Usuario

```javascript
db.client_drawers.aggregate([
  { $match: { user_id: "1764016044644335" } },
  { $project: { 
      user_id: 1,
      num_cuestionarios: { $size: "$services.shared_questionnaires" }
  }}
])
```

### 2.3 Ver Solo el Cuestionario Inicial (Más Antiguo)

```javascript
db.client_drawers.aggregate([
  { $match: { user_id: "1764016044644335" } },
  { $project: {
      initial_questionnaire: { 
        $arrayElemAt: ["$services.shared_questionnaires", 0] 
      }
  }}
])
```

### 2.4 Ver Solo el Último Cuestionario

```javascript
db.client_drawers.aggregate([
  { $match: { user_id: "1764016044644335" } },
  { $project: {
      latest_questionnaire: { 
        $arrayElemAt: ["$services.shared_questionnaires", -1] 
      }
  }}
])
```

### 2.5 Buscar Cuestionario por submission_id

```javascript
db.client_drawers.findOne(
  {
    user_id: "1764016044644335",
    "services.shared_questionnaires.submission_id": "quest_inicial_001"
  },
  {
    "services.shared_questionnaires.$": 1
  }
)
```

### 2.6 Python: Obtener Todos los Cuestionarios

```python
from repositories.client_drawer_repository import get_drawer_by_user_id

user_id = "1764016044644335"
drawer = await get_drawer_by_user_id(user_id)

all_questionnaires = drawer.services.shared_questionnaires

# Ordenar por fecha
all_questionnaires.sort(key=lambda q: q.submitted_at)

# Inicial (más antiguo)
initial = all_questionnaires[0]

# Último
latest = all_questionnaires[-1]

# Todos los seguimientos (excluyendo el inicial)
followups = all_questionnaires[1:]
```

---

## 3. Consultas de Planes

### 3.1 Ver Todos los Planes de un Usuario

```javascript
// mongosh edn360_app
db.training_plans_v2.find(
  { user_id: "1764016044644335" },
  { _id: 1, created_at: 1, is_evolutionary: 1, "plan.title": 1 }
).sort({ created_at: 1 })
```

**Resultado esperado:**
```json
[
  {
    "_id": ObjectId("674eabcd1234567890abcdef"),
    "created_at": "2025-01-20T12:00:00Z",
    "is_evolutionary": false,
    "plan": {
      "title": "Plan Foundational Upper/Lower - 4 días/semana"
    }
  },
  {
    "_id": ObjectId("674eabcd1234567890fedcba"),
    "created_at": "2025-01-27T14:00:00Z",
    "is_evolutionary": true,
    "plan": {
      "title": "Plan Evolutivo Upper/Lower - Fase 2"
    }
  }
]
```

### 3.2 Ver Solo el Plan Más Reciente

```javascript
db.training_plans_v2.find(
  { user_id: "1764016044644335" }
).sort({ created_at: -1 }).limit(1)
```

### 3.3 Ver Estructura Completa de un Plan

```javascript
db.training_plans_v2.findOne(
  { _id: ObjectId("674eabcd1234567890abcdef") }
)
```

### 3.4 Ver Solo las Sesiones de un Plan

```javascript
db.training_plans_v2.findOne(
  { _id: ObjectId("674eabcd1234567890abcdef") },
  { "plan.sessions": 1, _id: 0 }
)
```

### 3.5 Ver Solo los Ejercicios del Día 1

```javascript
db.training_plans_v2.aggregate([
  { $match: { _id: ObjectId("674eabcd1234567890abcdef") } },
  { $unwind: "$plan.sessions" },
  { $match: { "plan.sessions.id": "D1" } },
  { $project: { 
      "session_name": "$plan.sessions.name",
      "exercises": "$plan.sessions.blocks.exercises"
  }}
])
```

### 3.6 Contar Planes por Usuario

```javascript
db.training_plans_v2.aggregate([
  { $group: {
      _id: "$user_id",
      total_planes: { $sum: 1 },
      planes_evolutivos: {
        $sum: { $cond: ["$is_evolutionary", 1, 0] }
      }
  }}
])
```

### 3.7 Python: Obtener Plan Más Reciente

```python
edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]

user_id = "1764016044644335"

latest_plan = await edn360_db.training_plans_v2.find_one(
    {"user_id": user_id},
    {"_id": 0}
).sort("created_at", -1)

if latest_plan:
    print(f"Título: {latest_plan['plan']['title']}")
    print(f"Es evolutivo: {latest_plan.get('is_evolutionary', False)}")
    print(f"Número de sesiones: {len(latest_plan['plan']['sessions'])}")
```

### 3.8 Python: Obtener Todos los Planes para STATE

```python
# Recuperar todos los planes ordenados
all_plans_cursor = edn360_db.training_plans_v2.find(
    {"user_id": user_id},
    {"_id": 1, "created_at": 1, "plan": 1}
).sort("created_at", 1)  # Ascendente (más antiguo → más reciente)

all_plans = await all_plans_cursor.to_list(length=100)

# Filtrar hasta un plan específico (si se proporciona)
if previous_training_plan_id:
    selected_plan_index = -1
    for i, plan in enumerate(all_plans):
        if str(plan["_id"]) == previous_training_plan_id:
            selected_plan_index = i
            break
    
    if selected_plan_index >= 0:
        previous_plans = all_plans[:selected_plan_index + 1]
        last_plan = previous_plans[-1] if previous_plans else None
else:
    previous_plans = all_plans
    last_plan = previous_plans[-1] if previous_plans else None
```

---

## 4. Consultas de Usuarios

### 4.1 Ver Información de un Usuario

```javascript
// mongosh test_database
db.users.findOne(
  { _id: "1764016044644335" },
  { password: 0 }  // Excluir password
)
```

### 4.2 Listar Todos los Usuarios (Solo Nombres)

```javascript
db.users.find(
  {},
  { _id: 1, name: 1, email: 1, role: 1 }
).limit(20)
```

### 4.3 Buscar Usuario por Email

```javascript
db.users.findOne(
  { email: "jorge@example.com" }
)
```

### 4.4 Python: Obtener Usuario

```python
from bson import ObjectId

user_id = "1764016044644335"
user = await db.users.find_one({"_id": user_id})

if user:
    print(f"Nombre: {user.get('name')}")
    print(f"Email: {user.get('email')}")
    print(f"Rol: {user.get('role')}")
```

---

## 5. Operaciones Comunes

### 5.1 Agregar un Nuevo Cuestionario

```javascript
// mongosh test_database
db.client_drawers.updateOne(
  { user_id: "1764016044644335" },
  {
    $push: {
      "services.shared_questionnaires": {
        submission_id: "quest_seguimiento_002",
        submitted_at: new Date("2025-02-05T10:00:00Z"),
        source: "edn360",
        raw_payload: {
          nombre_completo: "Jorge Calcerrada",
          seguimiento: 2,
          progreso: "Excelente, sin dolor",
          adherencia: "100%"
        }
      }
    }
  }
)
```

### 5.2 Actualizar un Plan (Marcar como Enviado)

```javascript
// mongosh edn360_app
db.training_plans_v2.updateOne(
  { _id: ObjectId("674eabcd1234567890abcdef") },
  { $set: { status: "sent" } }
)
```

### 5.3 Eliminar el Último Plan de un Usuario

```javascript
db.training_plans_v2.deleteOne(
  { user_id: "1764016044644335" },
  { sort: { created_at: -1 } }
)
```

### 5.4 Python: Crear un Plan Mock

```python
from datetime import datetime, timezone

training_plan_doc = {
    "user_id": "1764016044644335",
    "questionnaire_submission_id": "quest_inicial_001",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "status": "draft",
    "version": "2.0.0",
    "source": "edn360_workflow_evolutionary_v1",
    "is_evolutionary": False,
    "plan": {
        "title": "Plan de Prueba",
        "summary": "Plan mock para testing",
        "goal": "Testing",
        "training_type": "upper_lower",
        "days_per_week": 4,
        "session_duration_min": 45,
        "weeks": 4,
        "sessions": [],
        "general_notes": []
    }
}

result = await edn360_db.training_plans_v2.insert_one(training_plan_doc)
print(f"Plan insertado con ID: {result.inserted_id}")
```

---

## 6. Queries para Debugging

### 6.1 Verificar Integridad de Datos de un Usuario

```javascript
// mongosh test_database

// 1. Usuario existe
db.users.countDocuments({ _id: "1764016044644335" })
// Debe retornar: 1

// 2. Tiene client_drawer
db.client_drawers.countDocuments({ user_id: "1764016044644335" })
// Debe retornar: 1

// 3. Tiene cuestionarios
db.client_drawers.aggregate([
  { $match: { user_id: "1764016044644335" } },
  { $project: { 
      num_cuestionarios: { $size: "$services.shared_questionnaires" }
  }}
])
// Debe retornar: num_cuestionarios > 0

// mongosh edn360_app

// 4. Tiene planes
db.training_plans_v2.countDocuments({ user_id: "1764016044644335" })
// Puede retornar: 0 (primer plan) o > 0 (planes evolutivos)
```

### 6.2 Ver Último Plan Generado en Todas las BDs

```javascript
// mongosh edn360_app
db.training_plans_v2.find({}).sort({ created_at: -1 }).limit(5)
```

### 6.3 Buscar Planes con Errores

```javascript
db.training_plans_v2.find({
  $or: [
    { "plan.sessions": { $size: 0 } },  // Sin sesiones
    { "plan.title": { $exists: false } }  // Sin título
  ]
})
```

### 6.4 Ver Historial de un Usuario (Timeline)

```javascript
// mongosh (conectar a ambas BDs)
// Esta query combina cuestionarios y planes

// Cuestionarios
use test_database
db.client_drawers.aggregate([
  { $match: { user_id: "1764016044644335" } },
  { $unwind: "$services.shared_questionnaires" },
  { $project: {
      type: { $literal: "questionnaire" },
      id: "$services.shared_questionnaires.submission_id",
      date: "$services.shared_questionnaires.submitted_at"
  }},
  { $sort: { date: 1 } }
])

// Planes
use edn360_app
db.training_plans_v2.aggregate([
  { $match: { user_id: "1764016044644335" } },
  { $project: {
      type: { $literal: "plan" },
      id: "$_id",
      title: "$plan.title",
      date: { $toDate: "$created_at" },
      is_evolutionary: 1
  }},
  { $sort: { date: 1 } }
])
```

**Resultado esperado (combinado):**
```
2025-01-15 | questionnaire | quest_inicial_001
2025-01-20 | plan          | Plan Foundational (is_evolutionary: false)
2025-01-25 | questionnaire | quest_seguimiento_001
2025-01-27 | plan          | Plan Evolutivo Fase 2 (is_evolutionary: true)
2025-02-05 | questionnaire | quest_seguimiento_002
2025-02-10 | plan          | Plan Evolutivo Fase 3 (is_evolutionary: true)
```

### 6.5 Verificar STATE Construido (Python Debug)

```python
import json

user_id = "1764016044644335"
current_questionnaire_id = "quest_seguimiento_001"
previous_training_plan_id = "674eabcd1234567890abcdef"

# 1. Cuestionarios
drawer = await get_drawer_by_user_id(user_id)
all_questionnaires = drawer.services.shared_questionnaires
all_questionnaires.sort(key=lambda q: q.submitted_at)

initial_questionnaire = all_questionnaires[0]
current_q = next((q for q in all_questionnaires if q.submission_id == current_questionnaire_id), None)
current_q_index = all_questionnaires.index(current_q) if current_q else -1
previous_followups = all_questionnaires[1:current_q_index] if current_q_index > 1 else []

# 2. Planes
edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
all_plans = await edn360_db.training_plans_v2.find(
    {"user_id": user_id},
    {"_id": 1, "created_at": 1, "plan": 1}
).sort("created_at", 1).to_list(length=100)

# Filtrar hasta previous_training_plan_id
selected_plan_index = -1
for i, plan in enumerate(all_plans):
    if str(plan["_id"]) == previous_training_plan_id:
        selected_plan_index = i
        break

if selected_plan_index >= 0:
    previous_plans = all_plans[:selected_plan_index + 1]
    last_plan = previous_plans[-1] if previous_plans else None
else:
    previous_plans = all_plans
    last_plan = previous_plans[-1] if previous_plans else None

# 3. Imprimir STATE
print("=" * 50)
print("STATE CONSTRUIDO:")
print("=" * 50)
print(f"Initial Questionnaire: {initial_questionnaire.submission_id}")
print(f"Current Questionnaire: {current_q.submission_id if current_q else 'None'}")
print(f"Previous Followups: {len(previous_followups)}")
print(f"Previous Plans: {len(previous_plans)}")
print(f"Last Plan: {last_plan['plan']['title'] if last_plan else 'None'}")
print(f"Is Evolutionary: {bool(last_plan)}")
print("=" * 50)
```

### 6.6 Verificar Logs del Workflow

```bash
# Ver logs del microservicio
tail -f /var/log/supervisor/edn360-workflow-service.out.log

# Buscar ejecuciones recientes
tail -n 200 /var/log/supervisor/edn360-workflow-service.out.log | grep -E "Detectado flujo|Tipo de generación|Previous plans"

# Ver logs del backend
tail -f /var/log/supervisor/backend.err.log

# Buscar construcción de STATE
tail -n 200 /var/log/supervisor/backend.err.log | grep -E "Cuestionarios recuperados|Planes previos recuperados|STATE construido"
```

---

## Resumen de Comandos Útiles

### Consulta Rápida: ¿Cuántos cuestionarios y planes tiene un usuario?

```javascript
// mongosh
use test_database
db.client_drawers.aggregate([
  { $match: { user_id: "USER_ID" } },
  { $project: { 
      num_cuestionarios: { $size: "$services.shared_questionnaires" }
  }}
])

use edn360_app
db.training_plans_v2.countDocuments({ user_id: "USER_ID" })
```

### Consulta Rápida: ¿Cuál es el último plan y es evolutivo?

```javascript
// mongosh edn360_app
db.training_plans_v2.find(
  { user_id: "USER_ID" },
  { _id: 1, created_at: 1, is_evolutionary: 1, "plan.title": 1 }
).sort({ created_at: -1 }).limit(1)
```

### Consulta Rápida: Timeline completo de un usuario

```bash
# Desde terminal con Python
python3 << 'EOF'
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def get_timeline(user_id):
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = client['test_database']
    edn360_db = client['edn360_app']
    
    # Cuestionarios
    drawer = await db.client_drawers.find_one({"user_id": user_id})
    if drawer:
        quests = drawer.get("services", {}).get("shared_questionnaires", [])
        print(f"Cuestionarios: {len(quests)}")
        for q in quests:
            print(f"  - {q['submitted_at']}: {q['submission_id']}")
    
    # Planes
    plans = await edn360_db.training_plans_v2.find(
        {"user_id": user_id}
    ).sort("created_at", 1).to_list(length=100)
    print(f"\nPlanes: {len(plans)}")
    for p in plans:
        print(f"  - {p['created_at']}: {p['plan']['title']} (evolutionary: {p.get('is_evolutionary', False)})")

asyncio.run(get_timeline("USER_ID"))
EOF
```

---

**Nota:** Reemplaza `"USER_ID"` con el ID real del usuario en todas las consultas.
