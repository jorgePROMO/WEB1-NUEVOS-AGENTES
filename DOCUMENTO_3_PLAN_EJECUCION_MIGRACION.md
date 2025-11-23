# DOCUMENTO 3: PLAN DE EJECUCIÓN Y MIGRACIÓN

**Sistema:** E.D.N.360 - Migración AS IS → TO BE (Client Drawer)  
**Fecha:** Enero 2025  
**Versión:** 1.0  
**Estado:** Pendiente de aprobación  
**Referencia:** Documento 2 vFINAL (Aprobado)  

---

## 📋 ÍNDICE

### PARTE 1: VISIÓN GENERAL
1. [Objetivos de la Migración](#1-objetivos)
2. [Visión General de las Fases](#2-visión-general)
3. [Principios de Seguridad](#3-principios-de-seguridad)

### PARTE 2: DETALLE POR FASE
4. [Fase 0: Preparación](#4-fase-0-preparación)
5. [Fase 1: Coexistencia AS IS + TO BE](#5-fase-1-coexistencia)
6. [Fase 2: Migración de Datos](#6-fase-2-migración-de-datos)
7. [Fase 3: Switch a Client Drawer](#7-fase-3-switch-a-client-drawer)
8. [Fase 4: Limpieza Legacy](#8-fase-4-limpieza-legacy)

### PARTE 3: MIGRACIÓN DE DATOS POR TIPO
9. [Migración de Cuestionarios](#9-migración-cuestionarios)
10. [Migración de Followups](#10-migración-followups)
11. [Migración de Medidas](#11-migración-medidas)
12. [Migración de Planes Antiguos](#12-migración-planes-antiguos)

### PARTE 4: CONTINGENCIA Y TIMELINE
13. [Plan de Rollback](#13-plan-de-rollback)
14. [Timeline Consolidado](#14-timeline-consolidado)
15. [Checklist de Aprobación](#15-checklist-aprobación)

---

## 1. OBJETIVOS

### 🎯 Objetivo Principal

> **Migrar EDN360 del modelo AS IS (6+ colecciones dispersas) al modelo TO BE (client_drawer) sin pérdida de datos, sin downtime, y sin afectar la experiencia del cliente.**

### ✅ Criterios de Éxito Global

1. **0% pérdida de datos:**
   - Todos los cuestionarios migrados
   - Todos los planes históricos preservados
   - Todas las medidas y seguimientos migrados

2. **0% downtime:**
   - Sistema disponible durante toda la migración
   - Clientes pueden seguir viendo planes

3. **0% regresiones funcionales:**
   - Generación de nuevos planes funciona igual o mejor
   - Historial de clientes accesible
   - Seguimientos mensuales funcionan

4. **Transición limpia:**
   - Código legacy eliminado al finalizar
   - Colecciones antiguas deprecadas
   - Documentación actualizada

---

## 2. VISIÓN GENERAL

### 📊 Las 5 Fases de la Migración

```
┌─────────────────────────────────────────────────────────────────┐
│ FASE 0: PREPARACIÓN (Sin impacto en producción)                │
│ - Crear modelos Pydantic                                       │
│ - Crear colección client_drawers                               │
│ - Tests unitarios                                              │
│ ────────────────────────────────────────────────────────────── │
│ Duración: 3-5 días                                             │
│ Rollback: N/A (no afecta producción)                           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ FASE 1: COEXISTENCIA (Dual-write mode)                         │
│ - Escritura en ambos sistemas (AS IS + TO BE)                  │
│ - Lectura sigue siendo AS IS                                   │
│ - Validación en paralelo                                       │
│ ────────────────────────────────────────────────────────────── │
│ Duración: 1-2 semanas                                          │
│ Rollback: Fácil (solo desactivar escritura TO BE)              │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ FASE 2: MIGRACIÓN DE DATOS (Offline batch)                     │
│ - Backup completo                                              │
│ - Migrar datos históricos a client_drawers                     │
│ - Validación exhaustiva                                        │
│ ────────────────────────────────────────────────────────────── │
│ Duración: 2-3 días                                             │
│ Rollback: Medio (restaurar desde backup)                       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ FASE 3: SWITCH A CLIENT_DRAWER (Critical moment)               │
│ - Orquestadores leen de client_drawers                         │
│ - Endpoints migrados a TO BE                                   │
│ - Monitoreo intensivo 48h                                      │
│ ────────────────────────────────────────────────────────────── │
│ Duración: 1 día (+ 48h monitoreo)                              │
│ Rollback: Difícil (requiere feature flag + revert)             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ FASE 4: LIMPIEZA LEGACY (Post-stabilización)                   │
│ - Eliminar código legacy                                       │
│ - Deprecar colecciones antiguas                                │
│ - Documentación final                                          │
│ ────────────────────────────────────────────────────────────── │
│ Duración: 2-3 días                                             │
│ Rollback: N/A (sistema ya estabilizado)                        │
└─────────────────────────────────────────────────────────────────┘

TOTAL: ~4 semanas (incluyendo monitoreo)
```

---

## 3. PRINCIPIOS DE SEGURIDAD

### 🔒 Reglas Inquebrantables

1. **Backup antes de TODO:**
   - Backup completo antes de cada fase crítica
   - Backups diferenciales durante la migración
   - Retención: 30 días mínimo

2. **Validación en CADA paso:**
   - Tests automáticos
   - Muestras aleatorias manuales
   - Comparación AS IS vs TO BE

3. **Feature flags para TODOS los cambios:**
   - `USE_CLIENT_DRAWER_READ`: Activar lectura de drawer
   - `USE_CLIENT_DRAWER_WRITE`: Activar escritura en drawer
   - `DISABLE_LEGACY_ENDPOINTS`: Desactivar endpoints antiguos

4. **Monitoreo intensivo:**
   - Logs estructurados
   - Métricas Prometheus
   - Alertas en Slack/Email

5. **Rollback plan SIEMPRE listo:**
   - Documentado paso a paso
   - Probado en staging
   - Tiempo de ejecución conocido

---

## 4. FASE 0: PREPARACIÓN

### 🎯 Objetivo

Crear toda la infraestructura TO BE sin afectar producción.

### 📋 Tareas

#### 4.1. Crear Modelos Pydantic

**Archivo:** `/app/backend/models/client_drawer.py`

```python
# Ya documentado en Documento 2, sección 3
# Incluye:
# - ClientDrawer
# - ServiceModule
# - QuestionnaireInicial
# - ClientContextSnapshot
# - etc.
```

**Validación:**
```python
# Test
def test_client_drawer_model_validation():
    """Verificar que el modelo Pydantic valida correctamente"""
    drawer = ClientDrawer(
        client_drawer_id="client_test",
        user_id="test_user",
        profile=ClientProfile(...),
        services=ClientServices(...)
    )
    assert drawer.client_drawer_id == "client_test"
```

---

#### 4.2. Crear Colección `client_drawers`

**Script:** `/app/backend/migration/scripts/00_create_collection.py`

```python
"""
Script 00: Crear colección client_drawers con índices
"""

from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv('MONGO_URL')
DB_NAME = os.getenv('DB_NAME')

async def create_client_drawers_collection():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Verificar si ya existe
    collections = await db.list_collection_names()
    if "client_drawers" in collections:
        print("✅ Collection 'client_drawers' already exists")
        return
    
    # Crear colección
    await db.create_collection("client_drawers")
    print("✅ Collection 'client_drawers' created")
    
    # Crear índices
    await db.client_drawers.create_index("user_id", unique=True)
    await db.client_drawers.create_index("meta.active_services")
    await db.client_drawers.create_index("services.training.active")
    await db.client_drawers.create_index("services.nutrition.active")
    
    print("✅ Indexes created")
    
    client.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_client_drawers_collection())
```

**Ejecución:**
```bash
cd /app/backend/migration
python scripts/00_create_collection.py
```

**Validación:**
```bash
# Verificar que la colección existe
mongosh $MONGO_URL/$DB_NAME --eval "db.client_drawers.getIndexes()"
```

---

#### 4.3. Crear Helper de Migración

**Archivo:** `/app/backend/migration/migration_helpers.py`

```python
"""
Helpers comunes para la migración
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class MigrationHelper:
    """Clase helper para operaciones de migración"""
    
    def __init__(self, db):
        self.db = db
    
    # ================================================
    # CONSTRUCCIÓN DE CUESTIONARIO JERÁRQUICO
    # ================================================
    
    def build_hierarchical_questionnaire(
        self,
        flat_responses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convierte cuestionario plano a estructura jerárquica (10 bloques).
        
        Input (AS IS):
        {
          "nombre_completo": "Jorge",
          "peso": "85",
          "objetivo_fisico": "Perder grasa",
          ...
        }
        
        Output (TO BE):
        {
          "personal_data": { "nombre_completo": "Jorge" },
          "measurements": { "peso_kg": 85 },
          "goals": { "primary_objective": "Perder grasa" },
          ...
        }
        """
        hierarchical = {
            "personal_data": {},
            "measurements": {},
            "health": {},
            "work_life": {},
            "sports_background": {},
            "availability": {},
            "daily_schedule": {},
            "nutrition_habits": {},
            "goals": {},
            "additional_info": {}
        }
        
        # Mapeo de campos planos → bloques jerárquicos
        field_mapping = {
            # Personal Data
            "nombre_completo": ("personal_data", "nombre_completo"),
            "email": ("personal_data", "email"),
            "fecha_nacimiento": ("personal_data", "fecha_nacimiento"),
            "edad": ("personal_data", "edad"),
            "sexo": ("personal_data", "sexo"),
            "profesion": ("personal_data", "profesion"),
            "telefono": ("personal_data", "telefono"),
            "whatsapp": ("personal_data", "whatsapp"),
            
            # Measurements
            "peso": ("measurements", "peso_kg"),
            "altura_cm": ("measurements", "altura_cm"),
            "grasa_porcentaje": ("measurements", "grasa_porcentaje"),
            "cintura_cm": ("measurements", "circunferencias.cintura_cm"),
            "cadera_cm": ("measurements", "circunferencias.cadera_cm"),
            
            # Health
            "medicamentos": ("health", "medications.current"),
            "alergias_intolerancias": ("health", "medications.allergies"),
            "enfermedad_cronica": ("health", "chronic_conditions.general"),
            "hernias_protusiones": ("health", "chronic_conditions.musculoskeletal.hernias_protusions"),
            "hipertension": ("health", "chronic_conditions.cardiovascular.hypertension"),
            "diabetes": ("health", "chronic_conditions.metabolic.diabetes"),
            
            # Work Life
            "estres_profesion": ("work_life", "occupation.stress_level"),
            "movimiento_trabajo": ("work_life", "occupation.movement_type"),
            "horas_trabajo": ("work_life", "occupation.hours_per_day"),
            "actividad_fisica_diaria": ("work_life", "daily_activity.activity_level"),
            
            # Sports Background
            "practicado_deporte": ("sports_background", "previous_sports.practiced"),
            "entrenado_gimnasio": ("sports_background", "gym_experience.trained_before"),
            "resistencia_cardiorespiratoria": ("sports_background", "current_fitness.cardiorespiratory"),
            "fuerza": ("sports_background", "current_fitness.strength"),
            "flexibilidad": ("sports_background", "current_fitness.flexibility"),
            
            # Availability
            "dias_semana_entrenar": ("availability", "training_schedule.days_per_week"),
            "tiempo_sesion": ("availability", "training_schedule.session_duration_min"),
            "entrena_manana_tarde": ("availability", "training_schedule.preferred_time"),
            "gimnasio": ("availability", "location.trains_at_gym"),
            "material_casa": ("availability", "location.home_equipment"),
            
            # Daily Schedule
            "hora_levanta": ("daily_schedule", "wake_up"),
            "hora_desayuno": ("daily_schedule", "breakfast"),
            "hora_comida": ("daily_schedule", "lunch"),
            "hora_cena": ("daily_schedule", "dinner"),
            "hora_acuesta": ("daily_schedule", "sleep"),
            "horas_duerme": ("daily_schedule", "sleep_hours"),
            
            # Nutrition Habits
            "comidas_dia": ("nutrition_habits", "meal_frequency"),
            "alimento_no_soporta": ("nutrition_habits", "preferences.disliked_foods"),
            "comida_favorita": ("nutrition_habits", "preferences.favorite_foods"),
            "dietas_anteriores": ("nutrition_habits", "diet_history"),
            "come_fuera_casa": ("nutrition_habits", "eating_patterns.eats_out_frequency"),
            "azucar_dulces_bolleria": ("nutrition_habits", "eating_patterns.sugar_sweets"),
            
            # Goals ⭐
            "objetivo_fisico": ("goals", "primary_objective"),
            "experiencia_ejercicio_constante": ("goals", "experience.consistency_history"),
            "nivel_energia_dia": ("goals", "experience.energy_level"),
            "motiva_ejercicio": ("goals", "motivation.why_exercise"),
            
            # Additional Info
            "comentarios_adicionales": ("additional_info", "comments")
        }
        
        # Aplicar mapeo
        for flat_key, value in flat_responses.items():
            if flat_key in field_mapping:
                block, nested_path = field_mapping[flat_key]
                
                # Manejar paths anidados (ej: "circunferencias.cintura_cm")
                self._set_nested_value(hierarchical[block], nested_path, value)
            else:
                # Campo no mapeado, log warning
                logger.warning(f"Unmapped field in questionnaire: {flat_key}")
        
        return hierarchical
    
    def _set_nested_value(self, obj: Dict, path: str, value: Any):
        """Set valor en path anidado (ej: 'a.b.c' → obj['a']['b']['c'] = value)"""
        keys = path.split(".")
        for key in keys[:-1]:
            if key not in obj:
                obj[key] = {}
            obj = obj[key]
        obj[keys[-1]] = value
    
    # ================================================
    # CONSTRUCCIÓN DE SNAPSHOT DESDE PLAN LEGACY
    # ================================================
    
    def build_snapshot_from_legacy_plan(
        self,
        training_plan: Dict,
        nutrition_plan: Dict,
        version: int
    ) -> Dict:
        """
        Construye un snapshot desde planes legacy que NO tienen snapshot_id.
        
        Reconstruye el ClientContext a partir de los outputs de E1-E9 y N0-N8
        guardados en los planes.
        """
        snapshot = {
            "snapshot_id": f"snapshot_legacy_v{version}",
            "version": version,
            "created_at": training_plan.get("generated_at", datetime.now(timezone.utc)),
            "trigger": "migrated_from_legacy",
            "client_context": {
                "meta": {
                    "client_id": training_plan["user_id"],
                    "snapshot_id": f"snapshot_legacy_v{version}",
                    "version": version
                },
                "training": {},
                "nutrition": {}
            },
            "plans_generated": {
                "training_plan_id": training_plan["_id"],
                "nutrition_plan_id": nutrition_plan["_id"] if nutrition_plan else None
            },
            "generation_job_id": training_plan.get("job_id", "unknown")
        }
        
        # Extraer outputs de E1-E9 del training_plan
        training_fields = [
            "client_summary", "profile", "constraints", "prehab", "progress",
            "capacity", "adaptation", "mesocycle", "sessions", "safe_sessions",
            "audit", "bridge_for_nutrition"
        ]
        
        for field in training_fields:
            if field in training_plan:
                snapshot["client_context"]["training"][field] = training_plan[field]
            elif f"e{training_fields.index(field)+1}_output" in training_plan:
                # Formato legacy: e1_output, e2_output, etc.
                output = training_plan[f"e{training_fields.index(field)+1}_output"]
                snapshot["client_context"]["training"][field] = output
        
        # Extraer outputs de N0-N8 del nutrition_plan
        if nutrition_plan:
            nutrition_fields = [
                "profile", "metabolism", "energy_strategy", "macro_design",
                "weekly_structure", "timing_plan", "adherence_report", "audit"
            ]
            
            for field in nutrition_fields:
                if field in nutrition_plan:
                    snapshot["client_context"]["nutrition"][field] = nutrition_plan[field]
        
        return snapshot
    
    # ================================================
    # VALIDACIÓN
    # ================================================
    
    async def validate_drawer(self, drawer: Dict) -> List[str]:
        """
        Valida un client_drawer completo.
        
        Returns:
            Lista de errores (vacía si OK)
        """
        errors = []
        
        # Validar estructura básica
        required_keys = ["_id", "user_id", "profile", "services", "meta"]
        for key in required_keys:
            if key not in drawer:
                errors.append(f"Missing required key: {key}")
        
        # Validar servicios activos
        if "services" in drawer:
            for service_name in ["training", "nutrition"]:
                service = drawer["services"].get(service_name)
                if service and service.get("active"):
                    # Servicio activo debe tener cuestionario inicial
                    if not service.get("questionnaires", {}).get("inicial"):
                        errors.append(
                            f"{service_name} is active but missing inicial questionnaire"
                        )
        
        # Validar coherencia de snapshots
        for service_name in ["training", "nutrition"]:
            service = drawer["services"].get(service_name)
            if service and service.get("snapshots"):
                snapshots = service["snapshots"]
                
                # Verificar versionado secuencial
                versions = [s["version"] for s in snapshots]
                if versions != list(range(1, len(versions) + 1)):
                    errors.append(
                        f"{service_name} snapshots have non-sequential versions: {versions}"
                    )
                
                # Verificar previous_snapshot_id
                for i, snapshot in enumerate(snapshots):
                    if i == 0:
                        # Primer snapshot no debe tener previous
                        if snapshot.get("previous_snapshot_id"):
                            errors.append(
                                f"{service_name} first snapshot has previous_snapshot_id"
                            )
                    else:
                        # Snapshots subsecuentes deben apuntar al anterior
                        expected_prev = snapshots[i-1]["snapshot_id"]
                        actual_prev = snapshot.get("previous_snapshot_id")
                        if actual_prev != expected_prev:
                            errors.append(
                                f"{service_name} snapshot v{snapshot['version']} "
                                f"has wrong previous_snapshot_id: {actual_prev} "
                                f"(expected {expected_prev})"
                            )
        
        return errors
```

---

#### 4.4. Tests Unitarios

**Archivo:** `/app/backend/tests/test_migration_helpers.py`

```python
import pytest
from migration.migration_helpers import MigrationHelper

def test_build_hierarchical_questionnaire():
    """Test: Conversión de cuestionario plano a jerárquico"""
    helper = MigrationHelper(None)
    
    flat_responses = {
        "nombre_completo": "Jorge Calcerrada",
        "peso": "85",
        "altura_cm": "178",
        "objetivo_fisico": "Perder grasa",
        "dias_semana_entrenar": "4"
    }
    
    hierarchical = helper.build_hierarchical_questionnaire(flat_responses)
    
    # Verificar estructura
    assert "personal_data" in hierarchical
    assert "measurements" in hierarchical
    assert "goals" in hierarchical
    
    # Verificar valores
    assert hierarchical["personal_data"]["nombre_completo"] == "Jorge Calcerrada"
    assert hierarchical["measurements"]["peso_kg"] == "85"
    assert hierarchical["goals"]["primary_objective"] == "Perder grasa"

def test_build_snapshot_from_legacy_plan():
    """Test: Construcción de snapshot desde plan legacy"""
    helper = MigrationHelper(None)
    
    training_plan = {
        "_id": "training_v1",
        "user_id": "1762...",
        "generated_at": "2025-01-03T10:00:00Z",
        "client_summary": {"objetivo": "Pérdida de grasa"},
        "capacity": {"volumen_semanal": 12}
    }
    
    nutrition_plan = {
        "_id": "nutrition_v1",
        "metabolism": {"tdee": 2400}
    }
    
    snapshot = helper.build_snapshot_from_legacy_plan(
        training_plan, nutrition_plan, version=1
    )
    
    # Verificar estructura
    assert snapshot["snapshot_id"] == "snapshot_legacy_v1"
    assert snapshot["version"] == 1
    assert snapshot["trigger"] == "migrated_from_legacy"
    
    # Verificar ClientContext
    assert snapshot["client_context"]["training"]["client_summary"]["objetivo"] == "Pérdida de grasa"
    assert snapshot["client_context"]["nutrition"]["metabolism"]["tdee"] == 2400

@pytest.mark.asyncio
async def test_validate_drawer():
    """Test: Validación de drawer"""
    helper = MigrationHelper(None)
    
    # Drawer válido
    valid_drawer = {
        "_id": "client_test",
        "user_id": "test",
        "profile": {},
        "services": {
            "training": {
                "active": True,
                "questionnaires": {
                    "inicial": {"version": "1.0.0"}
                },
                "snapshots": [
                    {"snapshot_id": "v1", "version": 1},
                    {"snapshot_id": "v2", "version": 2, "previous_snapshot_id": "v1"}
                ]
            }
        },
        "meta": {}
    }
    
    errors = await helper.validate_drawer(valid_drawer)
    assert len(errors) == 0
    
    # Drawer inválido: servicio activo sin cuestionario
    invalid_drawer = {
        "_id": "client_test",
        "user_id": "test",
        "profile": {},
        "services": {
            "training": {
                "active": True,
                "questionnaires": {}  # Falta inicial
            }
        },
        "meta": {}
    }
    
    errors = await helper.validate_drawer(invalid_drawer)
    assert len(errors) > 0
    assert "missing inicial questionnaire" in errors[0]
```

---

### ✅ Criterios de Validación Fase 0

| **Criterio** | **Validación** | **Estado** |
|---|---|---|
| Modelos Pydantic creados | Tests unitarios pasan | ⏳ Pendiente |
| Colección `client_drawers` existe | Query MongoDB exitoso | ⏳ Pendiente |
| Índices creados | `getIndexes()` muestra 4 índices | ⏳ Pendiente |
| Helpers de migración probados | Tests unitarios pasan | ⏳ Pendiente |

### 🔄 Rollback Fase 0

**N/A** - No afecta producción. Si hay errores, simplemente corregir y re-ejecutar.

### ⏱️ Duración Estimada

**3-5 días** (desarrollo + tests + revisión)

---

## 5. FASE 1: COEXISTENCIA

### 🎯 Objetivo

Escribir en AMBOS sistemas (AS IS + TO BE) sin cambiar la lectura. Validar que el drawer se puebla correctamente.

### 📋 Estrategia: Dual-Write Mode

```
Usuario completa cuestionario
    ↓
┌───────────────────────────────────────┐
│ Endpoint: POST /api/questionnaire     │
│                                       │
│ 1. Escribir en AS IS (actual)        │
│    nutrition_questionnaire_submissions│
│                                       │
│ 2. Escribir en TO BE (nuevo)         │
│    client_drawers                     │
│                                       │
│ 3. Comparar ambos escritos            │
│    (validación en background)         │
└───────────────────────────────────────┘
    ↓
Lectura SIGUE siendo AS IS
(Generación de planes lee de colecciones antiguas)
```

### 📋 Tareas

#### 5.1. Implementar Dual-Write en Endpoints

**Feature Flag:**

```python
# /app/backend/config.py

import os

class Config:
    # Feature flags
    USE_CLIENT_DRAWER_WRITE = os.getenv("USE_CLIENT_DRAWER_WRITE", "false").lower() == "true"
    USE_CLIENT_DRAWER_READ = os.getenv("USE_CLIENT_DRAWER_READ", "false").lower() == "true"
    DISABLE_LEGACY_ENDPOINTS = os.getenv("DISABLE_LEGACY_ENDPOINTS", "false").lower() == "true"
```

**Modificar Endpoint de Cuestionario:**

```python
# /app/backend/server.py

from config import Config
from migration.migration_helpers import MigrationHelper

@app.post("/api/questionnaire/submit")
async def submit_questionnaire(user_id: str, responses: Dict):
    """
    Endpoint de submission de cuestionario.
    
    FASE 1: Dual-write mode
    """
    
    # ========================================
    # ESCRITURA AS IS (Sistema Antiguo)
    # ========================================
    submission = {
        "_id": f"submission_{uuid.uuid4()}",
        "user_id": user_id,
        "responses": responses,
        "submitted_at": datetime.now(timezone.utc),
        "plan_generated": False,
        "plan_id": None
    }
    
    await db.nutrition_questionnaire_submissions.insert_one(submission)
    logger.info(f"✅ Written to AS IS: {submission['_id']}")
    
    # ========================================
    # ESCRITURA TO BE (Client Drawer)
    # ========================================
    if Config.USE_CLIENT_DRAWER_WRITE:
        try:
            helper = MigrationHelper(db)
            
            # Convertir a estructura jerárquica
            hierarchical_responses = helper.build_hierarchical_questionnaire(responses)
            
            # Crear questionnaire inicial
            questionnaire_inicial = {
                "submitted_at": datetime.now(timezone.utc),
                "version": "1.0.0",
                "schema_version": "questionnaire_training_v1",
                "responses": hierarchical_responses
            }
            
            # Extraer medidas para measurements[]
            measurement = {
                "measurement_id": f"measure_{uuid.uuid4()}",
                "date": datetime.now(timezone.utc),
                "tipo": "inicial",
                "source": "cuestionario_inicial",
                "data": {
                    "peso": responses.get("peso"),
                    "altura_cm": responses.get("altura_cm"),
                    "grasa_porcentaje": responses.get("grasa_porcentaje")
                }
            }
            
            # Extraer profile
            profile = {
                "nombre_completo": responses.get("nombre_completo"),
                "email": responses.get("email"),
                "fecha_nacimiento": responses.get("fecha_nacimiento"),
                "edad": int(responses.get("edad", 0)),
                "sexo": responses.get("sexo"),
                "profesion": responses.get("profesion"),
                "telefono": responses.get("telefono"),
                "whatsapp": responses.get("whatsapp"),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Upsert client_drawer
            await db.client_drawers.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "profile": profile,
                        "services.training.questionnaires.inicial": questionnaire_inicial,
                        "services.training.active": True,
                        "services.training.enrolled_at": datetime.now(timezone.utc),
                        "meta.updated_at": datetime.now(timezone.utc)
                    },
                    "$push": {
                        "services.training.measurements": measurement
                    },
                    "$addToSet": {
                        "meta.active_services": "training"
                    },
                    "$setOnInsert": {
                        "_id": f"client_{user_id}",
                        "user_id": user_id,
                        "meta.created_at": datetime.now(timezone.utc),
                        "meta.has_archived_snapshots": False,
                        "meta.status": "active"
                    }
                },
                upsert=True
            )
            
            logger.info(f"✅ Written to TO BE: client_{user_id}")
            
            # ========================================
            # VALIDACIÓN EN BACKGROUND
            # ========================================
            asyncio.create_task(
                validate_dual_write(user_id, submission["_id"])
            )
        
        except Exception as e:
            logger.error(f"❌ Error writing to TO BE: {e}")
            # NO FALLAR: AS IS ya se escribió correctamente
            # Solo loguear error para investigación
    
    return {"status": "success", "submission_id": submission["_id"]}


async def validate_dual_write(user_id: str, submission_id: str):
    """
    Valida que la escritura dual fue coherente.
    
    Ejecuta en background, no bloquea el response.
    """
    await asyncio.sleep(1)  # Dar tiempo a que se propaguen escrituras
    
    try:
        # Leer AS IS
        submission_as_is = await db.nutrition_questionnaire_submissions.find_one(
            {"_id": submission_id}
        )
        
        # Leer TO BE
        drawer_to_be = await db.client_drawers.find_one(
            {"user_id": user_id}
        )
        
        if not drawer_to_be:
            logger.error(f"❌ Dual-write validation failed: drawer not found for {user_id}")
            return
        
        # Comparar campos clave
        as_is_objetivo = submission_as_is["responses"].get("objetivo_fisico")
        to_be_objetivo = drawer_to_be["services"]["training"]["questionnaires"]["inicial"]["responses"]["goals"]["primary_objective"]
        
        if as_is_objetivo != to_be_objetivo:
            logger.error(
                f"❌ Dual-write MISMATCH for {user_id}: "
                f"AS IS objetivo='{as_is_objetivo}', TO BE objetivo='{to_be_objetivo}'"
            )
        else:
            logger.info(f"✅ Dual-write validation PASSED for {user_id}")
        
        # Guardar resultado de validación
        await db.dual_write_validations.insert_one({
            "user_id": user_id,
            "submission_id": submission_id,
            "validated_at": datetime.now(timezone.utc),
            "match": as_is_objetivo == to_be_objetivo,
            "as_is_objetivo": as_is_objetivo,
            "to_be_objetivo": to_be_objetivo
        })
    
    except Exception as e:
        logger.error(f"❌ Dual-write validation error for {user_id}: {e}")
```

---

#### 5.2. Activar Feature Flag

```bash
# En .env del backend
USE_CLIENT_DRAWER_WRITE=true
USE_CLIENT_DRAWER_READ=false  # Lectura sigue siendo AS IS

# Reiniciar backend
sudo supervisorctl restart backend
```

---

#### 5.3. Monitoreo de Dual-Write

**Dashboard de Métricas:**

```python
# /app/backend/endpoints/monitoring.py

@app.get("/admin/monitoring/dual-write-stats")
async def get_dual_write_stats():
    """
    Estadísticas de validación dual-write.
    """
    total_validations = await db.dual_write_validations.count_documents({})
    
    matching = await db.dual_write_validations.count_documents({"match": True})
    mismatching = await db.dual_write_validations.count_documents({"match": False})
    
    # Últimas 10 validaciones
    recent = await db.dual_write_validations.find().sort(
        "validated_at", -1
    ).limit(10).to_list(10)
    
    return {
        "total_validations": total_validations,
        "matching": matching,
        "mismatching": mismatching,
        "match_rate": matching / total_validations if total_validations > 0 else 0,
        "recent_validations": recent
    }
```

**Consultar Dashboard:**

```bash
curl http://localhost:8001/api/admin/monitoring/dual-write-stats
```

---

### ✅ Criterios de Validación Fase 1

| **Criterio** | **Validación** | **Umbral** |
|---|---|---|
| Escritura dual funciona | Cuestionarios nuevos en ambos sistemas | 100% |
| Match rate | Validación AS IS vs TO BE | > 98% |
| Sin errores críticos | Logs de backend | 0 errores |
| Performance | Tiempo de response endpoint | < 200ms |

**Validación Manual:**

```python
# Script: /app/backend/migration/scripts/01_validate_dual_write.py

async def validate_dual_write_sample():
    """Validar 10 clientes aleatorios"""
    
    # Obtener 10 submissions recientes
    submissions = await db.nutrition_questionnaire_submissions.find().sort(
        "submitted_at", -1
    ).limit(10).to_list(10)
    
    results = []
    
    for submission in submissions:
        user_id = submission["user_id"]
        
        # Leer drawer correspondiente
        drawer = await db.client_drawers.find_one({"user_id": user_id})
        
        if not drawer:
            results.append({
                "user_id": user_id,
                "status": "ERROR",
                "message": "Drawer not found"
            })
            continue
        
        # Comparar campos clave
        as_is_peso = submission["responses"].get("peso")
        to_be_peso = drawer["services"]["training"]["questionnaires"]["inicial"]["responses"]["measurements"]["peso_kg"]
        
        match = str(as_is_peso) == str(to_be_peso)
        
        results.append({
            "user_id": user_id,
            "status": "MATCH" if match else "MISMATCH",
            "as_is_peso": as_is_peso,
            "to_be_peso": to_be_peso
        })
    
    # Imprimir resultados
    for result in results:
        print(f"{result['user_id']}: {result['status']}")
    
    # Estadísticas
    matches = sum(1 for r in results if r["status"] == "MATCH")
    print(f"\nMatch rate: {matches}/{len(results)} ({matches/len(results)*100:.1f}%)")
    
    return results

if __name__ == "__main__":
    import asyncio
    asyncio.run(validate_dual_write_sample())
```

---

### 🔄 Rollback Fase 1

**Si hay problemas, desactivar escritura TO BE:**

```bash
# Desactivar feature flag
USE_CLIENT_DRAWER_WRITE=false

# Reiniciar backend
sudo supervisorctl restart backend
```

**Sistema vuelve a AS IS puro. Sin impacto en clientes.**

**Tiempo de rollback:** < 2 minutos

---

### ⏱️ Duración Estimada

**1-2 semanas** (escritura dual + monitoreo + ajustes)

---

## 6. FASE 2: MIGRACIÓN DE DATOS

### 🎯 Objetivo

Migrar TODOS los datos históricos de AS IS a client_drawers.

### ⚠️ CRÍTICO: Backup Completo

**Antes de CUALQUIER migración masiva:**

```bash
# Script: /app/backend/migration/scripts/backup_full_database.sh

#!/bin/bash

BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "🔒 Starting full database backup..."

# Backup de colecciones críticas
mongodump \
  --uri="$MONGO_URL" \
  --db="$DB_NAME" \
  --out="$BACKUP_DIR" \
  --collection=nutrition_questionnaire_submissions \
  --collection=followup_submissions \
  --collection=training_plans \
  --collection=nutrition_plans \
  --collection=users

echo "✅ Backup completed: $BACKUP_DIR"
echo "Size: $(du -sh $BACKUP_DIR)"

# Guardar metadata
echo "Backup created at $(date)" > $BACKUP_DIR/metadata.txt
echo "MongoDB URI: $MONGO_URL" >> $BACKUP_DIR/metadata.txt
echo "Database: $DB_NAME" >> $BACKUP_DIR/metadata.txt
```

**Ejecutar backup:**

```bash
cd /app/backend/migration/scripts
chmod +x backup_full_database.sh
./backup_full_database.sh
```

**Verificar backup:**

```bash
ls -lh /backups/
# Debe mostrar backup reciente con tamaño > 0
```

---

### 📋 Migración por Tipo de Dato

## (continúa en siguiente sección...)

---

## 9. MIGRACIÓN CUESTIONARIOS

### 📊 Origen → Destino

```
ORIGEN (AS IS):
nutrition_questionnaire_submissions
{
  _id: "submission_xyz",
  user_id: "1762...",
  responses: { /* Dict plano */ },
  submitted_at: "2025-01-02"
}

DESTINO (TO BE):
client_drawers.services.training.questionnaires.inicial
{
  submitted_at: "2025-01-02",
  version: "1.0.0",
  responses: { /* Dict jerárquico (10 bloques) */ }
}
```

### 📝 Script de Migración

**Archivo:** `/app/backend/migration/scripts/02_migrate_questionnaires.py`

```python
"""
Script 02: Migrar cuestionarios iniciales a client_drawers
"""

from motor.motor_asyncio import AsyncIOMotorClient
from migration_helpers import MigrationHelper
import os
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URL = os.getenv('MONGO_URL')
DB_NAME = os.getenv('DB_NAME')

async def migrate_questionnaires():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    helper = MigrationHelper(db)
    
    logger.info("Starting questionnaire migration...")
    
    # Obtener todos los submissions
    submissions = await db.nutrition_questionnaire_submissions.find({}).to_list(100000)
    
    total = len(submissions)
    migrated = 0
    errors = []
    
    for i, submission in enumerate(submissions):
        try:
            user_id = submission["user_id"]
            
            # Convertir a estructura jerárquica
            hierarchical = helper.build_hierarchical_questionnaire(
                submission["responses"]
            )
            
            # Crear questionnaire inicial
            questionnaire_inicial = {
                "submitted_at": submission.get("submitted_at", datetime.now(timezone.utc)),
                "version": "1.0.0",
                "schema_version": "questionnaire_training_v1",
                "responses": hierarchical
            }
            
            # Extraer profile
            responses = submission["responses"]
            profile = {
                "nombre_completo": responses.get("nombre_completo", ""),
                "email": responses.get("email", ""),
                "fecha_nacimiento": responses.get("fecha_nacimiento", ""),
                "edad": int(responses.get("edad", 0)),
                "sexo": responses.get("sexo", ""),
                "profesion": responses.get("profesion", ""),
                "telefono": responses.get("telefono", ""),
                "whatsapp": responses.get("whatsapp", ""),
                "created_at": submission.get("submitted_at", datetime.now(timezone.utc)),
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Extraer medida inicial
            measurement = {
                "measurement_id": f"measure_migrated_{submission['_id']}",
                "date": submission.get("submitted_at", datetime.now(timezone.utc)),
                "tipo": "inicial",
                "source": f"migrated_from_{submission['_id']}",
                "data": {
                    "peso": responses.get("peso"),
                    "altura_cm": responses.get("altura_cm"),
                    "grasa_porcentaje": responses.get("grasa_porcentaje")
                }
            }
            
            # Upsert client_drawer
            await db.client_drawers.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "profile": profile,
                        "services.training.questionnaires.inicial": questionnaire_inicial,
                        "services.training.active": True,
                        "services.training.enrolled_at": submission.get("submitted_at"),
                        "meta.updated_at": datetime.now(timezone.utc)
                    },
                    "$push": {
                        "services.training.measurements": measurement
                    },
                    "$addToSet": {
                        "meta.active_services": "training"
                    },
                    "$setOnInsert": {
                        "_id": f"client_{user_id}",
                        "user_id": user_id,
                        "meta.created_at": submission.get("submitted_at"),
                        "meta.has_archived_snapshots": False,
                        "meta.status": "active"
                    }
                },
                upsert=True
            )
            
            migrated += 1
            
            if (i + 1) % 100 == 0:
                logger.info(f"Progress: {i+1}/{total} ({migrated} migrated)")
        
        except Exception as e:
            logger.error(f"Error migrating {submission['_id']}: {e}")
            errors.append({
                "submission_id": submission["_id"],
                "user_id": submission.get("user_id"),
                "error": str(e)
            })
    
    # Log final
    logger.info(f"""
    ✅ Questionnaire migration completed:
    - Total submissions: {total}
    - Successfully migrated: {migrated}
    - Errors: {len(errors)}
    """)
    
    if errors:
        logger.error(f"Errors: {errors}")
    
    # Guardar log de migración
    await db.migration_logs.insert_one({
        "migration_type": "questionnaires",
        "total": total,
        "migrated": migrated,
        "errors": errors,
        "completed_at": datetime.now(timezone.utc)
    })
    
    client.close()
    
    return {
        "total": total,
        "migrated": migrated,
        "errors": errors
    }

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(migrate_questionnaires())
    print(f"\nMigration result: {result}")
```

**Ejecución:**

```bash
cd /app/backend/migration
python scripts/02_migrate_questionnaires.py
```

---

### ✅ Validación Post-Migración

**Script:** `/app/backend/migration/scripts/02_validate_questionnaires.py`

```python
async def validate_questionnaire_migration():
    """
    Validar que cuestionarios migraron correctamente.
    
    Compara muestras aleatorias AS IS vs TO BE.
    """
    
    # Obtener 20 submissions aleatorios
    submissions = await db.nutrition_questionnaire_submissions.aggregate([
        {"$sample": {"size": 20}}
    ]).to_list(20)
    
    results = []
    
    for submission in submissions:
        user_id = submission["user_id"]
        
        # Leer drawer
        drawer = await db.client_drawers.find_one({"user_id": user_id})
        
        if not drawer:
            results.append({
                "user_id": user_id,
                "status": "ERROR",
                "message": "Drawer not found"
            })
            continue
        
        # Comparar campos críticos
        as_is_resp = submission["responses"]
        to_be_resp = drawer["services"]["training"]["questionnaires"]["inicial"]["responses"]
        
        # Campo 1: Objetivo (crítico)
        as_is_objetivo = as_is_resp.get("objetivo_fisico")
        to_be_objetivo = to_be_resp["goals"]["primary_objective"]
        objetivo_match = as_is_objetivo == to_be_objetivo
        
        # Campo 2: Peso
        as_is_peso = as_is_resp.get("peso")
        to_be_peso = str(to_be_resp["measurements"]["peso_kg"])
        peso_match = str(as_is_peso) == to_be_peso
        
        # Campo 3: Días de entreno
        as_is_dias = as_is_resp.get("dias_semana_entrenar")
        to_be_dias = str(to_be_resp["availability"]["training_schedule"]["days_per_week"])
        dias_match = str(as_is_dias) == to_be_dias
        
        all_match = objetivo_match and peso_match and dias_match
        
        results.append({
            "user_id": user_id,
            "status": "PASS" if all_match else "FAIL",
            "objetivo_match": objetivo_match,
            "peso_match": peso_match,
            "dias_match": dias_match
        })
    
    # Estadísticas
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    
    print(f"\n✅ Validation results:")
    print(f"Passed: {passed}/{len(results)} ({passed/len(results)*100:.1f}%)")
    print(f"Failed: {failed}/{len(results)}")
    
    if failed > 0:
        print(f"\n❌ Failed validations:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"  - {r['user_id']}: {r}")
    
    # Umbral: 95% de éxito mínimo
    assert passed / len(results) >= 0.95, "Migration validation failed: < 95% match rate"
    
    return results
```

---

## 10. MIGRACIÓN FOLLOWUPS

### 📊 Origen → Destino

```
ORIGEN:
followup_submissions
{
  _id: "followup_xyz",
  user_id: "1762...",
  previous_plan_id: "training_v1",
  measurements: { peso: "83" },
  adherence: { ... }
}

DESTINO:
client_drawers.services.training.questionnaires.followups[]
[
  {
    followup_id: "followup_xyz",
    submitted_at: "2025-02-03",
    previous_snapshot_id: "snapshot_v1",  // ← Debe resolverse
    measurements: { peso: "83" },
    adherence: { ... }
  }
]
```

### 📝 Script de Migración

```python
# /app/backend/migration/scripts/03_migrate_followups.py

async def migrate_followups():
    """
    Migrar followups a client_drawers.
    
    DESAFÍO: Vincular followup con snapshot correcto.
    """
    
    followups = await db.followup_submissions.find({}).to_list(100000)
    
    total = len(followups)
    migrated = 0
    errors = []
    
    for followup in followups:
        try:
            user_id = followup["user_id"]
            previous_plan_id = followup.get("previous_plan_id")
            
            # Buscar snapshot que generó ese plan
            drawer = await db.client_drawers.find_one({"user_id": user_id})
            
            if not drawer:
                errors.append({
                    "followup_id": followup["_id"],
                    "error": "Drawer not found"
                })
                continue
            
            # Buscar snapshot por plan_id
            previous_snapshot_id = None
            for snapshot in drawer["services"]["training"]["snapshots"]:
                if snapshot["plans_generated"]["training_plan_id"] == previous_plan_id:
                    previous_snapshot_id = snapshot["snapshot_id"]
                    break
            
            if not previous_snapshot_id:
                # No se pudo resolver: usar snapshot más reciente
                if drawer["services"]["training"]["snapshots"]:
                    previous_snapshot_id = drawer["services"]["training"]["snapshots"][-1]["snapshot_id"]
                else:
                    previous_snapshot_id = None
            
            # Construir followup
            followup_doc = {
                "followup_id": followup["_id"],
                "submitted_at": followup.get("submission_date", datetime.now(timezone.utc)),
                "days_since_last": followup.get("days_since_last_plan", 30),
                "previous_snapshot_id": previous_snapshot_id,
                "measurement_type": followup.get("measurement_type", "smart_scale"),
                "measurements": followup.get("measurements", {}),
                "adherence": followup.get("adherence", {}),
                "wellbeing": followup.get("wellbeing", {}),
                "changes_perceived": followup.get("changes_perceived", {}),
                "feedback": followup.get("feedback", {})
            }
            
            # Añadir a drawer
            await db.client_drawers.update_one(
                {"user_id": user_id},
                {
                    "$push": {
                        "services.training.questionnaires.followups": followup_doc
                    }
                }
            )
            
            migrated += 1
        
        except Exception as e:
            logger.error(f"Error migrating followup {followup['_id']}: {e}")
            errors.append({
                "followup_id": followup["_id"],
                "error": str(e)
            })
    
    logger.info(f"Followups migration: {migrated}/{total} migrated, {len(errors)} errors")
    
    return {"total": total, "migrated": migrated, "errors": errors}
```

---

## 11. MIGRACIÓN MEDIDAS

(Incluido en migración de cuestionarios y followups)

---

## 12. MIGRACIÓN PLANES ANTIGUOS

### 📊 Desafío: Crear Snapshots Retroactivos

**Problema:** Planes antiguos NO tienen `snapshot_id` porque se crearon antes del TO BE.

**Solución:** Reconstruir snapshots desde los planes legacy.

### 📝 Script de Migración

```python
# /app/backend/migration/scripts/04_migrate_legacy_plans.py

async def migrate_legacy_plans():
    """
    Migrar planes legacy a client_drawers con snapshots retroactivos.
    """
    
    helper = MigrationHelper(db)
    
    # Obtener todos los training_plans que NO tienen snapshot_id
    legacy_plans = await db.training_plans.find({
        "snapshot_id": {"$exists": False}
    }).to_list(100000)
    
    total = len(legacy_plans)
    migrated = 0
    errors = []
    
    logger.info(f"Found {total} legacy plans to migrate")
    
    for plan in legacy_plans:
        try:
            user_id = plan["user_id"]
            
            # Buscar nutrition_plan correspondiente
            nutrition_plan = await db.nutrition_plans.find_one({
                "user_id": user_id,
                "generated_at": plan["generated_at"]
            })
            
            # Obtener drawer
            drawer = await db.client_drawers.find_one({"user_id": user_id})
            
            if not drawer:
                errors.append({
                    "plan_id": plan["_id"],
                    "error": "Drawer not found"
                })
                continue
            
            # Determinar versión del snapshot
            current_snapshots = drawer["services"]["training"]["snapshots"]
            version = len(current_snapshots) + 1
            
            # Construir snapshot retroactivo
            snapshot = helper.build_snapshot_from_legacy_plan(
                plan, nutrition_plan, version
            )
            
            # Añadir snapshot al drawer
            await db.client_drawers.update_one(
                {"user_id": user_id},
                {
                    "$push": {
                        "services.training.snapshots": snapshot
                    }
                }
            )
            
            # Actualizar plan con snapshot_id
            await db.training_plans.update_one(
                {"_id": plan["_id"]},
                {
                    "$set": {
                        "snapshot_id": snapshot["snapshot_id"],
                        "client_drawer_id": drawer["_id"]
                    }
                }
            )
            
            if nutrition_plan:
                await db.nutrition_plans.update_one(
                    {"_id": nutrition_plan["_id"]},
                    {
                        "$set": {
                            "snapshot_id": snapshot["snapshot_id"],
                            "client_drawer_id": drawer["_id"]
                        }
                    }
                )
            
            # Añadir referencia a plans[]
            await db.client_drawers.update_one(
                {"user_id": user_id},
                {
                    "$push": {
                        "services.training.plans": {
                            "plan_id": plan["_id"],
                            "version": version,
                            "generated_at": plan["generated_at"],
                            "snapshot_id": snapshot["snapshot_id"],
                            "month": plan.get("month"),
                            "year": plan.get("year"),
                            "status": "completed"
                        }
                    }
                }
            )
            
            migrated += 1
            
            if (migrated) % 100 == 0:
                logger.info(f"Progress: {migrated}/{total}")
        
        except Exception as e:
            logger.error(f"Error migrating plan {plan['_id']}: {e}")
            errors.append({
                "plan_id": plan["_id"],
                "error": str(e)
            })
    
    logger.info(f"Legacy plans migration: {migrated}/{total}, {len(errors)} errors")
    
    return {"total": total, "migrated": migrated, "errors": errors}
```

---

### ✅ Criterios de Validación Fase 2

| **Tipo de Dato** | **Total** | **Migrado** | **Match Rate** | **Estado** |
|---|---|---|---|---|
| Cuestionarios | N | N | > 95% | ⏳ |
| Followups | M | M | > 95% | ⏳ |
| Planes Legacy | P | P | > 90% | ⏳ |

**Validación Final:**

```python
# Script: 05_validate_full_migration.py

async def validate_full_migration():
    """Validación exhaustiva post-migración"""
    
    # 1. Contar registros
    total_submissions = await db.nutrition_questionnaire_submissions.count_documents({})
    total_drawers = await db.client_drawers.count_documents({})
    
    print(f"Submissions: {total_submissions}")
    print(f"Drawers: {total_drawers}")
    
    assert total_drawers >= total_submissions * 0.95, "Drawer count too low"
    
    # 2. Validar muestra aleatoria (50 clientes)
    sample_size = 50
    drawers_sample = await db.client_drawers.aggregate([
        {"$sample": {"size": sample_size}}
    ]).to_list(sample_size)
    
    for drawer in drawers_sample:
        errors = await helper.validate_drawer(drawer)
        if errors:
            print(f"❌ Drawer {drawer['_id']} has errors: {errors}")
    
    # 3. Validar que TODOS los planes tienen snapshot_id
    plans_without_snapshot = await db.training_plans.count_documents({
        "snapshot_id": {"$exists": False}
    })
    
    print(f"Plans without snapshot_id: {plans_without_snapshot}")
    assert plans_without_snapshot == 0, "Some plans still missing snapshot_id"
    
    print("✅ Full migration validation PASSED")
```

---

### 🔄 Rollback Fase 2

**Si migración falla:**

```bash
# 1. Restaurar desde backup
mongorestore --uri="$MONGO_URL" --db="$DB_NAME" /backups/YYYYMMDD_HHMMSS/

# 2. Eliminar client_drawers parcialmente migrados
mongo $MONGO_URL/$DB_NAME --eval "db.client_drawers.deleteMany({})"

# 3. Re-ejecutar migración con correcciones
```

**Tiempo estimado de rollback:** 30-60 minutos (dependiendo del tamaño de BD)

---

### ⏱️ Duración Estimada Fase 2

**2-3 días:**
- Backup: 2-4 horas
- Migración: 8-12 horas (dependiendo de volumen)
- Validación: 4-6 horas
- Correcciones: 1 día (si necesario)

---

## 7. FASE 3: SWITCH A CLIENT_DRAWER

### 🎯 Objetivo

Cambiar la **lectura** del sistema para que los orquestadores y agentes lean SOLO de `client_drawers`.

### ⚠️ MOMENTO CRÍTICO

**Esta es la fase más delicada.** Requiere:
- ✅ Fase 2 completada 100%
- ✅ Validación exhaustiva aprobada
- ✅ Backup reciente (< 24h)
- ✅ Monitoreo activo
- ✅ Equipo disponible para rollback si es necesario

---

### 📋 Tareas

#### 7.1. Modificar Orquestador

**Archivo:** `/app/backend/edn360/orchestrator.py`

```python
# Agregar al inicio del archivo
from config import Config

# Modificar método generate_initial_plan
async def generate_initial_plan_from_job(self, job_id: str):
    """
    Generar plan inicial.
    
    FASE 3: Lee de client_drawer si feature flag activo.
    """
    
    job = await db.generation_jobs.find_one({"_id": job_id})
    
    if Config.USE_CLIENT_DRAWER_READ:
        # ========================================
        # TO BE: Leer de client_drawer
        # ========================================
        logger.info(f"🆕 Reading from client_drawer (TO BE mode)")
        
        client_drawer = await db.client_drawers.find_one(
            {"_id": job["client_drawer_id"]}
        )
        
        if not client_drawer:
            raise ValueError(f"Client drawer not found: {job['client_drawer_id']}")
        
        # Extraer cuestionario
        training_service = client_drawer["services"]["training"]
        questionnaire_data = training_service["questionnaires"]["inicial"]["responses"]
        
        # Continuar con pipeline...
        result = await self._execute_training_initial(questionnaire_data, None)
        
        # Guardar snapshot en drawer
        await self._save_snapshot_to_drawer(client_drawer["_id"], result)
    
    else:
        # ========================================
        # AS IS: Leer de colección legacy
        # ========================================
        logger.info(f"📁 Reading from legacy collections (AS IS mode)")
        
        submission = await db.nutrition_questionnaire_submissions.find_one(
            {"_id": job["submission_id"]}
        )
        
        questionnaire_data = submission["responses"]
        
        # Pipeline legacy...
```

---

#### 7.2. Activar Feature Flag

```bash
# .env
USE_CLIENT_DRAWER_READ=true  # ← ACTIVAR
USE_CLIENT_DRAWER_WRITE=true

# Reiniciar backend
sudo supervisorctl restart backend
```

---

#### 7.3. Monitoreo Intensivo (48h)

**Dashboard de métricas:**

```python
@app.get("/admin/monitoring/switch-status")
async def get_switch_status():
    """Monitorear el switch AS IS → TO BE"""
    
    # Jobs procesados en últimas 24h
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    
    recent_jobs = await db.generation_jobs.find({
        "created_at": {"$gte": cutoff}
    }).to_list(1000)
    
    # Clasificar por modo
    to_be_jobs = [j for j in recent_jobs if "client_drawer_id" in j]
    as_is_jobs = [j for j in recent_jobs if "submission_id" in j and "client_drawer_id" not in j]
    
    # Tasa de éxito
    to_be_success = [j for j in to_be_jobs if j["status"] == "completed"]
    as_is_success = [j for j in as_is_jobs if j["status"] == "completed"]
    
    return {
        "last_24h": {
            "total_jobs": len(recent_jobs),
            "to_be_jobs": len(to_be_jobs),
            "as_is_jobs": len(as_is_jobs),
            "to_be_success_rate": len(to_be_success) / len(to_be_jobs) if to_be_jobs else 0,
            "as_is_success_rate": len(as_is_success) / len(as_is_jobs) if as_is_jobs else 0
        },
        "feature_flags": {
            "USE_CLIENT_DRAWER_READ": Config.USE_CLIENT_DRAWER_READ,
            "USE_CLIENT_DRAWER_WRITE": Config.USE_CLIENT_DRAWER_WRITE
        }
    }
```

---

### ✅ Criterios de Validación Fase 3

| **Criterio** | **Umbral** | **Validación** |
|---|---|---|
| Tasa de éxito jobs TO BE | > 95% | Monitoreo 48h |
| Sin errores críticos | 0 errores | Logs backend |
| Tiempo generación plan | < 120s | Métricas |
| Planes generados correctos | 100% | Muestra manual (10 planes) |

**Validación Manual:**

```python
# Generar 3 planes de prueba con clientes reales
# Revisar manualmente que:
# 1. Objetivo es correcto
# 2. Plan tiene coherencia
# 3. Historial del cliente es visible
```

---

### 🔄 Rollback Fase 3

**Si hay problemas graves:**

```bash
# 1. Desactivar feature flag INMEDIATAMENTE
USE_CLIENT_DRAWER_READ=false

# 2. Reiniciar backend
sudo supervisorctl restart backend

# 3. Sistema vuelve a AS IS
# Tiempo de rollback: < 2 minutos
```

**¿Cuándo hacer rollback?**
- Tasa de éxito < 90%
- Errores críticos recurrentes
- Planes generados incorrectos
- Cliente reporta problemas

---

### ⏱️ Duración Estimada Fase 3

**1 día + 48h monitoreo:**
- Switch: 1 hora
- Monitoreo intensivo: 48 horas
- Ajustes: según necesidad

---

## 8. FASE 4: LIMPIEZA LEGACY

### 🎯 Objetivo

Eliminar código y colecciones legacy. **Solo después de que Fase 3 esté 100% estable.**

### 📋 Tareas

#### 8.1. Deprecar Colecciones

```python
# Script: 06_deprecate_legacy_collections.py

async def deprecate_legacy_collections():
    """
    Renombrar colecciones legacy para deprecarlas (NO eliminar aún).
    """
    
    collections_to_deprecate = [
        "nutrition_questionnaire_submissions",
        "followup_submissions"
    ]
    
    for collection in collections_to_deprecate:
        new_name = f"{collection}_DEPRECATED_{datetime.now().strftime('%Y%m%d')}"
        
        await db[collection].rename(new_name)
        
        logger.info(f"✅ Deprecated: {collection} → {new_name}")
    
    print("⚠️ Legacy collections deprecated. Can be deleted after 30 days if no issues.")
```

#### 8.2. Eliminar Código Legacy

**Archivos a modificar:**

1. `/app/backend/server.py`
   - Eliminar endpoints legacy
   - Eliminar referencias a `nutrition_questionnaire_submissions`

2. `/app/backend/edn360/orchestrator.py`
   - Eliminar branch AS IS (if Config.USE_CLIENT_DRAWER_READ)
   - Simplificar a solo lectura de drawer

3. `/app/backend/config.py`
   - Eliminar feature flags (ya no necesarios)

---

### ✅ Criterios de Validación Fase 4

| **Criterio** | **Estado** |
|---|---|
| Colecciones legacy renombradas | ✅ |
| Código legacy eliminado | ✅ |
| Tests pasan | ✅ |
| Documentación actualizada | ✅ |

---

### ⏱️ Duración Estimada Fase 4

**2-3 días:**
- Deprecar colecciones: 1 hora
- Eliminar código: 1 día
- Tests: 1 día
- Documentación: 4 horas

---

## 13. PLAN DE ROLLBACK

### 🔄 Rollback por Fase

| **Fase** | **Dificultad** | **Tiempo** | **Procedimiento** |
|---|---|---|---|
| Fase 0 | Fácil | N/A | Sin impacto, solo rehacer |
| Fase 1 | Fácil | 2 min | Desactivar `USE_CLIENT_DRAWER_WRITE` |
| Fase 2 | Media | 30-60 min | Restaurar desde backup |
| Fase 3 | Media-Alta | 2-5 min | Desactivar `USE_CLIENT_DRAWER_READ` |
| Fase 4 | N/A | N/A | Sistema ya estabilizado |

---

### 🚨 Escenarios de Rollback

#### Escenario 1: Error en Dual-Write (Fase 1)

**Síntomas:**
- Match rate < 90%
- Errores en logs al escribir drawer

**Acción:**
```bash
# Desactivar escritura TO BE
echo "USE_CLIENT_DRAWER_WRITE=false" >> /app/backend/.env
sudo supervisorctl restart backend
```

**Impacto:** Ninguno. Sistema sigue en AS IS.

---

#### Escenario 2: Migración de Datos Falla (Fase 2)

**Síntomas:**
- Errores masivos en script de migración
- Validación < 95%

**Acción:**
```bash
# 1. Detener migración
# Ctrl+C en script

# 2. Restaurar backup
mongorestore --uri="$MONGO_URL" --db="$DB_NAME" --drop /backups/BACKUP_DIR/

# 3. Limpiar client_drawers parcial
mongo $MONGO_URL/$DB_NAME --eval "db.client_drawers.deleteMany({})"

# 4. Revisar errores y re-ejecutar
```

**Impacto:** Ninguno si se detecta rápido. Sistema sigue operando en AS IS.

---

#### Escenario 3: Switch Causa Errores (Fase 3)

**Síntomas:**
- Tasa de éxito jobs < 90%
- Clientes reportan planes incorrectos
- Errores críticos en logs

**Acción INMEDIATA:**
```bash
# 1. Desactivar lectura TO BE
echo "USE_CLIENT_DRAWER_READ=false" >> /app/backend/.env

# 2. Reiniciar backend
sudo supervisorctl restart backend

# 3. Verificar que sistema volvió a AS IS
curl http://localhost:8001/api/admin/monitoring/switch-status
```

**Tiempo de ejecución:** 2-5 minutos

**Impacto:** Breve interrupción (< 5 min). Jobs en cola se reintentarán.

---

## 14. TIMELINE CONSOLIDADO

### 📅 Calendario de Ejecución

```
SEMANA 1: Preparación + Coexistencia
├─ Lun-Mar: Fase 0 (Preparación)
│   └─ Crear modelos, colección, tests
├─ Mié: Activar Fase 1 (Dual-write)
└─ Jue-Dom: Monitoreo dual-write

SEMANA 2: Coexistencia (continuación)
├─ Lun-Vie: Monitoreo + ajustes
└─ Sáb-Dom: Preparar Fase 2

SEMANA 3: Migración de Datos
├─ Lun: Backup completo (4h)
├─ Mar: Migrar cuestionarios (6h)
├─ Mié: Migrar followups + medidas (4h)
├─ Jue: Migrar planes legacy (8h)
├─ Vie: Validación exhaustiva (8h)
└─ Sáb-Dom: Buffer para correcciones

SEMANA 4: Switch + Estabilización
├─ Lun 9:00 AM: Fase 3 - Activar switch
├─ Lun-Mar: Monitoreo intensivo 48h
├─ Mié: Revisión + decisión GO/NO-GO
└─ Jue-Vie: Ajustes finales

SEMANA 5: Limpieza
├─ Lun-Mar: Fase 4 - Deprecar colecciones
├─ Mié-Jue: Eliminar código legacy
└─ Vie: Documentación final

TOTAL: ~4-5 semanas
```

---

### 👥 Responsabilidades

| **Tarea** | **Responsable** | **Apoyo** |
|---|---|---|
| **Fase 0:** Desarrollo modelos | Equipo Dev | - |
| **Fase 1:** Implementar dual-write | Equipo Dev | - |
| **Fase 1:** Monitorear match rate | Equipo Dev | Jorge (revisión) |
| **Fase 2:** Ejecutar backups | Equipo Dev | DevOps |
| **Fase 2:** Ejecutar migración | Equipo Dev | - |
| **Fase 2:** Validar migración | Equipo Dev | Jorge (muestra) |
| **Fase 3:** Activar switch | Jorge + Equipo Dev | - |
| **Fase 3:** Monitoreo 48h | Equipo Dev (24/7 disponible) | Jorge (revisión) |
| **Fase 3:** Validar planes generados | Jorge | Equipo Dev |
| **Fase 4:** Limpieza código | Equipo Dev | - |
| **Rollback (si necesario)** | Equipo Dev (inmediato) | Jorge (aprobación) |

---

## 15. CHECKLIST DE APROBACIÓN

### ✅ Checklist Pre-Ejecución

Antes de iniciar la migración, verificar:

- [ ] Documento 2 (TO BE) aprobado por Jorge
- [ ] Documento 3 (Plan Ejecución) aprobado por Jorge
- [ ] Equipo disponible para 4 semanas dedicadas
- [ ] Backups automáticos configurados
- [ ] Monitoreo (logs, métricas) funcionando
- [ ] Scripts de migración probados en staging
- [ ] Scripts de rollback documentados y probados
- [ ] Cliente de prueba (Jorge1) identificado para validaciones
- [ ] Comunicación a clientes (si downtime esperado)

---

### ✅ Checklist Post-Fase

**Después de cada fase, verificar:**

#### Fase 0:
- [ ] Colección `client_drawers` creada
- [ ] Índices creados
- [ ] Tests unitarios pasan
- [ ] Helpers de migración probados

#### Fase 1:
- [ ] Feature flag `USE_CLIENT_DRAWER_WRITE` activado
- [ ] Dual-write funcionando (match rate > 98%)
- [ ] Sin errores críticos en logs
- [ ] Dashboard de monitoreo accesible

#### Fase 2:
- [ ] Backup completo realizado y verificado
- [ ] Cuestionarios migrados (validación > 95%)
- [ ] Followups migrados (validación > 95%)
- [ ] Planes legacy migrados (validación > 90%)
- [ ] Snapshots retroactivos creados
- [ ] Validación exhaustiva aprobada

#### Fase 3:
- [ ] Feature flag `USE_CLIENT_DRAWER_READ` activado
- [ ] Tasa de éxito jobs > 95% (48h monitoreo)
- [ ] Sin errores críticos
- [ ] Planes generados correctos (muestra manual)
- [ ] Jorge aprueba GO para Fase 4

#### Fase 4:
- [ ] Colecciones legacy deprecadas
- [ ] Código legacy eliminado
- [ ] Tests pasan
- [ ] Documentación actualizada
- [ ] Sistema estabilizado

---

### ✅ Criterio de Aprobación Final

**Para considerar la migración COMPLETA:**

1. ✅ Todas las fases completadas sin errores críticos
2. ✅ Sistema funcionando en TO BE (client_drawer) al 100%
3. ✅ Código legacy eliminado
4. ✅ Documentación actualizada
5. ✅ Jorge aprueba formalmente la migración
6. ✅ Sin incidentes reportados por clientes
7. ✅ Métricas de performance estables

---

## 📝 RESUMEN EJECUTIVO

### 🎯 Objetivo

Migrar EDN360 de arquitectura AS IS (6+ colecciones) a TO BE (client_drawer) en **4-5 semanas** sin pérdida de datos ni downtime.

### 📊 5 Fases

1. **Preparación** (3-5 días): Crear infraestructura TO BE
2. **Coexistencia** (1-2 semanas): Dual-write, validación paralela
3. **Migración** (2-3 días): Migrar datos históricos
4. **Switch** (1 día + 48h): Cambiar lectura a drawer
5. **Limpieza** (2-3 días): Eliminar legacy

### 🔒 Seguridad

- Backups antes de cada fase crítica
- Feature flags para activar/desactivar cambios
- Rollback documentado y probado
- Validación exhaustiva en cada paso

### ⏱️ Timeline

**Total: 4-5 semanas** (incluyendo monitoreo y buffer para correcciones)

### 👥 Responsabilidades

- **Equipo Dev:** Ejecución técnica, monitoreo, rollback
- **Jorge:** Validación de muestras, aprobación GO/NO-GO, decisión rollback

---

**¿Apruebas este Plan de Ejecución para proceder con la migración?**

---

**Fin del Documento 3**
