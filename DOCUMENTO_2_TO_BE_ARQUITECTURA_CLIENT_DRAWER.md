# DOCUMENTO 2: ARQUITECTURA TO BE (Client Drawer)

**Sistema:** E.D.N.360 - Nueva Arquitectura Unificada  
**Fecha:** Enero 2025  
**Versión:** 1.0  
**Cliente Referencia:** Jorge1  

---

## 📋 TABLA DE CONTENIDOS

1. [Visión del Client Drawer](#visión-del-client-drawer)
2. [Diseño de la Arquitectura Client Drawer](#diseño-de-la-arquitectura-client-drawer)
3. [Modelo de Datos Detallado](#modelo-de-datos-detallado)
4. [Flujo Completo: Cuestionario → Client Drawer → Planes](#flujo-completo)
5. [Ejemplo Real: Cliente Jorge1](#ejemplo-real-cliente-jorge1)
6. [Reglas de Oro del Sistema](#reglas-de-oro-del-sistema)
7. [Comparativa AS IS vs TO BE](#comparativa-as-is-vs-to-be)
8. [Lista EXPLÍCITA de Código a ELIMINAR](#lista-explícita-de-código-a-eliminar)

---

## VISIÓN DEL CLIENT DRAWER

### 🎯 Concepto Central

> **"Un cajón único por cliente donde vive TODA su información"**

El `client_drawer` es la **única fuente de verdad** del cliente en el sistema E.D.N.360.

### 📦 ¿Qué contiene el cajón?

```
client_drawer (por cliente)
├── 📁 profile                    # Datos personales y meta
│   ├── datos_basicos             # Nombre, email, edad, profesión
│   ├── datos_contacto            # Teléfono, WhatsApp
│   └── meta                      # created_at, updated_at
│
├── 📁 questionnaires             # Historial de cuestionarios
│   ├── inicial                   # Cuestionario detallado inicial
│   │   ├── submitted_at
│   │   ├── responses (dict)
│   │   └── version
│   └── followups[]               # Lista de seguimientos
│       ├── [0] mes_1
│       ├── [1] mes_2
│       └── ...
│
├── 📁 snapshots                  # Snapshots del ClientContext
│   ├── [0] snapshot_v1           # Primera generación
│   │   ├── snapshot_id
│   │   ├── created_at
│   │   ├── client_context        # ⭐ ClientContext COMPLETO
│   │   └── plans_generated       # Referencias a planes
│   ├── [1] snapshot_v2           # Seguimiento mes 1
│   └── ...
│
├── 📁 measurements               # Evolución de medidas
│   ├── [0] inicial               # Peso, grasa, medidas
│   ├── [1] mes_1
│   └── ...
│
├── 📁 plans                      # Referencias a planes generados
│   ├── training[]
│   │   ├── [0] plan_v1_jan2025
│   │   └── [1] plan_v2_feb2025
│   └── nutrition[]
│       ├── [0] plan_v1_jan2025
│       └── [1] plan_v2_feb2025
│
└── 📁 notes                      # Notas del entrenador
    ├── [0] nota_inicial
    └── [1] nota_seguimiento
```

### ✅ Principios del Client Drawer

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
   - Historial ilimitado de cuestionarios, medidas, seguimientos
   - Fácil navegación temporal (versión 1, 2, 3...)
   - Rollback posible a cualquier snapshot previo

---

## DISEÑO DE LA ARQUITECTURA CLIENT DRAWER

### 🏗️ Opción de Implementación: Colección Única con Subdocumentos

**Decisión:** Usar **UNA colección** `client_drawers` con subdocumentos anidados.

**Justificación:**
- ✅ Consulta atómica: Todo el cliente en 1 query
- ✅ Transaccionalidad: Actualizaciones ACID
- ✅ Simplicidad: No hay joins ni lookups
- ✅ Escalable: MongoDB soporta documentos de 16MB (suficiente para años de datos)

### 📐 Estructura de la Colección

```javascript
// Colección: client_drawers
{
  // ============================================
  // IDENTIFICACIÓN ÚNICA DEL CLIENTE
  // ============================================
  _id: "client_1762094831193507",  // client_<user_id>
  user_id: "1762094831193507",      // Referencia a users (para auth)
  
  // ============================================
  // PROFILE - Datos Personales y Meta
  // ============================================
  profile: {
    nombre_completo: "Jorge Calcerrada",
    email: "jorge@example.com",
    fecha_nacimiento: "1989-05-15",
    edad: 35,  // Calculado automáticamente
    sexo: "Hombre",
    profesion: "Ingeniero de Software",
    telefono: "+34612345678",
    whatsapp: "+34612345678",
    created_at: ISODate("2025-01-02T09:00:00Z"),
    updated_at: ISODate("2025-01-02T09:00:00Z")
  },
  
  // ============================================
  // QUESTIONNAIRES - Historial de Cuestionarios
  // ============================================
  questionnaires: {
    // Cuestionario inicial (el más completo)
    inicial: {
      submitted_at: ISODate("2025-01-02T09:00:00Z"),
      version: "v1.0",
      responses: {
        // MEDIDAS CORPORALES
        peso: "85",
        altura_cm: "178",
        grasa_porcentaje: "22",
        cintura_cm: "92",
        cadera_cm: "98",
        
        // SALUD Y MÉDICO
        medicamentos: "Ninguno",
        enfermedad_cronica: "Ninguna",
        alergias_intolerancias: "Lactosa (leve)",
        hernias_protusiones: "Hernia discal L4-L5 controlada",
        problemas_corazon: "No",
        hipertension: "No",
        diabetes: "No",
        
        // TRABAJO Y ESTRÉS
        estres_profesion: "Moderado-Alto",
        movimiento_trabajo: "Sedentario (9h frente a ordenador)",
        horas_trabajo: "9-10",
        descansa_trabajo: "Poco",
        actividad_fisica_diaria: "Poca (solo desplazamientos)",
        
        // EXPERIENCIA DEPORTIVA
        practicado_deporte: "Sí, natación competitiva (hace 10 años)",
        entrenado_gimnasio: "Sí, hace 2 años (6 meses)",
        resistencia_cardiorespiratoria: "Media",
        fuerza: "Baja",
        flexibilidad: "Baja",
        agilidad_coordinacion: "Media",
        
        // DISPONIBILIDAD
        dias_semana_entrenar: "4",
        tiempo_sesion: "45-60 min",
        entrena_manana_tarde: "Tarde (19:00-21:00)",
        gimnasio: "No",
        material_casa: "Mancuernas (hasta 20kg), esterilla, banda elástica, barra dominadas",
        
        // HORARIOS
        hora_levanta: "07:00",
        hora_desayuno: "07:30",
        hora_comida: "14:00",
        hora_cena: "21:00",
        hora_acuesta: "23:30",
        horas_duerme: "7-8",
        
        // HÁBITOS ALIMENTARIOS
        comidas_dia: "4",
        alimento_no_soporta: "Pescado azul",
        comida_favorita: "Pasta, arroz, pollo",
        dietas_anteriores: "Sí, keto y ayuno intermitente sin éxito",
        come_fuera_casa: "Sí, 2-3 días/semana (comida de trabajo)",
        azucar_dulces_bolleria: "A veces (fines de semana)",
        anade_sal: "Poco",
        bebidas_gas: "No",
        
        // OBJETIVOS ⭐ CRÍTICO
        objetivo_fisico: "Perder grasa",
        experiencia_ejercicio_constante: "Intermitente (3-6 meses máximo)",
        nivel_energia_dia: "Media-Baja",
        motiva_ejercicio: "Verme mejor, tener más energía para el día",
        comentarios_adicionales: "Quiero algo sostenible, sin dietas extremas"
      }
    },
    
    // Seguimientos mensuales
    followups: [
      // Seguimiento Mes 1 (Febrero 2025)
      {
        followup_id: "followup_1739550000000000",
        submitted_at: ISODate("2025-02-03T10:00:00Z"),
        days_since_last: 30,
        previous_snapshot_id: "snapshot_v1_jan2025",
        
        // Tipo de medición
        measurement_type: "smart_scale",
        
        // Mediciones
        measurements: {
          peso: "83",
          grasa_corporal: "20",
          masa_muscular: "42",
          grasa_visceral: "8",
          agua_corporal: "58",
          satisfecho_cambios: "SI"
        },
        
        // Adherencia
        adherence: {
          constancia_entrenamiento: "80% (3 de 4 sesiones/semana)",
          seguimiento_alimentacion: "70% (fines de semana difíciles)"
        },
        
        // Bienestar
        wellbeing: {
          factores_externos: "Proyecto intenso en el trabajo",
          energia_animo_motivacion: "Mejor que antes",
          sueno_estres: "Regular (7h promedio, estrés moderado)"
        },
        
        // Cambios percibidos
        changes_perceived: {
          molestias_dolor_lesion: "Ninguna nueva, hernia L4-L5 estable",
          cambios_corporales: "Más definición abdominal, menos hinchazón",
          fuerza_rendimiento: "Mejorando, puedo hacer más repeticiones"
        },
        
        // Feedback
        feedback: {
          objetivo_proximo_mes: "Seguir perdiendo grasa, ganar fuerza",
          cambios_deseados: "Aumentar intensidad si es seguro",
          comentarios_adicionales: "Me siento bien, quiero continuar"
        }
      }
      // Aquí se añadirían más seguimientos (mes 2, 3, etc.)
    ]
  },
  
  // ============================================
  // SNAPSHOTS - Historial de ClientContext
  // ============================================
  snapshots: [
    // Snapshot V1 - Plan Inicial (Enero 2025)
    {
      snapshot_id: "snapshot_v1_jan2025",
      version: 1,
      created_at: ISODate("2025-01-03T10:15:30Z"),
      trigger: "inicial",  // "inicial" | "followup" | "manual"
      
      // ⭐⭐⭐ AQUÍ SE GUARDA EL ClientContext COMPLETO ⭐⭐⭐
      client_context: {
        meta: {
          client_id: "client_1762094831193507",
          snapshot_id: "snapshot_v1_jan2025",
          version: 1,
          output_tier: "standard",
          selected_inputs: {
            cuestionario: "inicial",
            entrenamiento_base: null
          }
        },
        
        // raw_inputs YA NO SE PERSISTE (solo en memoria durante ejecución)
        // Los agentes leen directamente de client_drawer
        raw_inputs: null,
        
        training: {
          // E1 - Client Summary
          client_summary: {
            objetivo: "Pérdida de grasa corporal",
            nivel: "Principiante avanzado",
            limitaciones: ["Hernia discal L4-L5", "Sedentarismo laboral"],
            disponibilidad: "4 días/semana, 45-60min, tarde",
            material: "Casa (mancuernas 20kg, banda, barra dominadas)"
          },
          
          // E1 - Profile
          profile: { /* Análisis completo del cliente */ },
          
          // E1 - Constraints
          constraints: {
            lesiones: [
              {
                tipo: "Hernia discal L4-L5",
                restricciones: ["No flexión lumbar con carga", "No cargas axiales pesadas"],
                ejercicios_evitar: ["Peso muerto convencional", "Sentadilla profunda con barra"]
              }
            ],
            limitaciones_material: "Solo equipamiento casero",
            limitaciones_tiempo: "Máximo 60 min/sesión"
          },
          
          // E1 - Prehab
          prehab: {
            movilidad_lumbar: ["Cat-cow", "Bird dog"],
            estabilidad_core: ["Plancha frontal", "Dead bug"],
            frecuencia: "Diaria, 10 min"
          },
          
          // E2 - Capacity
          capacity: {
            volumen_semanal: 12,  // 12 series efectivas/grupo muscular/semana
            frecuencia_optima: 4,
            duracion_sesion: "45-50 min",
            intensidad_inicial: "RPE 6-7"
          },
          
          // E3 - Adaptation
          adaptation: {
            estres_externo: "Alto (trabajo)",
            ajustes: {
              volumen: "Mantener conservador primera semana",
              intensidad: "RPE máximo 7 en fase adaptativa"
            }
          },
          
          // E4 - Mesocycle
          mesocycle: {
            semanas: 4,
            estructura: [
              { semana: 1, fase: "Adaptación", volumen: "Bajo", intensidad: "Media" },
              { semana: 2, fase: "Acumulación", volumen: "Medio", intensidad: "Media" },
              { semana: 3, fase: "Intensificación", volumen: "Medio-Alto", intensidad: "Media-Alta" },
              { semana: 4, fase: "Descarga", volumen: "Bajo", intensidad: "Baja-Media" }
            ],
            patron_entrenamiento: "Torso-Pierna-Torso-Pierna"
          },
          
          // E5 - Sessions
          sessions: [
            {
              dia: 1,
              nombre: "Torso A - Empuje",
              ejercicios: [
                {
                  nombre: "Flexiones inclinadas",
                  series: 3,
                  reps: "10-12",
                  rpe: 7,
                  descanso: "90s"
                },
                {
                  nombre: "Press de hombros con mancuernas",
                  series: 3,
                  reps: "8-10",
                  rpe: 7,
                  descanso: "120s"
                }
                // ... más ejercicios
              ]
            }
            // ... más sesiones
          ],
          
          // E6 - Safe Sessions
          safe_sessions: [
            // Sesiones validadas con sustituciones por lesión
          ],
          
          // E7 - Formatted Plan (LEGACY - se genera en post-proceso)
          formatted_plan: null,
          
          // E8 - Audit
          audit: {
            volumen_total_semana: 48,
            distribucion_grupos: "Equilibrada",
            alertas: [],
            recomendaciones: ["Monitorear progresión de hernia L4-L5"]
          },
          
          // E9 - Bridge for Nutrition
          bridge_for_nutrition: {
            objetivo: "deficit_calorico",
            tdee_estimado: 2400,
            deficit_recomendado: 300,
            calorias_target: 2100,
            distribucion_macros_sugerida: {
              proteina: 165,  // g/día
              grasas: 70,
              carbohidratos: 210
            },
            sincronizacion_entrenamientos: [
              { dia: "Lunes", intensidad: "Media", tipo: "Torso" },
              { dia: "Miércoles", intensidad: "Media", tipo: "Pierna" }
            ]
          }
        },
        
        nutrition: {
          // N0 - Profile
          profile: { /* Análisis nutricional */ },
          
          // N1 - Metabolism
          metabolism: {
            tmb: 1750,
            neat: 350,
            tef: 200,
            eat: 100,
            tdee: 2400
          },
          
          // N2 - Energy Strategy
          energy_strategy: {
            tipo: "deficit_moderado",
            calorias_target: 2100,
            deficit_semanal: 2100,  // 300 kcal/día * 7 días
            perdida_estimada_mes: "1.8-2.2 kg"
          },
          
          // N3 - Macro Design
          macro_design: {
            proteina_g: 165,
            grasas_g: 70,
            carbohidratos_g: 210,
            fibra_g: 30
          },
          
          // N4 - Weekly Structure
          weekly_structure: {
            dias_entrenamiento: [
              {
                dia: "Lunes",
                calorias: 2200,
                carbohidratos: 230,
                tipo: "Alto CHO (Torso)"
              },
              {
                dia: "Martes",
                calorias: 2000,
                carbohidratos: 180,
                tipo: "Moderado"
              }
              // ... resto de días
            ]
          },
          
          // N5 - Timing Plan
          timing_plan: {
            comidas: [
              {
                nombre: "Desayuno",
                hora: "07:30",
                calorias: 500,
                macros: { proteina: 35, grasas: 20, carbohidratos: 50 }
              }
              // ... más comidas
            ]
          },
          
          // N6 - Menu Plan
          menu_plan: {
            // Menú completo generado
          },
          
          // N7 - Adherence Report
          adherence_report: {
            // Estrategias de adherencia
          },
          
          // N8 - Audit
          audit: {
            // Validación final
          }
        }
      },
      
      // Referencias a planes generados desde este snapshot
      plans_generated: {
        training_plan_id: "training_v1_jan2025",
        nutrition_plan_id: "nutrition_v1_jan2025"
      },
      
      // Job que generó este snapshot
      generation_job_id: "job_1736960100000000"
    },
    
    // Snapshot V2 - Seguimiento Mes 1 (Febrero 2025)
    {
      snapshot_id: "snapshot_v2_feb2025",
      version: 2,
      created_at: ISODate("2025-02-03T11:00:00Z"),
      trigger: "followup",
      followup_id: "followup_1739550000000000",
      previous_snapshot_id: "snapshot_v1_jan2025",
      
      client_context: {
        // ClientContext actualizado con ajustes del seguimiento
        // ...
      },
      
      plans_generated: {
        training_plan_id: "training_v2_feb2025",
        nutrition_plan_id: "nutrition_v2_feb2025"
      }
    }
  ],
  
  // ============================================
  // MEASUREMENTS - Evolución Temporal
  // ============================================
  measurements: [
    // Medición inicial
    {
      measurement_id: "measure_inicial",
      date: ISODate("2025-01-02T09:00:00Z"),
      tipo: "inicial",
      source: "cuestionario_inicial",
      data: {
        peso: 85,
        altura_cm: 178,
        grasa_porcentaje: 22,
        cintura_cm: 92,
        cadera_cm: 98
      }
    },
    
    // Medición Mes 1
    {
      measurement_id: "measure_mes1",
      date: ISODate("2025-02-03T10:00:00Z"),
      tipo: "followup",
      source: "followup_1739550000000000",
      data: {
        peso: 83,
        grasa_corporal: 20,
        masa_muscular: 42,
        grasa_visceral: 8
      }
    }
    // ... más mediciones
  ],
  
  // ============================================
  // PLANS - Referencias a Planes Generados
  // ============================================
  plans: {
    training: [
      {
        plan_id: "training_v1_jan2025",
        version: 1,
        generated_at: ISODate("2025-01-03T10:15:20Z"),
        snapshot_id: "snapshot_v1_jan2025",
        month: 1,
        year: 2025,
        status: "completed"  // "active" | "completed" | "archived"
      },
      {
        plan_id: "training_v2_feb2025",
        version: 2,
        generated_at: ISODate("2025-02-03T11:00:15Z"),
        snapshot_id: "snapshot_v2_feb2025",
        month: 2,
        year: 2025,
        status: "active"
      }
    ],
    
    nutrition: [
      {
        plan_id: "nutrition_v1_jan2025",
        version: 1,
        generated_at: ISODate("2025-01-03T10:15:25Z"),
        snapshot_id: "snapshot_v1_jan2025",
        month: 1,
        year: 2025,
        status: "completed"
      },
      {
        plan_id: "nutrition_v2_feb2025",
        version: 2,
        generated_at: ISODate("2025-02-03T11:00:20Z"),
        snapshot_id: "snapshot_v2_feb2025",
        month: 2,
        year: 2025,
        status: "active"
      }
    ]
  },
  
  // ============================================
  // NOTES - Notas del Entrenador
  // ============================================
  notes: [
    {
      note_id: "note_inicial",
      created_at: ISODate("2025-01-03T10:20:00Z"),
      created_by: "admin_jorge",
      content: "Cliente muy motivado, objetivo claro. Vigilar hernia L4-L5.",
      tags: ["inicial", "lesion"]
    },
    {
      note_id: "note_mes1",
      created_at: ISODate("2025-02-03T11:05:00Z"),
      created_by: "admin_jorge",
      content: "Excelente progreso. Perdió 2kg, sin molestias. Aumentar intensidad.",
      tags: ["seguimiento", "progreso"]
    }
  ],
  
  // ============================================
  // META - Información del Drawer
  // ============================================
  meta: {
    created_at: ISODate("2025-01-02T09:00:00Z"),
    updated_at: ISODate("2025-02-03T11:00:30Z"),
    current_snapshot: "snapshot_v2_feb2025",
    total_snapshots: 2,
    status: "active"  // "active" | "inactive" | "archived"
  }
}
```

---

## MODELO DE DATOS DETALLADO

### 📊 Esquema Pydantic para `client_drawer`

```python
# /app/backend/models/client_drawer.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

# ============================================
# PROFILE
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
# QUESTIONNAIRES
# ============================================
class QuestionnaireInicial(BaseModel):
    submitted_at: datetime
    version: str = "v1.0"
    responses: Dict[str, Any]  # Todos los campos del cuestionario

class QuestionnaireFollowup(BaseModel):
    followup_id: str
    submitted_at: datetime
    days_since_last: int
    previous_snapshot_id: str
    measurement_type: str  # "smart_scale" | "tape_measure" | "none"
    measurements: Optional[Dict[str, Any]] = None
    adherence: Dict[str, Any]
    wellbeing: Dict[str, Any]
    changes_perceived: Dict[str, Any]
    feedback: Dict[str, Any]

class Questionnaires(BaseModel):
    inicial: QuestionnaireInicial
    followups: List[QuestionnaireFollowup] = Field(default_factory=list)

# ============================================
# SNAPSHOTS
# ============================================
class SnapshotPlansGenerated(BaseModel):
    training_plan_id: str
    nutrition_plan_id: str

class ClientContextSnapshot(BaseModel):
    snapshot_id: str
    version: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trigger: str  # "inicial" | "followup" | "manual"
    followup_id: Optional[str] = None
    previous_snapshot_id: Optional[str] = None
    
    # ⭐ ClientContext COMPLETO (del orquestador)
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
    source: str  # ID del cuestionario o seguimiento
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
    status: str = "active"  # "active" | "completed" | "archived"

class PlansReferences(BaseModel):
    training: List[PlanReference] = Field(default_factory=list)
    nutrition: List[PlanReference] = Field(default_factory=list)

# ============================================
# NOTES
# ============================================
class TrainerNote(BaseModel):
    note_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str  # user_id del admin
    content: str
    tags: List[str] = Field(default_factory=list)

# ============================================
# CLIENT DRAWER - Modelo Principal
# ============================================
class ClientDrawer(BaseModel):
    """
    Cajón único del cliente - Única fuente de verdad
    """
    # Identificación
    client_drawer_id: str = Field(alias="_id")
    user_id: str
    
    # Secciones
    profile: ClientProfile
    questionnaires: Questionnaires
    snapshots: List[ClientContextSnapshot] = Field(default_factory=list)
    measurements: List[Measurement] = Field(default_factory=list)
    plans: PlansReferences = Field(default_factory=PlansReferences)
    notes: List[TrainerNote] = Field(default_factory=list)
    
    # Meta
    meta: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: str}
```

---

## FLUJO COMPLETO: CUESTIONARIO → CLIENT DRAWER → PLANES

### 🔄 Flujo Nuevo Simplificado

```
┌──────────────────────────────────────────────────────────────────────┐
│                         USUARIO CLIENTE                               │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                    Completa Cuestionario Inicial
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│              PASO 1: GUARDAR EN CLIENT_DRAWER                         │
├──────────────────────────────────────────────────────────────────────┤
│  Endpoint: POST /api/questionnaire/submit                            │
│                                                                       │
│  1. Validar cuestionario completo                                    │
│  2. Crear o actualizar client_drawer:                                │
│     {                                                                 │
│       _id: "client_<user_id>",                                       │
│       user_id: "1762...",                                            │
│       profile: { /* Extraído del cuestionario */ },                  │
│       questionnaires: {                                              │
│         inicial: {                                                   │
│           submitted_at: "2025-01-02T09:00:00Z",                      │
│           responses: { /* TODO el cuestionario */ }                  │
│         }                                                            │
│       },                                                             │
│       measurements: [{                                               │
│         date: "2025-01-02",                                          │
│         data: { peso: 85, altura: 178, ... }                         │
│       }],                                                            │
│       snapshots: [],  // Vacío, aún no hay planes                   │
│       plans: { training: [], nutrition: [] }                         │
│     }                                                                 │
│                                                                       │
│  ✅ ÚNICA ESCRITURA DEL CUESTIONARIO                                 │
└──────────────────────────────────────────────────────────────────────┘
                                │
                    Admin crea Generation Job
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│              PASO 2: CREAR JOB DE GENERACIÓN                          │
├──────────────────────────────────────────────────────────────────────┤
│  Endpoint: POST /admin/users/{user_id}/plans/generate_async          │
│                                                                       │
│  Input:                                                               │
│  {                                                                    │
│    client_id: "client_1762...",  // ← Apunta al drawer              │
│    mode: "full"                                                       │
│  }                                                                    │
│                                                                       │
│  Se crea job en generation_jobs:                                     │
│  {                                                                    │
│    job_id: "job_xyz",                                                │
│    user_id: "1762...",                                               │
│    client_drawer_id: "client_1762...",  // ← Referencia al drawer   │
│    type: "full",                                                      │
│    status: "pending"                                                  │
│  }                                                                    │
└──────────────────────────────────────────────────────────────────────┘
                                │
                    Job Worker lo detecta
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│              PASO 3: JOB WORKER LEE CLIENT_DRAWER                     │
├──────────────────────────────────────────────────────────────────────┤
│  1. Leer job de generation_jobs                                      │
│  2. ⭐ Leer client_drawer COMPLETO de MongoDB:                        │
│     client_drawer = await db.client_drawers.find_one(                │
│       {"_id": job["client_drawer_id"]}                               │
│     )                                                                 │
│                                                                       │
│  3. Construir ClientContext EN MEMORIA desde client_drawer:          │
│     - meta: Generar nuevo snapshot_id                                │
│     - raw_inputs: Extraer de questionnaires.inicial.responses        │
│     - training: Vacío (lo llenan E1-E9)                              │
│     - nutrition: Vacío (lo llenan N0-N8)                             │
│                                                                       │
│  ✅ NO HAY RECONSTRUCCIÓN: Solo lectura directa                      │
└──────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│              PASO 4: ORQUESTADOR EJECUTA AGENTES                      │
├──────────────────────────────────────────────────────────────────────┤
│  Exactamente igual que antes, pero:                                  │
│                                                                       │
│  - E1 lee de client_drawer.questionnaires.inicial                    │
│  - E2-E9 leen de ClientContext (arquitectura cajones)                │
│  - N0-N8 leen de ClientContext                                       │
│                                                                       │
│  ⭐ Los agentes NO saben que hay un drawer, solo ven ClientContext   │
└──────────────────────────────────────────────────────────────────────┘
                                │
                ClientContext completo generado
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│        PASO 5: GUARDAR SNAPSHOT EN CLIENT_DRAWER                      │
├──────────────────────────────────────────────────────────────────────┤
│  1. Crear snapshot con ClientContext COMPLETO:                       │
│     snapshot = {                                                      │
│       snapshot_id: "snapshot_v1_jan2025",                            │
│       version: 1,                                                     │
│       created_at: "2025-01-03T10:15:30Z",                            │
│       trigger: "inicial",                                            │
│       client_context: { /* ClientContext COMPLETO */ },              │
│       plans_generated: {                                             │
│         training_plan_id: null,  // Se llenará después               │
│         nutrition_plan_id: null                                      │
│       },                                                             │
│       generation_job_id: "job_xyz"                                   │
│     }                                                                 │
│                                                                       │
│  2. Actualizar client_drawer:                                        │
│     await db.client_drawers.update_one(                              │
│       {"_id": client_drawer_id},                                     │
│       {                                                              │
│         "$push": { "snapshots": snapshot },                          │
│         "$set": {                                                    │
│           "meta.updated_at": now,                                    │
│           "meta.current_snapshot": snapshot_id                       │
│         }                                                            │
│       }                                                              │
│     )                                                                 │
│                                                                       │
│  ✅ ClientContext PERSISTE en el drawer                              │
└──────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│        PASO 6: CREAR PLANES COMO VISTAS DERIVADAS                     │
├──────────────────────────────────────────────────────────────────────┤
│  1. Crear training_plan (SIN duplicar cuestionario):                 │
│     training_plan = {                                                │
│       _id: "training_v1_jan2025",                                    │
│       user_id: "1762...",                                            │
│       client_drawer_id: "client_1762...",  // ← Referencia           │
│       snapshot_id: "snapshot_v1_jan2025",  // ← Referencia           │
│                                                                       │
│       ⚠️ NO HAY questionnaire_data                                   │
│                                                                       │
│       // Solo datos del plan final                                   │
│       formatted_plan: "# PLAN DE ENTRENAMIENTO...",                  │
│       generated_at: "2025-01-03T10:15:20Z",                          │
│       month: 1,                                                       │
│       year: 2025,                                                     │
│       pdf_id: null                                                    │
│     }                                                                 │
│     await db.training_plans.insert_one(training_plan)                │
│                                                                       │
│  2. Crear nutrition_plan (ídem):                                     │
│     nutrition_plan = {                                               │
│       _id: "nutrition_v1_jan2025",                                   │
│       client_drawer_id: "client_1762...",                            │
│       snapshot_id: "snapshot_v1_jan2025",                            │
│       menu_plan: "...",                                              │
│       generated_at: "2025-01-03T10:15:25Z"                           │
│     }                                                                 │
│     await db.nutrition_plans.insert_one(nutrition_plan)              │
│                                                                       │
│  ✅ Planes son VISTAS, no copias                                     │
└──────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│        PASO 7: ACTUALIZAR REFERENCIAS EN CLIENT_DRAWER                │
├──────────────────────────────────────────────────────────────────────┤
│  1. Actualizar snapshot con IDs de planes:                           │
│     await db.client_drawers.update_one(                              │
│       {                                                              │
│         "_id": client_drawer_id,                                     │
│         "snapshots.snapshot_id": snapshot_id                         │
│       },                                                             │
│       {                                                              │
│         "$set": {                                                    │
│           "snapshots.$.plans_generated": {                           │
│             training_plan_id: "training_v1_jan2025",                 │
│             nutrition_plan_id: "nutrition_v1_jan2025"                │
│           }                                                          │
│         }                                                            │
│       }                                                              │
│     )                                                                 │
│                                                                       │
│  2. Actualizar lista de planes:                                      │
│     await db.client_drawers.update_one(                              │
│       {"_id": client_drawer_id},                                     │
│       {                                                              │
│         "$push": {                                                   │
│           "plans.training": {                                        │
│             plan_id: "training_v1_jan2025",                          │
│             version: 1,                                              │
│             snapshot_id: snapshot_id,                                │
│             status: "active"                                         │
│           },                                                         │
│           "plans.nutrition": { ... }                                 │
│         }                                                            │
│       }                                                              │
│     )                                                                 │
│                                                                       │
│  ✅ Navegación bidireccional: drawer ↔ planes                        │
└──────────────────────────────────────────────────────────────────────┘
```

### 🔄 Flujo de Seguimiento (Mes 2)

```
Cliente completa seguimiento mensual
    ↓
PASO 1: Guardar en client_drawer.questionnaires.followups[]
    - No crear nueva entrada
    - Append al array de followups del MISMO drawer
    ↓
PASO 2: Crear job con:
    - client_drawer_id (mismo del mes 1)
    - mode: "followup"
    - previous_snapshot_id: "snapshot_v1_jan2025"
    ↓
PASO 3: Job Worker lee client_drawer
    - Lee questionnaires.inicial (contexto original)
    - Lee followups[0] (último seguimiento)
    - Lee snapshots[-1] (snapshot previo)
    - Construye ClientContext con contexto histórico
    ↓
PASO 4: Orquestador ejecuta agentes
    - Agentes tienen acceso al plan previo
    - Pueden hacer progresión inteligente
    ↓
PASO 5: Crear snapshot_v2 en el MISMO drawer
    - snapshot_id: "snapshot_v2_feb2025"
    - version: 2
    - previous_snapshot_id: "snapshot_v1_jan2025"
    - trigger: "followup"
    - followup_id: "followup_xyz"
    ↓
PASO 6: Crear nuevos planes (training_v2, nutrition_v2)
    - Referencia al snapshot_v2
    - NO duplican cuestionario
    ↓
PASO 7: Actualizar referencias en drawer
    - Append a snapshots[]
    - Append a plans.training[] y plans.nutrition[]

✅ TODO en el MISMO client_drawer
✅ Historial completo navegable
```

---

## EJEMPLO REAL: CLIENTE JORGE1

### 📅 Timeline Completa

#### **2 Enero 2025 - Registro y Cuestionario Inicial**

**Acción:** Jorge1 completa el cuestionario inicial detallado.

**Resultado en BD:**

```javascript
// Colección: client_drawers
{
  _id: "client_1762094831193507",
  user_id: "1762094831193507",
  
  profile: {
    nombre_completo: "Jorge Calcerrada",
    email: "jorge@example.com",
    edad: 35,
    // ...
  },
  
  questionnaires: {
    inicial: {
      submitted_at: ISODate("2025-01-02T09:00:00Z"),
      responses: {
        objetivo_fisico: "Perder grasa",  // ⭐
        peso: "85",
        altura_cm: "178",
        // ... 100+ campos
      }
    },
    followups: []  // Vacío
  },
  
  snapshots: [],  // Vacío, aún no se generó plan
  measurements: [
    {
      measurement_id: "measure_inicial",
      date: ISODate("2025-01-02T09:00:00Z"),
      data: { peso: 85, grasa_porcentaje: 22 }
    }
  ],
  plans: { training: [], nutrition: [] },
  notes: [],
  meta: {
    created_at: ISODate("2025-01-02T09:00:00Z"),
    current_snapshot: null
  }
}
```

**Estado:** ✅ Client drawer creado, esperando generación de plan.

---

#### **3 Enero 2025 - Generación del Plan Inicial**

**Acción:** Admin crea job para generar plan completo (training + nutrition).

**Job creado:**
```javascript
// Colección: generation_jobs
{
  job_id: "job_1736960100000000",
  user_id: "1762094831193507",
  client_drawer_id: "client_1762094831193507",  // ← Nueva referencia
  type: "full",
  status: "pending"
}
```

**Proceso:**
1. Job worker lee `client_drawer`
2. Construye `ClientContext` desde `questionnaires.inicial`
3. Orquestador ejecuta E1-E9 y N0-N8
4. Post-procesador genera `formatted_plan` en Markdown

**Resultado en BD después del job:**

```javascript
// client_drawers (actualizado)
{
  _id: "client_1762094831193507",
  
  // ... profile y questionnaires sin cambios
  
  snapshots: [
    {
      snapshot_id: "snapshot_v1_jan2025",
      version: 1,
      created_at: ISODate("2025-01-03T10:15:30Z"),
      trigger: "inicial",
      
      // ⭐⭐⭐ ClientContext COMPLETO guardado aquí
      client_context: {
        meta: {
          client_id: "client_1762094831193507",
          snapshot_id: "snapshot_v1_jan2025",
          version: 1
        },
        raw_inputs: null,  // Ya no se guarda
        training: {
          client_summary: {
            objetivo: "Pérdida de grasa corporal",
            nivel: "Principiante avanzado",
            limitaciones: ["Hernia discal L4-L5"]
          },
          profile: { /* Análisis E1 */ },
          constraints: { /* E1 */ },
          capacity: { /* E2 */ },
          adaptation: { /* E3 */ },
          mesocycle: { /* E4 */ },
          sessions: [ /* E5 - Sesiones completas */ ],
          safe_sessions: [ /* E6 */ ],
          formatted_plan: "# PLAN DE ENTRENAMIENTO JORGE...",  // Markdown
          audit: { /* E8 */ },
          bridge_for_nutrition: { /* E9 */ }
        },
        nutrition: {
          profile: { /* N0 */ },
          metabolism: { /* N1 */ },
          energy_strategy: { /* N2 */ },
          macro_design: { /* N3 */ },
          weekly_structure: { /* N4 */ },
          timing_plan: { /* N5 */ },
          menu_plan: { /* N6 - Menú completo */ },
          adherence_report: { /* N7 */ },
          audit: { /* N8 */ }
        }
      },
      
      plans_generated: {
        training_plan_id: "training_v1_jan2025",
        nutrition_plan_id: "nutrition_v1_jan2025"
      },
      
      generation_job_id: "job_1736960100000000"
    }
  ],
  
  plans: {
    training: [
      {
        plan_id: "training_v1_jan2025",
        version: 1,
        snapshot_id: "snapshot_v1_jan2025",
        status: "active"
      }
    ],
    nutrition: [
      {
        plan_id: "nutrition_v1_jan2025",
        version: 1,
        snapshot_id: "snapshot_v1_jan2025",
        status: "active"
      }
    ]
  },
  
  meta: {
    updated_at: ISODate("2025-01-03T10:15:30Z"),
    current_snapshot: "snapshot_v1_jan2025",
    total_snapshots: 1
  }
}
```

```javascript
// Colección: training_plans
{
  _id: "training_v1_jan2025",
  user_id: "1762094831193507",
  client_drawer_id: "client_1762094831193507",  // ← Referencia
  snapshot_id: "snapshot_v1_jan2025",  // ← Referencia
  
  // ⚠️ NO HAY questionnaire_data
  
  // Solo el plan final
  formatted_plan: "# PLAN DE ENTRENAMIENTO - JORGE CALCERRADA\n\n## Objetivo...",
  generated_at: ISODate("2025-01-03T10:15:20Z"),
  month: 1,
  year: 2025,
  edited: false,
  pdf_id: null
}
```

```javascript
// Colección: nutrition_plans
{
  _id: "nutrition_v1_jan2025",
  user_id: "1762094831193507",
  client_drawer_id: "client_1762094831193507",  // ← Referencia
  snapshot_id: "snapshot_v1_jan2025",  // ← Referencia
  
  // ⚠️ NO HAY questionnaire_data
  
  menu_plan: "...",
  generated_at: ISODate("2025-01-03T10:15:25Z"),
  month: 1,
  year: 2025
}
```

**Estado:** ✅ Plan inicial completo, sin duplicaciones.

---

#### **3 Febrero 2025 - Seguimiento Mes 1**

**Acción:** Jorge1 completa el cuestionario de seguimiento mensual.

**Resultado en BD:**

```javascript
// client_drawers (actualizado con followup)
{
  _id: "client_1762094831193507",
  
  questionnaires: {
    inicial: { /* Sin cambios */ },
    
    followups: [
      // ⭐ Nuevo seguimiento añadido
      {
        followup_id: "followup_1739550000000000",
        submitted_at: ISODate("2025-02-03T10:00:00Z"),
        days_since_last: 30,
        previous_snapshot_id: "snapshot_v1_jan2025",
        
        measurement_type: "smart_scale",
        measurements: {
          peso: "83",  // Bajó 2kg
          grasa_corporal: "20",  // Bajó 2%
          masa_muscular: "42",
          satisfecho_cambios: "SI"
        },
        
        adherence: {
          constancia_entrenamiento: "80%",
          seguimiento_alimentacion: "70%"
        },
        
        wellbeing: {
          factores_externos: "Proyecto intenso trabajo",
          energia_animo_motivacion: "Mejor que antes",
          sueno_estres: "Regular"
        },
        
        changes_perceived: {
          molestias_dolor_lesion: "Ninguna nueva",
          cambios_corporales: "Más definición abdominal",
          fuerza_rendimiento: "Mejorando"
        },
        
        feedback: {
          objetivo_proximo_mes: "Seguir perdiendo grasa",
          cambios_deseados: "Aumentar intensidad si es seguro"
        }
      }
    ]
  },
  
  measurements: [
    { /* Medición inicial */ },
    
    // Nueva medición del seguimiento
    {
      measurement_id: "measure_mes1",
      date: ISODate("2025-02-03T10:00:00Z"),
      tipo: "followup",
      source: "followup_1739550000000000",
      data: {
        peso: 83,
        grasa_corporal: 20,
        masa_muscular: 42
      }
    }
  ],
  
  // snapshots y plans sin cambios (aún no se generó plan mes 2)
}
```

**Estado:** ✅ Seguimiento guardado, esperando generación de nuevo plan.

---

#### **3 Febrero 2025 - Generación del Plan Mes 2**

**Acción:** Admin crea job para generar plan de seguimiento.

**Job creado:**
```javascript
{
  job_id: "job_1739560000000000",
  user_id: "1762094831193507",
  client_drawer_id: "client_1762094831193507",  // ← Mismo drawer
  type: "full",
  trigger: "followup",
  previous_snapshot_id: "snapshot_v1_jan2025",  // ← Contexto del plan previo
  status: "pending"
}
```

**Proceso:**
1. Job worker lee `client_drawer` completo
2. Construye `ClientContext` con:
   - `questionnaires.inicial` (contexto base)
   - `questionnaires.followups[0]` (últimas medidas y feedback)
   - `snapshots[0]` (plan previo para progresión)
3. Orquestador ejecuta agentes con contexto histórico
4. Agentes hacen ajustes inteligentes (aumentar intensidad, ajustar macros)

**Resultado en BD:**

```javascript
// client_drawers (snapshot_v2 añadido)
{
  _id: "client_1762094831193507",
  
  snapshots: [
    { /* snapshot_v1_jan2025 sin cambios */ },
    
    // ⭐ Nuevo snapshot del mes 2
    {
      snapshot_id: "snapshot_v2_feb2025",
      version: 2,
      created_at: ISODate("2025-02-03T11:00:00Z"),
      trigger: "followup",
      followup_id: "followup_1739550000000000",
      previous_snapshot_id: "snapshot_v1_jan2025",  // ← Vínculo explícito
      
      client_context: {
        // ClientContext actualizado con ajustes
        training: {
          // ... ajustes basados en progreso
          mesocycle: {
            // Intensidad aumentada de RPE 7 → RPE 8
          },
          sessions: [
            // Sesiones progresadas (más peso, más series)
          ]
        },
        nutrition: {
          // Macros ajustados por pérdida de peso
          macro_design: {
            proteina_g: 165,  // Mantenida
            carbohidratos_g: 200,  // Reducidos ligeramente
            grasas_g: 70
          }
        }
      },
      
      plans_generated: {
        training_plan_id: "training_v2_feb2025",
        nutrition_plan_id: "nutrition_v2_feb2025"
      }
    }
  ],
  
  plans: {
    training: [
      { /* training_v1_jan2025 */ },
      {
        plan_id: "training_v2_feb2025",
        version: 2,
        snapshot_id: "snapshot_v2_feb2025",
        status: "active"
      }
    ],
    nutrition: [
      { /* nutrition_v1_jan2025 */ },
      {
        plan_id: "nutrition_v2_feb2025",
        version: 2,
        snapshot_id: "snapshot_v2_feb2025",
        status: "active"
      }
    ]
  },
  
  notes: [
    // Admin añade nota
    {
      note_id: "note_mes1",
      created_at: ISODate("2025-02-03T11:05:00Z"),
      created_by: "admin_jorge",
      content: "Excelente progreso. Perdió 2kg sin molestias. Aumenté intensidad RPE 7→8.",
      tags: ["seguimiento", "progreso", "intensificacion"]
    }
  ],
  
  meta: {
    updated_at: ISODate("2025-02-03T11:00:30Z"),
    current_snapshot: "snapshot_v2_feb2025",  // ← Actualizado
    total_snapshots: 2
  }
}
```

**Estado:** ✅ Plan mes 2 generado, historial completo en el drawer.

---

### 📊 Navegación Temporal en el Drawer de Jorge1

```javascript
// Ver plan actual
client_drawer.meta.current_snapshot
  → "snapshot_v2_feb2025"
  → plans_generated.training_plan_id = "training_v2_feb2025"

// Ver plan anterior
client_drawer.snapshots[0]
  → "snapshot_v1_jan2025"
  → plans_generated.training_plan_id = "training_v1_jan2025"

// Ver evolución de peso
client_drawer.measurements
  → [0]: 85 kg (inicial)
  → [1]: 83 kg (mes 1) → Pérdida de 2 kg ✅

// Ver cuestionario original
client_drawer.questionnaires.inicial.responses
  → objetivo_fisico: "Perder grasa"
  → hernias_protusiones: "Hernia discal L4-L5"

// Ver último seguimiento
client_drawer.questionnaires.followups[0]
  → satisfecho_cambios: "SI"
  → feedback.cambios_deseados: "Aumentar intensidad"

// Ver nota del entrenador
client_drawer.notes[0]
  → "Excelente progreso. Aumenté intensidad RPE 7→8."
```

---

## REGLAS DE ORO DEL SISTEMA

### ✅ Regla 1: Única Fuente de Verdad

> **"Si no está en el `client_drawer`, no existe para el sistema."**

**Implementación:**
- ❌ NO leer directamente de `questionnaire_responses`, `nutrition_questionnaire_submissions`
- ✅ SÍ leer siempre de `client_drawers`
- ❌ NO reconstruir contexto desde colecciones dispersas
- ✅ SÍ usar el snapshot más reciente del drawer

**Código:**
```python
# ❌ PROHIBIDO (Forma antigua)
submission = await db.nutrition_questionnaire_submissions.find_one({"_id": submission_id})
questionnaire_data = submission["responses"]

# ✅ CORRECTO (Nueva forma)
client_drawer = await db.client_drawers.find_one({"user_id": user_id})
questionnaire_data = client_drawer["questionnaires"]["inicial"]["responses"]
```

---

### ✅ Regla 2: Los Agentes Solo Leen de ClientContext

> **"Los agentes NO saben que existe un `client_drawer`. Solo ven el `ClientContext`."**

**Arquitectura de capas:**
```
┌─────────────────────────────────────────┐
│  AGENTES (E1-E9, N0-N8)                 │
│  ↑ Solo ven ClientContext               │
├─────────────────────────────────────────┤
│  ORQUESTADOR                            │
│  ↑ Construye ClientContext desde drawer │
├─────────────────────────────────────────┤
│  CLIENT_DRAWER (Fuente de verdad)       │
│  Colección: client_drawers              │
└─────────────────────────────────────────┘
```

**Responsabilidades:**
- **Job Worker:** Lee drawer, construye ClientContext
- **Orquestador:** Pasa ClientContext a agentes
- **Agentes:** Modifican SOLO su campo en ClientContext
- **Job Worker:** Guarda ClientContext completo de vuelta al drawer

---

### ✅ Regla 3: Los Planes Son Vistas Derivadas

> **"Los planes NO duplican datos. Son snapshots derivados."**

**Relación:**
```
client_drawer
  └── snapshots[0]
        ├── snapshot_id: "snapshot_v1"
        ├── client_context: { /* TODO */ }
        └── plans_generated:
              ├── training_plan_id: "training_v1"
              └── nutrition_plan_id: "nutrition_v1"

training_plans
  └── training_v1
        ├── snapshot_id: "snapshot_v1"  ← Referencia
        ├── formatted_plan: "..."        ← Solo el plan
        └── NO HAY questionnaire_data
```

**Si se necesita el cuestionario:**
```python
# Forma incorrecta (antigua)
questionnaire = training_plan["questionnaire_data"]  # ❌ No existe

# Forma correcta (nueva)
training_plan = await db.training_plans.find_one({"_id": plan_id})
snapshot_id = training_plan["snapshot_id"]

client_drawer = await db.client_drawers.find_one(
    {"snapshots.snapshot_id": snapshot_id}
)
snapshot = next(s for s in client_drawer["snapshots"] if s["snapshot_id"] == snapshot_id)
questionnaire = client_drawer["questionnaires"]["inicial"]["responses"]
```

---

### ✅ Regla 4: Versionado Explícito e Inmutable

> **"Los snapshots SON inmutables. Crear nuevo snapshot, NO editar el anterior."**

**Prohibido:**
```python
# ❌ PROHIBIDO: Editar snapshot existente
await db.client_drawers.update_one(
    {"_id": client_id, "snapshots.snapshot_id": snapshot_id},
    {"$set": {"snapshots.$.client_context.training.capacity": new_value}}
)
```

**Correcto:**
```python
# ✅ CORRECTO: Crear nuevo snapshot
new_snapshot = {
    "snapshot_id": f"snapshot_v{version + 1}",
    "version": version + 1,
    "previous_snapshot_id": previous_snapshot_id,
    "client_context": updated_context
}

await db.client_drawers.update_one(
    {"_id": client_id},
    {"$push": {"snapshots": new_snapshot}}
)
```

**Navegación temporal:**
```python
# Ver snapshot específico
snapshot_v1 = client_drawer["snapshots"][0]
snapshot_v2 = client_drawer["snapshots"][1]

# Ver snapshot actual
current_snapshot_id = client_drawer["meta"]["current_snapshot"]
current_snapshot = next(
    s for s in client_drawer["snapshots"]
    if s["snapshot_id"] == current_snapshot_id
)
```

---

### ✅ Regla 5: Agregación Temporal, No Duplicación

> **"Medidas, seguimientos y notas se AGREGAN al drawer. NO se crean nuevos registros."**

**Correcto:**
```python
# ✅ Añadir medición al drawer existente
await db.client_drawers.update_one(
    {"_id": client_id},
    {
        "$push": {
            "measurements": new_measurement,
            "questionnaires.followups": new_followup,
            "notes": new_note
        }
    }
)
```

**Prohibido:**
```python
# ❌ Crear documento separado para seguimiento
await db.followup_submissions.insert_one({
    "user_id": user_id,
    "responses": {...}
})
```

---

## COMPARATIVA AS IS vs TO BE

### 📊 Tabla Comparativa

| **Aspecto** | **AS IS (Actual)** | **TO BE (Client Drawer)** | **Mejora** |
|---|---|---|---|
| **Fuente de verdad** | 6+ colecciones dispersas | 1 colección: `client_drawers` | 🟢 **Unificación total** |
| **Duplicación de cuestionarios** | 3+ copias por cliente | 1 copia única | 🟢 **Eliminación 100%** |
| **ClientContext** | Solo en memoria (se destruye) | Persiste en snapshots[] | 🟢 **Trazabilidad completa** |
| **Versionado** | Manual (month, year) | Automático (version, snapshot_id) | 🟢 **Consistencia garantizada** |
| **Navegación temporal** | Imposible (planes sin vínculo) | Nativa (previous_snapshot_id) | 🟢 **Historial navegable** |
| **Reconstrucción de contexto** | Cada job desde cero | 1 query al drawer | 🟢 **Eficiencia x10** |
| **Seguimientos** | Nueva ejecución completa | Progresión desde snapshot previo | 🟢 **Inteligencia contextual** |
| **Referencias cruzadas** | Inconsistentes (múltiples) | Bidireccionales (drawer ↔ planes) | 🟢 **Integridad referencial** |
| **Espacio en BD (1 cliente, 12 meses)** | ~500 KB (25 copias cuest.) | ~120 KB (1 copia + snapshots) | 🟢 **Reducción 75%** |
| **Queries para historial completo** | 5+ queries + joins manuales | 1 query | 🟢 **Simplicidad total** |

---

### 💾 Ahorro de Espacio (Estimación)

**AS IS:**
```
Cuestionario: 10 KB
Cliente con 12 planes (1 año):
- nutrition_questionnaire_submissions: 10 KB
- training_plans × 12: 12 × 10 KB = 120 KB
- nutrition_plans × 12: 12 × 10 KB = 120 KB
TOTAL: 250 KB por cliente/año
```

**TO BE:**
```
Cuestionario: 10 KB (1 sola vez en drawer)
Snapshots × 12: 12 × 5 KB = 60 KB (solo ClientContext)
Planes (sin cuestionario) × 24: 24 × 2 KB = 48 KB
TOTAL: 118 KB por cliente/año
```

**Ahorro:** **53% menos espacio** por cliente.

---

### ⚡ Mejora de Performance

**Consulta: "Obtener historial completo del cliente Jorge1"**

**AS IS:**
```python
# 6 queries separadas
user = await db.users.find_one({"_id": user_id})
submissions = await db.nutrition_questionnaire_submissions.find({"user_id": user_id}).to_list()
training_plans = await db.training_plans.find({"user_id": user_id}).to_list()
nutrition_plans = await db.nutrition_plans.find({"user_id": user_id}).to_list()
followups = await db.followup_submissions.find({"user_id": user_id}).to_list()
notes = await db.notes.find({"user_id": user_id}).to_list()

# Luego: reconstruir manualmente el historial
# Ordenar por fechas, vincular planes con cuestionarios, etc.
```

**TO BE:**
```python
# 1 query única
client_drawer = await db.client_drawers.find_one({"user_id": user_id})

# TODO el historial está ahí, ordenado y vinculado:
historial = {
    "cuestionario_inicial": client_drawer["questionnaires"]["inicial"],
    "seguimientos": client_drawer["questionnaires"]["followups"],
    "snapshots": client_drawer["snapshots"],
    "planes": client_drawer["plans"],
    "medidas": client_drawer["measurements"],
    "notas": client_drawer["notes"]
}
```

**Mejora:** **De 6 queries a 1. ~5x más rápido.**

---

## LISTA EXPLÍCITA DE CÓDIGO A ELIMINAR

### 🗑️ FASE 1: Deprecar Colecciones Legacy

#### Colecciones a ELIMINAR (después de migración)

1. **`nutrition_questionnaire_submissions`**
   - **Propósito legacy:** Almacenar cuestionarios nutricionales
   - **Reemplazo:** `client_drawers.questionnaires.inicial`
   - **Acción:** Migrar datos → Eliminar colección
   - **Archivos afectados:**
     - `/app/backend/server.py` (líneas 700, 812, 927)

2. **`followup_submissions`**
   - **Propósito legacy:** Almacenar seguimientos mensuales
   - **Reemplazo:** `client_drawers.questionnaires.followups[]`
   - **Acción:** Migrar datos → Eliminar colección

3. **`questionnaire_responses`** (Opcional, fuera del core EDN360)
   - **Propósito:** Cuestionarios de prospección (landing page)
   - **Reemplazo:** Mantener separado (es CRM, no EDN360)
   - **Acción:** NO eliminar, pero NO usarlo en generación de planes

---

### 🗑️ FASE 2: Eliminar Campos Duplicados en Planes

#### Colecciones a MODIFICAR

1. **`training_plans`**
   - **Campo a eliminar:** `questionnaire_data`
   - **Campos a añadir:**
     - `client_drawer_id` (referencia)
     - `snapshot_id` (referencia)
   - **Archivos afectados:**
     - `/app/backend/server.py` (función `process_generation_job`)
     - `/app/backend/models.py` (modelo `TrainingPlanResponse`)

2. **`nutrition_plans`**
   - **Campo a eliminar:** `questionnaire_data`
   - **Campos a añadir:**
     - `client_drawer_id` (referencia)
     - `snapshot_id` (referencia)

---

### 🗑️ FASE 3: Eliminar Lógicas de Reconstrucción

#### Funciones a ELIMINAR o REFACTORIZAR

1. **`initialize_client_context()` - Simplificar**
   - **Archivo:** `/app/backend/edn360/client_context_utils.py`
   - **Lógica a eliminar:** Parseo manual del cuestionario desde dict
   - **Nueva lógica:** Leer directamente de `client_drawer`
   
   ```python
   # ❌ ELIMINAR (lógica antigua)
   def initialize_client_context(cuestionario_data: Dict):
       # Parseo manual de 100+ campos
       raw_inputs = RawInputs(
           cuestionario_inicial=json.dumps(cuestionario_data)
       )
       # ...
   
   # ✅ NUEVA LÓGICA
   def initialize_client_context_from_drawer(client_drawer: Dict):
       # Leer directamente del drawer estructurado
       questionnaire = client_drawer["questionnaires"]["inicial"]["responses"]
       # ...
   ```

2. **`process_generation_job()` - Refactorizar**
   - **Archivo:** `/app/backend/server.py`
   - **Lógica a eliminar:**
     ```python
     # ❌ ELIMINAR
     submission = await db.nutrition_questionnaire_submissions.find_one(...)
     questionnaire_data = submission["responses"]
     ```
   - **Nueva lógica:**
     ```python
     # ✅ NUEVA
     client_drawer = await db.client_drawers.find_one({"_id": job["client_drawer_id"]})
     questionnaire_data = client_drawer["questionnaires"]["inicial"]["responses"]
     ```

---

### 🗑️ FASE 4: Eliminar Endpoints Legacy

#### Endpoints a MODIFICAR o DEPRECAR

1. **POST `/api/questionnaire/submit`**
   - **Lógica antigua:** Guardar en `questionnaire_responses`
   - **Nueva lógica:** Crear/actualizar `client_drawer`

2. **POST `/api/nutrition-questionnaire/submit`**
   - **Lógica antigua:** Guardar en `nutrition_questionnaire_submissions`
   - **Nueva lógica:** Actualizar `client_drawer.questionnaires.inicial`

3. **POST `/api/followup/submit`**
   - **Lógica antigua:** Crear documento en `followup_submissions`
   - **Nueva lógica:** Append a `client_drawer.questionnaires.followups[]`

4. **POST `/admin/users/{user_id}/plans/generate_async`**
   - **Cambio:** Recibir `client_drawer_id` en vez de `submission_id`
   - **Validación:** Verificar que el drawer existe

---

### 🗑️ FASE 5: Eliminar Código de Compatibilidad Legacy

#### Bloques de código a ELIMINAR

1. **Orquestador: Manejo de agentes legacy**
   - **Archivo:** `/app/backend/edn360/orchestrator.py` (líneas 811-841)
   - **Bloque:**
     ```python
     else:
         # Compatibilidad: agente legacy (E2, E3, E4, E6, E7, E9)
         logger.warning(f"  ⚠️ {agent.agent_id} es legacy, simulando output con datos dummy")
         # ...
     ```
   - **Acción:** Eliminar después de refactorizar todos los agentes

2. **Doble guardado de `formatted_plan`**
   - **Archivo:** `/app/backend/server.py`
   - **Lógica a eliminar:**
     ```python
     # ❌ ELIMINAR: Guardar e7_output.formatted_plan
     training_plan["e7_output"] = {"formatted_plan": e7_result}
     
     # ✅ MANTENER: Solo formatted_plan post-procesado
     training_plan["formatted_plan"] = markdown_plan
     ```

---

### 📝 Resumen de Eliminaciones

| **Elemento** | **Tipo** | **Acción** | **Prioridad** |
|---|---|---|---|
| `nutrition_questionnaire_submissions` | Colección | Migrar → Eliminar | 🔴 Alta |
| `followup_submissions` | Colección | Migrar → Eliminar | 🔴 Alta |
| `questionnaire_data` en planes | Campo | Eliminar | 🔴 Alta |
| `initialize_client_context()` | Función | Refactorizar | 🟡 Media |
| `process_generation_job()` | Función | Refactorizar | 🔴 Alta |
| Endpoints de cuestionarios | API | Modificar | 🔴 Alta |
| Lógica legacy agentes | Código | Eliminar tras refactor | 🟢 Baja |

---

## CONCLUSIONES DEL DOCUMENTO TO BE

### ✅ Beneficios Clave de Client Drawer

1. **Simplicidad Arquitectónica:**
   - 1 colección en vez de 6
   - 1 query para todo el historial
   - 0 duplicaciones

2. **Trazabilidad Completa:**
   - Snapshots inmutables con ClientContext completo
   - Versionado explícito con vínculos
   - Navegación temporal nativa

3. **Eficiencia:**
   - 53% menos espacio en BD
   - 5x más rápido en consultas
   - Menos procesamiento (no reconstruir contexto)

4. **Escalabilidad:**
   - Historial ilimitado en el mismo drawer
   - Fácil añadir nuevos campos (notes, files, etc.)
   - Soporte nativo para múltiples agentes

5. **Mantenibilidad:**
   - Código más simple (menos colecciones)
   - Menos lógicas condicionales
   - Una única fuente de verdad

---

### 🎯 Próximo Paso: Documento 3 - Plan de Ejecución

El Documento 3 definirá:
1. **Fase por fase:** Cómo migrar sin romper producción
2. **Scripts de migración:** Código específico para mover datos
3. **Criterios de éxito:** Qué validar en cada fase
4. **Rollback points:** Cómo revertir si algo falla
5. **Timeline estimado:** Cuánto tiempo tomará cada fase

---

**Fin del Documento TO BE**
