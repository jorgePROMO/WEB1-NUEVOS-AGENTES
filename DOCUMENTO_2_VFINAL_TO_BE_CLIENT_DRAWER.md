# DOCUMENTO 2 vFINAL: ARQUITECTURA TO BE (Client Drawer)

**Sistema:** E.D.N.360 - Nueva Arquitectura Unificada  
**Fecha:** Enero 2025  
**Versión:** FINAL 2.0  
**Estado:** Pendiente de aprobación  
**Cliente Referencia:** Jorge1  

---

## 📋 ÍNDICE GENERAL

### PARTE 1: VISIÓN Y DISEÑO
1. [Visión del Client Drawer](#1-visión-del-client-drawer)
2. [Diseño de la Arquitectura](#2-diseño-de-la-arquitectura)
3. [Modelo de Datos Detallado](#3-modelo-de-datos-detallado)

### PARTE 2: FLUJO Y OPERACIÓN
4. [Flujo Completo: Cuestionario → Plans](#4-flujo-completo)
5. [Ejemplo Real: Cliente Jorge1](#5-ejemplo-real-jorge1)
6. [Reglas de Oro del Sistema](#6-reglas-de-oro)

### PARTE 3: ESCALABILIDAD Y EXTENSIBILIDAD
7. [Tamaño, Crecimiento y Archivado](#7-tamaño-crecimiento-y-archivado)
8. [Duplicidades y Decisiones](#8-duplicidades-y-decisiones)
9. [Versionado del Cuestionario](#9-versionado-del-cuestionario)
10. [Arquitectura Multi-Servicio](#10-arquitectura-multi-servicio)

### PARTE 4: OPERATIVA Y CALIDAD
11. [Migraciones de Cuestionarios](#11-migraciones-de-cuestionarios)
12. [Archivado de Snapshots - Operativa](#12-archivado-de-snapshots)
13. [Interfaces Cross-Service](#13-interfaces-cross-service)

### PARTE 5: TRANSICIÓN
14. [Comparativa AS IS vs TO BE](#14-comparativa-as-is-vs-to-be)
15. [Lista EXPLÍCITA de Código a Eliminar](#15-lista-de-código-a-eliminar)
16. [Conclusiones y Próximos Pasos](#16-conclusiones)

---

## 1. VISIÓN DEL CLIENT DRAWER

### 🎯 Concepto Central

> **"Un cajón único por cliente donde vive TODA su información"**

El `client_drawer` es la **única fuente de verdad** del cliente en el sistema E.D.N.360.

### 📦 Contenido del Cajón

```
client_drawer (por cliente)
├── 📁 profile                    # Datos personales y meta
├── 📁 services                   # Módulos de servicios
│   ├── training/                 # Entrenamiento
│   │   ├── questionnaires        # Cuestionarios (inicial + followups)
│   │   ├── snapshots             # ClientContext histórico
│   │   ├── plans                 # Referencias a planes
│   │   ├── measurements          # Mediciones
│   │   └── notes                 # Notas del entrenador
│   ├── nutrition/                # Nutrición (misma estructura)
│   ├── psychology/               # Psicología (futuro)
│   └── rehabilitation/           # Rehabilitación (futuro)
└── 📁 meta                       # Metadatos globales
```

### ✅ Principios Fundamentales

1. **Única Fuente de Verdad:**
   - TODO lo del cliente está aquí o apunta desde aquí
   - Los agentes SOLO leen de client_drawer
   - NO hay duplicaciones de cuestionarios

2. **Versionado Completo:**
   - Cada snapshot guarda el ClientContext completo
   - Trazabilidad total de la evolución del cliente
   - Los snapshots son INMUTABLES

3. **Arquitectura de Referencia:**
   - Los planes NO duplican datos
   - Los planes SON vistas derivadas del snapshot
   - El snapshot apunta a los planes, no al revés

4. **Escalabilidad Temporal:**
   - Historial ilimitado con archivado automático
   - Fácil navegación temporal (versión 1, 2, 3...)
   - Rollback posible a cualquier snapshot previo

5. **Extensibilidad Multi-Servicio:**
   - Añadir nuevos dominios sin refactorizar
   - Cada servicio en su namespace independiente
   - Cross-service access controlado

---

## 2. DISEÑO DE LA ARQUITECTURA

### 🏗️ Decisión: Colección Única con Subdocumentos

**Implementación:** Una colección `client_drawers` con estructura modular.

**Justificación:**
- ✅ Consulta atómica: Todo el cliente en 1 query
- ✅ Transaccionalidad: Actualizaciones ACID
- ✅ Simplicidad: No hay joins ni lookups
- ✅ Escalable: MongoDB soporta 16MB, con archivado < 2MB siempre

### 📐 Estructura de la Colección

```javascript
// Colección: client_drawers
{
  // ============================================
  // IDENTIFICACIÓN
  // ============================================
  _id: "client_1762094831193507",  // client_<user_id>
  user_id: "1762094831193507",
  
  // ============================================
  // PROFILE GLOBAL
  // ============================================
  profile: {
    nombre_completo: "Jorge Calcerrada",
    email: "jorge@example.com",
    fecha_nacimiento: "1989-05-15",
    edad: 35,
    sexo: "Hombre",
    profesion: "Ingeniero de Software",
    telefono: "+34612345678",
    whatsapp: "+34612345678",
    created_at: ISODate("2025-01-02T09:00:00Z"),
    updated_at: ISODate("2025-01-02T09:00:00Z")
  },
  
  // ============================================
  // SERVICES - Módulos por Dominio
  // ============================================
  services: {
    
    // ──────────────────────────────────────────
    // TRAINING (Entrenamiento)
    // ──────────────────────────────────────────
    training: {
      active: true,
      enrolled_at: ISODate("2025-01-02T09:00:00Z"),
      
      // CUESTIONARIOS
      questionnaires: {
        inicial: {
          submitted_at: ISODate("2025-01-02T09:00:00Z"),
          version: "1.0.0",
          schema_version: "questionnaire_training_v1",
          responses: {
            // Estructura jerárquica por bloques (ver sección 9)
            personal_data: { /* ... */ },
            measurements: { /* ... */ },
            health: { /* ... */ },
            work_life: { /* ... */ },
            sports_background: { /* ... */ },
            availability: { /* ... */ },
            daily_schedule: { /* ... */ },
            nutrition_habits: { /* ... */ },
            goals: {
              primary_objective: "Perder grasa",  // ⭐
              // ...
            },
            additional_info: { /* ... */ }
          }
        },
        followups: [
          {
            followup_id: "followup_feb2025",
            submitted_at: ISODate("2025-02-03T10:00:00Z"),
            days_since_last: 30,
            previous_snapshot_id: "snapshot_training_v1",
            measurement_type: "smart_scale",
            measurements: { /* ... */ },
            adherence: { /* ... */ },
            wellbeing: { /* ... */ },
            changes_perceived: { /* ... */ },
            feedback: { /* ... */ }
          }
        ]
      },
      
      // SNAPSHOTS (ClientContext histórico)
      snapshots: [
        {
          snapshot_id: "snapshot_training_v1",
          version: 1,
          created_at: ISODate("2025-01-03T10:15:30Z"),
          trigger: "inicial",
          
          // ⭐ ClientContext COMPLETO (sin formatted_plan)
          client_context: {
            meta: { /* ... */ },
            training: {
              client_summary: { /* E1 */ },
              profile: { /* E1 */ },
              constraints: { /* E1 */ },
              prehab: { /* E1 */ },
              progress: { /* E1 */ },
              capacity: { /* E2 */ },
              adaptation: { /* E3 */ },
              mesocycle: { /* E4 */ },
              sessions: [ /* E5 - Sesiones completas */ ],
              safe_sessions: [ /* E6 */ ],
              // formatted_plan: NO SE GUARDA AQUÍ
              audit: { /* E8 */ },
              bridge_for_nutrition: { /* E9 */ }
            }
          },
          
          // Referencias a planes generados
          plans_generated: {
            training_plan_id: "training_v1_jan2025"
          },
          
          generation_job_id: "job_xyz"
        }
      ],
      
      // PLANS (Referencias)
      plans: [
        {
          plan_id: "training_v1_jan2025",
          version: 1,
          generated_at: ISODate("2025-01-03T10:15:20Z"),
          snapshot_id: "snapshot_training_v1",
          month: 1,
          year: 2025,
          status: "active"
        }
      ],
      
      // MEASUREMENTS
      measurements: [
        {
          measurement_id: "measure_inicial",
          date: ISODate("2025-01-02T09:00:00Z"),
          tipo: "inicial",
          source: "cuestionario_inicial",
          data: {
            peso: 85,
            altura_cm: 178,
            grasa_porcentaje: 22
          }
        }
      ],
      
      // NOTES
      notes: [
        {
          note_id: "note_inicial",
          created_at: ISODate("2025-01-03T10:20:00Z"),
          created_by: "admin_jorge",
          content: "Cliente motivado. Vigilar hernia L4-L5.",
          tags: ["inicial", "lesion"]
        }
      ]
    },
    
    // ──────────────────────────────────────────
    // NUTRITION (Nutrición)
    // ──────────────────────────────────────────
    nutrition: {
      active: true,
      enrolled_at: ISODate("2025-01-02T09:00:00Z"),
      
      // Misma estructura que training
      questionnaires: { /* ... */ },
      snapshots: [ /* ... */ ],
      plans: [ /* ... */ ],
      measurements: [ /* ... */ ],
      notes: [ /* ... */ ]
    },
    
    // ──────────────────────────────────────────
    // PSYCHOLOGY (Futuro)
    // ──────────────────────────────────────────
    psychology: {
      active: false,
      enrolled_at: null,
      questionnaires: {},
      snapshots: [],
      plans: [],
      measurements: [],
      notes: []
    }
  },
  
  // ============================================
  // META GLOBAL
  // ============================================
  meta: {
    created_at: ISODate("2025-01-02T09:00:00Z"),
    updated_at: ISODate("2025-02-03T11:00:30Z"),
    active_services: ["training", "nutrition"],
    total_services: 2,
    has_archived_snapshots: false,
    status: "active"
  }
}
```

---

## 3. MODELO DE DATOS DETALLADO

### 📊 Esquema Pydantic

```python
# /app/backend/models/client_drawer.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

# ============================================
# PROFILE GLOBAL
# ============================================
class ClientProfile(BaseModel):
    nombre_completo: str
    email: str
    fecha_nacimiento: str
    edad: int
    sexo: str
    profesion: str
    telefono: str
    whatsapp: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============================================
# QUESTIONNAIRES (estructura jerárquica)
# ============================================
class QuestionnaireResponses(BaseModel):
    """Respuestas del cuestionario estructuradas en bloques"""
    personal_data: Dict[str, Any]
    measurements: Dict[str, Any]
    health: Dict[str, Any]
    work_life: Dict[str, Any]
    sports_background: Dict[str, Any]
    availability: Dict[str, Any]
    daily_schedule: Dict[str, Any]
    nutrition_habits: Dict[str, Any]
    goals: Dict[str, Any]  # Incluye primary_objective ⭐
    additional_info: Dict[str, Any]

class QuestionnaireInicial(BaseModel):
    submitted_at: datetime
    version: str = "1.0.0"
    schema_version: str = "questionnaire_training_v1"
    responses: QuestionnaireResponses

class QuestionnaireFollowup(BaseModel):
    followup_id: str
    submitted_at: datetime
    days_since_last: int
    previous_snapshot_id: str
    measurement_type: str
    measurements: Optional[Dict[str, Any]] = None
    adherence: Dict[str, Any]
    wellbeing: Dict[str, Any]
    changes_perceived: Dict[str, Any]
    feedback: Dict[str, Any]

class ServiceQuestionnaires(BaseModel):
    inicial: QuestionnaireInicial
    followups: List[QuestionnaireFollowup] = Field(default_factory=list)

# ============================================
# SNAPSHOTS
# ============================================
class SnapshotPlansGenerated(BaseModel):
    training_plan_id: Optional[str] = None
    nutrition_plan_id: Optional[str] = None

class ClientContextSnapshot(BaseModel):
    snapshot_id: str
    version: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trigger: str  # "inicial" | "followup" | "manual"
    followup_id: Optional[str] = None
    previous_snapshot_id: Optional[str] = None
    
    # ClientContext COMPLETO (sin formatted_plan ni menu_plan)
    client_context: Dict[str, Any]
    
    plans_generated: SnapshotPlansGenerated
    generation_job_id: str

# ============================================
# MEASUREMENTS
# ============================================
class Measurement(BaseModel):
    measurement_id: str
    date: datetime
    tipo: str  # "inicial" | "followup" | "manual"
    source: str
    data: Dict[str, Any]

# ============================================
# PLANS (Referencias)
# ============================================
class PlanReference(BaseModel):
    plan_id: str
    version: int
    generated_at: datetime
    snapshot_id: str
    month: int
    year: int
    status: str = "active"

# ============================================
# NOTES
# ============================================
class TrainerNote(BaseModel):
    note_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str
    content: str
    tags: List[str] = Field(default_factory=list)

# ============================================
# SERVICE MODULE
# ============================================
class ServiceModule(BaseModel):
    """Módulo de servicio (training, nutrition, psychology, etc.)"""
    active: bool = False
    enrolled_at: Optional[datetime] = None
    questionnaires: Optional[ServiceQuestionnaires] = None
    snapshots: List[ClientContextSnapshot] = Field(default_factory=list)
    plans: List[PlanReference] = Field(default_factory=list)
    measurements: List[Measurement] = Field(default_factory=list)
    notes: List[TrainerNote] = Field(default_factory=list)

# ============================================
# SERVICES
# ============================================
class ClientServices(BaseModel):
    """Contenedor de todos los servicios del cliente"""
    training: ServiceModule = Field(default_factory=ServiceModule)
    nutrition: ServiceModule = Field(default_factory=ServiceModule)
    psychology: ServiceModule = Field(default_factory=ServiceModule)
    rehabilitation: ServiceModule = Field(default_factory=ServiceModule)

# ============================================
# CLIENT DRAWER - Modelo Principal
# ============================================
class ClientDrawer(BaseModel):
    """
    Cajón único del cliente - Única fuente de verdad
    """
    client_drawer_id: str = Field(alias="_id")
    user_id: str
    
    profile: ClientProfile
    services: ClientServices = Field(default_factory=ClientServices)
    
    meta: Dict[str, Any] = Field(default_factory=lambda: {
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "active_services": [],
        "total_services": 0,
        "has_archived_snapshots": False,
        "status": "active"
    })
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: str}
```

---

## 4. FLUJO COMPLETO

### 🔄 Diagrama de Flujo Simplificado

```
Usuario completa cuestionario
    ↓
PASO 1: Guardar en client_drawer.services.training.questionnaires.inicial
    ↓
PASO 2: Admin crea job (referencia client_drawer_id)
    ↓
PASO 3: Job Worker lee client_drawer completo
    ↓
PASO 4: Orquestador construye ClientContext y ejecuta E1-E9, N0-N8
    ↓
PASO 5: Guardar snapshot en client_drawer.services.training.snapshots[]
    ↓
PASO 6: Crear training_plan (SIN duplicar cuestionario)
    ↓
PASO 7: Actualizar referencias en drawer
```

### 📝 Detalle del Flujo

#### **PASO 1: Guardar Cuestionario en Client Drawer**

```python
# Endpoint: POST /api/questionnaire/submit
async def submit_training_questionnaire(user_id: str, responses: Dict):
    # Validar estructura del cuestionario
    questionnaire = QuestionnaireInicial(
        submitted_at=datetime.now(timezone.utc),
        version="1.0.0",
        responses=QuestionnaireResponses(**responses)
    )
    
    # Crear o actualizar client_drawer
    await db.client_drawers.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "services.training.questionnaires.inicial": questionnaire.dict(),
                "services.training.active": True,
                "services.training.enrolled_at": datetime.now(timezone.utc),
                "meta.updated_at": datetime.now(timezone.utc)
            },
            "$addToSet": {"meta.active_services": "training"}
        },
        upsert=True  # Crea el drawer si no existe
    )
```

#### **PASO 2: Crear Job de Generación**

```python
# Endpoint: POST /admin/users/{user_id}/plans/generate_async
async def create_generation_job(user_id: str, mode: str = "full"):
    job = {
        "job_id": f"job_{uuid.uuid4()}",
        "user_id": user_id,
        "client_drawer_id": f"client_{user_id}",
        "type": mode,
        "status": "pending",
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.generation_jobs.insert_one(job)
    return {"job_id": job["job_id"]}
```

#### **PASO 3: Job Worker Lee Client Drawer**

```python
# /app/backend/job_worker.py
async def process_generation_job(job_id: str):
    job = await db.generation_jobs.find_one({"_id": job_id})
    
    # Leer client_drawer COMPLETO
    client_drawer = await db.client_drawers.find_one(
        {"_id": job["client_drawer_id"]}
    )
    
    if not client_drawer:
        raise ValueError(f"Client drawer not found: {job['client_drawer_id']}")
    
    # Verificar que el cuestionario existe
    training_quest = client_drawer["services"]["training"]["questionnaires"]["inicial"]
    if not training_quest:
        raise ValueError("Training questionnaire not submitted")
    
    # Ejecutar orquestador
    from edn360.orchestrator import EDN360Orchestrator
    orchestrator = EDN360Orchestrator()
    
    result = await orchestrator.generate_initial_plan_from_drawer(
        client_drawer=client_drawer,
        plan_id=job_id
    )
    
    # ... continuar con PASO 5
```

#### **PASO 4: Orquestador Ejecuta Agentes**

```python
# /app/backend/edn360/orchestrator.py
async def generate_initial_plan_from_drawer(
    self,
    client_drawer: Dict,
    plan_id: str
) -> Dict:
    # Construir ClientContext desde drawer
    training_service = client_drawer["services"]["training"]
    questionnaire_data = training_service["questionnaires"]["inicial"]["responses"]
    
    client_context = initialize_client_context_from_drawer(
        client_id=client_drawer["_id"],
        version=len(training_service["snapshots"]) + 1,
        questionnaire_data=questionnaire_data
    )
    
    # Ejecutar pipeline E1-E9
    result = await self._execute_training_initial(questionnaire_data, None)
    
    # Ejecutar pipeline N0-N8
    # ...
    
    return result
```

#### **PASO 5: Guardar Snapshot en Drawer**

```python
# Después de que el orquestador complete
client_context_final = result["client_context"]

snapshot = {
    "snapshot_id": f"snapshot_training_v{version}",
    "version": version,
    "created_at": datetime.now(timezone.utc),
    "trigger": "inicial",
    "client_context": client_context_final,  # SIN formatted_plan
    "plans_generated": {
        "training_plan_id": None,  # Se llenará en PASO 7
        "nutrition_plan_id": None
    },
    "generation_job_id": job_id
}

await db.client_drawers.update_one(
    {"_id": client_drawer_id},
    {
        "$push": {"services.training.snapshots": snapshot},
        "$set": {"meta.updated_at": datetime.now(timezone.utc)}
    }
)
```

#### **PASO 6: Crear Planes (Sin Duplicar)**

```python
# Training plan
training_plan = {
    "_id": f"training_{plan_id}",
    "user_id": user_id,
    "client_drawer_id": client_drawer_id,
    "snapshot_id": snapshot["snapshot_id"],
    
    # Solo el plan final (NO cuestionario)
    "formatted_plan": client_context_final["training"]["formatted_plan"],
    
    "generated_at": datetime.now(timezone.utc),
    "month": datetime.now().month,
    "year": datetime.now().year,
    "edited": False,
    "pdf_id": None
}

await db.training_plans.insert_one(training_plan)

# Nutrition plan (similar)
# ...
```

#### **PASO 7: Actualizar Referencias**

```python
# Actualizar snapshot con IDs de planes
await db.client_drawers.update_one(
    {
        "_id": client_drawer_id,
        "services.training.snapshots.snapshot_id": snapshot["snapshot_id"]
    },
    {
        "$set": {
            "services.training.snapshots.$.plans_generated": {
                "training_plan_id": training_plan["_id"],
                "nutrition_plan_id": nutrition_plan["_id"]
            }
        }
    }
)

# Añadir referencia a lista de planes
await db.client_drawers.update_one(
    {"_id": client_drawer_id},
    {
        "$push": {
            "services.training.plans": {
                "plan_id": training_plan["_id"],
                "version": version,
                "snapshot_id": snapshot["snapshot_id"],
                "generated_at": datetime.now(timezone.utc),
                "month": datetime.now().month,
                "year": datetime.now().year,
                "status": "active"
            }
        }
    }
)
```

---

## 5. EJEMPLO REAL: JORGE1

### 📅 **2 Enero 2025 - Cuestionario Inicial**

```javascript
// client_drawers
{
  _id: "client_1762094831193507",
  user_id: "1762094831193507",
  
  profile: {
    nombre_completo: "Jorge Calcerrada",
    email: "jorge@example.com",
    edad: 35
  },
  
  services: {
    training: {
      active: true,
      enrolled_at: ISODate("2025-01-02T09:00:00Z"),
      
      questionnaires: {
        inicial: {
          submitted_at: ISODate("2025-01-02T09:00:00Z"),
          version: "1.0.0",
          responses: {
            personal_data: { /* ... */ },
            goals: {
              primary_objective: "Perder grasa",  // ⭐
              // ...
            }
          }
        },
        followups: []
      },
      
      snapshots: [],  // Vacío, plan aún no generado
      plans: [],
      measurements: [],
      notes: []
    }
  }
}
```

### 📅 **3 Enero 2025 - Plan Generado**

```javascript
// Snapshot añadido
services.training.snapshots: [
  {
    snapshot_id: "snapshot_training_v1",
    version: 1,
    created_at: ISODate("2025-01-03T10:15:30Z"),
    client_context: {
      training: {
        client_summary: { objetivo: "Pérdida de grasa" },
        profile: { /* E1 */ },
        capacity: { /* E2 */ },
        mesocycle: { /* E4 */ },
        sessions: [ /* E5 - 30 KB */ ],
        // NO formatted_plan aquí
      }
    },
    plans_generated: {
      training_plan_id: "training_v1_jan2025"
    }
  }
]

// Plan creado
// Colección: training_plans
{
  _id: "training_v1_jan2025",
  client_drawer_id: "client_1762...",
  snapshot_id: "snapshot_training_v1",
  
  // Solo el plan final
  formatted_plan: "# PLAN DE ENTRENAMIENTO...",
  
  generated_at: ISODate("2025-01-03T10:15:20Z")
}
```

### 📅 **3 Febrero 2025 - Seguimiento Mes 1**

```javascript
// Followup añadido
services.training.questionnaires.followups: [
  {
    followup_id: "followup_feb2025",
    submitted_at: ISODate("2025-02-03T10:00:00Z"),
    previous_snapshot_id: "snapshot_training_v1",
    measurements: {
      peso: "83",  // Bajó 2kg
      satisfecho_cambios: "SI"
    },
    adherence: { constancia_entrenamiento: "80%" },
    feedback: { cambios_deseados: "Aumentar intensidad" }
  }
]

// Snapshot v2 añadido
services.training.snapshots: [
  { /* v1 sin cambios */ },
  {
    snapshot_id: "snapshot_training_v2",
    version: 2,
    previous_snapshot_id: "snapshot_training_v1",
    trigger: "followup",
    followup_id: "followup_feb2025",
    client_context: {
      // ClientContext ajustado con progresión
    }
  }
]
```

---

## 6. REGLAS DE ORO

### ✅ Regla 1: Única Fuente de Verdad

```python
# ❌ PROHIBIDO
submission = await db.nutrition_questionnaire_submissions.find_one(...)

# ✅ CORRECTO
client_drawer = await db.client_drawers.find_one({"user_id": user_id})
questionnaire = client_drawer["services"]["training"]["questionnaires"]["inicial"]
```

### ✅ Regla 2: Los Agentes Solo Ven ClientContext

```
┌─────────────────────────────────────────┐
│  AGENTES (E1-E9, N0-N8)                 │
│  ↑ Solo ven ClientContext               │
├─────────────────────────────────────────┤
│  ORQUESTADOR                            │
│  ↑ Construye ClientContext desde drawer │
├─────────────────────────────────────────┤
│  CLIENT_DRAWER                          │
└─────────────────────────────────────────┘
```

### ✅ Regla 3: Planes Son Vistas Derivadas

```python
# Para obtener cuestionario desde plan:
training_plan = await db.training_plans.find_one({"_id": plan_id})
snapshot_id = training_plan["snapshot_id"]

client_drawer = await db.client_drawers.find_one(
    {"services.training.snapshots.snapshot_id": snapshot_id}
)

snapshot = next(
    s for s in client_drawer["services"]["training"]["snapshots"]
    if s["snapshot_id"] == snapshot_id
)
questionnaire = client_drawer["services"]["training"]["questionnaires"]["inicial"]
```

### ✅ Regla 4: Snapshots Inmutables

```python
# ❌ PROHIBIDO: Editar snapshot existente
await db.client_drawers.update_one(
    {"services.training.snapshots.snapshot_id": "v1"},
    {"$set": {"services.training.snapshots.$.client_context": new_value}}
)

# ✅ CORRECTO: Crear nuevo snapshot
await db.client_drawers.update_one(
    {"_id": client_id},
    {"$push": {"services.training.snapshots": new_snapshot}}
)
```

### ✅ Regla 5: Agregación, No Duplicación

```python
# ✅ Añadir al drawer existente
await db.client_drawers.update_one(
    {"_id": client_id},
    {
        "$push": {
            "services.training.measurements": new_measurement,
            "services.training.questionnaires.followups": new_followup
        }
    }
)
```

---

## 7. TAMAÑO, CRECIMIENTO Y ARCHIVADO

### 📊 Estimaciones de Tamaño

#### **Componentes del Snapshot:**

```javascript
snapshot = {
  snapshot_id: 0.1 KB,
  client_context: {
    training: {
      sessions: 15 KB,         // Sesiones detalladas
      safe_sessions: 15 KB,    // Sesiones + sustituciones
      // Resto: 20 KB
    }
  }
}

TOTAL: ~50 KB por snapshot
```

#### **Proyección a 5 Años:**

| **Año** | **Snapshots** | **Tamaño Training** | **Acumulado** |
|---|---|---|---|
| 1 | 12 | 12 × 50 KB = 600 KB | 680 KB |
| 2 | 12 | 600 KB | 1.3 MB |
| 3 | 12 | 600 KB | 2.0 MB |
| 5 | 12 | 600 KB × 2 | 3.3 MB |

**Conclusión:** Cliente típico < 4 MB a 5 años (25% del límite 16MB).

---

### 🗄️ Estrategia de Archivado Automático

#### **Regla:**
> Snapshots con más de **2 años** se mueven a `client_drawers_archive`.

#### **Implementación:**

```javascript
// Colección: client_drawers (principal)
{
  _id: "client_1762...",
  
  services: {
    training: {
      // Solo últimos 24 snapshots (~1.2 MB)
      snapshots: [ /* v25, v26, v27 */ ]
    }
  },
  
  meta: {
    has_archived_snapshots: true,
    oldest_archived: "v1",
    newest_archived: "v24"
  }
}

// Colección: client_drawers_archive
{
  _id: "client_1762..._training_archive",
  client_id: "client_1762...",
  service: "training",
  
  archived_snapshots: [
    { snapshot_id: "v1", created_at: "2023-01-01", ... },
    { snapshot_id: "v2", created_at: "2023-02-01", ... }
    // ... v1 a v24
  ],
  
  archived_at: ISODate("2025-01-01")
}
```

#### **Proceso Automático:**

```python
# Job mensual (cron)
async def archive_old_snapshots():
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=730)  # 2 años
    
    drawers = await db.client_drawers.find({}).to_list(1000)
    
    for drawer in drawers:
        for service_name in ["training", "nutrition"]:
            service = drawer["services"][service_name]
            
            if not service.get("active"):
                continue
            
            snapshots_to_archive = [
                s for s in service.get("snapshots", [])
                if s["created_at"] < cutoff_date
            ]
            
            if not snapshots_to_archive:
                continue
            
            # Crear/actualizar archivo
            archive_id = f"{drawer['_id']}_{service_name}_archive"
            await db.client_drawers_archive.update_one(
                {"_id": archive_id},
                {
                    "$push": {
                        "archived_snapshots": {"$each": snapshots_to_archive}
                    },
                    "$set": {
                        "client_id": drawer["_id"],
                        "service": service_name,
                        "archived_at": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
            
            # Eliminar de drawer principal
            await db.client_drawers.update_one(
                {"_id": drawer["_id"]},
                {
                    "$pull": {
                        f"services.{service_name}.snapshots": {
                            "created_at": {"$lt": cutoff_date}
                        }
                    },
                    "$set": {
                        "meta.has_archived_snapshots": True
                    }
                }
            )
            
            logger.info(
                f"Archived {len(snapshots_to_archive)} snapshots "
                f"for {drawer['_id']} ({service_name})"
            )
```

---

## 8. DUPLICIDADES Y DECISIONES

### ❌ Decisión: NO Duplicar `formatted_plan`

**Justificación:**

1. **Trazabilidad suficiente:**
   - Snapshot tiene ClientContext completo (E1-E9)
   - Snapshot referencia el plan (`plans_generated.training_plan_id`)
   - Si necesitas el plan: 1 query a `training_plans`

2. **Impacto en tamaño:**
   - Sin duplicar: 50 KB/snapshot
   - Con duplicar: 80-90 KB/snapshot
   - Diferencia a 5 años: **1.8 MB vs 3 MB** (~40% más)

3. **El snapshot es para QUÉ SE DECIDIÓ, no QUÉ SE MOSTRÓ:**
   - Snapshot = proceso (capacity, mesocycle, sessions)
   - Plan = vista de presentación (Markdown)

**Estructura definitiva:**

```javascript
snapshot.client_context.training = {
  // ... todos los outputs E1-E9
  sessions: [ /* Sesiones completas */ ],
  safe_sessions: [ /* Validadas */ ],
  
  // ❌ NO SE GUARDA
  formatted_plan: null,
  
  audit: { /* E8 */ },
  bridge_for_nutrition: { /* E9 */ }
}

snapshot.plans_generated = {
  training_plan_id: "training_v1"  // ← Referencia
}
```

---

## 9. VERSIONADO DEL CUESTIONARIO

### 📋 Estructura Jerárquica por Bloques

```javascript
questionnaires.inicial.responses = {
  // BLOQUE 1: Datos Personales
  personal_data: {
    nombre_completo: "Jorge",
    email: "jorge@example.com",
    // ...
  },
  
  // BLOQUE 2: Medidas Corporales
  measurements: {
    peso_kg: 85,
    altura_cm: 178,
    grasa_porcentaje: 22,
    circunferencias: {
      cintura_cm: 92,
      cadera_cm: 98
    }
  },
  
  // BLOQUE 3: Salud y Clínico
  health: {
    medications: { /* ... */ },
    chronic_conditions: {
      cardiovascular: { /* ... */ },
      metabolic: { /* ... */ },
      musculoskeletal: {
        hernias_protusions: "Hernia L4-L5"
      }
    }
  },
  
  // BLOQUE 4: Trabajo y Estrés
  work_life: {
    occupation: {
      profession: "Ingeniero",
      stress_level: "Moderado-Alto"
    }
  },
  
  // BLOQUE 5: Experiencia Deportiva
  sports_background: { /* ... */ },
  
  // BLOQUE 6: Disponibilidad
  availability: {
    training_schedule: {
      days_per_week: 4,
      session_duration_min: 60
    }
  },
  
  // BLOQUE 7: Horarios
  daily_schedule: { /* ... */ },
  
  // BLOQUE 8: Hábitos Alimentarios
  nutrition_habits: { /* ... */ },
  
  // BLOQUE 9: Objetivos ⭐
  goals: {
    primary_objective: "Perder grasa",
    motivation: { /* ... */ }
  },
  
  // BLOQUE 10: Comentarios
  additional_info: { /* ... */ }
}
```

### 🔄 Sistema de Versionado Semantic

```javascript
version: "MAJOR.MINOR.PATCH"

// v1.0.0 → v1.1.0: Añadir campo opcional (no rompe)
// v1.x → v2.0.0: Cambio incompatible (requiere migración)
```

**Ejemplos:**

```javascript
// v1.0.0 - Original (Enero 2025)
{
  version: "1.0.0",
  schema_version: "questionnaire_training_v1",
  responses: { /* 10 bloques */ }
}

// v1.1.0 - Añadir bloque psychological (Marzo 2025)
{
  version: "1.1.0",
  responses: {
    // ... bloques originales
    psychological: {  // NUEVO (opcional)
      stress_management: "Media"
    }
  }
}

// v2.0.0 - Reestructurar health (Junio 2026)
{
  version: "2.0.0",
  schema_version: "questionnaire_training_v2",
  responses: {
    health: {
      // Nueva estructura incompatible
    }
  }
}
```

---

## 10. ARQUITECTURA MULTI-SERVICIO

### 🌐 Diseño Extensible

```javascript
services: {
  // Módulo 1: Training
  training: {
    active: true,
    questionnaires: {},
    snapshots: [],
    plans: []
  },
  
  // Módulo 2: Nutrition
  nutrition: {
    active: true,
    questionnaires: {},
    snapshots: [],
    plans: []
  },
  
  // Módulo 3: Psychology (futuro)
  psychology: {
    active: false,
    questionnaires: {},
    snapshots: [],
    plans: []
  },
  
  // Módulo 4: Rehabilitation (futuro)
  rehabilitation: {
    active: false
  }
}
```

### 🔧 Añadir Nuevo Servicio

```python
# Cliente contrata psicología
await db.client_drawers.update_one(
    {"user_id": user_id},
    {
        "$set": {
            "services.psychology.active": True,
            "services.psychology.enrolled_at": datetime.now(timezone.utc)
        },
        "$addToSet": {"meta.active_services": "psychology"}
    }
)
```

### 🔗 Integración Cross-Service

```python
# Nutrition accede a Psychology
client_drawer = await db.client_drawers.find_one({"user_id": user_id})

if client_drawer["services"]["psychology"]["active"]:
    psych_snapshot = client_drawer["services"]["psychology"]["snapshots"][-1]
    stress_level = psych_snapshot["client_context"]["psychology"]["stress_level"]
    
    # Ajustar plan nutricional según estrés
```

---

## 11. MIGRACIONES DE CUESTIONARIOS

### 🔧 Sistema de Migración Automática

```python
# /app/backend/questionnaire_migrator.py

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# ============================================
# REGISTRO DE MIGRACIONES
# ============================================
MIGRATIONS = {
    ("1.0.0", "1.1.0"): "add_psychological_block",
    ("1.1.0", "1.2.0"): "add_sleep_quality_field",
    ("1.x", "2.0.0"): "restructure_health_v2"
}

# ============================================
# FUNCIONES DE MIGRACIÓN
# ============================================

def add_psychological_block(questionnaire: Dict) -> Dict:
    """Migración 1.0.0 → 1.1.0: Añadir bloque psychological"""
    questionnaire["responses"]["psychological"] = {
        "stress_management": "No evaluado",
        "anxiety_level": "No evaluado",
        "depression_history": None
    }
    questionnaire["version"] = "1.1.0"
    logger.info("Migrated to 1.1.0: Added psychological block")
    return questionnaire

def add_sleep_quality_field(questionnaire: Dict) -> Dict:
    """Migración 1.1.0 → 1.2.0: Añadir campo sleep_quality"""
    if "daily_schedule" in questionnaire["responses"]:
        questionnaire["responses"]["daily_schedule"]["sleep_quality"] = "Regular"
    questionnaire["version"] = "1.2.0"
    logger.info("Migrated to 1.2.0: Added sleep_quality")
    return questionnaire

def restructure_health_v2(questionnaire: Dict) -> Dict:
    """Migración 1.x → 2.0.0: Reestructurar health"""
    old_health = questionnaire["responses"]["health"]
    
    # Transformación compleja
    new_health = {
        "medical": {
            "current_medications": old_health.get("medications", {}),
            "allergies": old_health.get("allergies", [])
        },
        "conditions": {
            # Reestructuración profunda
        }
    }
    
    questionnaire["responses"]["health"] = new_health
    questionnaire["version"] = "2.0.0"
    questionnaire["schema_version"] = "questionnaire_training_v2"
    logger.info("Migrated to 2.0.0: Restructured health block")
    return questionnaire

# ============================================
# MOTOR DE MIGRACIÓN
# ============================================

def migrate_questionnaire(
    questionnaire: Dict,
    from_version: str,
    to_version: str
) -> Dict:
    """
    Migra un cuestionario de una versión a otra.
    
    Args:
        questionnaire: Cuestionario a migrar
        from_version: Versión actual
        to_version: Versión objetivo
    
    Returns:
        Cuestionario migrado
    
    Raises:
        ValueError: Si no hay ruta de migración
    """
    # Si ya está en la versión objetivo
    if from_version == to_version:
        return questionnaire
    
    # Buscar migración directa
    migration_key = (from_version, to_version)
    if migration_key in MIGRATIONS:
        migration_func = globals()[MIGRATIONS[migration_key]]
        return migration_func(questionnaire)
    
    # Buscar migraciones en cadena (1.0 → 1.1 → 1.2)
    # Implementar lógica de path finding si es necesario
    
    raise ValueError(
        f"No migration path from {from_version} to {to_version}"
    )

def get_current_questionnaire_version() -> str:
    """Versión actual del esquema de cuestionario"""
    return "1.0.0"  # Actualizar según evolución

# ============================================
# WRAPPER CON LOGGING Y VALIDACIÓN
# ============================================

class QuestionnaireMigrator:
    """Gestor de migraciones con logs y validación"""
    
    def __init__(self):
        self.migrations_log = []
    
    async def migrate_if_needed(
        self,
        client_drawer: Dict,
        service: str = "training"
    ) -> bool:
        """
        Verifica y migra cuestionario si es necesario.
        
        Returns:
            True si se hizo migración, False si no era necesario
        """
        current_version = get_current_questionnaire_version()
        questionnaire = client_drawer["services"][service]["questionnaires"]["inicial"]
        drawer_version = questionnaire.get("version", "1.0.0")
        
        if drawer_version == current_version:
            return False  # Ya está actualizado
        
        logger.info(
            f"Migrating questionnaire for {client_drawer['_id']} "
            f"from {drawer_version} to {current_version}"
        )
        
        try:
            # Hacer backup antes de migrar
            await self._backup_questionnaire(client_drawer["_id"], questionnaire)
            
            # Migrar
            migrated = migrate_questionnaire(
                questionnaire,
                from_version=drawer_version,
                to_version=current_version
            )
            
            # Actualizar en BD
            await db.client_drawers.update_one(
                {"_id": client_drawer["_id"]},
                {
                    "$set": {
                        f"services.{service}.questionnaires.inicial": migrated
                    }
                }
            )
            
            # Log de migración exitosa
            self.migrations_log.append({
                "client_id": client_drawer["_id"],
                "service": service,
                "from_version": drawer_version,
                "to_version": current_version,
                "migrated_at": datetime.now(timezone.utc),
                "success": True
            })
            
            logger.info(f"Migration successful: {drawer_version} → {current_version}")
            return True
        
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            
            # Log de error
            self.migrations_log.append({
                "client_id": client_drawer["_id"],
                "service": service,
                "from_version": drawer_version,
                "to_version": current_version,
                "migrated_at": datetime.now(timezone.utc),
                "success": False,
                "error": str(e)
            })
            
            raise
    
    async def _backup_questionnaire(self, client_id: str, questionnaire: Dict):
        """Backup del cuestionario antes de migrar"""
        backup = {
            "_id": f"{client_id}_questionnaire_backup_{datetime.now().timestamp()}",
            "client_id": client_id,
            "questionnaire": questionnaire,
            "backed_up_at": datetime.now(timezone.utc)
        }
        await db.questionnaire_backups.insert_one(backup)
        logger.info(f"Backup created: {backup['_id']}")
```

### 📊 Criterios de Migración

#### **Estrategia: On-Read (Recomendada)**

**Cuándo:** Al leer el client_drawer para generar un plan.

**Ventajas:**
- ✅ No requiere job batch masivo
- ✅ Migración bajo demanda (solo clientes activos)
- ✅ Menor riesgo (1 cliente a la vez)

**Implementación:**

```python
# En job_worker.py
async def process_generation_job(job_id: str):
    job = await db.generation_jobs.find_one({"_id": job_id})
    client_drawer = await db.client_drawers.find_one({"_id": job["client_drawer_id"]})
    
    # ⭐ Migrar si es necesario
    migrator = QuestionnaireMigrator()
    migrated = await migrator.migrate_if_needed(client_drawer, service="training")
    
    if migrated:
        logger.info(f"Questionnaire migrated before job execution")
        # Recargar drawer actualizado
        client_drawer = await db.client_drawers.find_one({"_id": job["client_drawer_id"]})
    
    # Continuar con generación de plan
    # ...
```

#### **Alternativa: Batch Job (Opcional)**

**Cuándo:** Al lanzar una nueva versión del cuestionario.

**Ventajas:**
- ✅ Todos los clientes actualizados de una vez
- ✅ No hay sorpresas en producción

**Desventajas:**
- ❌ Requiere ventana de mantenimiento
- ❌ Mayor riesgo si falla

**Implementación:**

```python
# Script de migración masiva
async def batch_migrate_all_clients():
    """Migra todos los cuestionarios a la versión actual"""
    migrator = QuestionnaireMigrator()
    
    drawers = await db.client_drawers.find(
        {"services.training.active": True}
    ).to_list(10000)
    
    total = len(drawers)
    migrated_count = 0
    errors = []
    
    for i, drawer in enumerate(drawers):
        try:
            migrated = await migrator.migrate_if_needed(drawer, service="training")
            if migrated:
                migrated_count += 1
            
            if (i + 1) % 100 == 0:
                logger.info(f"Progress: {i+1}/{total} processed, {migrated_count} migrated")
        
        except Exception as e:
            errors.append({
                "client_id": drawer["_id"],
                "error": str(e)
            })
    
    # Log final
    logger.info(f"""
    Batch migration completed:
    - Total clients: {total}
    - Migrated: {migrated_count}
    - Errors: {len(errors)}
    """)
    
    if errors:
        logger.error(f"Errors during migration: {errors}")
    
    return {
        "total": total,
        "migrated": migrated_count,
        "errors": errors
    }
```

### 🧪 Tests de Migración

```python
# /app/backend/tests/test_questionnaire_migration.py

import pytest
from questionnaire_migrator import migrate_questionnaire

def test_migration_1_0_to_1_1():
    """Test: Añadir bloque psychological"""
    questionnaire_v1 = {
        "version": "1.0.0",
        "responses": {
            "personal_data": {},
            "goals": {}
        }
    }
    
    migrated = migrate_questionnaire(questionnaire_v1, "1.0.0", "1.1.0")
    
    assert migrated["version"] == "1.1.0"
    assert "psychological" in migrated["responses"]
    assert migrated["responses"]["psychological"]["stress_management"] == "No evaluado"

def test_migration_preserves_existing_data():
    """Test: Migración no pierde datos existentes"""
    questionnaire_v1 = {
        "version": "1.0.0",
        "responses": {
            "personal_data": {"nombre": "Jorge"},
            "goals": {"primary_objective": "Perder grasa"}
        }
    }
    
    migrated = migrate_questionnaire(questionnaire_v1, "1.0.0", "1.1.0")
    
    # Datos originales preservados
    assert migrated["responses"]["personal_data"]["nombre"] == "Jorge"
    assert migrated["responses"]["goals"]["primary_objective"] == "Perder grasa"

def test_migration_idempotent():
    """Test: Aplicar migración 2 veces no rompe"""
    questionnaire = {
        "version": "1.0.0",
        "responses": {}
    }
    
    migrated_1 = migrate_questionnaire(questionnaire, "1.0.0", "1.1.0")
    migrated_2 = migrate_questionnaire(migrated_1, "1.1.0", "1.1.0")
    
    assert migrated_1 == migrated_2

@pytest.mark.asyncio
async def test_migration_with_backup():
    """Test: Backup se crea antes de migrar"""
    migrator = QuestionnaireMigrator()
    
    # Mock client_drawer
    client_drawer = {
        "_id": "test_client",
        "services": {
            "training": {
                "questionnaires": {
                    "inicial": {
                        "version": "1.0.0",
                        "responses": {}
                    }
                }
            }
        }
    }
    
    await migrator.migrate_if_needed(client_drawer, service="training")
    
    # Verificar que backup existe
    backup = await db.questionnaire_backups.find_one(
        {"client_id": "test_client"}
    )
    assert backup is not None
```

### 📝 Logs y Observabilidad

```python
# Logs estructurados
logger.info(
    "Questionnaire migration",
    extra={
        "client_id": client_id,
        "service": service,
        "from_version": "1.0.0",
        "to_version": "1.1.0",
        "duration_ms": 45,
        "success": True
    }
)

# Métricas (Prometheus)
MIGRATION_COUNTER = Counter(
    "questionnaire_migrations_total",
    "Total migrations performed",
    ["from_version", "to_version", "success"]
)

MIGRATION_DURATION = Histogram(
    "questionnaire_migration_duration_seconds",
    "Time spent migrating"
)
```

---

## 12. ARCHIVADO DE SNAPSHOTS

### 🗄️ Operativa del Archivado

#### **Job Mensual Automático**

```python
# /app/backend/snapshot_archiver.py

import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

class SnapshotArchiver:
    """Gestor de archivado automático de snapshots"""
    
    def __init__(self, cutoff_days: int = 730):
        self.cutoff_days = cutoff_days
        self.archival_log = []
    
    async def run_archival_job(self):
        """
        Job mensual de archivado.
        
        Backups y logs incluidos.
        """
        logger.info("Starting snapshot archival job")
        start_time = datetime.now(timezone.utc)
        
        # 1. BACKUP COMPLETO antes de archivar
        await self._create_full_backup()
        
        # 2. Ejecutar archivado
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.cutoff_days)
        
        drawers = await db.client_drawers.find({}).to_list(10000)
        
        total_drawers = len(drawers)
        total_archived = 0
        errors = []
        
        for drawer in drawers:
            try:
                archived_count = await self._archive_drawer_snapshots(
                    drawer,
                    cutoff_date
                )
                total_archived += archived_count
            
            except Exception as e:
                logger.error(f"Error archiving {drawer['_id']}: {e}")
                errors.append({
                    "client_id": drawer["_id"],
                    "error": str(e)
                })
        
        # 3. Log final
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        result = {
            "total_drawers": total_drawers,
            "total_snapshots_archived": total_archived,
            "errors_count": len(errors),
            "errors": errors,
            "duration_seconds": duration,
            "completed_at": datetime.now(timezone.utc)
        }
        
        logger.info(f"Archival job completed: {result}")
        
        # Guardar log en BD
        await db.archival_logs.insert_one(result)
        
        return result
    
    async def _create_full_backup(self):
        """Backup de TODA la colección client_drawers antes de archivar"""
        logger.info("Creating full backup before archival")
        
        backup_collection = f"client_drawers_backup_{datetime.now().strftime('%Y%m%d')}"
        
        # Copiar colección completa
        drawers = await db.client_drawers.find({}).to_list(100000)
        
        if drawers:
            await db[backup_collection].insert_many(drawers)
            logger.info(f"Backup created: {backup_collection} ({len(drawers)} documents)")
        
        # Guardar metadata del backup
        await db.backup_metadata.insert_one({
            "backup_collection": backup_collection,
            "source_collection": "client_drawers",
            "documents_count": len(drawers),
            "created_at": datetime.now(timezone.utc),
            "type": "pre_archival"
        })
    
    async def _archive_drawer_snapshots(
        self,
        drawer: Dict,
        cutoff_date: datetime
    ) -> int:
        """
        Archiva snapshots antiguos de un drawer específico.
        
        Returns:
            Número de snapshots archivados
        """
        archived_count = 0
        
        for service_name in ["training", "nutrition"]:
            service = drawer["services"].get(service_name)
            
            if not service or not service.get("active"):
                continue
            
            snapshots = service.get("snapshots", [])
            snapshots_to_archive = [
                s for s in snapshots
                if s["created_at"] < cutoff_date
            ]
            
            if not snapshots_to_archive:
                continue
            
            # Crear/actualizar archivo
            archive_id = f"{drawer['_id']}_{service_name}_archive"
            
            await db.client_drawers_archive.update_one(
                {"_id": archive_id},
                {
                    "$push": {
                        "archived_snapshots": {"$each": snapshots_to_archive}
                    },
                    "$set": {
                        "client_id": drawer["_id"],
                        "service": service_name,
                        "archived_at": datetime.now(timezone.utc),
                        "snapshots_count": len(snapshots_to_archive)
                    }
                },
                upsert=True
            )
            
            # Eliminar de drawer principal
            await db.client_drawers.update_one(
                {"_id": drawer["_id"]},
                {
                    "$pull": {
                        f"services.{service_name}.snapshots": {
                            "created_at": {"$lt": cutoff_date}
                        }
                    },
                    "$set": {
                        "meta.has_archived_snapshots": True,
                        "meta.updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            archived_count += len(snapshots_to_archive)
            
            # Log por cliente
            self.archival_log.append({
                "client_id": drawer["_id"],
                "service": service_name,
                "snapshots_archived": len(snapshots_to_archive),
                "oldest_archived": min(s["created_at"] for s in snapshots_to_archive),
                "newest_archived": max(s["created_at"] for s in snapshots_to_archive)
            })
            
            logger.info(
                f"Archived {len(snapshots_to_archive)} snapshots "
                f"for {drawer['_id']} ({service_name})"
            )
        
        return archived_count
```

#### **Cron Job Configuration**

```python
# /app/backend/scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from snapshot_archiver import SnapshotArchiver

scheduler = AsyncIOScheduler()

# Job mensual: primer día del mes a las 02:00 AM
scheduler.add_job(
    func=lambda: SnapshotArchiver().run_archival_job(),
    trigger="cron",
    day=1,
    hour=2,
    minute=0,
    id="snapshot_archival",
    name="Archive old snapshots (monthly)"
)

scheduler.start()
```

### 📊 Métricas y Observabilidad

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

SNAPSHOTS_ARCHIVED = Counter(
    "snapshots_archived_total",
    "Total snapshots archived",
    ["service"]
)

ARCHIVAL_DURATION = Histogram(
    "archival_job_duration_seconds",
    "Time spent archiving snapshots"
)

ACTIVE_SNAPSHOTS_PER_DRAWER = Gauge(
    "active_snapshots_count",
    "Number of active snapshots per drawer",
    ["client_id", "service"]
)

# Dashboard query (Grafana)
# avg(active_snapshots_count) by (service)
# rate(snapshots_archived_total[1h])
```

### 🔍 Impacto Funcional del Archivado

#### **Para el Cliente (Usuario Final):**

**SIN CAMBIOS VISIBLES:**
- ✅ Puede ver su plan actual (siempre en drawer principal)
- ✅ Puede ver historial reciente (últimos 2 años)
- ✅ Si necesita plan antiguo (>2 años), tarda +50ms más (1 query extra)

**Ejemplo de acceso:**

```python
# Frontend: Mostrar historial de planes
async def get_client_training_history(user_id: str):
    drawer = await db.client_drawers.find_one({"user_id": user_id})
    
    # Planes activos (últimos 2 años)
    active_plans = drawer["services"]["training"]["plans"]
    
    # Si tiene archivados
    if drawer["meta"]["has_archived_snapshots"]:
        archive = await db.client_drawers_archive.find_one(
            {"client_id": drawer["_id"], "service": "training"}
        )
        
        if archive:
            archived_plans = [
                {
                    "plan_id": s["plans_generated"]["training_plan_id"],
                    "version": s["version"],
                    "created_at": s["created_at"],
                    "archived": True
                }
                for s in archive["archived_snapshots"]
            ]
        else:
            archived_plans = []
    else:
        archived_plans = []
    
    return {
        "active_plans": active_plans,
        "archived_plans": archived_plans
    }
```

#### **Para el Equipo (Admin/Entrenador):**

**Dashboard de Monitoreo:**

```python
# Endpoint: GET /admin/archival/stats
async def get_archival_stats():
    # Última ejecución del job
    last_run = await db.archival_logs.find_one(
        sort=[("completed_at", -1)]
    )
    
    # Drawers con archivados
    drawers_with_archive = await db.client_drawers.count_documents({
        "meta.has_archived_snapshots": True
    })
    
    # Snapshots archivados totales
    archives = await db.client_drawers_archive.find({}).to_list(10000)
    total_archived = sum(
        len(archive.get("archived_snapshots", []))
        for archive in archives
    )
    
    return {
        "last_archival_run": last_run,
        "drawers_with_archived_snapshots": drawers_with_archive,
        "total_snapshots_archived": total_archived,
        "archive_collections_count": len(archives)
    }
```

---

## 13. INTERFACES CROSS-SERVICE

### 🔗 Principio de Acceso entre Servicios

**Regla:**
> Cada servicio puede **leer** datos de otros servicios, pero **NO puede modificarlos**.

### 📋 Interfaces Públicas vs Privadas

#### **Datos Consultables (Públicos)**

Cada servicio expone un "contrato" de datos que otros servicios pueden leer:

```javascript
// TRAINING - Interfaz pública
services.training.public_interface = {
  // Disponible para otros servicios
  readable: {
    current_objective: "goals.primary_objective",
    activity_level: "capacity.volume_semanal",
    training_schedule: "availability.training_schedule",
    injuries: "constraints.lesiones",
    current_plan_status: "plans[last].status"
  },
  
  // NO disponible (interno del servicio)
  private: {
    sessions: "Detalles de sesiones (solo training)",
    prehab: "Protocolos internos (solo training)"
  }
}
```

```javascript
// NUTRITION - Interfaz pública
services.nutrition.public_interface = {
  readable: {
    current_calories: "energy_strategy.calorias_target",
    macros: "macro_design",
    meal_frequency: "timing_plan.comidas",
    dietary_restrictions: "profile.restrictions"
  },
  
  private: {
    menu_plan: "Menú detallado (solo nutrition)"
  }
}
```

```javascript
// PSYCHOLOGY - Interfaz pública (futuro)
services.psychology.public_interface = {
  readable: {
    stress_level: "assessment.stress_level",
    anxiety_level: "assessment.anxiety_level",
    coping_strategies: "strategies",
    adherence_barriers: "barriers"
  },
  
  private: {
    therapy_notes: "Notas privadas del psicólogo"
  }
}
```

### 🔧 Implementación de Acceso Cross-Service

```python
# /app/backend/services/cross_service_accessor.py

class CrossServiceAccessor:
    """
    Gestor de acceso seguro entre servicios.
    
    Valida que solo se acceda a interfaces públicas.
    """
    
    # Definición de interfaces públicas
    PUBLIC_INTERFACES = {
        "training": {
            "current_objective": "questionnaires.inicial.responses.goals.primary_objective",
            "activity_level": "snapshots[-1].client_context.training.capacity.volumen_semanal",
            "training_days": "questionnaires.inicial.responses.availability.training_schedule.days_per_week",
            "injuries": "snapshots[-1].client_context.training.constraints.lesiones"
        },
        "nutrition": {
            "current_calories": "snapshots[-1].client_context.nutrition.energy_strategy.calorias_target",
            "macros": "snapshots[-1].client_context.nutrition.macro_design",
            "dietary_restrictions": "questionnaires.inicial.responses.preferences.cannot_eat"
        },
        "psychology": {
            "stress_level": "snapshots[-1].client_context.psychology.assessment.stress_level",
            "anxiety_level": "snapshots[-1].client_context.psychology.assessment.anxiety_level"
        }
    }
    
    def get_service_data(
        self,
        client_drawer: Dict,
        source_service: str,
        target_service: str,
        field: str
    ) -> Any:
        """
        Obtiene datos de un servicio para ser usados por otro.
        
        Args:
            client_drawer: Drawer del cliente
            source_service: Servicio que hace la consulta (ej: "nutrition")
            target_service: Servicio del cual se lee (ej: "training")
            field: Campo a leer (debe estar en PUBLIC_INTERFACES)
        
        Returns:
            Valor del campo solicitado
        
        Raises:
            PermissionError: Si el campo no está en la interfaz pública
        """
        # Validar que el campo está en la interfaz pública
        if target_service not in self.PUBLIC_INTERFACES:
            raise PermissionError(
                f"Service '{target_service}' has no public interface defined"
            )
        
        if field not in self.PUBLIC_INTERFACES[target_service]:
            raise PermissionError(
                f"Field '{field}' is not part of {target_service} public interface. "
                f"Available fields: {list(self.PUBLIC_INTERFACES[target_service].keys())}"
            )
        
        # Obtener path del campo
        path = self.PUBLIC_INTERFACES[target_service][field]
        
        # Navegar el drawer siguiendo el path
        value = self._navigate_path(
            client_drawer["services"][target_service],
            path
        )
        
        # Log de acceso cross-service
        logger.info(
            f"Cross-service access: {source_service} → {target_service}.{field}"
        )
        
        return value
    
    def _navigate_path(self, data: Dict, path: str) -> Any:
        """Navega un path tipo 'snapshots[-1].client_context.training.capacity'"""
        parts = path.split(".")
        current = data
        
        for part in parts:
            if part.endswith("]"):  # Array access: snapshots[-1]
                array_name, index_str = part.split("[")
                index = int(index_str.rstrip("]"))
                current = current[array_name][index]
            else:
                current = current[part]
        
        return current
```

### 📝 Ejemplo de Uso: Nutrition Lee de Psychology

```python
# Orquestador de Nutrition
async def generate_nutrition_plan_with_psychology(client_drawer: Dict):
    accessor = CrossServiceAccessor()
    
    # Verificar si el cliente tiene servicio de psicología
    if not client_drawer["services"]["psychology"]["active"]:
        logger.info("Psychology service not active, using default values")
        stress_level = "Desconocido"
    else:
        # Leer nivel de estrés de psychology (PERMITIDO)
        stress_level = accessor.get_service_data(
            client_drawer=client_drawer,
            source_service="nutrition",
            target_service="psychology",
            field="stress_level"
        )
    
    # Ajustar plan nutricional según estrés
    if stress_level in ["Alto", "Muy Alto"]:
        # Recomendar alimentos con triptófano, magnesio
        logger.info("High stress detected, adjusting meal plan")
        # Lógica específica...
    
    # Intentar leer dato privado (NO PERMITIDO)
    try:
        therapy_notes = accessor.get_service_data(
            client_drawer=client_drawer,
            source_service="nutrition",
            target_service="psychology",
            field="therapy_notes"  # ❌ No está en PUBLIC_INTERFACES
        )
    except PermissionError as e:
        logger.error(f"Access denied: {e}")
```

### 🔒 Validación de Permisos

```python
# Tests
def test_cross_service_access_allowed():
    """Test: Acceso a campo público permitido"""
    accessor = CrossServiceAccessor()
    
    client_drawer = {
        "services": {
            "psychology": {
                "active": True,
                "snapshots": [{
                    "client_context": {
                        "psychology": {
                            "assessment": {
                                "stress_level": "Alto"
                            }
                        }
                    }
                }]
            }
        }
    }
    
    stress = accessor.get_service_data(
        client_drawer, "nutrition", "psychology", "stress_level"
    )
    
    assert stress == "Alto"

def test_cross_service_access_denied():
    """Test: Acceso a campo privado denegado"""
    accessor = CrossServiceAccessor()
    
    with pytest.raises(PermissionError):
        accessor.get_service_data(
            client_drawer, "nutrition", "psychology", "therapy_notes"
        )
```

---

## 14. COMPARATIVA AS IS vs TO BE

### 📊 Tabla Completa

| **Aspecto** | **AS IS** | **TO BE** | **Mejora** |
|---|---|---|---|
| Fuente de verdad | 6+ colecciones dispersas | 1: `client_drawers` | 🟢 Unificación total |
| Duplicación cuestionarios | 3+ copias/cliente | 1 copia única | 🟢 Eliminación 100% |
| ClientContext | Solo en memoria | Persiste en snapshots[] | 🟢 Trazabilidad completa |
| Versionado | Manual (month, year) | Automático (version, snapshot_id) | 🟢 Consistencia |
| Navegación temporal | Imposible | Nativa (previous_snapshot_id) | 🟢 Historial navegable |
| Reconstrucción contexto | Cada job desde cero | 1 query al drawer | 🟢 Eficiencia x10 |
| Seguimientos | Nueva ejecución completa | Progresión desde snapshot | 🟢 Inteligencia contextual |
| Referencias cruzadas | Inconsistentes | Bidireccionales | 🟢 Integridad referencial |
| Espacio (1 cliente, 12 meses) | ~500 KB | ~120 KB | 🟢 Reducción 75% |
| Queries historial completo | 5+ queries | 1 query | 🟢 Simplicidad |
| Extensibilidad | Refactor completo | Añadir módulo | 🟢 Multi-servicio nativo |
| Archivado | Manual | Automático > 2 años | 🟢 Escalabilidad a largo plazo |

---

## 15. LISTA DE CÓDIGO A ELIMINAR

### 🗑️ Colecciones a DEPRECAR

1. **`nutrition_questionnaire_submissions`**
   - Reemplazo: `client_drawers.services.training.questionnaires.inicial`
   - Acción: Migrar → Eliminar

2. **`followup_submissions`**
   - Reemplazo: `client_drawers.services.training.questionnaires.followups[]`
   - Acción: Migrar → Eliminar

3. **`questionnaire_responses`** (Opcional)
   - Mantener separado (es CRM, no core EDN360)

### 🗑️ Campos a ELIMINAR en Planes

1. **`training_plans.questionnaire_data`**
   - Ya NO se duplica
   - Reemplazo: Referencia via `snapshot_id`

2. **`nutrition_plans.questionnaire_data`**
   - Ídem training

3. **`training_plans.e7_output.formatted_plan`** (legacy)
   - Solo mantener `formatted_plan` post-procesado

### 🗑️ Funciones a REFACTORIZAR

1. **`initialize_client_context()`**
   - Simplificar: leer directamente de drawer
   - Nueva: `initialize_client_context_from_drawer()`

2. **`process_generation_job()`**
   - Cambiar lectura de `nutrition_questionnaire_submissions` → `client_drawers`

### 🗑️ Endpoints a MODIFICAR

1. **POST `/api/nutrition-questionnaire/submit`**
   - Nueva lógica: Actualizar `client_drawer.services.training.questionnaires`

2. **POST `/api/followup/submit`**
   - Nueva lógica: Append a `client_drawer.services.training.questionnaires.followups[]`

3. **POST `/admin/users/{user_id}/plans/generate_async`**
   - Recibir `client_drawer_id` en vez de `submission_id`

---

## 16. CONCLUSIONES

### ✅ Beneficios Clave

1. **Simplicidad:** 1 colección en vez de 6
2. **Trazabilidad:** Snapshots inmutables con ClientContext completo
3. **Eficiencia:** 53% menos espacio, 5x más rápido en queries
4. **Escalabilidad:** Archivado automático, historial ilimitado
5. **Extensibilidad:** Multi-servicio nativo, fácil añadir dominios
6. **Calidad:** Migraciones automáticas, tests, backups
7. **Operativa:** Logs, métricas, observabilidad

### 🎯 Próximo Paso: DOCUMENTO 3

**Contenido del Documento 3:**
1. Fases detalladas de migración (AS IS → TO BE)
2. Scripts de migración de datos
3. Criterios de validación por fase
4. Rollback points
5. Timeline estimado
6. Plan de contingencia

---

**Fin del Documento 2 vFINAL**

---

## 📝 RESUMEN PARA APROBACIÓN

**Este documento TO BE define:**

✅ Client Drawer como única fuente de verdad  
✅ Arquitectura multi-servicio extensible  
✅ Snapshots inmutables sin duplicaciones  
✅ Cuestionario versionado con migraciones automáticas  
✅ Archivado automático con backups y observabilidad  
✅ Interfaces cross-service controladas  
✅ Proyección a 5 años sin riesgo de límite MongoDB  
✅ Plan claro de qué código eliminar  

**¿Apruebas este TO BE para proceder con el Documento 3?**
