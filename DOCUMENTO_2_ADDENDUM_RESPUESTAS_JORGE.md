# DOCUMENTO 2 - ADDENDUM: Respuestas a Puntos Críticos

**Fecha:** Enero 2025  
**Versión:** 1.1  
**Autor:** Equipo Técnico EDN360  
**Revisión de:** Jorge Calcerrada  

---

## 📋 ÍNDICE DE RESPUESTAS

1. [Tamaño y Crecimiento del Client Drawer](#1-tamaño-y-crecimiento-del-client-drawer)
2. [Duplicidad Mínima Aceptable en Snapshots](#2-duplicidad-mínima-aceptable-en-snapshots)
3. [Estructura del Cuestionario - Versionado](#3-estructura-del-cuestionario-versionado)
4. [Multi-Producto y Escalabilidad](#4-multi-producto-y-escalabilidad)
5. [Actualización del Documento 2](#5-actualización-del-documento-2)

---

## 1️⃣ TAMAÑO Y CRECIMIENTO DEL CLIENT DRAWER

### 📊 Estimaciones Realistas de Tamaño

#### **Componentes del Client Drawer:**

```javascript
client_drawer = {
  profile: ~1 KB,                    // Datos básicos (fijos)
  questionnaires: {
    inicial: ~10 KB,                 // Cuestionario completo (1 vez)
    followups: ~3 KB × N_followups   // Cada seguimiento
  },
  snapshots: ~50 KB × N_snapshots,   // ClientContext completo
  measurements: ~0.5 KB × N_medidas,
  plans: ~1 KB × N_planes,           // Solo referencias
  notes: ~0.5 KB × N_notas,
  meta: ~0.5 KB
}
```

#### **Desglose del Snapshot (50 KB estimado):**

```javascript
snapshot = {
  snapshot_id: 0.1 KB,
  version: 0.1 KB,
  created_at: 0.1 KB,
  trigger: 0.1 KB,
  
  // El grueso del tamaño:
  client_context: {
    meta: 0.5 KB,
    training: {
      client_summary: 1 KB,
      profile: 3 KB,
      constraints: 2 KB,
      prehab: 2 KB,
      progress: 1 KB,
      capacity: 2 KB,
      adaptation: 1 KB,
      mesocycle: 3 KB,
      sessions: 15 KB,        // ⚠️ Sesiones detalladas (mayor peso)
      safe_sessions: 15 KB,   // ⚠️ Sesiones + sustituciones
      formatted_plan: 0 KB,   // ❌ NO SE GUARDARÁ AQUÍ (ver punto 2)
      audit: 1 KB,
      bridge_for_nutrition: 1 KB
    },
    nutrition: {
      profile: 2 KB,
      metabolism: 1 KB,
      energy_strategy: 1 KB,
      macro_design: 1 KB,
      weekly_structure: 2 KB,
      timing_plan: 2 KB,
      menu_plan: 0 KB,        // ❌ NO SE GUARDARÁ AQUÍ
      adherence_report: 1 KB,
      audit: 1 KB
    }
  },
  
  plans_generated: 0.2 KB,    // Solo IDs
  generation_job_id: 0.1 KB
}

TOTAL POR SNAPSHOT: ~50 KB (SIN formatted_plan ni menu_plan)
```

**Nota crítica:** `formatted_plan` (Markdown) puede ser 20-30 KB. **NO lo duplicaremos** en el snapshot (ver punto 2).

---

### 📈 Proyección a 3-5 Años

#### **Escenario Típico: Cliente Activo**

**Suposiciones:**
- 12 seguimientos/año (1 por mes)
- 1 nota del entrenador cada 2 meses (6/año)
- 1 medición por seguimiento (12/año)

**Año 1:**
```
Cuestionario inicial: 10 KB
Snapshots (12): 12 × 50 KB = 600 KB
Followups (12): 12 × 3 KB = 36 KB
Measurements (12): 12 × 0.5 KB = 6 KB
Notes (6): 6 × 0.5 KB = 3 KB
Plans refs (24): 24 × 1 KB = 24 KB
---
TOTAL AÑO 1: ~680 KB
```

**Año 2:**
```
Snapshots adicionales (12): 600 KB
Followups adicionales (12): 36 KB
Measurements (12): 6 KB
Notes (6): 3 KB
Plans refs (24): 24 KB
---
TOTAL AÑO 2: +669 KB
ACUMULADO: 1,349 KB (~1.3 MB)
```

**Año 3:**
```
Total año 3: +669 KB
ACUMULADO: 2,018 KB (~2 MB)
```

**Año 5:**
```
Total año 5: +669 KB × 2
ACUMULADO: 3,356 KB (~3.3 MB)
```

#### **Escenario Pesimista: Cliente Muy Activo + Regeneraciones**

**Suposiciones adicionales:**
- Cliente regenera plan 2 veces extra/año (por ajustes manuales): +24 snapshots/año
- Notas semanales del entrenador: 52/año

**Año 5 (pesimista):**
```
Snapshots: 36 × 5 años = 180 × 50 KB = 9,000 KB (~9 MB)
Followups: 60 × 3 KB = 180 KB
Notes: 260 × 0.5 KB = 130 KB
Resto: ~200 KB
---
ACUMULADO: ~9.5 MB
```

---

### 🚨 Análisis de Riesgo

| **Escenario** | **Tamaño a 5 años** | **% del límite 16MB** | **Riesgo** |
|---|---|---|---|
| Típico (12 seguimientos/año) | ~3.3 MB | 20% | 🟢 **Bajo** |
| Activo (24 regeneraciones/año) | ~6.5 MB | 40% | 🟡 **Medio** |
| Pesimista (36 snapshots/año + notas) | ~9.5 MB | 60% | 🟠 **Alto** |

**Conclusión:**
- ✅ Cliente típico: **Sin riesgo** hasta 10+ años
- ⚠️ Cliente muy activo: **Monitorear** a partir de año 7-8
- 🚨 Cliente pesimista: **Archivado necesario** a partir de año 8-10

---

### 🗄️ Estrategia de Archivado (Preventiva)

#### **Propuesta: Archivado Automático de Snapshots Antiguos**

**Regla:**
> Snapshots con más de **2 años de antigüedad** se mueven automáticamente a `client_drawers_archive`.

**Implementación:**

```javascript
// Colección PRINCIPAL: client_drawers
{
  _id: "client_1762...",
  
  // Snapshots ACTIVOS (últimos 2 años)
  snapshots: [
    { snapshot_id: "v25", created_at: "2024-11-01" },
    { snapshot_id: "v26", created_at: "2024-12-01" },
    { snapshot_id: "v27", created_at: "2025-01-01" }
    // ... solo últimos 24 snapshots (~1.2 MB)
  ],
  
  // Meta indica que hay archivo
  meta: {
    has_archived_snapshots: true,
    oldest_snapshot_archived: "v1",
    newest_snapshot_archived: "v24"
  }
}

// Colección de ARCHIVO: client_drawers_archive
{
  _id: "client_1762..._archive",
  client_id: "client_1762...",
  
  // Snapshots ARCHIVADOS (más de 2 años)
  archived_snapshots: [
    { snapshot_id: "v1", created_at: "2023-01-01", ... },
    { snapshot_id: "v2", created_at: "2023-02-01", ... },
    // ... hasta v24
  ],
  
  archived_at: ISODate("2025-01-01T00:00:00Z")
}
```

**Ventajas:**
- ✅ `client_drawer` principal siempre < 2 MB
- ✅ Acceso rápido a historial reciente (últimos 2 años)
- ✅ Historial completo preservado (accesible con 1 query extra)
- ✅ Rollback a snapshots antiguos posible

**Acceso a snapshots archivados:**
```python
# Consulta normal (últimos 2 años)
drawer = await db.client_drawers.find_one({"_id": client_id})

# Si necesitas snapshot antiguo
if drawer["meta"]["has_archived_snapshots"]:
    archive = await db.client_drawers_archive.find_one({"client_id": client_id})
    snapshot_v5 = next(s for s in archive["archived_snapshots"] if s["snapshot_id"] == "v5")
```

**Proceso automático de archivado:**
```python
# Job mensual (cron)
async def archive_old_snapshots():
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=730)  # 2 años
    
    drawers = await db.client_drawers.find({
        "snapshots.created_at": {"$lt": cutoff_date}
    }).to_list(1000)
    
    for drawer in drawers:
        snapshots_to_archive = [
            s for s in drawer["snapshots"]
            if s["created_at"] < cutoff_date
        ]
        
        if not snapshots_to_archive:
            continue
        
        # Crear/actualizar archivo
        await db.client_drawers_archive.update_one(
            {"client_id": drawer["_id"]},
            {
                "$push": {
                    "archived_snapshots": {"$each": snapshots_to_archive}
                },
                "$set": {"archived_at": datetime.now(timezone.utc)}
            },
            upsert=True
        )
        
        # Eliminar de drawer principal
        await db.client_drawers.update_one(
            {"_id": drawer["_id"]},
            {
                "$pull": {
                    "snapshots": {"created_at": {"$lt": cutoff_date}}
                },
                "$set": {
                    "meta.has_archived_snapshots": True
                }
            }
        )
```

---

### ✅ Recomendación Final sobre Tamaño

**Decisión:**
1. **Implementar client_drawer como está** (1 colección principal)
2. **Añadir archivado automático preventivo** a partir de año 1 de producción
3. **Monitorear tamaño real** en primeros 6 meses de uso
4. **Política de archivado configurable:**
   - Por defecto: 2 años en drawer principal
   - Clientes premium/especiales: 5 años sin archivar (si necesario)

**Con esta estrategia:**
- ✅ Drawer principal NUNCA excederá ~2 MB
- ✅ Sin riesgo de límite 16 MB (margen 8x)
- ✅ Acceso a historial completo preservado

---

## 2️⃣ DUPLICIDAD MÍNIMA ACEPTABLE EN SNAPSHOTS

### 🔍 Análisis: ¿Guardar `formatted_plan` en Snapshot?

**Situación actual propuesta en Doc 2:**
```javascript
snapshot.client_context.training.formatted_plan = "# PLAN MARKDOWN..."  // 20-30 KB
training_plan.formatted_plan = "# PLAN MARKDOWN..."  // 20-30 KB
```

**Duplicación:** ❌ Sí, 20-30 KB duplicados

---

### 📋 Casos de Uso: ¿Cuándo se necesita el `formatted_plan`?

1. **Mostrar plan al cliente:** 
   - Se lee de `training_plans` (collection optimizada para lectura rápida)
   - NO necesita snapshot

2. **Generar PDF del plan:**
   - Se lee de `training_plans`
   - NO necesita snapshot

3. **Auditar qué se generó en snapshot_v5:**
   - Se necesita saber QUÉ plan se generó
   - Pero el plan completo está en `training_plans` (referenciado por `snapshot_id`)

4. **Debugging: ¿Qué salió mal en la generación?**
   - Se necesita el ClientContext intermedio (E1-E9 outputs)
   - El `formatted_plan` es el RESULTADO final, no el proceso

5. **Regenerar plan desde snapshot antiguo:**
   - Se necesita el ClientContext para re-ejecutar E7 (formatter)
   - NO se necesita el plan viejo, se genera uno nuevo

---

### ✅ Decisión: NO Duplicar `formatted_plan`

**Justificación:**

1. **Trazabilidad suficiente:**
   - El snapshot guarda TODOS los datos intermedios (E1-E9 outputs)
   - El snapshot referencia el plan generado (`plans_generated.training_plan_id`)
   - Si necesitas el plan, haces 1 query a `training_plans`

2. **El snapshot es para entender QUÉ SE DECIDIÓ, no QUÉ SE MOSTRÓ:**
   - Snapshot = proceso de decisión (capacity, mesocycle, sessions)
   - Plan = vista de presentación (Markdown para el cliente)

3. **Impacto en tamaño:**
   - Sin `formatted_plan` y `menu_plan` en snapshot: 50 KB/snapshot
   - Con ambos duplicados: 80-90 KB/snapshot
   - Diferencia a 5 años: 1.8 MB vs 3 MB (~40% más pesado)

4. **Regeneración posible:**
   - Si se necesita "rehacer" el plan, se ejecuta el post-procesador desde el snapshot
   - No se pierde nada

**Contraejemplo descartado:**
- "¿Y si cambiamos el formato del Markdown y queremos ver cómo se veía antes?"
- Respuesta: El plan histórico está en `training_plans`, no se toca

---

### 📐 Nueva Estructura del Snapshot (Definitiva)

```javascript
snapshot = {
  snapshot_id: "v1",
  version: 1,
  
  client_context: {
    training: {
      // ... todos los outputs E1-E9
      sessions: [ /* Sesiones completas */ ],
      safe_sessions: [ /* Sesiones validadas */ ],
      
      // ❌ NO SE GUARDA formatted_plan aquí
      formatted_plan: null,  // O simplemente no incluir el campo
      
      audit: { /* E8 */ },
      bridge_for_nutrition: { /* E9 */ }
    },
    
    nutrition: {
      // ... todos los outputs N0-N8
      timing_plan: { /* N5 */ },
      
      // ❌ NO SE GUARDA menu_plan aquí
      menu_plan: null,
      
      adherence_report: { /* N7 */ },
      audit: { /* N8 */ }
    }
  },
  
  // ✅ Referencias a los planes generados
  plans_generated: {
    training_plan_id: "training_v1",
    nutrition_plan_id: "nutrition_v1"
  }
}
```

**Tamaño resultante:**
- Snapshot: ~50 KB (en vez de 80-90 KB)
- Training plan: 25 KB (formatted_plan)
- Nutrition plan: 15 KB (menu_plan)
- Total: ~90 KB (sin duplicación)

**Acceso al plan desde snapshot:**
```python
# 1. Leer snapshot
snapshot = drawer["snapshots"][0]

# 2. Obtener plan referenciado
plan_id = snapshot["plans_generated"]["training_plan_id"]
plan = await db.training_plans.find_one({"_id": plan_id})

formatted_plan = plan["formatted_plan"]
```

---

### ✅ Recomendación Final sobre Duplicidad

**Decisión:**
1. ❌ **NO guardar** `formatted_plan` ni `menu_plan` dentro del snapshot
2. ✅ **Guardar** todos los outputs intermedios (E1-E9, N0-N8) en el snapshot
3. ✅ **Referenciar** los planes generados desde el snapshot
4. ✅ **Mantener** planes completos en `training_plans` y `nutrition_plans`

**Beneficios:**
- Reducción ~40% del tamaño del snapshot
- Sin pérdida de trazabilidad
- Planes accesibles con 1 query extra (aceptable)

---

## 3️⃣ ESTRUCTURA DEL CUESTIONARIO - VERSIONADO

### 🔍 Problema Actual: Dict Plano

**Situación propuesta en Doc 2:**
```javascript
questionnaires.inicial.responses = {
  "nombre_completo": "Jorge",
  "peso": "85",
  "objetivo_fisico": "Perder grasa",
  "hernias_protusiones": "Hernia L4-L5",
  // ... 100+ campos planos
}
```

**Problemas:**
1. ❌ Sin estructura semántica (todos los campos al mismo nivel)
2. ❌ Difícil versionar (añadir campo nuevo = cambio no documentado)
3. ❌ Difícil validar (¿qué campos son obligatorios?)
4. ❌ Difícil evolucionar (renombrar campo = romper histórico)

---

### ✅ Propuesta: Cuestionario Estructurado y Versionado

#### **Estructura Jerárquica por Bloques**

```javascript
questionnaires.inicial = {
  submitted_at: ISODate("2025-01-02T09:00:00Z"),
  version: "1.0.0",  // ⭐ Semver: MAJOR.MINOR.PATCH
  schema_version: "questionnaire_training_v1",
  
  responses: {
    // ============================================
    // BLOQUE 1: DATOS PERSONALES
    // ============================================
    personal_data: {
      nombre_completo: "Jorge Calcerrada",
      email: "jorge@example.com",
      fecha_nacimiento: "1989-05-15",
      edad: 35,  // Calculado
      sexo: "Hombre",
      profesion: "Ingeniero de Software",
      telefono: "+34612345678",
      whatsapp: "+34612345678"
    },
    
    // ============================================
    // BLOQUE 2: MEDIDAS CORPORALES
    // ============================================
    measurements: {
      peso_kg: 85,
      altura_cm: 178,
      grasa_porcentaje: 22,
      circunferencias: {
        cintura_cm: 92,
        cadera_cm: 98,
        biceps_relajado_cm: null,
        biceps_flexionado_cm: null,
        muslo_cm: null
      }
    },
    
    // ============================================
    // BLOQUE 3: SALUD Y CLÍNICO
    // ============================================
    health: {
      medications: {
        current: "Ninguno",
        allergies: "Lactosa (leve)"
      },
      chronic_conditions: {
        cardiovascular: {
          heart_problems: false,
          hypertension: false
        },
        metabolic: {
          diabetes: false,
          cholesterol: "Normal"
        },
        musculoskeletal: {
          hernias_protusions: "Hernia discal L4-L5 controlada",
          arthritis: false,
          scoliosis: false
        }
      },
      lifestyle: {
        smoking: {
          smokes: false,
          quantity: null
        },
        alcohol: {
          drinks: true,
          frequency: "Social (fines de semana)"
        }
      }
    },
    
    // ============================================
    // BLOQUE 4: TRABAJO Y ESTRÉS
    // ============================================
    work_life: {
      occupation: {
        profession: "Ingeniero de Software",
        stress_level: "Moderado-Alto",
        movement_type: "Sedentario",
        hours_per_day: "9-10"
      },
      daily_activity: {
        desk_time_hours: 9,
        standing_time_hours: 1,
        walking_time_hours: 0.5,
        activity_level: "Baja"
      },
      rest: {
        breaks_during_work: "Poco",
        work_from_home: true
      }
    },
    
    // ============================================
    // BLOQUE 5: EXPERIENCIA DEPORTIVA
    // ============================================
    sports_background: {
      previous_sports: {
        practiced: true,
        sports: ["Natación competitiva"],
        years_ago: 10,
        level: "Competitivo amateur"
      },
      gym_experience: {
        trained_before: true,
        last_time: "Hace 2 años",
        duration: "6 meses",
        with_trainer: false
      },
      current_fitness: {
        cardiorespiratory: "Media",
        strength: "Baja",
        flexibility: "Baja",
        agility_coordination: "Media"
      }
    },
    
    // ============================================
    // BLOQUE 6: DISPONIBILIDAD
    // ============================================
    availability: {
      training_schedule: {
        days_per_week: 4,
        session_duration_min: 60,
        preferred_time: "Tarde (19:00-21:00)",
        flexible_schedule: false
      },
      location: {
        trains_at_gym: false,
        home_equipment: [
          "Mancuernas hasta 20kg",
          "Esterilla",
          "Banda elástica",
          "Barra dominadas"
        ]
      }
    },
    
    // ============================================
    // BLOQUE 7: HÁBITOS HORARIOS
    // ============================================
    daily_schedule: {
      wake_up: "07:00",
      breakfast: "07:30",
      lunch: "14:00",
      dinner: "21:00",
      sleep: "23:30",
      sleep_hours: 7.5,
      sleep_quality: "Regular"
    },
    
    // ============================================
    // BLOQUE 8: HÁBITOS ALIMENTARIOS
    // ============================================
    nutrition_habits: {
      meal_frequency: 4,
      meal_structure: "3 principales + 1 snack",
      preferences: {
        favorite_foods: ["Pasta", "Arroz", "Pollo"],
        disliked_foods: ["Pescado azul"],
        cannot_eat: []
      },
      eating_patterns: {
        eats_out_frequency: "2-3 días/semana",
        junk_food_frequency: "A veces (fines de semana)",
        adds_salt: "Poco",
        drinks_soda: false,
        sugar_sweets: "Ocasional"
      },
      diet_history: [
        {
          type: "Cetogénica",
          duration_months: 2,
          year: 2022,
          result: "Sin éxito"
        },
        {
          type: "Ayuno intermitente",
          duration_months: 3,
          year: 2023,
          result: "Sin éxito"
        }
      ]
    },
    
    // ============================================
    // BLOQUE 9: OBJETIVOS Y MOTIVACIÓN ⭐
    // ============================================
    goals: {
      primary_objective: "Perder grasa",  // ⭐ CRÍTICO
      secondary_objectives: ["Ganar fuerza", "Más energía"],
      motivation: {
        why_exercise: "Verme mejor, sentirme con más energía",
        why_now: "Cansado de empezar y dejarlo",
        what_motivates: "Ver resultados tangibles"
      },
      experience: {
        consistency_history: "Intermitente (3-6 meses máximo)",
        obstacles: ["Falta de constancia", "No sé qué comer"],
        energy_level: "Media-Baja"
      }
    },
    
    // ============================================
    // BLOQUE 10: COMENTARIOS Y NOTAS
    // ============================================
    additional_info: {
      comments: "Quiero algo sostenible, sin dietas extremas",
      trainer_notes: null,  // Para uso del entrenador
      special_requests: []
    }
  }
}
```

---

### 🔄 Sistema de Versionado del Cuestionario

#### **Estrategia: Semantic Versioning**

```javascript
version: "MAJOR.MINOR.PATCH"

MAJOR: Cambios incompatibles (eliminar campos, cambiar tipos)
MINOR: Nuevos campos opcionales (añadir bloque nuevo)
PATCH: Correcciones menores (typos, renombrar sin romper)
```

**Ejemplos:**

```javascript
// v1.0.0 - Cuestionario inicial (Enero 2025)
{
  version: "1.0.0",
  schema_version: "questionnaire_training_v1",
  responses: { /* estructura original */ }
}

// v1.1.0 - Añadir bloque "psychological" (Marzo 2025)
{
  version: "1.1.0",
  schema_version: "questionnaire_training_v1",
  responses: {
    // ... bloques originales
    
    // NUEVO BLOQUE (opcional)
    psychological: {
      stress_management: "Media",
      anxiety_level: "Baja",
      depression_history: false
    }
  }
}

// v2.0.0 - Cambio incompatible: reestructurar health (Junio 2026)
{
  version: "2.0.0",
  schema_version: "questionnaire_training_v2",
  responses: {
    // Estructura completamente nueva para health
    health: {
      // Nueva estructura incompatible con v1.x
    }
  }
}
```

---

### 🔧 Migración Automática de Versiones Antiguas

**Problema:** Cliente Jorge1 tiene cuestionario v1.0.0, sistema usa v1.2.0.

**Solución:** Función de migración automática.

```python
# /app/backend/questionnaire_migrator.py

def migrate_questionnaire(questionnaire: Dict, from_version: str, to_version: str) -> Dict:
    """
    Migra un cuestionario de una versión a otra.
    
    Ejemplos:
    - 1.0.0 → 1.1.0: Añadir campos nuevos con valores por defecto
    - 1.0.0 → 2.0.0: Reestructuración completa
    """
    
    # Caso 1: v1.0.0 → v1.1.0 (añadir bloque psychological)
    if from_version == "1.0.0" and to_version == "1.1.0":
        questionnaire["responses"]["psychological"] = {
            "stress_management": "No evaluado",
            "anxiety_level": "No evaluado",
            "depression_history": None
        }
        questionnaire["version"] = "1.1.0"
        return questionnaire
    
    # Caso 2: v1.x → v2.0.0 (migración mayor)
    if from_version.startswith("1.") and to_version.startswith("2."):
        # Migración compleja con transformación de datos
        old_health = questionnaire["responses"]["health"]
        
        # Reestructurar según nuevo schema
        new_health = transform_health_v1_to_v2(old_health)
        
        questionnaire["responses"]["health"] = new_health
        questionnaire["version"] = "2.0.0"
        questionnaire["schema_version"] = "questionnaire_training_v2"
        return questionnaire
    
    # Si no hay migración disponible, devolver error
    raise ValueError(f"No migration path from {from_version} to {to_version}")


def get_current_questionnaire_version() -> str:
    """Versión actual del esquema de cuestionario"""
    return "1.0.0"


async def ensure_questionnaire_compatibility(client_drawer: Dict):
    """
    Asegura que el cuestionario del drawer está en la versión actual.
    Si no lo está, migra automáticamente.
    """
    current_version = get_current_questionnaire_version()
    drawer_version = client_drawer["questionnaires"]["inicial"]["version"]
    
    if drawer_version != current_version:
        logger.info(f"Migrando cuestionario de {drawer_version} a {current_version}")
        
        migrated = migrate_questionnaire(
            client_drawer["questionnaires"]["inicial"],
            from_version=drawer_version,
            to_version=current_version
        )
        
        # Actualizar en BD
        await db.client_drawers.update_one(
            {"_id": client_drawer["_id"]},
            {"$set": {"questionnaires.inicial": migrated}}
        )
```

---

### ✅ Recomendación Final sobre Cuestionario

**Decisión:**
1. ✅ **Estructurar cuestionario en 10 bloques** (personal_data, measurements, health, etc.)
2. ✅ **Versionado Semantic** (MAJOR.MINOR.PATCH)
3. ✅ **Migraciones automáticas** entre versiones
4. ✅ **Mantener historial:** Snapshots antiguos preservan su versión original
5. ✅ **Compatibilidad:** Sistema lee cualquier versión y migra si es necesario

**Implementación:**
- Fase 1 (migración): Mantener dict plano compatible (para no romper migración)
- Fase 2 (post-migración): Introducir estructura jerárquica progresivamente
- Fase 3 (futuro): Nuevos cuestionarios ya usan estructura jerárquica

---

## 4️⃣ MULTI-PRODUCTO Y ESCALABILIDAD

### 🌐 Visión: EDN360 como Plataforma Multi-Servicio

**Objetivo:** Permitir que `client_drawer` escale a múltiples dominios profesionales.

---

### 📐 Arquitectura Extensible

#### **Diseño Actual (Training + Nutrition):**

```javascript
client_drawer = {
  _id: "client_1762...",
  
  // Datos generales (compartidos por todos los servicios)
  profile: { /* común */ },
  
  // Módulo TRAINING
  questionnaires: {
    training_inicial: { /* cuestionario de entrenamiento */ },
    training_followups: []
  },
  snapshots_training: [ /* snapshots de entrenamiento */ ],
  
  // Módulo NUTRITION
  questionnaires: {
    nutrition_inicial: { /* cuestionario nutricional */ },
    nutrition_followups: []
  },
  snapshots_nutrition: [ /* snapshots de nutrición */ ]
}
```

**Problema:** ❌ No es extensible a otros dominios.

---

#### **Nuevo Diseño Multi-Servicio:**

```javascript
client_drawer = {
  _id: "client_1762...",
  user_id: "1762...",
  
  // ============================================
  // PROFILE GLOBAL (compartido por todos los servicios)
  // ============================================
  profile: {
    nombre_completo: "Jorge Calcerrada",
    email: "jorge@example.com",
    fecha_nacimiento: "1989-05-15",
    // ... datos comunes
  },
  
  // ============================================
  // SERVICES - Módulos por Dominio
  // ============================================
  services: {
    
    // ──────────────────────────────────────────
    // MÓDULO 1: TRAINING
    // ──────────────────────────────────────────
    training: {
      active: true,
      enrolled_at: ISODate("2025-01-02"),
      
      questionnaires: {
        inicial: { /* cuestionario training */ },
        followups: []
      },
      
      snapshots: [
        {
          snapshot_id: "training_v1",
          version: 1,
          client_context: {
            // ClientContext específico de training
            training: { /* E1-E9 */ }
          },
          plans_generated: {
            training_plan_id: "training_v1"
          }
        }
      ],
      
      plans: [
        { plan_id: "training_v1", version: 1 }
      ],
      
      measurements: [],  // Medidas específicas de training
      notes: []          // Notas específicas de training
    },
    
    // ──────────────────────────────────────────
    // MÓDULO 2: NUTRITION
    // ──────────────────────────────────────────
    nutrition: {
      active: true,
      enrolled_at: ISODate("2025-01-02"),
      
      questionnaires: {
        inicial: { /* cuestionario nutrition */ },
        followups: []
      },
      
      snapshots: [
        {
          snapshot_id: "nutrition_v1",
          version: 1,
          client_context: {
            // ClientContext específico de nutrition
            nutrition: { /* N0-N8 */ }
          },
          plans_generated: {
            nutrition_plan_id: "nutrition_v1"
          }
        }
      ],
      
      plans: [
        { plan_id: "nutrition_v1", version: 1 }
      ],
      
      measurements: [],
      notes: []
    },
    
    // ──────────────────────────────────────────
    // MÓDULO 3: PSYCHOLOGY (Futuro)
    // ──────────────────────────────────────────
    psychology: {
      active: false,  // No contratado aún
      enrolled_at: null,
      
      // Estructura idéntica a training/nutrition
      questionnaires: {},
      snapshots: [],
      plans: [],
      measurements: [],
      notes: []
    },
    
    // ──────────────────────────────────────────
    // MÓDULO 4: REHABILITATION (Futuro)
    // ──────────────────────────────────────────
    rehabilitation: {
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
  // META (Global)
  // ============================================
  meta: {
    created_at: ISODate("2025-01-02"),
    updated_at: ISODate("2025-01-02"),
    active_services: ["training", "nutrition"],
    total_services: 2
  }
}
```

---

### 🔧 Añadir Nuevo Servicio (Ejemplo: Psychology)

**Paso 1: Cliente contrata servicio de psicología deportiva**

```python
# Endpoint: POST /api/services/psychology/enroll
async def enroll_psychology_service(user_id: str):
    await db.client_drawers.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "services.psychology.active": True,
                "services.psychology.enrolled_at": datetime.now(timezone.utc),
                "meta.active_services": ["training", "nutrition", "psychology"],
                "meta.total_services": 3
            }
        }
    )
```

**Paso 2: Cliente completa cuestionario de psicología**

```python
async def submit_psychology_questionnaire(user_id: str, responses: Dict):
    questionnaire = {
        "submitted_at": datetime.now(timezone.utc),
        "version": "1.0.0",
        "schema_version": "questionnaire_psychology_v1",
        "responses": responses
    }
    
    await db.client_drawers.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "services.psychology.questionnaires.inicial": questionnaire
            }
        }
    )
```

**Paso 3: Generar plan psicológico**

```python
# Orquestador de Psychology (P1-P9)
result = await psychology_orchestrator.generate_initial_plan(
    questionnaire_data=drawer["services"]["psychology"]["questionnaires"]["inicial"],
    client_id=user_id
)

# Guardar snapshot en services.psychology.snapshots[]
snapshot = {
    "snapshot_id": "psychology_v1",
    "version": 1,
    "client_context": {
        "psychology": {
            "profile": { /* P1 */ },
            "assessment": { /* P2 */ },
            "strategies": { /* P3 */ },
            // ... outputs P1-P9
        }
    },
    "plans_generated": {
        "psychology_plan_id": "psychology_v1"
    }
}

await db.client_drawers.update_one(
    {"user_id": user_id},
    {
        "$push": {
            "services.psychology.snapshots": snapshot
        }
    }
)
```

---

### 🔗 Integración Cross-Servicio

**Ejemplo:** Plan de nutrición debe considerar estado psicológico del cliente.

```python
# Orquestador de Nutrition accede a módulo de Psychology
client_drawer = await db.client_drawers.find_one({"user_id": user_id})

# Verificar si tiene servicio de psicología
if client_drawer["services"]["psychology"]["active"]:
    # Obtener último snapshot de psychology
    psychology_snapshot = client_drawer["services"]["psychology"]["snapshots"][-1]
    
    # Extraer info relevante
    stress_level = psychology_snapshot["client_context"]["psychology"]["assessment"]["stress_level"]
    coping_strategies = psychology_snapshot["client_context"]["psychology"]["strategies"]
    
    # Usar info para ajustar plan nutricional
    # Ejemplo: Si estrés alto, recomendar alimentos con triptófano
```

**Ventajas:**
- ✅ Cada servicio es independiente
- ✅ Servicios pueden leer datos de otros módulos (con permisos)
- ✅ Cliente puede contratar servicios a la carta
- ✅ Historial completo en 1 lugar

---

### 📊 Comparativa: Arquitectura Monolítica vs Multi-Servicio

| **Aspecto** | **Monolítica (Actual)** | **Multi-Servicio (Propuesta)** |
|---|---|---|
| Añadir nuevo dominio | ❌ Requiere refactor completo | ✅ Añadir módulo en `services.{domain}` |
| Separación de datos | ❌ Todo mezclado | ✅ Cada servicio en su namespace |
| Cliente multi-servicio | ❌ Complejo de gestionar | ✅ Nativo en el diseño |
| Migración a futuro | ❌ Difícil | ✅ No rompe servicios existentes |
| Licenciar a terceros | ❌ Código acoplado | ✅ Módulos independientes |

---

### ✅ Recomendación Final sobre Multi-Servicio

**Decisión:**
1. ✅ **Implementar arquitectura multi-servicio desde el inicio**
2. ✅ **Módulo `services.{domain}`** para cada servicio profesional
3. ✅ **Profile global compartido** entre servicios
4. ✅ **Snapshots independientes** por servicio
5. ✅ **Cross-service access** permitido (con validación)

**Implementación:**
- Fase 1: Migrar training + nutrition a `services.training` y `services.nutrition`
- Fase 2: Añadir psychology, rehabilitation según demanda
- Fase 3: API pública para que terceros añadan sus propios módulos

**Código modular:**
```python
# Cada servicio tiene su propio orquestador
training_orchestrator = TrainingOrchestrator()
nutrition_orchestrator = NutritionOrchestrator()
psychology_orchestrator = PsychologyOrchestrator()  # Futuro

# Registro de servicios disponibles
AVAILABLE_SERVICES = {
    "training": training_orchestrator,
    "nutrition": nutrition_orchestrator,
    # "psychology": psychology_orchestrator  # Añadir cuando esté listo
}
```

---

## 5️⃣ ACTUALIZACIÓN DEL DOCUMENTO 2

### 📝 Secciones a Añadir/Modificar en el Documento 2

1. **Sección 1.5: Estimaciones de Tamaño y Archivado**
   - Tabla de proyecciones a 3-5 años
   - Estrategia de archivado automático
   - Código de proceso de archivado

2. **Sección 2.3: Decisión sobre Duplicidades**
   - NO guardar `formatted_plan` ni `menu_plan` en snapshots
   - Justificación técnica
   - Nueva estructura del snapshot

3. **Sección 3.2: Cuestionario Estructurado y Versionado**
   - Estructura jerárquica por bloques (10 bloques)
   - Sistema de versionado Semantic
   - Migraciones automáticas

4. **Sección 4: Arquitectura Multi-Servicio**
   - Nueva estructura `services.{domain}`
   - Ejemplos de extensión (psychology, rehab)
   - Cross-service integration

5. **Actualizar Lista de Código a Eliminar:**
   - Eliminar secciones sobre duplicación de `formatted_plan`
   - Añadir scripts de reestructuración del cuestionario

---

## ✅ RESUMEN DE DECISIONES FINALES

| **Punto Crítico** | **Decisión** | **Impacto** |
|---|---|---|
| **1. Tamaño y crecimiento** | Client drawer principal < 2 MB<br>Archivado automático a 2 años | 🟢 Sin riesgo de límite 16MB<br>Escalable a 10+ años |
| **2. Duplicidad snapshots** | NO guardar `formatted_plan`<br>Solo outputs intermedios (E1-E9) | 🟢 Reducción 40% tamaño<br>Sin pérdida de trazabilidad |
| **3. Estructura cuestionario** | 10 bloques jerárquicos<br>Versionado Semantic<br>Migraciones automáticas | 🟢 Fácil evolucionar<br>Compatibilidad garantizada |
| **4. Multi-servicio** | Arquitectura `services.{domain}`<br>Módulos independientes | 🟢 Escalable a N servicios<br>Licenciable a terceros |

---

**Próximo paso:** Una vez revises y apruebes estas decisiones, actualizaré el **DOCUMENTO 2** con estas secciones y podremos pasar al **DOCUMENTO 3: Plan de Ejecución por Fases**.

---

**Fin del Addendum**
