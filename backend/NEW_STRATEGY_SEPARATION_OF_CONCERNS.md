# ✅ NUEVA ESTRATEGIA IMPLEMENTADA - Separación de Responsabilidades

**Fecha:** 7 de diciembre 2024  
**Status:** ✅ DESPLEGADO Y LISTO PARA TESTING

---

## 🎯 CAMBIO DE ESTRATEGIA

### ❌ Estrategia ANTERIOR (fallida):
- E4 responsable de generar exercise_code EXACTOS
- Validación DURA que rompía todo el plan por un código inválido
- Jorge haciendo de QA manual permanente
- Sistema generaba 0 planes

### ✅ Estrategia NUEVA (implementada):
- **E4:** Genera lógica de entrenamiento + descripciones de ejercicios
- **E6:** Mapea descripciones → códigos canónicos (con fuzzy matching)
- **Sistema:** SIEMPRE genera un plan (aunque algunos códigos sean "sospechosos")
- **Backend:** Enriquece con nombres/videos

---

## 🔧 CAMBIOS IMPLEMENTADOS

### 1️⃣ E4 - Prompt Simplificado

**ANTES:** ~2500 palabras, obsesionado con exercise_code exactos

**AHORA:** ~800 palabras, enfocado en lógica de entrenamiento

**Nuevo enfoque:**
```
YOUR JOB: Design the training LOGIC (patterns, volume, intensity)
NOT YOUR JOB: Finding exact exercise codes (E6 will handle that)

For exercise_id, use DESCRIPTIVE names like:
- "press_banca_barra" (bench press barbell)
- "sentadilla_barra" (barbell squat)  
- "remo_barra" (barbell row)

Format: [exercise_name]_[equipment]
Equipment: barra, mancuernas, maquina, polea, peso_corporal

E6 will map your descriptive IDs to canonical codes.
```

**Beneficios:**
- ✅ E4 hace lo que hace bien: decidir patrones, volumen, intensidad
- ✅ No necesita "adivinar" strings exactos de IDs
- ✅ Prompt más corto → mejor retención de instrucciones

---

### 2️⃣ E4 Schema - Sin Validación Dura

**ANTES:**
```typescript
exercise_id: z.string()
  .refine(
    (code) => VALID_EXERCISE_CODES.includes(code),
    { message: "❌ INVALID exercise_code. Plan REJECTED" }
  )
```

**AHORA:**
```typescript
exercise_id: z.string(), // E4 generates descriptive IDs, E6 maps to canonical
```

**Beneficio:** El plan NO se rompe por un código descriptivo que E6 puede mapear

---

### 3️⃣ E6 - Mapper Fortalecido

**ANTES:** Desactivado / código legacy

**AHORA:** Activo como mapper de descriptive → canonical

**Nueva responsabilidad:**
```
YOUR JOB: Map E4's descriptive exercise_id to a CANONICAL exercise_code.

MAPPING STRATEGY:
1. Try exact match first
2. If no exact match, use fuzzy matching on:
   - Name similarity
   - Movement pattern
   - Equipment type
   - Muscle group
3. Pick the BEST canonical code from the catalog (1243 codes)

MAPPING EXAMPLES:
- "press_banca_barra" → "press_banca_barra" (exact)
- "pec_deck" → "aperturas_medias_poleas" (fuzzy)
- "cable_fly" → "aperturas_poleas_tumbado" (fuzzy)
- "horizontal_press_machine" → "press_horizontal_maquina_palanca" (fuzzy)
```

**Beneficios:**
- ✅ Garantiza que TODOS los códigos son canónicos
- ✅ Usa fuzzy matching cuando E4 no acierta exactamente
- ✅ Loggea las correcciones para visibilidad
- ✅ NO rompe el plan, solo corrige

---

### 4️⃣ Reducción Temporal de Ejercicios

**Cambio:** 3 ejercicios por sesión (temporalmente)

**Razón:**
- JSON más corto
- Menos probabilidad de error de sintaxis
- Más fácil de debuggear

**Plan de escala:**
1. Probar con 3 ejercicios
2. Si funciona, escalar a 4
3. Luego a 5
4. Finalmente a 6 (objetivo)

---

## 📊 FLUJO COMPLETO NUEVO

