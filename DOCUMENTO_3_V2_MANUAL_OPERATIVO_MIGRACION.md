# DOCUMENTO 3 v2: MANUAL OPERATIVO DE MIGRACIÓN

**Sistema:** E.D.N.360 - Migración AS IS → TO BE (Client Drawer)  
**Tipo:** Manual de Ejecución Obligatorio  
**Fecha:** Enero 2025  
**Versión:** 2.0 FINAL  
**Estado:** Pendiente de aprobación formal  
**Referencia:** Documento 2 vFINAL (Aprobado)  

---

## ⚠️ ADVERTENCIA CRÍTICA

Este documento es un **manual de ejecución obligatorio**, no una guía orientativa.

**Ninguna fase puede ejecutarse sin:**
1. Cumplir íntegramente los requisitos especificados
2. Superar los criterios de validación establecidos
3. Obtener aprobación formal de Jorge Calcerrada en los puntos GO/NO-GO

**Desviación de este manual = suspensión inmediata de la migración.**

---

## 📋 ÍNDICE

### PARTE 1: FUNDAMENTOS
1. [Modelo de Cuestionario Único EDN360](#1-modelo-cuestionario-único)
2. [Mapa Contractual Legacy → TO BE](#2-mapa-contractual)
3. [Estrategia Oficial Anti-Duplicados](#3-estrategia-anti-duplicados)

### PARTE 2: FASES DE EJECUCIÓN
4. [Fase 0: Preparación](#4-fase-0-preparación)
5. [Fase 0.5: STAGING (OBLIGATORIA)](#5-fase-05-staging)
6. [Fase 1: Coexistencia Dual-Write](#6-fase-1-coexistencia)
7. [Fase 2: Migración Histórica](#7-fase-2-migración)
8. [Fase 3: Switch a Client Drawer](#8-fase-3-switch)
9. [Fase 4: Limpieza Legacy](#9-fase-4-limpieza)

### PARTE 3: OPERATIVA Y CONTROL
10. [Tabla de Umbrales y Acciones](#10-umbrales-y-acciones)
11. [Listado Completo de Scripts](#11-listado-scripts)
12. [Plan de Rollback](#12-plan-rollback)
13. [Puntos de Supervisión Jorge](#13-supervisión-jorge)
14. [Criterios de Cierre Técnico](#14-cierre-técnico)

---

## 1. MODELO CUESTIONARIO ÚNICO

### 🎯 Realidad Clínica

**PRINCIPIO FUNDAMENTAL:**

> En EDN360 **NO existen cuestionarios separados por dominio** (entrenamiento/nutrición).

**Solo existen 2 tipos de cuestionarios:**

1. **Cuestionario Inicial (Anamnesis EDN360):**
   - Una única captura integral del cliente
   - Incluye datos de entrenamiento Y nutrición
   - Una sola fecha de submission por cliente

2. **Cuestionario de Seguimiento (Seguimiento EDN360):**
   - Una única evaluación de progreso integral
   - Incluye adherencia y cambios en entrenamiento Y nutrición
   - Una sola fecha de submission por seguimiento

**Cualquier referencia a "cuestionario de entrenamiento" o "cuestionario de nutrición" como entidades separadas es incorrecta y debe eliminarse.**

---

### 📐 Estructura TO BE Oficial

```javascript
client_drawer = {
  _id: "client_1762094831193507",
  user_id: "1762094831193507",
  
  profile: {
    // Datos personales globales
    nombre_completo: "Jorge Calcerrada",
    email: "jorge@example.com",
    // ...
  },
  
  services: {
    // ============================================
    // SHARED: Cuestionarios únicos EDN360
    // ============================================
    shared: {
      questionnaires: {
        // Cuestionario inicial único
        inicial: {
          submitted_at: ISODate("2025-01-02T09:00:00Z"),
          version: "1.0.0",
          schema_version: "questionnaire_edn360_v1",
          
          // Sección de entrenamiento
          training_section: {
            personal_data: { /* ... */ },
            measurements: { /* ... */ },
            health: { /* ... */ },
            work_life: { /* ... */ },
            sports_background: { /* ... */ },
            availability: { /* ... */ },
            daily_schedule: { /* ... */ },
            goals: {
              primary_objective: "Perder grasa"  // ⭐
            }
          },
          
          // Sección de nutrición
          nutrition_section: {
            nutrition_habits: { /* ... */ },
            preferences: { /* ... */ },
            diet_history: { /* ... */ },
            eating_patterns: { /* ... */ }
          }
        },
        
        // Seguimientos únicos
        followups: [
          {
            followup_id: "followup_feb2025",
            submitted_at: ISODate("2025-02-03T10:00:00Z"),
            days_since_last: 30,
            previous_snapshot_training_id: "snapshot_training_v1",
            previous_snapshot_nutrition_id: "snapshot_nutrition_v1",
            
            // Sección de entrenamiento
            training_section: {
              measurements: { peso: "83", grasa: "20" },
              adherence: { constancia_entrenamiento: "80%" },
              changes_perceived: { fuerza: "Mejorando" },
              feedback: { objetivo_proximo_mes: "Seguir perdiendo grasa" }
            },
            
            // Sección de nutrición
            nutrition_section: {
              adherence: { seguimiento_alimentacion: "70%" },
              changes_perceived: { saciedad: "Buena" },
              feedback: { cambios_deseados: "Más variedad de recetas" }
            }
          }
        ]
      }
    },
    
    // ============================================
    // TRAINING: Snapshots y planes de entrenamiento
    // ============================================
    training: {
      active: true,
      enrolled_at: ISODate("2025-01-02T09:00:00Z"),
      
      snapshots: [
        {
          snapshot_id: "snapshot_training_v1",
          version: 1,
          created_at: ISODate("2025-01-03T10:15:30Z"),
          trigger: "inicial",
          
          // ClientContext de entrenamiento
          client_context: {
            training: {
              client_summary: { /* E1 */ },
              profile: { /* E1 */ },
              constraints: { /* E1 */ },
              capacity: { /* E2 */ },
              mesocycle: { /* E4 */ },
              sessions: [ /* E5 */ ],
              // ... E1-E9 outputs
            }
          },
          
          plans_generated: {
            training_plan_id: "training_v1_jan2025"
          }
        }
      ],
      
      plans: [
        {
          plan_id: "training_v1_jan2025",
          version: 1,
          snapshot_id: "snapshot_training_v1",
          generated_at: ISODate("2025-01-03T10:15:20Z"),
          status: "active"
        }
      ],
      
      measurements: [],  // Si aplica medidas específicas de entreno
      notes: []
    },
    
    // ============================================
    // NUTRITION: Snapshots y planes de nutrición
    // ============================================
    nutrition: {
      active: true,
      enrolled_at: ISODate("2025-01-02T09:00:00Z"),
      
      snapshots: [
        {
          snapshot_id: "snapshot_nutrition_v1",
          version: 1,
          created_at: ISODate("2025-01-03T10:15:35Z"),
          trigger: "inicial",
          
          // ClientContext de nutrición
          client_context: {
            nutrition: {
              profile: { /* N0 */ },
              metabolism: { /* N1 */ },
              macro_design: { /* N3 */ },
              // ... N0-N8 outputs
            }
          },
          
          plans_generated: {
            nutrition_plan_id: "nutrition_v1_jan2025"
          }
        }
      ],
      
      plans: [
        {
          plan_id: "nutrition_v1_jan2025",
          version: 1,
          snapshot_id: "snapshot_nutrition_v1",
          generated_at: ISODate("2025-01-03T10:15:25Z"),
          status: "active"
        }
      ],
      
      measurements: [],
      notes: []
    }
  },
  
  meta: {
    created_at: ISODate("2025-01-02T09:00:00Z"),
    updated_at: ISODate("2025-02-03T11:00:30Z"),
    active_services: ["training", "nutrition"],
    has_archived_snapshots: false,
    status: "active"
  }
}
```

---

### 🔄 Uso por Pipeline

**Pipeline de Entrenamiento (E1-E9):**

Lee datos de:
```python
training_data = client_drawer["services"]["shared"]["questionnaires"]["inicial"]["training_section"]
```

**Pipeline de Nutrición (N0-N8):**

Lee datos de:
```python
nutrition_data = client_drawer["services"]["shared"]["questionnaires"]["inicial"]["nutrition_section"]
```

**Snapshots y planes:**
- Se mantienen separados por dominio
- `services.training.snapshots[]` para entrenamiento
- `services.nutrition.snapshots[]` para nutrición

---

## 2. MAPA CONTRACTUAL

### 📋 Tabla Oficial: Colecciones Legacy → Client Drawer

Esta tabla es el **contrato oficial de migración**. No admite interpretaciones.

| **Colección Legacy** | **Servicio Destino** | **Ruta en Client Drawer** | **Tipo de Dato** |
|---|---|---|---|
| `questionnaire_responses` | `shared` | `services.shared.questionnaires.inicial` | Anamnesis EDN360 (cuestionario inicial único) |
| `followup_submissions` | `shared` | `services.shared.questionnaires.followups[]` | Seguimiento integral EDN360 |
| `training_plans` | `training` | `services.training.plans[]` | Plan histórico de entrenamiento |
| `nutrition_plans` | `nutrition` | `services.nutrition.plans[]` | Plan histórico de nutrición |

**Notas:**

1. **`questionnaire_responses` vs `nutrition_questionnaire_submissions`:**
   - En el sistema actual puede haber dos colecciones con nombres distintos
   - Ambas deben consolidarse en `services.shared.questionnaires.inicial`
   - La migración unificará estos datos

2. **`followup_submissions`:**
   - Puede haber seguimientos solo de training, solo de nutrition, o completos
   - Todos van a `services.shared.questionnaires.followups[]`
   - Cada seguimiento tiene `training_section` y/o `nutrition_section`

3. **Planes históricos:**
   - Los planes se mantienen en sus servicios respectivos
   - NO se duplican cuestionarios en planes
   - Planes referencian snapshots via `snapshot_id`

---

## 3. ESTRATEGIA ANTI-DUPLICADOS

### 🔒 Estrategia Oficial Aprobada

**Declaración formal:**

> "Estrategia oficial aprobada para la migración de datos históricos:  
> **Cutoff por fecha (`dual_write_start_at`) + Checks de idempotencia por IDs lógicos**"

---

### 📅 Parámetro Crítico: `dual_write_start_at`

**Definición:**

```python
# /app/backend/config.py

class MigrationConfig:
    # Timestamp exacto de inicio del dual-write
    # TODO: Definir antes de ejecutar Fase 1
    DUAL_WRITE_START_AT = datetime(2025, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
    
    # Feature flags
    USE_CLIENT_DRAWER_WRITE = os.getenv("USE_CLIENT_DRAWER_WRITE", "false").lower() == "true"
    USE_CLIENT_DRAWER_READ = os.getenv("USE_CLIENT_DRAWER_READ", "false").lower() == "true"
```

**Uso:**

- **Fase 1 (Dual-Write):** Todos los nuevos cuestionarios con `submitted_at >= DUAL_WRITE_START_AT` se escriben en ambos sistemas (legacy + drawer)
- **Fase 2 (Migración Batch):** Solo migra registros con `submitted_at < DUAL_WRITE_START_AT`

---

### ✅ Reglas de No Duplicación

#### Regla 1: Cutoff Temporal

```python
# En scripts de Fase 2

# Migrar solo registros históricos (antes del dual-write)
submissions_to_migrate = await db.nutrition_questionnaire_submissions.find({
    "submitted_at": {"$lt": MigrationConfig.DUAL_WRITE_START_AT}
}).to_list(100000)

# Los submissions con submitted_at >= DUAL_WRITE_START_AT ya están en drawer
# NO los volvemos a migrar
```

#### Regla 2: Idempotencia por IDs Lógicos

Antes de insertar en `client_drawers`, verificar existencia:

```python
# Verificar si cuestionario inicial ya existe
existing_drawer = await db.client_drawers.find_one({
    "user_id": user_id,
    "services.shared.questionnaires.inicial": {"$exists": True}
})

if existing_drawer:
    logger.info(f"✅ Drawer {user_id} already has inicial questionnaire (skipping)")
    continue  # No duplicar

# Verificar followup_id
existing_followup = await db.client_drawers.find_one({
    "user_id": user_id,
    "services.shared.questionnaires.followups.followup_id": followup_id
})

if existing_followup:
    logger.info(f"✅ Followup {followup_id} already exists (skipping)")
    continue

# Verificar measurement_id (si aplica)
existing_measurement = await db.client_drawers.find_one({
    "user_id": user_id,
    "services.training.measurements.measurement_id": measurement_id
})

# Etc.
```

#### Regla 3: Validación Post-Migración

```python
# Después de Fase 2, verificar coherencia de contadores

# Total submissions legacy antes del cutoff
legacy_count = await db.nutrition_questionnaire_submissions.count_documents({
    "submitted_at": {"$lt": MigrationConfig.DUAL_WRITE_START_AT}
})

# Total drawers con cuestionario inicial
drawer_count = await db.client_drawers.count_documents({
    "services.shared.questionnaires.inicial": {"$exists": True}
})

# Debe ser: drawer_count >= legacy_count * 0.95
assert drawer_count >= legacy_count * 0.95, "Migration incomplete: too few drawers"
```

---

### 🚨 Detección de Duplicados

**Script de validación:**

```python
# /app/backend/migration/scripts/detect_duplicates.py

async def detect_duplicates_in_drawers():
    """
    Detecta duplicados en drawers después de migración.
    
    Si encuentra > 0 duplicados: PAUSA INMEDIATA.
    """
    
    duplicates = []
    
    # Verificar followups duplicados (mismo followup_id)
    drawers = await db.client_drawers.find({}).to_list(100000)
    
    for drawer in drawers:
        followups = drawer["services"]["shared"]["questionnaires"].get("followups", [])
        followup_ids = [f["followup_id"] for f in followups]
        
        # Detectar duplicados
        seen = set()
        for fid in followup_ids:
            if fid in seen:
                duplicates.append({
                    "client_id": drawer["_id"],
                    "duplicate_followup_id": fid
                })
            seen.add(fid)
    
    if duplicates:
        logger.error(f"❌ DUPLICATES DETECTED: {len(duplicates)}")
        for dup in duplicates:
            logger.error(f"  - {dup}")
        
        raise Exception("MIGRATION PAUSED: Duplicates detected")
    
    logger.info("✅ No duplicates found")
    return duplicates
```

---

## 4. FASE 0: PREPARACIÓN

### 🎯 Objetivo

Crear infraestructura TO BE sin afectar producción.

---

### 📋 Tareas

#### 4.1. Crear Modelos Pydantic

**Archivo:** `/app/backend/models/client_drawer.py`

**Modelo principal:**

```python
class SharedQuestionnaires(BaseModel):
    """Cuestionarios únicos EDN360 (training + nutrition)"""
    inicial: Optional[QuestionnaireInicial] = None
    followups: List[QuestionnaireFollowup] = Field(default_factory=list)

class QuestionnaireInicial(BaseModel):
    submitted_at: datetime
    version: str = "1.0.0"
    schema_version: str = "questionnaire_edn360_v1"
    training_section: Dict[str, Any]
    nutrition_section: Dict[str, Any]

class ServiceShared(BaseModel):
    """Servicio compartido para cuestionarios únicos"""
    questionnaires: SharedQuestionnaires = Field(default_factory=SharedQuestionnaires)

class ClientServices(BaseModel):
    shared: ServiceShared = Field(default_factory=ServiceShared)
    training: ServiceModule = Field(default_factory=ServiceModule)
    nutrition: ServiceModule = Field(default_factory=ServiceModule)

class ClientDrawer(BaseModel):
    client_drawer_id: str = Field(alias="_id")
    user_id: str
    profile: ClientProfile
    services: ClientServices = Field(default_factory=ClientServices)
    meta: Dict[str, Any]
```

---

#### 4.2. Crear Colección `client_drawers`

**Script:** `/app/backend/migration/scripts/00_create_collection.py`

```python
async def create_client_drawers_collection():
    """Crear colección con índices"""
    
    # Crear colección
    await db.create_collection("client_drawers")
    
    # Índices
    await db.client_drawers.create_index("user_id", unique=True)
    await db.client_drawers.create_index("services.shared.questionnaires.inicial.submitted_at")
    await db.client_drawers.create_index("services.training.active")
    await db.client_drawers.create_index("services.nutrition.active")
    
    print("✅ Collection created with indexes")
```

**Ejecución:**
```bash
python /app/backend/migration/scripts/00_create_collection.py
```

---

#### 4.3. Tests Unitarios

**Archivo:** `/app/backend/tests/test_client_drawer_model.py`

```python
def test_shared_questionnaires_structure():
    """Test: Estructura de cuestionarios compartidos"""
    drawer = ClientDrawer(
        client_drawer_id="client_test",
        user_id="test",
        profile=ClientProfile(...),
        services=ClientServices(
            shared=ServiceShared(
                questionnaires=SharedQuestionnaires(
                    inicial=QuestionnaireInicial(
                        submitted_at=datetime.now(),
                        training_section={"goals": {"primary_objective": "Perder grasa"}},
                        nutrition_section={"preferences": {}}
                    )
                )
            )
        ),
        meta={}
    )
    
    assert drawer.services.shared.questionnaires.inicial is not None
    assert "training_section" in drawer.services.shared.questionnaires.inicial.dict()
    assert "nutrition_section" in drawer.services.shared.questionnaires.inicial.dict()
```

---

### ✅ Criterios de Validación Fase 0

| **Criterio** | **Validación** |
|---|---|
| Modelos Pydantic con `services.shared` | Tests unitarios pasan |
| Colección `client_drawers` creada | Query MongoDB exitoso |
| Índices correctos | 4+ índices verificados |

### 🔄 Rollback Fase 0

N/A - Sin impacto en producción.

### ⏱️ Duración Estimada

**3-5 días** (tras aprobación formal del documento)

---

## 5. FASE 0.5: STAGING

### 🎯 Objetivo

**Fase obligatoria:** Simular migración completa en entorno aislado antes de tocar producción.

---

### ⚠️ REGLA DE BLOQUEO

> **"Sin superar la FASE 0.5 en staging con resultados aceptables, NO se autoriza la ejecución de Fase 2 ni Fase 3 en producción."**

---

### 📋 Requisitos de Entrada

1. **Dump reciente de producción:**
   ```bash
   # Crear dump de BD de producción
   mongodump --uri="$PROD_MONGO_URL" --db="$PROD_DB_NAME" --out=/backups/staging_dump_$(date +%Y%m%d)
   ```

2. **Entorno staging configurado:**
   - MongoDB staging aislado
   - Backend staging con código idéntico a prod
   - Variables de entorno staging

3. **Restaurar dump en staging:**
   ```bash
   mongorestore --uri="$STAGING_MONGO_URL" --db="staging_db" /backups/staging_dump_YYYYMMDD
   ```

---

### 📋 Ejecución en Staging

Ejecutar **de principio a fin** las siguientes fases:

1. **Fase 0:** Crear `client_drawers`, índices, modelos
2. **Fase 1:** Activar dual-write en staging
3. **Fase 2:** Ejecutar migración histórica completa
4. **Fase 3:** Switch de lectura a `client_drawers`

**Usando los mismos scripts, flags y parámetros que se usarán en producción.**

---

### 📊 Output Obligatorio de Staging

Al finalizar, debe existir un **informe de staging** con:

#### Métricas de Tiempo

| **Script** | **Duración** | **Tiempo/Batch** |
|---|---|---|
| 02_migrate_questionnaires.py | 2h 15min | 45s / 1000 registros |
| 03_migrate_followups.py | 1h 30min | 30s / 1000 registros |
| 04_migrate_legacy_plans.py | 3h 45min | 60s / 1000 planes |

#### Volumen de Datos Migrados

| **Tipo** | **Total Legacy** | **Migrado** | **Match Rate** |
|---|---|---|---|
| Cuestionarios iniciales | 15,234 | 15,180 | 99.6% |
| Followups | 8,456 | 8,420 | 99.5% |
| Training plans | 12,890 | 12,850 | 99.7% |
| Nutrition plans | 12,890 | 12,850 | 99.7% |

#### Errores y Correcciones

```
Errores detectados en staging:
1. Error: 54 cuestionarios con campos faltantes
   - Corrección: Script ajustado para manejar valores null
   
2. Error: 12 planes sin user_id válido
   - Corrección: Filtro añadido en migración

3. Error: Timeout en batch de 5000 registros
   - Corrección: Tamaño de batch reducido a 1000
```

#### Ajustes Aplicados

```
Optimizaciones aplicadas tras staging:
- Índice adicional en submitted_at (mejora 40% velocidad)
- Batch size reducido de 5000 → 1000 (evita timeouts)
- Timeout aumentado de 60s → 120s en scripts
```

---

### ✅ Criterios de Aprobación Staging

| **Criterio** | **Umbral** | **Estado** |
|---|---|---|
| Match rate cuestionarios | ≥ 95% | ⏳ |
| Match rate followups | ≥ 95% | ⏳ |
| Match rate planes | ≥ 90% | ⏳ |
| Errores críticos | 0 | ⏳ |
| Duplicados detectados | 0 | ⏳ |

**Solo con TODOS los criterios en ✅ se aprueba pasar a producción.**

---

### 🔄 Rollback Staging

Si staging falla:
1. No afecta producción (entorno aislado)
2. Corregir scripts
3. Re-ejecutar staging desde cero
4. Repetir hasta superar criterios

---

### ⏱️ Duración Estimada

**5-7 días:**
- Setup staging: 1 día
- Ejecución completa: 2-3 días
- Análisis y ajustes: 2-3 días

---

## 6. FASE 1: COEXISTENCIA

### 🎯 Objetivo

Escribir en AMBOS sistemas (AS IS + TO BE) sin cambiar la lectura.

---

### 📅 Definir `DUAL_WRITE_START_AT`

**Antes de activar Fase 1, definir:**

```python
# /app/backend/config.py

class MigrationConfig:
    # Ejemplo: 1 de Febrero 2025, 00:00:00 UTC
    DUAL_WRITE_START_AT = datetime(2025, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
```

**Este timestamp marca la frontera:**
- Antes: Se migrará en Fase 2
- Después: Se gestiona por dual-write

---

### 📋 Tareas

#### 6.1. Implementar Dual-Write

**Script:** `/app/backend/migration/scripts/01_enable_dual_write.py`

**Modificar endpoint:**

```python
# /app/backend/server.py

@app.post("/api/questionnaire/submit")
async def submit_questionnaire(user_id: str, responses: Dict):
    """
    Submission de cuestionario EDN360 (único).
    
    FASE 1: Dual-write mode activo.
    """
    
    # ========================================
    # ESCRITURA AS IS (Legacy)
    # ========================================
    submission = {
        "_id": f"submission_{uuid.uuid4()}",
        "user_id": user_id,
        "responses": responses,  # Dict plano
        "submitted_at": datetime.now(timezone.utc),
        "plan_generated": False
    }
    
    await db.nutrition_questionnaire_submissions.insert_one(submission)
    logger.info(f"✅ Written to AS IS: {submission['_id']}")
    
    # ========================================
    # ESCRITURA TO BE (Client Drawer)
    # ========================================
    if Config.USE_CLIENT_DRAWER_WRITE:
        try:
            # Separar responses en secciones training/nutrition
            training_section = extract_training_section(responses)
            nutrition_section = extract_nutrition_section(responses)
            
            # Construir cuestionario inicial
            questionnaire_inicial = {
                "submitted_at": datetime.now(timezone.utc),
                "version": "1.0.0",
                "schema_version": "questionnaire_edn360_v1",
                "training_section": training_section,
                "nutrition_section": nutrition_section
            }
            
            # Extraer profile
            profile = extract_profile(responses)
            
            # Upsert client_drawer
            await db.client_drawers.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "profile": profile,
                        "services.shared.questionnaires.inicial": questionnaire_inicial,
                        "meta.updated_at": datetime.now(timezone.utc)
                    },
                    "$setOnInsert": {
                        "_id": f"client_{user_id}",
                        "user_id": user_id,
                        "services.training.active": True,
                        "services.nutrition.active": True,
                        "meta.created_at": datetime.now(timezone.utc),
                        "meta.active_services": ["training", "nutrition"],
                        "meta.status": "active"
                    }
                },
                upsert=True
            )
            
            logger.info(f"✅ Written to TO BE: client_{user_id}")
            
            # Validación background
            asyncio.create_task(validate_dual_write(user_id, submission["_id"]))
        
        except Exception as e:
            logger.error(f"❌ Error writing to TO BE: {e}")
            # NO FALLAR: AS IS ya se escribió
    
    return {"status": "success", "submission_id": submission["_id"]}
```

---

#### 6.2. Activar Feature Flag

```bash
# .env
USE_CLIENT_DRAWER_WRITE=true
USE_CLIENT_DRAWER_READ=false  # Lectura sigue en AS IS

# Reiniciar
sudo supervisorctl restart backend
```

---

#### 6.3. Monitoreo

**Dashboard:**

```python
@app.get("/admin/monitoring/dual-write-stats")
async def get_dual_write_stats():
    total = await db.dual_write_validations.count_documents({})
    matching = await db.dual_write_validations.count_documents({"match": True})
    
    return {
        "total_validations": total,
        "matching": matching,
        "match_rate": matching / total if total > 0 else 0
    }
```

---

### ✅ Criterios de Validación Fase 1

| **Criterio** | **Umbral** |
|---|---|
| Match rate | > 98% |
| Sin errores críticos | 0 |

### 🔄 Rollback Fase 1

```bash
# Desactivar
USE_CLIENT_DRAWER_WRITE=false
sudo supervisorctl restart backend
```

**Tiempo:** < 2 minutos

---

### ⏱️ Duración Estimada

**1-2 semanas** (monitoreo + ajustes)

---

## 7. FASE 2: MIGRACIÓN

### 🎯 Objetivo

Migrar datos históricos (`submitted_at < DUAL_WRITE_START_AT`) a `client_drawers`.

---

### 🔒 BACKUP OBLIGATORIO

**Antes de ejecutar Fase 2:**

```bash
# Script: /app/backend/migration/scripts/backup_full_database.sh

#!/bin/bash
BACKUP_DIR="/backups/pre_phase2_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

mongodump --uri="$MONGO_URL" --db="$DB_NAME" --out="$BACKUP_DIR"

echo "✅ Backup: $BACKUP_DIR"
du -sh $BACKUP_DIR
```

**Verificar que backup existe y tiene tamaño > 0 antes de continuar.**

---

### 📋 Migración por Tipo

#### 7.1. Migrar Cuestionarios Iniciales

**Script:** `/app/backend/migration/scripts/02_migrate_questionnaires.py`

```python
async def migrate_questionnaires():
    """
    Migrar cuestionarios iniciales a services.shared.questionnaires.inicial
    
    REGLA: Solo migrar submitted_at < DUAL_WRITE_START_AT
    """
    
    cutoff = MigrationConfig.DUAL_WRITE_START_AT
    
    # Obtener submissions legacy antes del cutoff
    submissions = await db.nutrition_questionnaire_submissions.find({
        "submitted_at": {"$lt": cutoff}
    }).to_list(100000)
    
    total = len(submissions)
    migrated = 0
    skipped = 0
    errors = []
    
    for submission in submissions:
        try:
            user_id = submission["user_id"]
            
            # CHECK DE IDEMPOTENCIA
            existing = await db.client_drawers.find_one({
                "user_id": user_id,
                "services.shared.questionnaires.inicial": {"$exists": True}
            })
            
            if existing:
                logger.info(f"⏭️ Skipped {user_id}: inicial already exists")
                skipped += 1
                continue
            
            # Separar en secciones
            training_section = extract_training_section(submission["responses"])
            nutrition_section = extract_nutrition_section(submission["responses"])
            
            # Construir cuestionario
            questionnaire = {
                "submitted_at": submission.get("submitted_at"),
                "version": "1.0.0",
                "schema_version": "questionnaire_edn360_v1",
                "training_section": training_section,
                "nutrition_section": nutrition_section
            }
            
            # Profile
            profile = extract_profile(submission["responses"])
            
            # Upsert drawer
            await db.client_drawers.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "profile": profile,
                        "services.shared.questionnaires.inicial": questionnaire,
                        "services.training.active": True,
                        "services.nutrition.active": True,
                        "meta.updated_at": datetime.now(timezone.utc)
                    },
                    "$setOnInsert": {
                        "_id": f"client_{user_id}",
                        "user_id": user_id,
                        "meta.created_at": submission.get("submitted_at"),
                        "meta.active_services": ["training", "nutrition"],
                        "meta.status": "active"
                    }
                },
                upsert=True
            )
            
            migrated += 1
            
            if migrated % 100 == 0:
                logger.info(f"Progress: {migrated}/{total}")
        
        except Exception as e:
            logger.error(f"Error: {submission['_id']}: {e}")
            errors.append({"submission_id": submission["_id"], "error": str(e)})
    
    logger.info(f"""
    ✅ Questionnaires migration:
    - Total: {total}
    - Migrated: {migrated}
    - Skipped: {skipped}
    - Errors: {len(errors)}
    """)
    
    return {"total": total, "migrated": migrated, "skipped": skipped, "errors": errors}
```

---

#### 7.2. Migrar Followups

**Script:** `/app/backend/migration/scripts/03_migrate_followups.py`

```python
async def migrate_followups():
    """
    Migrar followups a services.shared.questionnaires.followups[]
    
    REGLA: Solo migrar submitted_at < DUAL_WRITE_START_AT
    """
    
    cutoff = MigrationConfig.DUAL_WRITE_START_AT
    
    followups = await db.followup_submissions.find({
        "submission_date": {"$lt": cutoff}
    }).to_list(100000)
    
    total = len(followups)
    migrated = 0
    skipped = 0
    errors = []
    
    for followup in followups:
        try:
            user_id = followup["user_id"]
            followup_id = followup["_id"]
            
            # CHECK DE IDEMPOTENCIA
            existing = await db.client_drawers.find_one({
                "user_id": user_id,
                "services.shared.questionnaires.followups.followup_id": followup_id
            })
            
            if existing:
                logger.info(f"⏭️ Skipped {followup_id}: already exists")
                skipped += 1
                continue
            
            # Separar secciones
            training_section = {
                "measurements": followup.get("measurements", {}),
                "adherence": followup.get("adherence", {}).get("training", {}),
                "changes_perceived": followup.get("changes_perceived", {}).get("training", {}),
                "feedback": followup.get("feedback", {}).get("training", {})
            }
            
            nutrition_section = {
                "adherence": followup.get("adherence", {}).get("nutrition", {}),
                "changes_perceived": followup.get("changes_perceived", {}).get("nutrition", {}),
                "feedback": followup.get("feedback", {}).get("nutrition", {})
            }
            
            # Resolver previous_snapshot_ids
            # (Buscar snapshots que generaron previous_plan_id)
            previous_training_snapshot = None
            previous_nutrition_snapshot = None
            # ... lógica de resolución
            
            followup_doc = {
                "followup_id": followup_id,
                "submitted_at": followup.get("submission_date"),
                "days_since_last": followup.get("days_since_last_plan", 30),
                "previous_snapshot_training_id": previous_training_snapshot,
                "previous_snapshot_nutrition_id": previous_nutrition_snapshot,
                "training_section": training_section,
                "nutrition_section": nutrition_section
            }
            
            # Push al drawer
            await db.client_drawers.update_one(
                {"user_id": user_id},
                {"$push": {"services.shared.questionnaires.followups": followup_doc}}
            )
            
            migrated += 1
        
        except Exception as e:
            logger.error(f"Error: {followup['_id']}: {e}")
            errors.append({"followup_id": followup["_id"], "error": str(e)})
    
    logger.info(f"Followups migration: {migrated}/{total}, skipped {skipped}, errors {len(errors)}")
    
    return {"total": total, "migrated": migrated, "skipped": skipped, "errors": errors}
```

---

#### 7.3. Vincular Planes Legacy

**Script:** `/app/backend/migration/scripts/04_link_legacy_plans.py`

```python
async def link_legacy_plans():
    """
    Actualizar training_plans y nutrition_plans con referencias a drawer.
    Crear snapshots retroactivos si es necesario.
    """
    
    # Planes sin snapshot_id
    legacy_plans = await db.training_plans.find({
        "snapshot_id": {"$exists": False}
    }).to_list(100000)
    
    for plan in legacy_plans:
        try:
            user_id = plan["user_id"]
            
            drawer = await db.client_drawers.find_one({"user_id": user_id})
            if not drawer:
                continue
            
            # Crear snapshot retroactivo
            version = len(drawer["services"]["training"]["snapshots"]) + 1
            
            snapshot = {
                "snapshot_id": f"snapshot_legacy_training_v{version}",
                "version": version,
                "created_at": plan.get("generated_at"),
                "trigger": "migrated_from_legacy",
                "client_context": {
                    "training": extract_training_context_from_plan(plan)
                },
                "plans_generated": {
                    "training_plan_id": plan["_id"]
                }
            }
            
            # Añadir snapshot
            await db.client_drawers.update_one(
                {"user_id": user_id},
                {"$push": {"services.training.snapshots": snapshot}}
            )
            
            # Actualizar plan
            await db.training_plans.update_one(
                {"_id": plan["_id"]},
                {
                    "$set": {
                        "client_drawer_id": drawer["_id"],
                        "snapshot_id": snapshot["snapshot_id"]
                    }
                }
            )
        
        except Exception as e:
            logger.error(f"Error linking plan {plan['_id']}: {e}")
```

---

### ✅ Validación Post-Fase 2

**Script:** `/app/backend/migration/scripts/05_validate_migration.py`

```python
async def validate_migration():
    """Validación exhaustiva de migración"""
    
    # Contar legacy vs drawer
    legacy_count = await db.nutrition_questionnaire_submissions.count_documents({
        "submitted_at": {"$lt": MigrationConfig.DUAL_WRITE_START_AT}
    })
    
    drawer_count = await db.client_drawers.count_documents({
        "services.shared.questionnaires.inicial": {"$exists": True}
    })
    
    match_rate = drawer_count / legacy_count if legacy_count > 0 else 0
    
    print(f"Legacy submissions: {legacy_count}")
    print(f"Drawers migrated: {drawer_count}")
    print(f"Match rate: {match_rate * 100:.1f}%")
    
    # Umbral: 95%
    assert match_rate >= 0.95, f"Match rate too low: {match_rate}"
    
    # Verificar duplicados
    duplicates = await detect_duplicates_in_drawers()
    assert len(duplicates) == 0, "Duplicates detected"
    
    print("✅ Validation PASSED")
```

---

### 🔄 Rollback Fase 2

Si falla:

```bash
# 1. Restaurar backup
mongorestore --uri="$MONGO_URL" --db="$DB_NAME" --drop /backups/pre_phase2_YYYYMMDD_HHMMSS/

# 2. Limpiar drawers parciales
mongo $MONGO_URL/$DB_NAME --eval "db.client_drawers.deleteMany({})"

# 3. Corregir scripts y re-ejecutar
```

**Tiempo:** 30-60 min

---

### ⏱️ Duración Estimada

**2-3 días** (según volumen en staging)

---

## 8. FASE 3: SWITCH

### 🎯 Objetivo

Cambiar lectura a `client_drawers`. **Momento más crítico.**

---

### ⚠️ PRE-REQUISITOS

- ✅ Fase 2 completada 100%
- ✅ Validación > 95%
- ✅ Backup reciente (< 24h)
- ✅ Equipo disponible para rollback

---

### 📋 Tareas

#### 8.1. Modificar Orquestador

```python
# /app/backend/edn360/orchestrator.py

async def generate_initial_plan(self, job_id: str):
    """
    Generar plan.
    
    FASE 3: Lee de client_drawer.
    """
    
    job = await db.generation_jobs.find_one({"_id": job_id})
    
    if Config.USE_CLIENT_DRAWER_READ:
        # TO BE
        drawer = await db.client_drawers.find_one({"_id": job["client_drawer_id"]})
        
        # Leer cuestionario compartido
        questionnaire = drawer["services"]["shared"]["questionnaires"]["inicial"]
        
        # Pipeline training usa training_section
        training_data = questionnaire["training_section"]
        
        # Pipeline nutrition usa nutrition_section
        nutrition_data = questionnaire["nutrition_section"]
        
        # Ejecutar pipelines...
    else:
        # AS IS (legacy)
        # ...
```

---

#### 8.2. Activar Switch

```bash
# .env
USE_CLIENT_DRAWER_READ=true

# Reiniciar
sudo supervisorctl restart backend
```

---

#### 8.3. Monitoreo 48h

```python
@app.get("/admin/monitoring/switch-status")
async def get_switch_status():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    
    recent_jobs = await db.generation_jobs.find({
        "created_at": {"$gte": cutoff}
    }).to_list(1000)
    
    to_be_jobs = [j for j in recent_jobs if "client_drawer_id" in j]
    success = [j for j in to_be_jobs if j["status"] == "completed"]
    
    return {
        "to_be_jobs": len(to_be_jobs),
        "success_rate": len(success) / len(to_be_jobs) if to_be_jobs else 0
    }
```

---

### ✅ Criterios Fase 3

| **Criterio** | **Umbral** |
|---|---|
| Tasa éxito jobs TO BE | > 95% |
| Sin errores críticos | 0 |

---

### 🔄 Rollback Fase 3

```bash
# INMEDIATO
USE_CLIENT_DRAWER_READ=false
sudo supervisorctl restart backend
```

**Tiempo:** < 5 min

---

### ⏱️ Duración

**1 día + 48h monitoreo**

---

## 9. FASE 4: LIMPIEZA

### 🎯 Objetivo

Eliminar código legacy. **Solo tras estabilización completa.**

---

### 📋 Tareas

#### 9.1. Deprecar Colecciones

```python
# /app/backend/migration/scripts/06_deprecate_collections.py

async def deprecate_legacy_collections():
    """Renombrar (NO eliminar) colecciones legacy"""
    
    date_suffix = datetime.now().strftime("%Y%m%d")
    
    collections = [
        "nutrition_questionnaire_submissions",
        "followup_submissions"
    ]
    
    for col in collections:
        new_name = f"{col}_DEPRECATED_{date_suffix}"
        await db[col].rename(new_name)
        print(f"✅ Deprecated: {col} → {new_name}")
    
    print("⚠️ Can be deleted after 30 days if no issues")
```

---

#### 9.2. Eliminar Código Legacy

Archivos a modificar:
- `/app/backend/server.py` (eliminar endpoints legacy)
- `/app/backend/edn360/orchestrator.py` (eliminar branch AS IS)
- `/app/backend/config.py` (eliminar feature flags)

---

### ⏱️ Duración

**2-3 días**

---

## 10. UMBRALES Y ACCIONES

### 📊 Tabla de Decisión Operativa

Esta tabla es un **árbol de decisión obligatorio**. No admite interpretaciones.

| **Métrica** | **Umbral / Resultado** | **Acción Obligatoria** | **Responsable** |
|---|---|---|---|
| **Match rate cuestionarios** | < 90% | Rollback Fase 2 completo | Equipo Dev |
| **Match rate cuestionarios** | 90–95% | Revisar casos fallidos, corregir, revalidar antes de avanzar | Equipo Dev + Jorge |
| **Match rate cuestionarios** | ≥ 95% | ✅ OK para avanzar a Fase 3 | Jorge aprueba |
| **Match rate followups** | < 90% | Rollback Fase 2 | Equipo Dev |
| **Match rate followups** | 90–95% | Revisar y corregir | Equipo Dev + Jorge |
| **Match rate followups** | ≥ 95% | ✅ OK | Jorge aprueba |
| **Planes sin snapshot_id** | > 0 | Bloquear avance hasta resolver a 0 | Equipo Dev |
| **Errores críticos en script** | ≥ 1 | Pausar todo hasta resolución | Equipo Dev |
| **Duplicados detectados** | > 0 | Pausa inmediata + análisis de causa | Equipo Dev |
| **Tasa éxito jobs TO BE (Fase 3)** | < 90% | Rollback Fase 3 inmediato | Jorge + Equipo Dev |
| **Tasa éxito jobs TO BE (Fase 3)** | 90–95% | Investigar errores, no avanzar hasta > 95% | Equipo Dev |
| **Tasa éxito jobs TO BE (Fase 3)** | ≥ 95% | ✅ OK, continuar monitoreo 48h | Jorge aprueba |

---

### 🚨 Acciones Inmediatas ante Fallo

#### Escenario 1: Match Rate < 90% en Fase 2

**Acción:**
1. DETENER migración inmediatamente
2. Ejecutar rollback Fase 2
3. Analizar errores en logs
4. Corregir scripts
5. Re-ejecutar en staging
6. Solicitar re-aprobación a Jorge

---

#### Escenario 2: Duplicados Detectados

**Acción:**
1. PAUSA INMEDIATA de migración
2. Ejecutar script de detección:
   ```python
   duplicates = await detect_duplicates_in_drawers()
   ```
3. Analizar causa raíz
4. Eliminar duplicados manualmente si es posible
5. Corregir script para evitar recurrencia
6. Re-validar

---

#### Escenario 3: Tasa Éxito < 90% en Fase 3

**Acción:**
1. Rollback inmediato (desactivar `USE_CLIENT_DRAWER_READ`)
2. Analizar logs de jobs fallidos
3. Identificar causa (¿datos faltantes? ¿error de código?)
4. Corregir
5. Re-aprobar con Jorge antes de reactivar

---

## 11. LISTADO SCRIPTS

### 📂 Estructura de Scripts

```
/app/backend/migration/
├── scripts/
│   ├── 00_create_collection.py
│   ├── 01_enable_dual_write.py
│   ├── 02_migrate_questionnaires.py
│   ├── 03_migrate_followups.py
│   ├── 04_link_legacy_plans.py
│   ├── 05_validate_migration.py
│   ├── 06_deprecate_collections.py
│   └── 07_rollback_phase_2.py
├── helpers/
│   ├── migration_helpers.py
│   └── duplicate_detector.py
└── config.py
```

---

### 📋 Detalle de Scripts

#### **00_create_collection.py**

**Objetivo:** Crear colección `client_drawers` con índices

**Entradas:** N/A

**Salidas:**
- Colección `client_drawers` creada
- 4 índices creados

**Riesgos:** Ninguno (sin impacto en prod)

**Criterio de éxito:** Colección existe y tiene índices

---

#### **01_enable_dual_write.py**

**Objetivo:** Activar escritura dual AS IS + TO BE

**Entradas:**
- Feature flag `USE_CLIENT_DRAWER_WRITE`
- Timestamp `DUAL_WRITE_START_AT`

**Salidas:**
- Nuevos cuestionarios se escriben en ambos sistemas
- Validaciones en background

**Riesgos:** Bajo (AS IS sigue funcionando si TO BE falla)

**Criterio de éxito:** Match rate > 98%

---

#### **02_migrate_questionnaires.py**

**Objetivo:** Migrar cuestionarios iniciales históricos

**Entradas:**
- Colección `nutrition_questionnaire_submissions`
- Filtro: `submitted_at < DUAL_WRITE_START_AT`

**Salidas:**
- Drawers con `services.shared.questionnaires.inicial` poblado

**Riesgos:** MEDIO
- Puede generar duplicados si no se valida idempotencia
- Timeout en batches grandes

**Criterio de éxito:**
- Match rate ≥ 95%
- 0 duplicados

---

#### **03_migrate_followups.py**

**Objetivo:** Migrar seguimientos históricos

**Entradas:**
- Colección `followup_submissions`
- Filtro: `submission_date < DUAL_WRITE_START_AT`

**Salidas:**
- Drawers con `services.shared.questionnaires.followups[]` poblado

**Riesgos:** MEDIO
- Resolver `previous_snapshot_id` puede fallar si no hay snapshot

**Criterio de éxito:**
- Match rate ≥ 95%
- 0 duplicados

---

#### **04_link_legacy_plans.py**

**Objetivo:** Vincular planes legacy con snapshots

**Entradas:**
- Colecciones `training_plans`, `nutrition_plans`
- Drawers existentes

**Salidas:**
- Planes con `snapshot_id` y `client_drawer_id`
- Snapshots retroactivos creados

**Riesgos:** BAJO
- Snapshot retroactivo puede ser incompleto

**Criterio de éxito:**
- 0 planes sin `snapshot_id`

---

#### **05_validate_migration.py**

**Objetivo:** Validación exhaustiva post-migración

**Entradas:**
- Drawers migrados
- Datos legacy

**Salidas:**
- Informe de validación con match rates

**Riesgos:** Ninguno (solo lectura)

**Criterio de éxito:**
- Todos los match rates > 95%
- 0 duplicados

---

#### **06_deprecate_collections.py**

**Objetivo:** Renombrar colecciones legacy

**Entradas:**
- Colecciones legacy

**Salidas:**
- Colecciones renombradas `*_DEPRECATED_YYYYMMDD`

**Riesgos:** BAJO (rename reversible)

**Criterio de éxito:**
- Colecciones renombradas correctamente

---

#### **07_rollback_phase_2.py**

**Objetivo:** Restaurar desde backup

**Entradas:**
- Path del backup

**Salidas:**
- BD restaurada al estado pre-migración

**Riesgos:** MEDIO
- Pierde datos creados entre backup y rollback

**Criterio de éxito:**
- BD restaurada correctamente

---

## 12. PLAN ROLLBACK

### 🔄 Rollback por Fase

| **Fase** | **Dificultad** | **Tiempo** | **Procedimiento** |
|---|---|---|---|
| Fase 0 | Fácil | N/A | Sin impacto, rehacer |
| Fase 1 | Fácil | 2 min | Desactivar `USE_CLIENT_DRAWER_WRITE` |
| Fase 2 | Media | 30-60 min | Restaurar backup + limpiar drawers |
| Fase 3 | Media | 2-5 min | Desactivar `USE_CLIENT_DRAWER_READ` |
| Fase 4 | N/A | N/A | Sistema estabilizado |

---

### 🚨 Procedimientos Detallados

#### Rollback Fase 1

```bash
# 1. Desactivar dual-write
echo "USE_CLIENT_DRAWER_WRITE=false" >> /app/backend/.env

# 2. Reiniciar
sudo supervisorctl restart backend

# 3. Verificar
curl http://localhost:8001/api/admin/monitoring/dual-write-stats
```

---

#### Rollback Fase 2

```bash
# 1. Restaurar backup
mongorestore --uri="$MONGO_URL" --db="$DB_NAME" --drop /backups/pre_phase2_YYYYMMDD_HHMMSS/

# 2. Limpiar client_drawers
mongo $MONGO_URL/$DB_NAME --eval "db.client_drawers.deleteMany({})"

# 3. Verificar
mongo $MONGO_URL/$DB_NAME --eval "db.client_drawers.count()"
# Debe ser 0

# 4. Corregir scripts
# ... análisis de errores

# 5. Re-ejecutar en staging
```

---

#### Rollback Fase 3

```bash
# 1. INMEDIATO: Desactivar lectura TO BE
echo "USE_CLIENT_DRAWER_READ=false" >> /app/backend/.env

# 2. Reiniciar
sudo supervisorctl restart backend

# 3. Verificar que volvió a AS IS
curl http://localhost:8001/api/admin/monitoring/switch-status
# Debe mostrar USE_CLIENT_DRAWER_READ=false
```

---

## 13. SUPERVISIÓN JORGE

### 👤 Puntos de Intervención Manual

Jorge debe intervenir en los siguientes puntos:

---

#### Punto 1: Aprobación GO Fase 0.5 → Fase 2

**Cuándo:** Tras completar staging

**Qué revisar:**
- Informe de staging completo
- Métricas de tiempo reales
- Match rates en staging
- Errores y correcciones aplicadas

**Acción:** Aprobar o rechazar paso a producción

---

#### Punto 2: Validación Manual Pre-Fase 2

**Cuándo:** Antes de ejecutar migración en producción

**Qué revisar:**
- Muestra aleatoria de 5 clientes:
  - Ver cuestionario inicial en AS IS
  - Ver historial de seguimientos
  - Ver planes históricos (training + nutrition)

**Acción:** Confirmar que datos son correctos

---

#### Punto 3: Aprobación GO Fase 2 → Fase 3

**Cuándo:** Tras completar Fase 2 y validación

**Qué revisar:**
- Match rates post-migración
- Informe de duplicados (debe ser 0)
- Muestra aleatoria de 5 clientes post-migración:
  - Ver drawer completo
  - Comparar con datos legacy
  - Verificar coherencia

**Acción:** Aprobar o rechazar switch

---

#### Punto 4: Validación Manual Post-Fase 3

**Cuándo:** Tras activar switch (primeras 24h)

**Qué revisar:**
- Generar 3 planes de prueba con clientes reales
- Revisar que:
  - Objetivo es correcto
  - Plan tiene coherencia
  - Historial del cliente visible

**Acción:** Aprobar continuar o solicitar rollback

---

#### Punto 5: Aprobación Cierre Fase 4

**Cuándo:** Tras estabilización completa

**Qué revisar:**
- Informe final de migración
- Métricas de performance
- Colecciones legacy deprecadas

**Acción:** Aprobar cierre formal de migración

---

## 14. CIERRE TÉCNICO

### ✅ Criterios de Cierre

La migración se considera **completada técnicamente** cuando:

1. ✅ **Agentes leen exclusivamente de `client_drawers`:**
   - Código legacy eliminado
   - Feature flags removidos
   - Sin referencias a colecciones legacy en código

2. ✅ **Colecciones legacy deprecadas:**
   - Renombradas con sufijo `_DEPRECATED_YYYYMMDD`
   - Documentado que pueden eliminarse tras 30 días

3. ✅ **Informe final de migración creado:**
   ```
   Informe Final de Migración EDN360
   ==================================
   
   Fecha de inicio: 1 Febrero 2025
   Fecha de cierre: 15 Marzo 2025
   Duración total: 6 semanas
   
   Métricas:
   - Cuestionarios migrados: 15,180 / 15,234 (99.6%)
   - Followups migrados: 8,420 / 8,456 (99.5%)
   - Planes vinculados: 25,700 / 25,780 (99.7%)
   - Duplicados detectados: 0
   
   Incidencias:
   - 3 errores menores corregidos en staging
   - 0 incidencias en producción
   
   Acciones correctoras:
   - Ajuste de timeout en script 02
   - Índice adicional en submitted_at
   
   Performance:
   - Tiempo generación plan: 85s (antes 90s, mejora 5%)
   - Queries historial: 1 query (antes 5+, mejora 80%)
   
   Estado: ✅ COMPLETADO
   ```

4. ✅ **Tests de regresión pasan:**
   - Generación de planes funciona
   - Historial accesible
   - Seguimientos funcionan

5. ✅ **Jorge aprueba formalmente:**
   - Revisión del informe
   - Aprobación escrita en documento

---

### 📝 Documentación Final

Al cierre, debe existir:

1. **DOCUMENTO 2 vFINAL** (aprobado)
2. **DOCUMENTO 3 v2** (este documento, aprobado)
3. **Informe de Staging** (con métricas reales)
4. **Informe Final de Migración** (con métricas de producción)
5. **Logs de migración** (guardados en BD)

---

## 📝 RESUMEN EJECUTIVO

### 🎯 Objetivo

Migrar EDN360 de AS IS a TO BE (client_drawer) en **6-7 semanas** sin pérdida de datos ni downtime.

---

### 📊 Fases

0. **Preparación** (3-5 días)
0.5. **STAGING** (5-7 días) ⚠️ OBLIGATORIA
1. **Coexistencia** (1-2 semanas)
2. **Migración** (2-3 días)
3. **Switch** (1 día + 48h)
4. **Limpieza** (2-3 días)

---

### 🔒 Seguridad

- Backups antes de cada fase crítica
- Feature flags para rollback rápido
- Validación exhaustiva (umbrales > 95%)
- Plan de rollback documentado

---

### 👥 Responsabilidades

- **Equipo Dev:** Ejecución técnica, monitoreo, rollback
- **Jorge:** Validación de muestras, aprobación GO/NO-GO, decisión rollback

---

### ✅ Aprobación

**Este manual operativo requiere aprobación formal de Jorge Calcerrada antes de iniciar ejecución.**

---

**Fin del Manual Operativo**