```
┌─────────────────────────────────────────────────────────────┐
│  E1 - Analizador de Perfil                                   │
│  Input: Cuestionario texto libre                             │
│  Output: profile { edad, nivel, objetivo, lesiones... }      │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  E3 - Training Summary                                       │
│  Input: profile                                               │
│  Output: training_context { tipo, días, constraints... }     │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  E4 - Training Plan Generator (SIMPLIFIED)                   │
│  Responsabilidad: LÓGICA de entrenamiento                    │
│  - Patrones de movimiento                                    │
│  - Volumen (series, reps)                                    │
│  - Intensidad (RPE/RIR)                                      │
│  - exercise_id DESCRIPTIVOS (no necesariamente canónicos)    │
│  Output: training_plan con "press_banca_barra", "pec_deck"   │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  E5 - Training Plan Validator                                │
│  Ajusta: series, reps, RPE, notas (seguridad)               │
│  NO toca exercise_id                                         │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  E6 - Exercise Mapper (FORTALECIDO) ⭐ CLAVE                │
│  Responsabilidad: MAPEO a códigos canónicos                  │
│  Input: exercise_id descriptivos de E4                       │
│  Process:                                                     │
│    1. Intenta match exacto con catálogo                      │
│    2. Si no, fuzzy matching:                                 │
│       - Similitud de nombre                                  │
│       - Patrón de movimiento                                 │
│       - Equipo                                               │
│       - Grupo muscular                                       │
│    3. Elige MEJOR código canónico (1243 opciones)           │
│  Output: exercise_code CANÓNICOS                             │
│  Logging: Registra fuzzy matches para visibilidad            │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  E7 - Training Plan Assembler                                │
│  Transforma a estructura cliente-friendly                    │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  E7.5 - Training Plan Enricher                               │
│  Input: exercise_code CANÓNICOS (de E6)                      │
│  Agrega: name_es, video_url, primary_group                   │
│  Fuente: exercise_catalog_edn360.json                        │
│  Output: Plan enriquecido con TODOS los datos                │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  BACKEND PYTHON                                              │
│  - Bloque A: Calentamiento (template)                        │
│  - Bloque B: De E7.5 (enriched)                             │
│  - Bloque C: Core (template)                                │
│  - Bloque D: Cardio (template)                              │
│  Output: Plan completo → training_plans_v2                   │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ VENTAJAS DE LA NUEVA ESTRATEGIA

### 1. **Siempre Genera un Plan**
- Antes: 1 código inválido → 0 planes
- Ahora: E6 corrige códigos → 1 plan completo

### 2. **Separación Clara de Responsabilidades**
- E4: Lógica de entrenamiento (lo que hace bien)
- E6: Mapping de códigos (puede usar fuzzy matching)
- E7.5: Enrichment (nombres, videos)

### 3. **Más Robusto**
- Si E4 dice "pec_deck" → E6 mapea a "aperturas_medias_poleas"
- Si E4 dice "cable_fly" → E6 mapea a "aperturas_poleas_tumbado"
- Plan sigue funcionando

### 4. **Mejor para el Usuario (Jorge)**
- No necesita hacer de QA manual
- Puede ver planes "imperfectos" pero funcionales
- Puede hacer testing funcional (lógica, videos) en lugar de testing de "¿se generó algo?"

### 5. **Escalable**
- Empezamos con 3 ejercicios
- Si funciona, escalamos gradualmente
- Ajustamos E6 según patrones que vemos

---

## 🧪 TESTING ESPERADO

### Primera Generación:
**Objetivo:** Que genere UN PLAN COMPLETO sin romperse

**Validar:**
1. ✅ Plan se genera (no error 500)
2. ✅ Tiene bloques A, B, C, D
3. ✅ Tiene ejercicios (aunque sean 3 por sesión)
4. ✅ Todos los exercise_code son canónicos (gracias a E6)
5. ✅ Todos tienen name, video_url (si existen en catálogo)

**NO validar todavía:**
- Si los ejercicios son los "perfectos" para el perfil
- Si el volumen es exactamente correcto
- Si la selección es óptima

**Eso viene después, cuando el sistema GENERE algo consistentemente.**

---

## 📋 LOGS A REVISAR

Cuando Jorge genere el próximo plan, revisar:

```bash
# Ver si E6 está haciendo fuzzy matching
grep "Fuzzy match\|fuzzy\|E6" /var/log/supervisor/edn360-workflow-service.out.log | tail -20

# Ver si hay errores
tail -n 50 /var/log/supervisor/edn360-workflow-service.err.log

# Ver el plan generado
python3 << EOF
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def get_latest():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['edn360_app']
    plan = await db.training_plans_v2.find_one({}, sort=[("created_at", -1)])
    print(f"Status: {plan.get('status')}")
    print(f"Tiene plan: {bool(plan.get('plan'))}")
    if plan.get('plan'):
        sessions = plan['plan'].get('sessions', [])
        print(f"Sesiones: {len(sessions)}")
        if sessions:
            ejercicios = sessions[0].get('bloques_estructurados', {}).get('B', {}).get('exercises', [])
            print(f"Ejercicios sesión 1: {len(ejercicios)}")
            for ej in ejercicios[:3]:
                print(f"  - {ej.get('exercise_code')}: {ej.get('name', 'SIN NOMBRE')}")
    await client.close()

asyncio.run(get_latest())
